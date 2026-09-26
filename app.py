from __future__ import annotations
from pathlib import Path
import json, random, secrets, sys
import streamlit as st

ROOT=Path(__file__).resolve().parent
CONTENT=ROOT/"content"; MATERIALS=ROOT/"materials"; ICON=ROOT/"assets"/"stellar_evolution_icon.png"
sys.path.insert(0,str(ROOT))
from web_labs import lab02,lab03,lab04,lab05,lab06,lab07,lab08
import web_labs_00_01 as early_labs

MODULES=[
 ("00","Observables estelares"),("01","Fotometría y extinción"),("02","Estructura mecánica"),
 ("03","Polítropos y Lane–Emden"),("04","Fuentes de energía"),("05","Transporte de energía"),
 ("06","Atmósferas estelares"),("07","Secuencia principal"),("08","Evolución post-ZAMS")
]
SECTIONS=["Inicio","Teoría","Símbolos","Predicción","Laboratorio","Material de clase","Nivel 1","Nivel 2","Nivel 3"]

st.set_page_config(page_title="Estructura y Evolución Estelar",page_icon="⭐",layout="wide",initial_sidebar_state="expanded")
st.markdown("""<style>
.block-container {padding-top:2.8rem;padding-bottom:3rem;max-width:1350px;}
[data-testid="stSidebar"] {background:#eef4f8;}
.ee-title{font-size:2.1rem;font-weight:800;color:#17324d;margin-bottom:.1rem;}
.ee-sub{font-size:1.05rem;color:#116c6c;margin-bottom:1rem;}
.ee-card{background:white;border:1px solid #c7d7e2;border-radius:10px;padding:1rem 1.15rem;margin:.5rem 0 1rem;}
.ee-note{background:#fff4df;border-left:5px solid #c98826;padding:.8rem 1rem;border-radius:6px;}
</style>""",unsafe_allow_html=True)

def page_header(t,s):
    a,b=st.columns([1,7])
    with a:st.image(str(ICON),width=92)
    with b:
        st.markdown(f'<div class="ee-title">{t}</div>',unsafe_allow_html=True)
        st.markdown(f'<div class="ee-sub">{s}</div>',unsafe_allow_html=True)

def mdir(mid):return CONTENT/f"modulo{mid}"
def load(mid):
    d=mdir(mid)
    return json.loads((d/"modulo.json").read_text(encoding="utf-8")),json.loads((d/"levels.json").read_text(encoding="utf-8"))
def md(mid,n):return (mdir(mid)/n).read_text(encoding="utf-8")

def seed():
    k="_stable_answer_shuffle_seed"
    if k not in st.session_state:st.session_state[k]=secrets.randbits(64)
    return st.session_state[k]
def order(key,n):
    k=f"_choice_order_{key}"
    if k not in st.session_state:
        q=list(range(n));random.Random(f"{seed()}::{key}").shuffle(q);st.session_state[k]=q
    return list(st.session_state[k])

with st.sidebar:
    st.image(str(ICON),width=128);st.markdown("## Estructura y Evolución Estelar");st.caption("Web v1.2 · curso completo")
    label=st.radio("Módulos",[f"{m} · {t}" for m,t in MODULES],key="module_selector")
    MID=label[:2]
    st.divider();section=st.radio("Ruta del módulo",SECTIONS,key=f"route_{MID}")
    st.caption("observación → parámetros globales → estructura → energía → evolución")

CFG,LEVELS=load(MID)

def home():
    page_header("Estructura y Evolución Estelar",f"Módulo {MID} — {CFG['title']}")
    st.markdown(f'<div class="ee-card"><b>{CFG["title"]}</b><br>{CFG.get("subtitle","")}</div>',unsafe_allow_html=True)
    nlab=len(CFG.get("lab_experiments",[]))
    lcounts=[len(LEVELS["levels"][str(i)]["items"]) for i in (1,2,3)]
    c1,c2,c3,c4=st.columns(4);c1.metric("Módulo",MID);c2.metric("Laboratorio",f"{nlab or '—'} experimentos");c3.metric("Nivel 1",f"{lcounts[0]} actividades");c4.metric("Niveles 2–3",f"{lcounts[1]} + {lcounts[2]}")
    st.markdown('<div class="ee-note"><b>Web v1.2:</b> módulos 00–08 habilitados.</div>',unsafe_allow_html=True)

def predictions():
    page_header("Predicción",f"Módulo {MID} · primero prediga, después compruebe")
    for i,q in enumerate(CFG["predictions"],1):
        st.markdown(f"### {i}. {q['question']}");qid=f"{MID}_pred_{i}";o=order(qid,len(q["options"]));shown=[q["options"][j] for j in o]
        ans=st.radio("Respuesta",shown,index=None,key=qid,label_visibility="collapsed")
        if st.button("Comprobar",key=f"chk_{qid}"):
            if ans is None:st.warning("Seleccione una alternativa.")
            elif o[shown.index(ans)]==q["correct"]:st.success(q["ok"])
            else:st.error(q["bad"])
        st.divider()

def material():
    page_header("Material de clase",f"Módulo {MID} · fuentes originales")
    for item in CFG.get("materials",[]):
        p=MATERIALS/item["file"];st.markdown(f"### {item['label']}")
        if p.exists():st.download_button("Descargar PDF",p.read_bytes(),file_name=p.name,mime="application/pdf",key=f"pdf_{MID}_{p.name}")
        else:st.error(f"No se encontró {p.name}")
        st.divider()

