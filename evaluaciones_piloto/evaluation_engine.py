"""Server-side store, deterministic unique assignments and signed receipts.
The roster is an allowlist, not identity authentication. Never publish key or DB.
"""
from __future__ import annotations
import copy, hashlib, hmac, itertools, json, math, os, random, re, secrets, sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from evaluation_config import Config, EvaluationError, norm_name, load_config
from evaluation_questions import EXAM_ID, VERSION, TITLE, QUESTIONS

DECLARATION='Declaro que soy el estudiante identificado y que realizo personalmente esta actividad.'

def utc_now(): return datetime.now(timezone.utc).isoformat(timespec='seconds')
def canonical(obj): return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')
def checksum(obj): return hashlib.sha256(canonical(obj)).hexdigest()
def signature(obj,key): return hmac.new(key,canonical(obj),hashlib.sha256).hexdigest()
def token_hash(token):
    if not isinstance(token,str) or not re.fullmatch(r'[A-Za-z0-9_-]{32,128}',token.strip()): raise EvaluationError('Código de recuperación no válido.')
    return hashlib.sha256(token.strip().encode('ascii')).hexdigest()

def assignment(config,rut):
    # 5! unique permutations, assigned without replacement to the sorted roster.
    # Freeze roster and key during the exercise. Snapshot is also persisted in DB.
    if rut not in config.roster: raise EvaluationError('Estudiante no habilitado.')
    i=list(config.roster).index(rut)
    permutations=list(itertools.permutations(range(len(QUESTIONS))))
    random.Random(signature(['order',EXAM_ID,VERSION],config.key)).shuffle(permutations)
    bank=[copy.deepcopy(QUESTIONS[j]) for j in permutations[i]]
    rng=random.Random(signature(['options',EXAM_ID,VERSION,rut],config.key))
    # One decimal place, same operation (squaring), 120 distinct ratios from 1.5 to 13.4.
    # Shuffle parameter assignment independently of question order.
    factors=list(range(15,135))
    random.Random(signature(['ratio',EXAM_ID,VERSION],config.key)).shuffle(factors)
    ratio=factors[i]/10
    for q in bank:
        if q['type']=='choice': rng.shuffle(q['options'])
        if q['id']=='P03':
            q['parameters']={'radio_B_sobre_A':ratio}
            q['prompt']=f'Dos estrellas tienen la misma temperatura efectiva. El cociente de radios R_B/R_A es {ratio:.1f}. Determine L_B/L_A (sin unidades).'
    return bank

def validate_answer(q,value):
    if not isinstance(value,str): raise EvaluationError('Formato de respuesta no válido.')
    value=value.strip()
    if not value:return ''
    if q['type']=='choice':
        if value not in {o['id'] for o in q['options']}: raise EvaluationError('Seleccione una alternativa disponible.')
    elif q['type']=='numeric':
        if len(value)>80 or not re.fullmatch(r'[+-]?(?:\d+(?:[.,]\d*)?|[.,]\d+)(?:[eE][+-]?\d+)?',value):raise EvaluationError('Ingrese un número, con punto o coma decimal, o deje en blanco.')
        if not math.isfinite(float(value.replace(',','.'))):raise EvaluationError('Ingrese un número finito.')
    elif q['type']=='text':
        if len(value)>3000: raise EvaluationError('La respuesta no puede superar 3000 caracteres.')
    else: raise EvaluationError('Tipo de pregunta no reconocido.')
    return value

