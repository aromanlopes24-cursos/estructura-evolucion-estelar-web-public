#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import argparse, json, sys

ROOT=Path(__file__).resolve().parent.parent
CFG=ROOT/"course_access.json"
ALL=[f"{i:02d}" for i in range(9)]

def load():
    if CFG.exists():
        return json.loads(CFG.read_text(encoding="utf-8"))
    return {
        "enabled_modules":["00","01","02"],
        "show_locked_modules":True,
        "locked_label":"próximamente",
        "student_message":"Los módulos se habilitan progresivamente según el avance de las clases."
    }

ap=argparse.ArgumentParser(
    description="Controla qué módulos del curso están disponibles para estudiantes."
)
g=ap.add_mutually_exclusive_group()
g.add_argument("--through", type=int, choices=range(0,9),
               help="Habilita todos los módulos desde 00 hasta N.")
g.add_argument("--modules", nargs="+",
               help="Lista explícita, por ejemplo: --modules 00 01 02 04")
g.add_argument("--show", action="store_true",
               help="Muestra la configuración actual.")
args=ap.parse_args()

cfg=load()

if args.show or (args.through is None and args.modules is None):
    print("COURSE_ACCESS")
    print("enabled_modules =", " ".join(cfg.get("enabled_modules",[])))
    print("show_locked_modules =", cfg.get("show_locked_modules",True))
    print("locked_label =", cfg.get("locked_label","próximamente"))
    raise SystemExit(0)

if args.through is not None:
    enabled=ALL[:args.through+1]
else:
    enabled=[]
    for x in args.modules:
        m=str(x).zfill(2)
        if m not in ALL:
            print(f"ERROR: módulo inválido: {x}",file=sys.stderr)
            raise SystemExit(2)
        if m not in enabled:
            enabled.append(m)
    if "00" not in enabled:
        print("ERROR: el Módulo 00 debe permanecer habilitado.",file=sys.stderr)
        raise SystemExit(2)

cfg["enabled_modules"]=enabled
CFG.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("COURSE_ACCESS_UPDATED=PASS")
print("enabled_modules =", " ".join(enabled))
print("archivo =", CFG)
