"""Run the upstream parser suite with a regression that fails before the candidate fix."""
from pathlib import Path
import argparse,json,shutil,subprocess,tempfile
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);a=p.parse_args()
here=Path(__file__).resolve().parent
change=json.loads((here/'source-change.json').read_text())
with tempfile.TemporaryDirectory(prefix='creta-cancel-tests-') as tmp:
    mod=Path(tmp)/'wireless-carplay-aa'
    shutil.copytree(a.source/'mods/wireless-carplay-aa',mod)
    test=mod/'tools/cpturns/test/hmgapi/mods/wireless/dipo/CpTurnsTest.java'
    s=test.read_text()
    for title in ['India route stop still clears HUD','state 0: HUD cleared',
                  'source change (Maps to Waze): HUD cleared; the reset state is 0 until the phone resends it, so cleared again']:
        start=s.index('expect("'+title+'"');end=s.index(');',start)
        s=s[:end]+', "tbt 0 0 0.0 0.0 -1 0 0 0 -1"'+s[end:]
    # A session disconnect while guiding also clears the main symbol exactly once.
    at='        t.disconnected();\n        expect("iAP2 session ended: HUD cleared"'
    extra='''        t.guiding = true;
        t.disconnected();
        expect("active disconnect clears main cluster once", "2c 0 0 0 0 0 0 0 0 0", "lanes f1", "hud f2", "hud f2", "tbt 0 0 0.0 0.0 -1 0 0 0 -1");
'''
    assert at in s;s=s.replace(at,extra+at,1)
    idle='        c = new Cluster();\n        CpTurns idle = new CpTurns(new android.content.Context(), c, null);\n        idle.stop();\n        expect("fresh idle stop leaves stock main display alone", "2c 0 0 0 0 0 0 0 0 0", "lanes f1", "hud f2", "hud f2");\n'
    s=s.replace('        Car.unit = Car.DISTANCE_MILES;',idle+'        Car.unit = Car.DISTANCE_MILES;',1)
    test.write_text(s)
    cmd=['sh',str(mod/'tools/cpturns/test.sh')]
    before=subprocess.run(cmd,capture_output=True,text=True)
    assert before.returncode!=0 and 'FAIL  state 0: HUD cleared' in before.stdout,before.stdout+before.stderr
    code=mod/'src/hmgapi/mods/wireless/dipo/CpTurns.java';s=code.read_text()
    for edit in change:
        assert s.count(edit['old'])==1, edit['old']
        s=s.replace(edit['old'],edit['new'])
    code.write_text(s)
    after=subprocess.run(cmd,capture_output=True,text=True)
    print(after.stdout,end='');print(after.stderr,end='')
    assert after.returncode==0
print('PASS: original code fails new clearing regression; candidate passes upstream suite including idle/repeated stops, active disconnect and custom display lifecycle.')
