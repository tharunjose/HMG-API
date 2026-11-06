"""Derive a signed, optional diesel stop-display trial from a trusted stage 08 package."""
import argparse
import hashlib
import json
import re
import subprocess
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REF = json.loads((HERE / 'reference.json').read_text())
p = argparse.ArgumentParser(description=__doc__)
for name in ('baseline', 'key', 'engine-classes', 'baksmali', 'output'):
    p.add_argument('--' + name, type=Path, required=True)
p.add_argument('--smali-classpath', required=True)
p.add_argument('--java', default='java')
a = p.parse_args()
if not a.key.is_file() or a.output.exists():
    p.error('An existing owner key and a new output filename are required')

def run(*args):
    subprocess.run([a.java, *map(str, args)], check=True)

def signing(op, folder, *extra):
    run('-cp', a.engine_classes, 'hmgapi.engine.Signing', op, folder, *extra)

def pack(folder, target):
    with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for file in sorted(folder.rglob('*')):
            if file.is_file():
                z.write(file, file.relative_to(folder))

def disassemble(file, folder):
    run('-jar', a.baksmali, 'd', '-a', '19', file, '-o', folder)

def digest(file):
    return hashlib.sha256(file.read_bytes()).hexdigest()

with tempfile.TemporaryDirectory(prefix='diesel-stop-build-') as tmp:
    work = Path(tmp)
    outer, mod = work/'wrapper', work/'mod'
    with zipfile.ZipFile(a.baseline) as z:
        z.extractall(outer)
    inner = outer/'mod/package.zip'
    with zipfile.ZipFile(inner) as z:
        z.extractall(mod)
    signing('verify', mod)
    manifest = mod/'META-HMGAPI/manifest.json'
    author = json.loads(manifest.read_text())['uuid']
    meta = json.loads((mod/'mod.json').read_text())
    assert meta['id'] == 'wireless-carplay-aa' and meta['version'] == '2.5.0-diesel.1'
    assert meta['system']['product'] == 'SU2IFL.IND.0000.V010.001.260430'
    jar = mod/'hooks.jar'
    assert digest(jar) == REF['input_hooks_sha256'], 'Unexpected upstream hooks'
    tree = work/'classes'
    disassemble(jar, tree)
    before = {f.relative_to(tree): digest(f) for f in tree.rglob('*.smali')}
    target = tree/REF['class']
    source = target.read_text()
    for edit in json.loads((HERE/'dex-edits.json').read_text()):
        assert source.count(edit['old']) == 1, edit['old']
        source = source.replace(edit['old'], edit['new'])
    source, count = re.subn(r'(?ms)^\.method stop\(\)V$.*?^\.end method$', lambda _: (HERE/'stop.smali').read_text().strip(), source)
    assert count == 1
    target.write_text(source)
    dex = work/'classes.dex'
    run('-cp', a.smali_classpath, 'org.jf.smali.Main', 'assemble', '-a', '19', tree, '-o', dex)
    assert dex.read_bytes()[:8] == b'dex\n035\x00'
    with zipfile.ZipFile(jar, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        z.write(dex, 'classes.dex')
    checked = work/'checked'
    disassemble(jar, checked)
    after = {f.relative_to(checked): digest(f) for f in checked.rglob('*.smali')}
    assert before.keys() == after.keys()
    assert [str(k) for k in before if before[k] != after[k]] == [REF['class']]
    # Include ONLY the three edited methods and field in the rebuilt class.
    def bodies(code):
        return dict(re.findall(r'(?ms)^\.method ([^\n]+)\n(.*?^\.end method$)', code))
    rebuilt = bodies((checked/REF['class']).read_text())
    original = bodies(source)
    assert set(rebuilt) == set(original)
    # Assembler changes address labels. All untouched method bodies must match exactly.
    changed = {'stop()V', 'turn(Ljava/lang/Integer;Lhmgapi/mods/wireless/dipo/CpTurns$Update;)V', 'sessionStarted()V'}
    assert all(rebuilt[k] == v for k, v in original.items() if k not in changed)
    assert '->tbtInfo(IIFFIIIII)V' in rebuilt['stop()V'] and '->mainOwner:' in rebuilt['stop()V']
    meta['version'] = REF['candidate_mod_version']
    (mod/'mod.json').write_text(json.dumps(meta, indent=2)+'\n')
    signing('sign', mod, a.key)
    signing('verify', mod)
    assert json.loads(manifest.read_text())['uuid'] == author, 'Owner key mismatch'
    pack(mod, inner)
    desc = outer/'NEMESIS.data'
    text = desc.read_text()
    assert 'package-version=2.5.0.1\n' in text
    desc.write_text(text.replace('package-version=2.5.0.1\n', 'package-version=2.5.0.2\n'))
    pack(outer, a.output)
    print('Verified original signer, original hooks hash and rebuilt class comparison.')
    print('Output SHA256', digest(a.output))
