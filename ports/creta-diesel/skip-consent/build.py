"""Build a same-size, checksum-gated ODEX patch with the existing HMG-API tool.

Only the normal startup call changes: T(0) -> dc(). No APK rebuild, deodex
reassembly, new core tool, profile/password change, or background timer.
"""
import argparse
import hashlib
import io
import json
import struct
import subprocess
import tempfile
import zlib
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
REF = json.loads((HERE / 'reference.json').read_text())


def digest(data, algorithm='md5'):
    return hashlib.new(algorithm, data).hexdigest()


def patched_odex(raw):
    if digest(raw, 'sha256') != REF['odex_sha256']:
        raise ValueError('Wrong SystemUI ODEX')
    result = bytearray(raw)
    offset, length = struct.unpack_from('<II', raw, 8)
    assert raw[:8] == b'dey\n036\x00' and raw[offset:offset+8] == b'dex\n035\x00'
    assert struct.unpack_from('<I', raw, offset+8)[0] == zlib.adler32(raw[offset+12:offset+length]) & 0xffffffff
    at = REF['instruction_file_offset']
    assert raw[at:at+6].hex() == REF['instruction_before']
    result[at:at+6] = bytes.fromhex(REF['instruction_after'])
    # Dalvik's optimized DEX checksum covers the modified code. Preserve the
    # original SHA1 identifier, dependency table, register maps, and ODEX header:
    # the SHA1 identifies the pre-optimization DEX, not the optimized bytes.
    checksum = zlib.adler32(result[offset+12:offset+length]) & 0xffffffff
    struct.pack_into('<I', result, offset+8, checksum)
    assert len(result) == len(raw)
    changed = {i for i, (a, b) in enumerate(zip(raw, result)) if a != b}
    assert changed <= set(range(at, at+6)) | set(range(offset+8, offset+12))
    assert result[:offset] == raw[:offset] and result[offset+length:] == raw[offset+length:]
    if 'patched_odex_md5' in REF:
        assert digest(result) == REF['patched_odex_md5']
    return bytes(result)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('stock-dir', 'baseline', 'key', 'engine-classes', 'lpatch', 'output'):
        p.add_argument('--'+name, type=Path, required=True)
    p.add_argument('--java', required=True)
    a = p.parse_args()
    if a.output.exists():
        p.error('Use a new output filename')
    if digest((a.stock_dir/'SystemUI.apk').read_bytes(), 'sha256') != REF['apk_sha256']:
        p.error('Wrong SystemUI APK')
    if digest(a.baseline.read_bytes(), 'sha256') != '04e0834b0965c6ac7524b9ae9ee35aadeb9a192a04c861fd842d995fe7101706':
        p.error('Expected tested stage08 wrapper')
    raw = (a.stock_dir/'SystemUI.odex').read_bytes()
    patched = patched_odex(raw)
    with tempfile.TemporaryDirectory(prefix='creta-odex-skip-') as tmp:
        work = Path(tmp)
        mod = work/'mod'
        mod.mkdir()
        target = work/'SystemUI.odex'
        target.write_bytes(patched)
        recipe = subprocess.check_output(['python3', str(REPO/'tools/mkrecipe.py'),
                  'creta-skip-consent', '/system/priv-app/SystemUI.odex',
                  str(a.stock_dir/'SystemUI.odex'), str(target)])
        (mod/'systemui.recipe').write_bytes(recipe)
        rebuilt = work/'rebuilt.odex'
        subprocess.run([str(a.lpatch), 'apply', str(mod/'systemui.recipe'),
                        str(a.stock_dir/'SystemUI.odex'), str(rebuilt)], check=True)
        assert rebuilt.read_bytes() == patched
        changes = {'changes':[{'type':'recipe','path':'/system/priv-app/SystemUI.odex',
                              'stock':REF['odex_md5'],'recipe':'systemui.recipe'}]}
        (mod/'patches.json').write_text(json.dumps(changes,indent=2)+'\n')
        (mod/'mod.json').write_bytes((HERE/'mod.json').read_bytes())
        signer = [a.java,'-cp',str(a.engine_classes),'hmgapi.engine.Signing']
        subprocess.run([*signer,'sign',str(mod),str(a.key)],check=True)
        subprocess.run([*signer,'verify',str(mod)],check=True)
        payload = io.BytesIO()
        with ZipFile(payload,'w',ZIP_DEFLATED) as z:
            for f in sorted(mod.rglob('*')):
                if f.is_file():z.write(f,f.relative_to(mod))
        with ZipFile(a.baseline) as base:
            with ZipFile(io.BytesIO(base.read('mod/package.zip'))) as inner:
                author=json.loads(inner.read('META-HMGAPI/manifest.json'))['uuid']
            assert json.loads((mod/'META-HMGAPI/manifest.json').read_text())['uuid']==author
            pre=(HERE/'preinstall.sh').read_text().replace('@APK_MD5@',REF['apk_md5']).replace('@ODEX_MD5@',REF['odex_md5']).replace('@PATCHED_MD5@',digest(patched))
            a.output.parent.mkdir(parents=True,exist_ok=True)
            with ZipFile(a.output,'x',ZIP_DEFLATED) as z:
                z.write(HERE/'NEMESIS.data','NEMESIS.data')
                z.writestr('mod/id','creta-skip-consent\n')
                z.writestr('mod/package.zip',payload.getvalue())
                z.writestr('scripts/preinstall.sh',pre)
                for name in ('bin/open.sh','scripts/postinstall.sh','scripts/preuninstall.sh'):
                    z.writestr(name,base.read(name))
        report={'stock_odex_md5':digest(raw),'patched_odex_md5':digest(patched),
                'modified_instruction_offset':hex(REF['instruction_file_offset']),
                'changed_bytes':sum(a!=b for a,b in zip(raw,patched)),
                'apk':'unchanged','core_tools':'unchanged','package_sha256':digest(a.output.read_bytes(),'sha256'),
                'on_car':'not tested'}
        a.output.with_suffix('.build.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(report,indent=2))


if __name__ == '__main__':main()