def level_state(level):
    base=f"{MID}_{level}";ik=f"idx_{base}";dk=f"done_{base}";fk=f"fb_{base}"
    if ik not in st.session_state:st.session_state[ik]=0
    if dk not in st.session_state:st.session_state[dk]=set()
    if fk not in st.session_state:st.session_state[fk]={}
    return ik,dk,fk
def close_num(x,it):
    a=float(it["answer"]);return abs(x-a)<=max(float(it.get("abs_tol",0)),float(it.get("rel_tol",0))*abs(a))

def render_level(level):
    block=LEVELS["levels"][level];page_header(f"Nivel {level}",f"Módulo {MID} · {block['title']}");st.caption(block["subtitle"])
    ik,dk,fk=level_state(level);items=block["items"];idx=st.session_state[ik];done=st.session_state[dk]
    st.progress(len(done)/len(items));st.caption(f"{len(done)} de {len(items)} actividades completadas")
    if idx>=len(items):
        st.success(f"Nivel {level} completado.")
        if st.button("Reiniciar nivel",key=f"rst_{MID}_{level}"):st.session_state[ik]=0;st.session_state[dk]=set();st.session_state[fk]={};st.rerun()
        return
    it=items[idx];iid=it["id"];st.markdown(f"## Actividad {idx+1} de {len(items)} · {it.get('title','')}")
    if it.get("resource"):st.info("Recurso sugerido: "+it["resource"])
    st.write(it["prompt"])
    if it["type"]=="choice":
        o=order(iid,len(it["options"]));shown=[it["options"][j] for j in o];ans=st.radio("Respuesta",shown,index=None,key=f"ans_{iid}")
        if st.button("Comprobar",key=f"check_{iid}"):
            if ans is None:st.session_state[dk].discard(idx);st.session_state[fk][iid]=("warn","Seleccione una alternativa.")
            else:
                oi=o[shown.index(ans)]
                if oi==it["correct"]:st.session_state[dk].add(idx);st.session_state[fk][iid]=("ok",it["feedback"][oi])
                else:st.session_state[dk].discard(idx);st.session_state[fk][iid]=("bad",it["feedback"][oi]+" Inténtelo nuevamente.")
            st.rerun()
    elif it["type"]=="numeric":
        raw=st.text_input(f"Respuesta {it.get('unit','')}".strip(),key=f"ans_{iid}")
        if st.button("Comprobar",key=f"check_{iid}"):
            try:x=float(raw.strip().replace(",","."))
            except:st.session_state[dk].discard(idx);st.session_state[fk][iid]=("bad","Ingrese un valor numérico válido.")
            else:
                if close_num(x,it):
                    st.session_state[dk].add(idx);msg=it["correct_feedback"]+("\n\n"+it.get("solution","") if it.get("solution") else "");st.session_state[fk][iid]=("ok",msg)
                else:st.session_state[dk].discard(idx);st.session_state[fk][iid]=("bad",it["wrong_feedback"]+" Revise el planteamiento.")
            st.rerun()
    else:
        st.warning("No se califica automáticamente. Escriba su razonamiento y compárelo con criterios explícitos.")
        st.caption("Intente explicar la idea física en 2–4 frases. Puede incluir ecuaciones, pero diga también qué significan.")
        raw=st.text_area("Su razonamiento",height=220,key=f"ans_{iid}",placeholder="Relación física → qué ocurre → por qué.")
        if st.button("Mostrar criterios",key=f"check_{iid}"):
            s=raw.strip()
            if not s:st.session_state[dk].discard(idx);st.session_state[fk][iid]=("bad","Escriba al menos una idea.")
            else:
                msg=("Su respuesta es breve; puede ampliarla.\n\n" if len(s)<40 else "")+"CRITERIOS:\n\n"+"\n".join("• "+x for x in it["criteria"])
                if it.get("guide"):msg+="\n\nGUÍA:\n"+it["guide"]
                st.session_state[dk].add(idx);st.session_state[fk][iid]=("criteria",msg)
            st.rerun()
    fb=st.session_state[fk].get(iid)
    if fb:
        typ,msg=fb
        if typ=="ok":st.success(msg)
        elif typ=="warn":st.warning(msg)
        elif typ=="criteria":st.markdown(msg)
        else:st.error(msg)
    st.divider();a,b=st.columns(2)
    with a:
        if idx>0 and st.button("← Anterior",key=f"prev_{MID}_{level}_{idx}"):st.session_state[ik]=idx-1;st.rerun()
    with b:
        if idx in st.session_state[dk]:
            if st.button("Finalizar ✓" if idx==len(items)-1 else "Siguiente →",key=f"next_{MID}_{level}_{idx}",type="primary"):st.session_state[ik]=idx+1;st.rerun()

def laboratory():
    if MID in ("00","01"):
        early_labs.set_page_header(page_header)
        (early_labs.lab00 if MID=="00" else early_labs.lab01)()
    else:
        {"02":lab02,"03":lab03,"04":lab04,"05":lab05,"06":lab06,"07":lab07,"08":lab08}[MID]()

if section=="Inicio":home()
elif section=="Teoría":page_header("Teoría",f"Módulo {MID}");st.markdown(md(MID,"NOTAS_ESTUDIO.md"))
elif section=="Símbolos":page_header("Símbolos",f"Módulo {MID}");st.markdown(md(MID,"SIMBOLOS.md"))
elif section=="Predicción":predictions()
elif section=="Laboratorio":laboratory()
elif section=="Material de clase":material()
elif section=="Nivel 1":render_level("1")
elif section=="Nivel 2":render_level("2")
elif section=="Nivel 3":render_level("3")