class Store:
    def __init__(self,path,config=None):
        self.config=config or load_config(); self.path=Path(path).expanduser().resolve()
        self.path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        try: fd=os.open(self.path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
        except FileExistsError: pass
        else: os.close(fd)
        with self.connection() as c:
            c.execute('PRAGMA journal_mode=WAL')
            c.execute('''CREATE TABLE IF NOT EXISTS attempts (attempt_id TEXT PRIMARY KEY, token_hash TEXT UNIQUE NOT NULL, rut TEXT UNIQUE NOT NULL, name TEXT NOT NULL, email TEXT NOT NULL, started_at TEXT NOT NULL, saved_at TEXT NOT NULL, finalized_at TEXT, questions TEXT NOT NULL, answers TEXT NOT NULL)''')
            c.execute('CREATE TABLE IF NOT EXISTS settings (name TEXT PRIMARY KEY, value TEXT NOT NULL)')
            fingerprint=signature([EXAM_ID,VERSION,self.config.mode,self.config.roster],self.config.key)
            c.execute('INSERT OR IGNORE INTO settings VALUES (?,?)',('configuration',fingerprint))
            if c.execute('SELECT value FROM settings WHERE name=?',('configuration',)).fetchone()[0]!=fingerprint:
                raise EvaluationError('La configuración cambió. No reutilice esta base de datos; consulte al profesor.')
            c.commit()
    @contextmanager
    def connection(self):
        c=sqlite3.connect(self.path,timeout=20); c.row_factory=sqlite3.Row
        try: yield c
        except BaseException: c.rollback();raise
        finally:c.close()
    def _row(self,c,token):
        r=c.execute('SELECT * FROM attempts WHERE token_hash=?',(token_hash(token),)).fetchone()
        if r is None:raise EvaluationError('No se encontró el intento. Revise el código o consulte al profesor.')
        r=dict(r);r.pop('token_hash');r['questions']=json.loads(r['questions']);r['answers']=json.loads(r['answers']);return r
    def start(self,name,rut,email,declared):
        name=norm_name(name);rut,email=self.config.match(rut,email)
        if declared is not True: raise EvaluationError('Confirme la declaración de autoría.')
        token=secrets.token_urlsafe(32);now=utc_now()
        with self.connection() as c:
            c.execute('BEGIN IMMEDIATE')
            if c.execute('SELECT 1 FROM attempts WHERE rut=?',(rut,)).fetchone(): raise EvaluationError('Ya existe un intento. Utilice su código de recuperación o contacte al profesor.')
            c.execute('INSERT INTO attempts VALUES (?,?,?,?,?,?,?,?,?,?)',(secrets.token_hex(8).upper(),token_hash(token),rut,name,email,now,now,None,canonical(assignment(self.config,rut)).decode(),'{}'));c.commit()
        return token
    def read(self,token):
        with self.connection() as c:return self._row(c,token)
    def save(self,token,qid,value):
        with self.connection() as c:
            c.execute('BEGIN IMMEDIATE');r=self._row(c,token)
            if r['finalized_at']:raise EvaluationError('El intento ya está finalizado y no puede modificarse.')
            q=next((q for q in r['questions'] if q['id']==qid),None)
            if q is None:raise EvaluationError('Pregunta no reconocida.')
            value=validate_answer(q,value);a=r['answers']
            if value:a[qid]=value
            else:a.pop(qid,None)
            c.execute('UPDATE attempts SET answers=?,saved_at=? WHERE attempt_id=?',(canonical(a).decode(),utc_now(),r['attempt_id']));c.commit();return self._row(c,token)
    def finish(self,token):
        with self.connection() as c:
            c.execute('BEGIN IMMEDIATE');r=self._row(c,token)
            if not r['finalized_at']:
                now=utc_now();c.execute('UPDATE attempts SET finalized_at=?,saved_at=? WHERE attempt_id=?',(now,now,r['attempt_id']))
            c.commit();return self._row(c,token)
    def export(self,token,checkpoint=False):
        r=self.read(token)
        if not checkpoint and not r['finalized_at']:raise EvaluationError('Finalice el intento antes de descargar la entrega.')
        if checkpoint and r['finalized_at']:raise EvaluationError('El intento ya está finalizado. Descargue la entrega.')
        items=[]
        for q in r['questions']:
            a=r['answers'].get(q['id']);item=dict(q,answer=a)
            if q['type']=='choice':item['answer_text']=next((o['text'] for o in q['options'] if o['id']==a),None)
            items.append(item)
        p={'schema':'eee.evaluacion.entrega/2','mode':'practica_sin_nota','kind':'respaldo' if checkpoint else 'entrega','exam_id':EXAM_ID,'version':VERSION,'title':TITLE,'attempt_id':r['attempt_id'],'student':{'name':r['name'],'rut':r['rut'],'email':r['email']},'declaration':DECLARATION,'declared':True,'started_at_utc':r['started_at'],'saved_at_utc':r['saved_at'],'finalized_at_utc':r['finalized_at'],'answered':len(r['answers']),'total':len(items),'items':items}
        envelope={'payload':p,'integrity_sha256':checksum(p),'server_hmac_sha256':signature(p,self.config.key)}
        return f"EEE_P3_{'RESPALDO' if checkpoint else 'PRACTICA'}_{r['attempt_id']}.json", (json.dumps(envelope,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()

def verify_export(data,config=None,allow_checkpoint=False):
    config=config or load_config()
    try:
        if len(data)>200_000:raise EvaluationError('Archivo demasiado grande.')
        obj=json.loads(data);p=obj['payload']
        if not hmac.compare_digest(obj['integrity_sha256'],checksum(p)) or not hmac.compare_digest(obj['server_hmac_sha256'],signature(p,config.key)):raise EvaluationError('Integridad o sello HMAC no coincide.')
        if (p['schema'],p['mode'],p['exam_id'],p['version'],p['title'])!=('eee.evaluacion.entrega/2','practica_sin_nota',EXAM_ID,VERSION,TITLE):raise EvaluationError('Versión o modo no reconocido.')
        if p['kind']!='entrega' and not (allow_checkpoint and p['kind']=='respaldo'):raise EvaluationError('No es una entrega final.')
        if not re.fullmatch(r'[A-F0-9]{16}',p['attempt_id']) or p['declared'] is not True or p['declaration']!=DECLARATION:raise EvaluationError('Identificador o declaración inválidos.')
        r,e=config.match(p['student']['rut'],p['student']['email']);norm_name(p['student']['name'])
        expected=assignment(config,r);n=0
        if len(p['items'])!=len(expected):raise EvaluationError('Número de preguntas no válido.')
        for q,item in zip(expected,p['items']):
            a=item['answer']; expected_item=dict(q,answer=a)
            if q['type']=='choice':expected_item['answer_text']=next((o['text'] for o in q['options'] if o['id']==a),None)
            if item!=expected_item:raise EvaluationError('Variante, orden o alternativas no coinciden.')
            if a is not None:
                if not validate_answer(q,a):raise EvaluationError('Respuesta vacía no normalizada.')
                n+=1
        if p['total']!=len(expected) or p['answered']!=n:raise EvaluationError('Conteo de respuestas inconsistente.')
        start=datetime.fromisoformat(p['started_at_utc']);saved=datetime.fromisoformat(p['saved_at_utc'])
        if start.utcoffset() is None or saved.utcoffset() is None or saved<start:raise EvaluationError('Fechas no válidas.')
        if p['kind']=='entrega':
            end=datetime.fromisoformat(p['finalized_at_utc'])
            if end.utcoffset() is None or end!=saved:raise EvaluationError('Fecha de finalización no válida.')
        elif p['finalized_at_utc'] is not None:raise EvaluationError('Respaldo no válido.')
        return p
    except EvaluationError:raise
    except (ValueError,TypeError,KeyError,AttributeError,OverflowError):raise EvaluationError('Archivo de evaluación no válido.') from None
