"""Exercise the shipped receiver and its cluster calls against a clock and a broadcast fixture."""
from pathlib import Path
import subprocess, tempfile, sys
here = Path(__file__).resolve().parent
stubs = {
'android/content/Context': '''public BroadcastReceiver r; public int n; public Context getApplicationContext(){return this;} public Intent registerReceiver(BroadcastReceiver r,IntentFilter f){n++;this.r=r;return null;}''',
'android/content/BroadcastReceiver': '''public boolean sticky; public boolean isInitialStickyBroadcast(){return sticky;} public void onReceive(Context c,Intent i){}''',
'android/content/IntentFilter': '''public IntentFilter(String action){if(!action.endsWith(".NAVI_GPS_CHANGED"))throw new AssertionError();}''',
'android/content/Intent': '''public String action; public int heading; public String getAction(){return action;} public int getIntExtra(String k,int d){return k.equals("com.hkmc.telematics.gis.extra.HEADING")?heading:d;}''',
'android/os/SystemClock': '''public static long t; public static long elapsedRealtime(){return t;}'''
}
test = '''
package hmgapi.mods.wireless.dipo;
import android.content.*;
import android.os.SystemClock;
import hmgapi.hook.Cluster;
class CheckCompass {
    public static void main(String[] args) {
        Context x=new Context(); Cluster c=new Cluster(); Intent i=new Intent();
        DieselCompass.watch(x); DieselCompass.watch(x);
        assert x.n==1 && !DieselCompass.restore(c);
        i.action=DieselCompass.ACTION; i.heading=120;
        x.r.sticky=true; x.r.onReceive(x,i); assert !DieselCompass.restore(c);
        x.r.sticky=false; x.r.onReceive(x,i); assert DieselCompass.restore(c);
        assert c.calls.toString().equals("[tbt 8 0 247.5 0.0 0 0 0 0 -1]"): c.calls;
        c.calls.clear(); SystemClock.t=30001; assert !DieselCompass.restore(c);
        i.action="wrong"; x.r.onReceive(x,i); assert !DieselCompass.restore(c);
        i.action=DieselCompass.ACTION; i.heading=361; x.r.onReceive(x,i);
        assert !DieselCompass.restore(c) && c.calls.isEmpty();
        i.heading=360; x.r.onReceive(x,i); assert DieselCompass.restore(c);
        assert c.calls.get(0).equals("tbt 8 0 0.0 0.0 0 0 0 0 -1");
    }
}
'''
with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp); files=[sys.argv[1], here/'DieselCompass.java']
    for name,body in stubs.items():
        f=root/(name+'.java'); f.parent.mkdir(parents=True,exist_ok=True)
        pkg, cls=name.rsplit('/',1)
        f.write_text('package '+pkg.replace('/','.')+'; public class '+cls+'{'+body+'}')
        files.append(f)
    f=root/'CheckCompass.java'; f.write_text(test); files.append(f)
    subprocess.run(['javac','--release','8','-d',root,*files],check=True)
    subprocess.run(['java','-ea','-cp',root,'hmgapi.mods.wireless.dipo.CheckCompass'],check=True)
print('PASS: one listener; no heading, sticky, unrelated, invalid and stale inputs ignored; fresh OEM heading produces one main compass frame.')
