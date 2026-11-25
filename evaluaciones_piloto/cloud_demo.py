"""Community Cloud load-test entrypoint. Synthetic data only, no real roster."""
import hmac
import os
from pathlib import Path
import re
import runpy
import sys
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from evaluation_config import load_config
from preparar_demo import demo_rows
from teste_carga_browser_v4 import audit_database


def setting(name, default=''):
    # Match the original app's setting precedence.
    if name in os.environ:
        return os.environ[name]
    try:
        return str(st.secrets.get(name, default))
    except Exception:
        return default


def validate():
    if setting('EEE_MODE') != 'demo':
        raise ValueError('Synthetic mode required')
    if setting('EEE_PROFESSOR_EMAIL').strip():
        raise ValueError('No email destination in cloud test')
    cfg = load_config(setting)
    if cfg.roster != dict(demo_rows(50)):
        raise ValueError('Synthetic roster required')
    db = setting('EEE_EVAL_DB')
    if not re.fullmatch(r'/tmp/eee-cloud-demo-[0-9a-f]{24}\.sqlite3', db):
        raise ValueError('Invalid demo DB path')
    audit_key = setting('EEE_DEMO_AUDIT_KEY')
    if not re.fullmatch(r'[0-9a-f]{64}', audit_key) or hmac.compare_digest(audit_key, cfg.key.hex()):
        raise ValueError('Separate private audit key required')
    n = int(setting('EEE_DEMO_N'))
    if n not in (1, 21, 30):
        raise ValueError('Invalid test size')
    return cfg, Path(db), audit_key, n

try:
    cfg, db, audit_key, n = validate()
except Exception:
    st.error('Instancia de ensayo no configurada. Sólo se permite el modo DEMO con datos ficticios. Contacte al profesor.')
    st.stop()

if st.query_params.get('auditoria') == '1':
    st.set_page_config(page_title='Auditoría técnica DEMO', page_icon='⭐', layout='centered')
    st.title('Auditoría técnica · DEMO')
    st.caption('Sólo datos ficticios. No es una interfaz de evaluación de estudiantes reales.')
    with st.form('audit_access'):
        candidate = st.text_input('Clave privada de auditoría', type='password', max_chars=64)
        submitted = st.form_submit_button('Verificar banco de prueba')
    if submitted:
        if not hmac.compare_digest(candidate.encode('utf-8'), audit_key.encode('ascii')):
            st.error('Acceso no autorizado.')
        else:
            try:
                report = audit_database(db, cfg, n)
                st.json(report)
                import json
                st.download_button('Descargar informe de auditoría', json.dumps(report, indent=2, ensure_ascii=False)+'\n', file_name='auditoria_servidor_demo.json', mime='application/json', on_click='ignore')
            except Exception:
                st.error('No se pudo auditar el banco de prueba. Consulte los registros del servidor.')
    st.stop()

# Run the unchanged, locally homologated application on every Streamlit rerun.
runpy.run_path(str(ROOT / 'evaluaciones.py'), run_name='__main__')
