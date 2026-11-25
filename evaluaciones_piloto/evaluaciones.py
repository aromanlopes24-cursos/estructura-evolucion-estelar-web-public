"""Punto de entrada independiente del piloto de evaluaciones EEE."""
from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import streamlit as st

from evaluation_engine import Store, EvaluationError
from evaluation_config import load_config
from evaluation_engine import DECLARATION
from evaluation_questions import VERSION, TITLE, DEMO_MINUTES

ROOT = Path(__file__).resolve().parent
ICON = ROOT / 'assets' / 'stellar_evolution_icon.png'

st.set_page_config(page_title='Estructura y Evolución Estelar · Evaluaciones', page_icon='⭐', layout='centered')
st.markdown('''<style>
.block-container {padding-top:2rem; padding-bottom:3rem; max-width:920px;}
[data-testid="stSidebar"] {background:#eef4f8;}
</style>''', unsafe_allow_html=True)


def setting(name, default=''):
    value = os.environ.get(name)
    if value is not None:
        return value
    try:
        return str(st.secrets.get(name, default))
    except (FileNotFoundError, KeyError):
        return default
    except Exception:
        # A missing secrets.toml must not prevent local practice.
        return default


@st.cache_resource
def get_store():
    config = load_config(setting)
    db = setting('EEE_EVAL_DB', '').strip()
    if config.mode == 'roster' and not db:
        raise EvaluationError('Configure EEE_EVAL_DB en un volumen privado y persistente.')
    return Store(Path(db or Path.home() / '.local/share/eee-evaluaciones/piloto_131.sqlite3'), config)


def move(screen, idx=None):
    st.session_state['ev_screen'] = screen
    if idx is not None:
        st.session_state['ev_idx'] = idx
    st.rerun()


def attach(token, new=False):
    st.session_state['ev_code'] = token.strip()
    st.session_state['ev_screen'] = 'code' if new else 'review'
    st.session_state['ev_idx'] = 0
    st.rerun()


def logout():
    for key in list(st.session_state.keys()):
        if key.startswith('ev_'):
            del st.session_state[key]
    st.rerun()


@st.fragment(run_every='15s')
def demo_clock(started_at):
    elapsed = max(0, int((datetime.now(timezone.utc) - datetime.fromisoformat(started_at)).total_seconds()))
    remaining = max(0, DEMO_MINUTES * 60 - elapsed)
    mm, ss = divmod(remaining, 60)
    st.caption(f'Reloj de demostración: {mm:02d}:{ss:02d} restantes de {DEMO_MINUTES} min. '
               'No limita el tiempo ni cierra esta práctica.')


with st.sidebar:
    if ICON.is_file():
        st.image(str(ICON), width=112)
    st.markdown('### Estructura y Evolución Estelar')
    st.caption(f'Web {VERSION} · Evaluaciones')
    st.markdown('**Práctica sin calificación**')
    st.write('1. Identifíquese.\n2. Guarde sus respuestas.\n3. Revise y finalice.\n4. Descargue el archivo y envíelo por correo.')
    st.info('Si se interrumpe la conexión, vuelva a entrar con su código de recuperación. Se recuperará el último guardado confirmado, mientras el almacenamiento del servidor siga disponible.')

st.title(TITLE)
st.caption('Universidad de La Serena · Estructura y Evolución Estelar · Actividad de familiarización')

try:
    store = get_store()
except (OSError, sqlite3.Error, EvaluationError):
    st.error('La configuración privada o el almacenamiento no están disponibles. No inicie la práctica; avise al profesor.')
    st.stop()

code = st.session_state.get('ev_code')
if not code:
    st.info('Esta actividad no tiene nota. Permite practicar el procedimiento de identificación y entrega. El RUT y el correo deben coincidir con la lista privada del profesor. El nombre no requiere coincidencia literal.')
    if store.config.mode == 'demo':
        st.warning('Modo DEMO — sólo estudiantes ficticios. No ingrese datos personales reales.')
    new_tab, resume_tab = st.tabs(['Iniciar una práctica', 'Recuperar un intento'])
    with new_tab:
        with st.form('ev_new'):
            name = st.text_input('Nombre y apellido(s)', max_chars=120)
            rut = st.text_input('RUT', max_chars=20, placeholder='12.345.678-5')
            email = st.text_input('Correo institucional', max_chars=200)
            declared = st.checkbox(DECLARATION)
            start = st.form_submit_button('Iniciar práctica', type='primary', use_container_width=True)
        if start:
            try:
                token = store.start(name, rut, email, declared)
            except EvaluationError as exc:
                st.warning(str(exc))
            except (OSError, sqlite3.Error):
                st.error('No se pudo crear el intento. Vuelva a intentarlo.')
            else:
                attach(token, new=True)
    with resume_tab:
        with st.form('ev_resume'):
            entered = st.text_input('Código de recuperación', type='password', max_chars=128)
            resume = st.form_submit_button('Recuperar', type='primary', use_container_width=True)
        if resume:
            try:
                store.read(entered)
            except EvaluationError as exc:
                st.warning(str(exc))
            except (OSError, sqlite3.Error):
                st.error('No se pudo acceder al almacenamiento. Vuelva a intentarlo.')
            else:
                attach(entered)
    st.stop()

