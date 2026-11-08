"""Exercise integrity and refusal paths with synthetic files, never an attached car."""
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile

here = Path(__file__).resolve().parent
files = ['app/HKMC_VehicleSetting.apk', 'app/HKMC_VehicleSetting.odex',
         'app/SettingsCommon.apk', 'app/SettingsCommon.odex',
         'framework/hkmc-res.apk', 'framework/framework-res.apk']

def check(mode):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        system = root / 'system'
        storage = root / 'storage'
        usb = storage / 'usb0'
        usb.mkdir(parents=True)
        mock = root / 'mock'
        mock.mkdir()
        for name in files:
            p = system / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(('synthetic:' + name).encode())
        original = {name: (system / name).read_bytes() for name in files}
        (usb / 'CRETA-VEHICLESETTINGS-CAPTURE').write_text('fixture')
        (system / 'bin').mkdir()
        hash_tool = system / 'bin/lpatch'
        hash_tool.write_text('#!' + sys.executable + '\n' + '''import hashlib,sys,os
p=sys.argv[2]
if os.environ['MODE']=='hash-tool-failure': sys.exit(9)
if os.environ['MODE']=='empty-hash': sys.exit(0)
if os.environ['MODE']=='malformed-hash': print('z'*32); sys.exit(0)
if os.environ['MODE']=='copy-corrupt' and '/storage/' in p: print('0'*32); sys.exit(0)
print(hashlib.md5(open(p,'rb').read()).hexdigest())
''')
        hash_tool.chmod(0o755)
        (mock / 'getprop').write_text('''#!/bin/sh
case "$1" in
 ro.build.product) [ "$MODE" = wrong-product ] && echo wrong || echo SU2IFL.IND.0000.V010.001.260430;;
 ro.mobis.onebindir) [ "$MODE" = wrong-variant ] && echo wrong || echo su2ifl_in;;
esac
''')
        (mock / 'am').write_text('#!/bin/sh\nexit 0\n')
        (mock / 'sync').write_text('#!/bin/sh\nexit 0\n')
        (mock / 'cp').write_text('''#!/bin/sh
[ "$MODE" = copy-failed ] && exit 1
/bin/cp "$@" || exit 1
if [ "$MODE" = source-changed ]; then echo changed >> "$1"; fi
''')
        for p in mock.iterdir(): p.chmod(0o755)
        if mode == 'no-marker': (usb / 'CRETA-VEHICLESETTINGS-CAPTURE').unlink()
        if mode == 'missing-odex': (system / files[1]).unlink()
        if mode == 'missing-resource': (system / files[-1]).unlink()
        if mode == 'no-hash-tool': hash_tool.unlink()
        if mode == 'preserve':
            (usb / 'CRETA-VEHICLESETTINGS').mkdir()
            (usb / 'CRETA-VEHICLESETTINGS/prior').write_text('keep')
        def translated(name):
            s = (here / name).read_text()
            s = s.replace('export PATH=/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin',
                          'export PATH=' + str(mock) + ':/usr/bin:/bin')
            s = s.replace('/system/', str(system) + '/').replace('/storage/', str(storage) + '/')
            p = root / name
            p.write_text(s)
            return p
        env = dict(os.environ, MODE=mode, PATH=str(mock) + ':/usr/bin:/bin')
        pre = subprocess.run(['/bin/sh', translated('preinstall.sh')], env=env, capture_output=True)
        assert (pre.returncode != 0) == (mode in ['wrong-product','wrong-variant','no-hash-tool','missing-odex']), mode
        result = subprocess.run(['/bin/sh', translated('capture.sh')], env=env,
                                capture_output=True, timeout=15)
        good = mode in ['success', 'preserve']
        assert (result.returncode == 0) == good, (mode, result.stdout, result.stderr)
        dirs = sorted(usb.glob('CRETA-VEHICLESETTINGS*'))
        reports = [p for p in dirs if p.is_dir()]
        if mode in ['wrong-product','wrong-variant','no-marker','no-hash-tool']:
            assert not reports, mode
        else:
            report = usb / ('CRETA-VEHICLESETTINGS-2' if mode == 'preserve' else 'CRETA-VEHICLESETTINGS')
            assert (report / 'COMPLETE.txt').exists() == good, mode
            if good:
                lines = (report / 'MD5SUMS').read_text().splitlines()
                assert len(lines) == 6
                for name in files:
                    p = report / Path(name).name
                    assert p.read_bytes() == original[name]
                    assert hashlib.md5(p.read_bytes()).hexdigest() + '  ' + p.name in lines
                assert not (report / 'FAILED.txt').exists()
            else:
                assert (report / 'FAILED.txt').exists(), mode
        if mode == 'preserve':
            assert (usb / 'CRETA-VEHICLESETTINGS/prior').read_text() == 'keep'
        if mode != 'source-changed':
            for name, content in original.items():
                if (system / name).exists(): assert (system / name).read_bytes() == content
        print('PASS', mode)

for name in ['capture.sh', 'preinstall.sh']:
    subprocess.run(['/bin/sh', '-n', here / name], check=True)
for mode in ['success','preserve','wrong-product','wrong-variant','no-marker','no-hash-tool',
             'missing-odex','missing-resource','copy-failed','copy-corrupt',
             'hash-tool-failure','empty-hash','malformed-hash','source-changed']:
    check(mode)
