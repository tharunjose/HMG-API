"""Validate the built ZIP using Nemesis's actual native metadata parser."""
import argparse
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

p = argparse.ArgumentParser()
p.add_argument('--nemesis-source', type=Path, required=True, help='Nemesis Sources directory')
a = p.parse_args()
here = Path(__file__).resolve().parent
harness = r'''#include "nemesis.h"
int read_file(const char *path,char *buf,size_t cap) {
    FILE *f=fopen(path,"rb"); if(!f)return -1;
    size_t n=fread(buf,1,cap-1,f); buf[n]=0; fclose(f); return (int)n;
}
int main(int argc,char **argv) {
    ini_file ini; pkg_meta m; char err[1024],reasons[1024];
    if(argc!=2)return 2;
    if(ini_load(&ini,argv[1]))return 3;
    int rc=meta_parse(&ini,&m,err,sizeof(err));
    if(rc) { printf("%s\n",err); ini_free(&ini); return 1; }
    int c=meta_compat(&m,"SU2IFL.IND.0000.V010.001.260430","su2ifl_in",NULL,reasons,sizeof(reasons));
    ini_free(&ini);
    if(c!=COMPAT_FULL)return 4;
    puts("parsed; full compatibility"); return 0;
}
'''
with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp)
    (root/'check.c').write_text(harness)
    native=a.nemesis_source.resolve()/'native'
    subprocess.run(['cc','-Wall','-Wextra','-I',str(native),str(root/'check.c'),
                    str(native/'ini.c'),str(native/'meta.c'),'-o',str(root/'check')],check=True)
    subprocess.run([sys.executable,str(here/'build.py'),'--out',str(root/'built')],check=True)
    with zipfile.ZipFile(root/'built/creta-vehiclesettings-capture.zip') as z:
        fixed=z.read('NEMESIS.data').decode()
    (root/'fixed.data').write_text(fixed)
    subprocess.run([str(root/'check'),str(root/'fixed.data')],check=True)
    old=fixed.replace('Copies Vehicle Settings and UI files for offline analysis.',
                     'Copies the vehicle settings app and UI dependencies for offline analysis.')
    assert old != fixed
    (root/'old.data').write_text(old)
    r=subprocess.run([str(root/'check'),str(root/'old.data')],capture_output=True,text=True)
    assert r.returncode==1 and 'short-desc is over 64 characters' in r.stdout, r
    print('PASS: original rejection reproduced; corrected ZIP descriptor accepted')