try:
    attempt = store.read(code)
except EvaluationError as exc:
    st.warning(str(exc))
    if st.button('Volver al acceso'):
        logout()
    st.stop()
except (OSError, sqlite3.Error):
    st.error('No se pudo recuperar el intento. Conserve el código y vuelva a intentarlo.')
    st.stop()

questions = attempt['questions']
answers = attempt['answers']
count = len(answers)
total = len(questions)
with st.sidebar:
    st.divider()
    st.text(attempt['name'])
    st.caption('Identificación cotejada con la lista; autoría declarada.')
    st.caption(f"Intento: {attempt['attempt_id']}")
    with st.expander('Ver código de recuperación'):
        st.code(code, language=None)
        st.caption('Es privado: permite acceder a este intento. No lo envíe por correo.')
    if st.button('Cerrar sesión', key='ev_logout', use_container_width=True):
        logout()

if attempt['finalized_at']:
    st.success('Práctica finalizada. Las respuestas registradas ya no se pueden modificar.')
    st.write(f'{count} de {total} preguntas respondidas. Esta práctica no tiene nota.')
    try:
        filename, content = store.export(code)
    except (OSError, sqlite3.Error, EvaluationError):
        st.error('No se pudo generar el archivo. Recupere el intento con su código y vuelva a intentarlo.')
        st.stop()
    st.markdown('### Entrega al profesor')
    st.write('Descargue el archivo JSON. No lo modifique ni cambie su extensión. '
             'Adjúntelo a un mensaje enviado desde el mismo correo institucional que registró al entrar.')
    st.download_button('Descargar archivo de entrega (.json)', content, file_name=filename,
                       mime='application/json', on_click='ignore', key=f'ev_final_download_{attempt["attempt_id"]}',
                       type='primary', use_container_width=True)
    subject = f'EEE - Simulación Prueba 3 - {attempt["attempt_id"]}'
    recipient = store.config.professor_email
    st.markdown('**Asunto del mensaje:**')
    st.code(subject, language=None)
    if recipient and '@' in recipient and not any(c.isspace() for c in recipient):
        st.write('Destinatario:', recipient)
        body = 'Estimado profesor:\n\nAdjunto el archivo de entrega de la simulación de la Prueba N.º 3.\n\nSaludos.'
        link = f'mailto:{quote(recipient, safe="@.")}?subject={quote(subject)}&body={quote(body)}'
        st.markdown(f'[Abrir un mensaje de correo]({link})')
    else:
        st.caption('Destinatario: el correo institucional indicado por el profesor en las instrucciones de la actividad.')
    st.warning('La descarga NO envía el correo. Adjunte manualmente el archivo descargado, envíe el mensaje y compruebe su carpeta Enviados.')
    st.caption(f'Archivo esperado: {filename}')
    st.info('Si la descarga se interrumpe, vuelva a pulsar el botón de descarga. '
            'También puede recuperar este intento finalizado con su código privado y descargar el mismo archivo. '
            'No inicie otro intento.')
    with st.expander('Ver resumen de las respuestas entregadas'):
        for i, q in enumerate(questions, 1):
            st.markdown(f'**{i}. {q["title"]}**')
            a = answers.get(q['id'], '')
            if q['type'] == 'choice':
                a = next((o['text'] for o in q['options'] if o['id'] == a), '')
            st.text(a or 'Sin responder')
    st.stop()

if st.session_state.get('ev_screen') == 'code':
    st.markdown('### Guarde su código de recuperación')
    st.code(code, language=None)
    st.write('Copie este código y guárdelo en un lugar privado. Si cierra la página o cambia de navegador, '
             'lo necesitará para recuperar las respuestas guardadas. No comparta el código con otras personas.')
    confirmed = st.checkbox('He guardado el código de recuperación.', key='ev_code_confirmed')
    if st.button('Comenzar las preguntas', type='primary', disabled=not confirmed, use_container_width=True):
        move('question', 0)
    st.stop()

st.progress(count / total, text=f'{count} de {total} preguntas respondidas')
demo_clock(attempt['started_at'])
st.caption('Guardado: sólo se registran los datos al pulsar un botón «Guardar…». Antes de cerrar o cambiar de página, guarde la respuesta.')

