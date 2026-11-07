package creta.capture;
import java.io.*;
import java.lang.reflect.*;
import java.util.*;
/** One-shot metadata and explicitly reviewed cache getters. Never invokes a setter. */
public final class CapabilityRead {
 public static void main(String[] args) throws Exception {
  String product=(String)Class.forName("android.os.SystemProperties").getMethod("get",String.class).invoke(null,"ro.build.product");
  if(!"SU2IFL.IND.0000.V010.001.260430".equals(product))throw new SecurityException("wrong product");
  File output=new File(args[0]);
  PrintWriter schema=new PrintWriter(new File(output,"runtime-interfaces.txt"));
  PrintWriter reads=new PrintWriter(new File(output,"cached-readings.tsv"));
  reads.println("service\tmethod\tresult");
  BufferedReader input=new BufferedReader(new FileReader(args[1]));
  String line; Map<String,Object> services=new HashMap<String,Object>();
  try {
   while((line=input.readLine())!=null){
    String[] p=line.split("\\t"); if(p.length!=3)continue;
    String field=p[0],type=p[1],name=p[2];
    // The generated list contains only no-argument get/is methods with primitive results.
    if(!(name.startsWith("get")||name.startsWith("is")))throw new SecurityException("non-reader");
    try {
     Class<?> iface=Class.forName(type); Method method=iface.getMethod(name);
     Class<?> result=method.getReturnType();
     if(method.getParameterTypes().length!=0||!result.isPrimitive()||result==Void.TYPE)throw new SecurityException("unsafe signature");
     if(!services.containsKey(type)){
      String service=(String)Class.forName("com.hkmc.Service").getField(field).get(null);
      Object binder=Class.forName("android.os.ServiceManager").getMethod("getService",String.class).invoke(null,service);
      Object proxy=Class.forName(type+"$Stub").getMethod("asInterface",Class.forName("android.os.IBinder")).invoke(null,binder);
      services.put(type,proxy);
      ArrayList<String> signatures=new ArrayList<String>();
      for(Method m:iface.getDeclaredMethods())signatures.add(m.toGenericString());
      Collections.sort(signatures); for(String s:signatures)schema.println(s);schema.flush();
     }
     Object proxy=services.get(type);
     if(proxy==null)reads.println(field+"\t"+name+"\tUNAVAILABLE");
     else reads.println(field+"\t"+name+"\t"+method.invoke(proxy));
    }catch(Throwable t){reads.println(field+"\t"+name+"\tERROR:"+t.getClass().getSimpleName());}
    reads.flush(); Thread.sleep(10);
   }
  } finally {input.close();schema.close();reads.close();}
  new File(output,"CACHE-READS-FINISHED.txt").createNewFile();
 }
}
