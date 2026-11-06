"""Exercise the actual startup scheduler with two seats and legacy settings."""
from pathlib import Path
import subprocess
import tempfile

here = Path(__file__).resolve().parent
stubs = {
'android/content/BroadcastReceiver': 'public abstract class BroadcastReceiver { public abstract void onReceive(Context c,Intent i); }',
'android/content/Context': 'public class Context { public Intent sticky=new Intent(); public Intent registerReceiver(BroadcastReceiver r,IntentFilter f){return sticky;} public Intent registerReceiver(BroadcastReceiver r,IntentFilter f,String p,android.os.Handler h){return sticky;} }',
'android/content/Intent': 'public class Intent { public int status; public String getAction(){return "com.hkmc.intent.action.ACTION_ACC_STATUS_CHANGED";} public int getIntExtra(String k,int d){return status;} }',
'android/content/IntentFilter': 'public class IntentFilter { public IntentFilter(String a){} }',
'android/os/Looper': 'public class Looper {}',
'android/os/HandlerThread': 'public class HandlerThread { public HandlerThread(String s){} public void start(){} public Looper getLooper(){return new Looper();} }',
'android/os/Handler': 'public class Handler { public Handler(Looper l){} public java.util.List<Runnable> q=new java.util.ArrayList<Runnable>(); public boolean post(Runnable r){q.add(r);return true;} public boolean postDelayed(Runnable r,long n){return post(r);} public void runAll(){int n=0;while(!q.isEmpty()){if(n++>100)throw new AssertionError("unbounded");q.remove(0).run();}} }',
'android/os/ServiceManager': 'public class ServiceManager { public static Object getService(String s){return s;} }',
'hmgapi/hook/ModEntry': 'public class ModEntry { public void zygoteInit(ModContext m){} }',
'hmgapi/hook/ModContext': '''public class ModContext {
 public java.util.Map<String,Object> settings=new java.util.HashMap<String,Object>();
 public boolean enabled(){return true;}
 public boolean settingBoolean(String k,boolean d){Object v=settings.get(k);return v==null?d:(Boolean)v;}
 public String settingString(String k,String d){Object v=settings.get(k);return v==null?d:(String)v;}
 public void log(String s){}
 public Object hook(ClassLoader l,String p,MethodHook h){return null;}
}''',
'hmgapi/hook/MethodHook': '''public class MethodHook {
 protected void afterHookedMethod(Param p)throws Throwable{}
 public static class Param {public Object[] args;public Object getResult(){return null;}public boolean hasThrowable(){return false;}}
}''',
'hmgapi/hook/Points': '''public class Points {
 public static int right=2,left=2;public static boolean failRight,loseReply;
 public static java.util.List<String> writes=new java.util.ArrayList<String>();
 public static Object get(ClassLoader l,String p,Object o){return p;}
 public static Object call(ClassLoader l,String p,Object o,Object...a){
  if(p.endsWith("_service_stub.as_interface"))return o;
  if(p.endsWith("ast_seat_heat_state")){if(failRight)throw new RuntimeException();return right;}
  if(p.endsWith("drv_seat_heat_state"))return left;
  if(p.contains("seat_heat_")){writes.add(p+" "+a[0]);if(loseReply)throw new RuntimeException();return null;}
  throw new AssertionError(p);
 }
}'''
}
test = '''
package hmgapi.mods.creta;
import hmgapi.hook.*;
import android.content.*;
import android.os.*;
import java.lang.reflect.*;
public class SchedulerTest {
 static void check(int right,int left,boolean fail,boolean lose,
                   boolean driver,boolean passenger,String level,String passengerLevel,String expected)throws Exception{
  Points.right=right;Points.left=left;Points.failRight=fail;Points.loseReply=lose;Points.writes.clear();
  ModContext mod=new ModContext();mod.settings.put("startup_enabled",driver);
  mod.settings.put("level",level);
  if(passenger){mod.settings.put("passenger_enabled",true);mod.settings.put("passenger_level",passengerLevel);}
  AutoVent vent=new AutoVent(); Context context=new Context();Handler worker=new Handler(new Looper());
  Method method=AutoVent.class.getDeclaredMethod("scheduleSeats",ModContext.class,Context.class,Handler.class,IntentFilter.class,int.class);
  method.setAccessible(true);
  method.invoke(vent,mod,context,worker,new IntentFilter("test"),0);
  worker.runAll();
  assert Points.writes.toString().equals(expected):Points.writes;
  method.invoke(vent,mod,context,worker,new IntentFilter("test"),0);
  worker.runAll();assert Points.writes.toString().equals(expected):"duplicate start wrote again";
 }
 public static void main(String[] args)throws Exception{
  String right="framework.usm_service.seat_heat_passenger";
  String left="framework.usm_service.seat_heat_driver";
  check(2,2,false,false,true,false,"medium","high","["+right+" 4]");
  check(2,2,false,false,true,true,"high","low","["+right+" 5, "+left+" 3]");
  check(4,2,false,false,true,true,"high","medium","["+left+" 4]");
  check(2,2,false,false,false,true,"high","low","["+left+" 3]");
  check(2,2,true,false,true,true,"high","low","["+left+" 3]");
  check(2,2,false,true,true,true,"high","medium","["+right+" 5, "+left+" 4]");
  check(2,2,false,false,false,false,"high","high","[]");
  System.out.println("PASS actual scheduler: legacy driver settings, passenger default off, independent levels, occupied selections, failures and no repeated writes");
 }
}
'''
with tempfile.TemporaryDirectory() as temp:
    root = Path(temp)
    files = []
    for name, body in stubs.items():
        p = root/(name+'.java')
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('package '+name.rsplit('/',1)[0].replace('/','.')+';\n'+body)
        files.append(p)
    test_file = root/'SchedulerTest.java'
    test_file.write_text(test)
    subprocess.run(['javac','--release','8','-d',root,*files,test_file,
                    here/'AutoVent.java',here/'StartCycle.java',here/'SeatTarget.java'],check=True)
    subprocess.run(['java','-ea','-cp',root,'hmgapi.mods.creta.SchedulerTest'],check=True)
