#!/usr/bin/env python3
"""Create synthetic roster and secret outside the code repository. Idempotent."""
import argparse,csv,os,secrets
from pathlib import Path
from evaluation_config import rut_dv

def demo_rows(n=50):
    # Synthetic data: not a claim that these RUTs are unassigned. Never use with real persons.
    return [(f'{90000000+i}-{rut_dv(90000000+i)}',f'prueba{i:02d}@example.invalid') for i in range(1,n+1)]

def create(path):
    path.mkdir(parents=True,exist_ok=True,mode=0o700)
    roster=path/'estudiantes_demo.csv';key=path/'clave.hex'
    if not roster.exists():
        with os.fdopen(os.open(roster,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w',newline='') as f:
            w=csv.writer(f);w.writerow(['rut','correo']);w.writerows(demo_rows())
    if not key.exists():
        with os.fdopen(os.open(key,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as f:f.write(secrets.token_hex(32)+'\n')
    return roster,key

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('directorio',type=Path,nargs='?',default=Path.home()/'.local/share/eee-evaluaciones/131-demo');a=p.parse_args();r,k=create(a.directorio);print('Lista ficticia:',r);print('Clave privada creada o conservada:',k);print('Primer estudiante de prueba:',*demo_rows()[0])
