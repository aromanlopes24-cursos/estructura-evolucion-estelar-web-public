"""Private configuration: RUT/email allowlist and signing key. Never commit real data."""
import csv, io, json, os, re, secrets
from pathlib import Path
from dataclasses import dataclass

class EvaluationError(ValueError): pass

def normalize_rut(raw):
    s=re.sub(r'[.\-\s]', '', str(raw)).upper()
    if not re.fullmatch(r'[0-9]{1,8}[0-9K]',s):
        raise EvaluationError('RUT no válido. Incluya el dígito verificador.')
    body=str(int(s[:-1])); dv=s[-1]
    if int(body)==0 or rut_dv(body)!=dv:
        raise EvaluationError('RUT no válido. Revise el dígito verificador.')
    return body+'-'+dv

def rut_dv(body):
    n=11-sum(int(c)*(2+i%6) for i,c in enumerate(reversed(str(body))))%11
    return '0' if n==11 else 'K' if n==10 else str(n)

def norm_email(raw):
    s=str(raw).strip().lower()
    if len(s)>200 or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',s):
        raise EvaluationError('Correo electrónico no válido.')
    return s

def norm_name(raw):
    s=' '.join(str(raw).split())
    if not 2<=len(s)<=120 or not any(c.isalpha() for c in s):
        raise EvaluationError('Ingrese su nombre y apellido(s).')
    return s

@dataclass(frozen=True)
class Config:
    roster: dict
    key: bytes
    professor_email: str
    mode: str

    def match(self,rut,email):
        r=normalize_rut(rut); e=norm_email(email)
        if self.roster.get(r)!=e:
            raise EvaluationError('No se pudo validar la identificación. Revise los datos o contacte al profesor.')
        return r,e

def load_config(get=os.environ.get):
    mode=get('EEE_MODE','demo')
    if mode not in ('demo','roster'):
        raise EvaluationError('Configuración de modo no válida.')
    raw=get('EEE_ROSTER_CSV','')
    if not raw:
        path=get('EEE_ROSTER_PATH','')
        if not path: raise EvaluationError('Falta la lista privada de estudiantes habilitados.')
        raw=Path(path).expanduser().read_text(encoding='utf-8-sig')
    reader=csv.DictReader(io.StringIO(raw.lstrip('\ufeff')))
    if not {'rut','correo'}.issubset(reader.fieldnames or []):
        raise EvaluationError('CSV requiere columnas rut,correo.')
    roster={}; emails=set()
    for row in reader:
        if not any(str(v or '').strip() for v in row.values()): continue
        r=normalize_rut(row['rut']);e=norm_email(row['correo'])
        if r in roster or e in emails: raise EvaluationError('RUT o correo duplicado en lista.')
        if mode=='demo' and not e.endswith('@example.invalid'): raise EvaluationError('Modo demo: sólo correos ficticios @example.invalid.')
        roster[r]=e;emails.add(e)
    if not 1<=len(roster)<=120: raise EvaluationError('La lista debe tener entre 1 y 120 estudiantes.')
    key=get('EEE_SIGNING_KEY','')
    if not key:
        path=get('EEE_KEY_PATH','')
        if not path: raise EvaluationError('Falta clave privada de verificación.')
        key=Path(path).expanduser().read_text().strip()
    if not re.fullmatch(r'[a-fA-F0-9]{64}',key): raise EvaluationError('Clave privada inválida (64 caracteres hexadecimales).')
    professor=get('EEE_PROFESSOR_EMAIL','').strip()
    if professor: professor=norm_email(professor)
    if mode=='roster' and not professor: raise EvaluationError('Configure el correo institucional del profesor.')
    return Config(dict(sorted(roster.items())),bytes.fromhex(key),professor,mode)
