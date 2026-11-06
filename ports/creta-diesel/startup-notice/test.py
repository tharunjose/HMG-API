"""Test bounded dismissal and restoration of the pre-install permission choices."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile

here = Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as temp:
    root = Path(temp)
    binary = root/'system/bin/hmgapid'
    binary.parent.mkdir(parents=True)
    allow = root/'data/hmgapi/settings/allow'
    allow.mkdir(parents=True)
    binary.write_text('''#!/bin/sh
case "$1" in
 allow)
  if [ "$3" = on ]; then echo on > "$ROOT/data/hmgapi/settings/allow/$2"
  else rm -f "$ROOT/data/hmgapi/settings/allow/$2"; fi;;
 vehicle) echo "gear.park $TEST_PARK";;
 vehicle-do) echo "$*" >> "$ROOT/calls"; echo 'ok startup notice dismissed';;
esac
''')
    binary.chmod(0o700)
    scripts = root/'scripts'
    scripts.mkdir()
    for p in here.glob('*.sh'):
        shutil.copyfile(p,scripts/p.name)
    (scripts/'postinstall-engine.sh').write_text('exit 0\n')
    (scripts/'preuninstall-engine.sh').write_text('exit 0\n')
    env = dict(os.environ, ROOT=str(root), TEST_PARK='1')
    command_permission = allow/'cmd.creta-startup-notice.startup_notice'
    command_permission.write_text('on')
    subprocess.run(['sh',scripts/'postinstall.sh'],cwd=root,env=env,check=True)
    assert (allow/'startup_notice').exists() and command_permission.exists()
    subprocess.run(['sh',scripts/'postinstall.sh'],cwd=root,env=env,check=True)
    subprocess.run(['sh',scripts/'preuninstall.sh'],cwd=root,env=env,check=True)
    assert not (allow/'startup_notice').exists() and command_permission.exists()
    (scripts/'postinstall-engine.sh').write_text('exit 1\n')
    assert subprocess.run(['sh',scripts/'postinstall.sh'],cwd=root,env=env).returncode==1
    assert not (allow/'startup_notice').exists() and command_permission.exists()
    # Only the exact one-shot request may reach the fake vehicle, after a valid Park reading.
    (root/'sleep').write_text('#!/bin/sh\nexit 0\n')
    (root/'sleep').chmod(0o700)
    code=(here/'dismiss.sh').read_text().replace(
        'export PATH=/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin',
        'export PATH='+str(root)+':/usr/bin:/bin').replace('H=/system/bin/hmgapid','H='+str(binary))
    for state in ('1','0','-'):
        calls = root/'calls'
        calls.unlink(missing_ok=True)
        result=subprocess.run(['sh','-c',code],cwd=root,env=dict(env,TEST_PARK=state),capture_output=True)
        if state=='1':
            assert result.returncode==0 and calls.read_text()=='vehicle-do startup_notice dismiss\n'
        else:
            assert not calls.exists()
print('PASS Park gate, bounded unavailable state, single request, prior permissions and installer failure restoration.')
