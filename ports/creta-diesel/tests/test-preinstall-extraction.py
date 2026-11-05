"""Regress the preinstall under Nemesis's real 0644 ZIP extraction semantics."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import zipfile

import argparse
ROOT = Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stock',type=Path,required=True)
parser.add_argument('--lpatch',type=Path,required=True)
parser.add_argument('--package',type=Path,default=ROOT/'out/07-base/packages/hmgapi.zip')
args=parser.parse_args()
STOCK = args.stock.resolve()
PACKAGE = args.package.resolve()
with tempfile.TemporaryDirectory(prefix='creta-extraction-') as temp:
    work = Path(temp)
    stage = work / 'stage'
    car = work / 'car'
    shutil.copytree(STOCK, car)
    feature = car / 'system/onebin/su2ifl_in/featurexml.cfg'
    feature.parent.mkdir(parents=True)
    feature.write_text('fixture\n')
    with zipfile.ZipFile(PACKAGE) as archive:
        archive.extractall(stage)
    for path in stage.rglob('*'):
        if path.is_file():
            path.chmod(0o644)
    # Host-built copy of the same lpatch source substitutes for its ARM binary.
    shutil.copyfile(args.lpatch.resolve(), stage / 'payload/lpatch')
    (stage / 'payload/lpatch').chmod(0o644)
    bindir = work / 'bin'
    bindir.mkdir()
    getprop = bindir / 'getprop'
    getprop.write_text('#!/bin/sh\ncase "$1" in ro.build.product) echo "${TEST_PRODUCT:-SU2IFL.IND.0000.V010.001.260430}";; ro.mobis.onebindir) echo su2ifl_in;; esac\n')
    getprop.chmod(0o755)
    env = dict(os.environ, PATH=str(bindir) + ':' + os.environ['PATH'])
    metadata = stage / 'stock.md5'
    metadata.write_text(metadata.read_text().replace('  /system/', '  ' + str(car) + '/system/'))
    script = (stage / 'scripts/preinstall-diesel.sh').read_text()
    script = script.replace('/system/onebin/', str(car) + '/system/onebin/').replace('/data/hmgapi/', str(car) + '/data/hmgapi/')

    def run(body, environment):
        return subprocess.run(['/bin/sh', '-c', body], cwd=stage, env=environment, capture_output=True, text=True)

    old = script.replace('chmod 755 ./payload/lpatch ./payload/hmgapid || exit 1\n', '')
    result = run(old, env)
    assert result.returncode != 0 and 'Permission denied' in result.stderr, result
    print('Reproduced original failure: permission denied before installation.')
    result = run(script, env)
    assert result.returncode == 0, result.stdout + result.stderr
    assert os.access(stage / 'payload/lpatch', os.X_OK)
    assert os.access(stage / 'payload/hmgapid', os.X_OK)
    print('Corrected preinstall passes after every ZIP member starts as 0644.')
    result = run(script, dict(env, TEST_PRODUCT='SU2IEV.IND.0000.V010.001.260430'))
    assert result.returncode != 0 and 'Wrong product' in result.stdout
    (car / 'system/lib/libCarPlayCore.so').write_bytes(b'changed')
    result = run(script, env)
    assert result.returncode != 0 and 'Stock bytes differ' in result.stdout
    print('Wrong-product and modified-stock checks still reject installation.')
