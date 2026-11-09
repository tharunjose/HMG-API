"""Linux container test of the real ARM daemon/client through qemu-arm."""
import os
from pathlib import Path
import signal
import socket
import subprocess
import tempfile
import threading
import time

source=Path('/src')
with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp);(root/'state').mkdir();(root/'mods').mkdir()
    sockname='creta-base-test-'+str(os.getpid());vehicle=sockname+'-vehicle'
    out=root/'bin';out.mkdir()
    env=dict(os.environ,OUT=str(out))
    subprocess.run(['sh','core/hmgapid/build.sh','-DNOCAPCHECK','-DROOTDIR="'+str(root)+'"',
                    '-DSH="/bin/sh"','-DSOCK_NAME="'+sockname+'"','-DVEHICLE_SOCK="'+vehicle+'"',
                    '-DBOOTMARK="'+str(root/'bootmark')+'"'],cwd=source,env=env,check=True)
    cmd=['qemu-arm',str(out/'hmgapid')]
    (root/'boot.sh').write_text('#!/bin/sh\necho run >> "'+str(root/'bootcount')+'"\n/bin/sleep 4\n')
    start=time.monotonic()
    r=subprocess.run(cmd+['boot'],capture_output=True,timeout=2)
    assert r.returncode==0 and time.monotonic()-start<2,r
    for _ in range(50):
        if (root/'bootcount').exists():break
        time.sleep(.05)
    assert (root/'bootcount').read_text()=='run\n'
    subprocess.run(cmd+['boot'],capture_output=True,check=True,timeout=2)
    time.sleep(.1);assert (root/'bootcount').read_text()=='run\n'
    print('PASS boot returns without waiting; repeated trigger runs once',flush=True)
    def case(name,fields,chunks,expected,keep=False):
        server=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);server.bind('\0'+vehicle);server.listen(1)
        request=[]
        def serve():
            conn,_=server.accept();request.append(conn.recv(1024))
            try:
                for chunk in chunks:
                    conn.sendall(chunk);time.sleep(.015)
                if keep:time.sleep(3.3)
            except BrokenPipeError:pass
            finally:conn.close();server.close()
        t=threading.Thread(target=serve);t.start();start=time.monotonic()
        r=subprocess.run(cmd+['vehicle',*fields],capture_output=True,timeout=5)
        duration=time.monotonic()-start;t.join()
        assert r.returncode==expected,(name,r.returncode,r.stdout,r.stderr)
        if expected:assert r.stdout==b'',(name,r.stdout)
        else:
            assert r.stdout==b''.join(chunks),(name,r.stdout)
            if keep:assert duration<2,(name,duration)
        assert request[0]==('read '+' '.join(fields)+'\n').encode(),request
        print('PASS',name,'rc',r.returncode,flush=True)
    fields=['battery12v.soc','gear.park']
    case('single complete socket left open',[fields[0]],[b'battery12v.soc 79\n'],0,True)
    case('multi fragmented socket left open',fields,[b'battery12',b'v.soc 79\ngear.',b'park 1\n'],0,True)
    case('unavailable sentinel',[fields[0]],[b'battery12v.soc -\n'],0)
    case('partial close',fields,[b'battery12v.soc 79\n'],1)
    case('partial timeout',fields,[b'battery12v.soc 79\n'],1,True)
    case('empty close',fields,[],1)
    case('truncated final line',fields,[b'battery12v.soc 79\ngear.park 1'],1)
    case('wrong field',fields,[b'battery12v.soc 79\nwrong 1\n'],1)
    case('duplicate field',fields,[b'battery12v.soc 79\nbattery12v.soc 80\n'],1)
    case('extra line',fields,[b'battery12v.soc 79\ngear.park 1\nextra 1\n'],1)
    for _ in range(12):case('repeat connection',[fields[0]],[b'battery12v.soc 79\n'],0)
    # The daemon's children cannot outlive this disposable container. No host daemon is touched.