screen = st.session_state.get('ev_screen', 'review')
if screen == 'review':
    st.markdown('### Revisión antes de la entrega')
    st.write('Puede volver a cualquier pregunta, responderla o modificarla antes de finalizar.')
    for i, q in enumerate(questions):
        a = answers.get(q['id'], '')
        label = 'Respondida' if a else 'Pendiente'
        left, right = st.columns([4, 1])
        with left:
            st.markdown(f'**{i+1}. {q["title"]}** · {label}')
            if a and q['type'] == 'choice':
                st.text(next((o['text'] for o in q['options'] if o['id'] == a), a))
            elif a:
                st.text(a[:180] + ('…' if len(a) > 180 else ''))
        with right:
            if st.button('Editar', key=f'ev_edit_{attempt["attempt_id"]}_{q["id"]}', use_container_width=True):
                move('question', i)
    if count < total:
        st.warning(f'Quedan {total-count} preguntas sin responder. Puede entregarlas en blanco o completarlas ahora.')
    if st.button('Volver a la primera pendiente', disabled=count == total, use_container_width=True):
        move('question', next(i for i,q in enumerate(questions) if q['id'] not in answers))
    st.divider()
    try:
        backup_name, backup_data = store.export(code, checkpoint=True)
        st.download_button('Descargar respaldo de respuestas guardadas (.json)', backup_data, file_name=backup_name, mime='application/json', on_click='ignore', key=f'ev_backup_download_{attempt["attempt_id"]}', use_container_width=True)
        st.caption('Guarde el respaldo en privado. No es la entrega final. Si el servidor pierde los datos, contacte al profesor con este archivo; no permite reabrir automáticamente la prueba.')
    except (OSError, sqlite3.Error, EvaluationError):
        st.warning('No se pudo generar el respaldo; vuelva a intentarlo.')
    with st.form(f'ev_finish_{attempt["attempt_id"]}'):
        confirmation = st.checkbox('Confirmo que deseo entregar estas respuestas de forma definitiva.')
        finish = st.form_submit_button('Finalizar y generar archivo', type='primary', use_container_width=True)
    if finish:
        if not confirmation:
            st.warning('Marque la casilla de confirmación antes de finalizar.')
        else:
            try:
                store.finish(code)
            except (OSError, sqlite3.Error, EvaluationError):
                st.error('No se confirmó la entrega. Vuelva a intentarlo; se conservarán las respuestas guardadas.')
            else:
                st.rerun()
    st.stop()

idx = min(max(int(st.session_state.get('ev_idx', 0)), 0), total - 1)
q = questions[idx]
current = answers.get(q['id'], '')
st.markdown(f'### Pregunta {idx+1} de {total} · {q["title"]}')
st.write(q['prompt'])
if q.get('formula'):
    st.latex(q['formula'])
if q.get('figure'):
    st.image(str(ROOT / 'figures' / (q['figure'] + '.png')), use_container_width=True)

# Form submission commits the current widget value before moving to another question.
# Distinct widget keys prevent cross-attempt and cross-question contamination.
key = f'ev_answer_{attempt["attempt_id"]}_{q["id"]}'
with st.form(f'ev_question_{attempt["attempt_id"]}_{q["id"]}'):
    if q['type'] == 'choice':
        opts = [''] + [o['id'] for o in q['options']]
        labels = {'': 'Dejar sin responder'}
        labels.update({o['id']: f'{chr(65+i)}. {o["text"]}' for i,o in enumerate(q['options'])})
        value = st.radio('Seleccione una alternativa', opts,
                         index=opts.index(current) if current in opts else 0,
                         format_func=labels.__getitem__, key=key)
    elif q['type'] == 'numeric':
        value = st.text_input('Respuesta numérica (punto o coma decimal)', value=current, key=key, max_chars=80)
    else:
        value = st.text_area('Su respuesta', value=current, key=key, height=160, max_chars=3000)
    c1, c2 = st.columns(2)
    with c1:
        previous = st.form_submit_button('← Guardar y anterior', disabled=idx == 0, use_container_width=True)
    with c2:
        following = st.form_submit_button('Guardar y siguiente →' if idx+1 < total else 'Guardar e ir a revisión →',
                                          type='primary', use_container_width=True)
    c3, c4 = st.columns(2)
    with c3:
        save = st.form_submit_button('Guardar respuesta', use_container_width=True)
    with c4:
        review = st.form_submit_button('Guardar e ir a revisión', use_container_width=True)

if previous or following or save or review:
    try:
        store.save(code, q['id'], value)
    except EvaluationError as exc:
        st.warning(str(exc))
    except (OSError, sqlite3.Error):
        st.error('No se confirmó el guardado. No cierre la página; vuelva a intentarlo.')
    else:
        if previous:
            move('question', idx-1)
        elif following and idx+1 < total:
            move('question', idx+1)
        elif following or review:
            move('review')
        else:
            st.session_state['ev_saved'] = True
            st.rerun()
if st.session_state.pop('ev_saved', False):
    st.success('Respuesta guardada en el servidor.')
