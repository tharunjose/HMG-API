"""Host tests: exact product gate, reader restrictions, bounded/partial shell captures."""
from pathlib import Path
import os,subprocess,tempfile,json,hashlib
HERE=Path(__file__).resolve().parent
JAVA=Path(os.environ['CRETA_JAVA']);JAVAC=JAVA.with_name('javac')
with tempfile.TemporaryDirectory() as t:
 root=Path(t);src=root/'src';cl=root/'classes';cl.mkdir()
 fixtures={
 'android/os/SystemProperties.java':'package android.os; public class SystemProperties { public static String get(String k){return System.getProperty("test.product","SU2IFL.IND.0000.V010.001.260430");}}',
 'android/os/IBinder.java':'package android.os; public interface IBinder {}',
 'android/os/ServiceManager.java':'package android.os; public class ServiceManager {public static IBinder getService(String n){return null;}}',
 'com/hkmc/Service.java':'package com.hkmc; public class Service {public static String USM_SERVICE="test";}',
 'com/hkmc/usm/IUSMService.java':'''package com.hkmc.usm; public interface IUSMService {int getCache(); int getUnavailable(); void setUnsafe(); public static class Stub {public static IUSMService asInterface(android.os.IBinder b){return new IUSMService(){public int getCache(){return 2;} public int getUnavailable(){return -1;} public void setUnsafe(){throw new AssertionError("setter called");}};}}}'''}
 for name,body in fixtures.items():p=src/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(body)
 subprocess.run([str(JAVAC),'--release','8','-d',str(cl),str(HERE/'CapabilityRead.java'),*map(str,src.rglob('*.java'))],check=True)
 allow=root/'readers.tsv';allow.write_text('USM_SERVICE\tcom.hkmc.usm.IUSMService\tgetCache\nUSM_SERVICE\tcom.hkmc.usm.IUSMService\tgetUnavailable\n')
 out=root/'java-out';out.mkdir()
 cmd=[str(JAVA),'-cp',str(cl),'creta.capture.CapabilityRead',str(out),str(allow)]
 subprocess.run(cmd,check=True)
 text=(out/'cached-readings.tsv').read_text();assert 'getCache\t2' in text and 'getUnavailable\t-1' in text
 assert (out/'CACHE-READS-FINISHED.txt').exists()
 bad=subprocess.run([str(JAVA),'-Dtest.product=wrong',*cmd[1:]],capture_output=True);assert bad.returncode!=0
 allow.write_text('USM_SERVICE\tcom.hkmc.usm.IUSMService\tsetUnsafe\n')
 bad=subprocess.run(cmd,capture_output=True);assert bad.returncode!=0 and b'non-reader' in bad.stderr
 # Exercise actual shell control flow with stand-ins; no real system files/services.
 bin=root/'bin';bin.mkdir();usb=root/'usb0';usb.mkdir();(usb/'CRETA-CAPABILITY-CAPTURE').touch()
 bindir=root/'package/bin';bindir.mkdir(parents=True);(bindir/'capture.jar').touch();(bindir/'readers.tsv').write_text('test')
 commands={'getprop':'case "$1" in ro.build.product) echo "${TEST_PRODUCT:-SU2IFL.IND.0000.V010.001.260430}";; ro.mobis.onebindir) echo su2ifl_in;; esac',
 'hmgapid':'echo "read-only $*"','service':'echo test-services','getevent':'echo test-input','pm':'echo test-packages','sync':'exit 0',
 'app_process':'[ "$TEST_PARTIAL" = 1 ] || touch "$3/CACHE-READS-FINISHED.txt"; echo test-reader',
 'sleep':'/bin/sleep 0.05'}
 for name,body in commands.items():f=bin/name;f.write_text('#!/bin/sh\n'+body+'\n');f.chmod(0o755)
 body=(HERE/'capture.sh').read_text().replace('#!/system/bin/sh','#!/bin/sh').replace('export PATH=/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin','export PATH="'+str(bin)+':/usr/bin:/bin"')
 for old,new in [('/system/bin/hmgapid',str(bin/'hmgapid')),('/storage/usb0',str(usb)),('/storage/usb1',str(root/'none1')),('/storage/usb2',str(root/'none2')),('/system/app/',str(root/'system/app')+'/'),('/system/priv-app/',str(root/'system/priv-app')+'/'),('/system/framework/',str(root/'system/framework')+'/'),('/data/hmgapi/',str(root/'data/hmgapi')+'/')]:body=body.replace(old,new)
 script=bindir/'capture.sh';script.write_text(body)
 subprocess.run(['sh','-n',str(script)],check=True)
 subprocess.run(['sh',str(script)],check=True,stdout=subprocess.DEVNULL)
 assert (usb/'CRETA-CAPABILITIES/COMPLETE.txt').exists()
 assert 'TIMEOUT' not in (usb/'CRETA-CAPABILITIES/status.txt').read_text()
 subprocess.run(['sh',str(script)],env=dict(os.environ,TEST_PARTIAL='1'),check=True,stdout=subprocess.DEVNULL)
 assert (usb/'CRETA-CAPABILITIES-2/PARTIAL.txt').exists() and (usb/'CRETA-CAPABILITIES/COMPLETE.txt').exists()
 before=set(usb.iterdir());p=subprocess.run(['sh',str(script)],env=dict(os.environ,TEST_PRODUCT='wrong'),capture_output=True);assert p.returncode!=0 and set(usb.iterdir())==before
 # Confirm the bounded command terminates its own hung child and keeps useful evidence.
 (bin/'getevent').write_text('#!/bin/sh\nexec /bin/sleep 20\n')
 subprocess.run(['sh',str(script)],timeout=5,check=True,stdout=subprocess.DEVNULL)
 assert 'input-devices TIMEOUT' in (usb/'CRETA-CAPABILITIES-3/status.txt').read_text()
 print('PASS cache-reader mock, unknown values retained, setter refused, firmware gate, completion/partial distinction, repeat preservation and bounded timeout.')
