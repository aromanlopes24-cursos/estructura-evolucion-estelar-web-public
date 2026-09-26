#!/usr/bin/env python3
"""Núcleo — Módulo 08: Evolución post-ZAMS.

Se usan sólo relaciones cuantitativas explícitas del material:

1) Principio del espejo:
   contracción interna -> expansión externa
   expansión interna   -> contracción externa

2) Virial, en forma proporcional:
   E_grav ∝ -1/R_core  para masa fija.

3) Límite de Schönberg–Chandrasekhar según el material:
   q_SC = 0.37 (mu_e/mu_c)^2

4) Estados evolutivos y valores explícitos citados en las notas.

No se generan trayectorias HR numéricas sintéticas.
"""

from __future__ import annotations

def mirror_response(delta_core_radius: float) -> dict:
    """Qualitative mirror principle from the supplied material."""
    if delta_core_radius < 0:
        return {
            "core": "contracción",
            "envelope": "expansión",
            "Tc": "aumenta",
            "Pc": "aumenta",
            "sign_product": "ΔR_env / ΔR_core < 0",
        }
    if delta_core_radius > 0:
        return {
            "core": "expansión",
            "envelope": "contracción",
            "Tc": "disminuye",
            "Pc": "disminuye",
            "sign_product": "ΔR_env / ΔR_core < 0",
        }
    return {
        "core": "sin cambio",
        "envelope": "sin respuesta",
        "Tc": "sin cambio",
        "Pc": "sin cambio",
        "sign_product": "—",
    }

def normalized_gravitational_energy(radius_ratio: float) -> float:
    """Egrav/Egrav_ref for fixed mass, with Egrav ∝ -1/R."""
    if radius_ratio <= 0:
        raise ValueError("radius_ratio debe ser > 0")
    return -1.0/radius_ratio

def sc_limit(mu_env: float, mu_core: float) -> float:
    """Source formula q_SC = 0.37 (mu_e/mu_c)^2."""
    if mu_env <= 0 or mu_core <= 0:
        raise ValueError("mu_env y mu_core deben ser > 0")
    return 0.37*(mu_env/mu_core)**2

def sc_state(q_core: float, mu_env: float, mu_core: float) -> dict:
    if q_core < 0:
        raise ValueError("q_core debe ser >= 0")
    qlim=sc_limit(mu_env,mu_core)
    if q_core < qlim:
        status="por debajo del límite"
        response="núcleo isotérmico estable según el esquema del material"
    elif abs(q_core-qlim) < 1e-9:
        status="en el límite"
        response="umbral de estabilidad del núcleo"
    else:
        status="por encima del límite"
        response="contracción del núcleo y evolución hacia gigante roja según el material"
    return {"q_sc":qlim,"status":status,"response":response}

EARLY_STAGES = [
    {
        "name":"ZAMS",
        "core":"fusión estable de H en el núcleo",
        "shell":"no",
        "envelope":"equilibrio hidrostático y térmico",
        "observable":"L y Teff casi constantes en la descripción del material",
    },
    {
        "name":"H → He en el núcleo",
        "core":"aumenta μ; contracción gradual y calentamiento",
        "shell":"no",
        "envelope":"ajuste lento",
        "observable":"L aumenta lentamente",
    },
    {
        "name":"Agotamiento de H central / SGB",
        "core":"He inerte; contracción; T y densidad centrales aumentan",
        "shell":"comienza después en región adyacente",
        "envelope":"se expande",
        "observable":"Teff disminuye ligeramente; L aumenta; R crece",
    },
    {
        "name":"H en capa",
        "core":"He inerte sigue comprimiéndose y calentándose",
        "shell":"fusión de H activa alrededor del núcleo",
        "envelope":"expansión y convección externa",
        "observable":"aumenta la energía térmica; avance hacia RGB",
    },
    {
        "name":"RGB",
        "core":"He inerte; material lo describe como degenerado en esta etapa",
        "shell":"H activa",
        "envelope":"convectiva e hinchada",
        "observable":"R ↑, Teff ↓, L ↑",
    },
]

ADVANCED_STAGES = [
    {
        "name":"Fin SP / subgigante",
        "core":"H central agotándose; contracción",
        "burning":"H pasa a una capa",
        "surface":"expansión de capas exteriores",
    },
    {
        "name":"Primer dredge-up",
        "core":"colapso parcial",
        "burning":"H en capa",
        "surface":"mezcla convectiva lleva He, 13C y 14N hacia la superficie",
    },
    {
        "name":"RGB",
        "core":"contracción y calentamiento",
        "burning":"H en capa",
        "surface":"R ↑, L ↑, Teff ↓",
    },
    {
        "name":"Flash de He",
        "core":"Tc ≈ 1.3×10^8 K; He comienza a fusionarse en C bajo degeneración electrónica",
        "burning":"ignición rápida de He",
        "surface":"núcleo se expande; luminosidad superficial disminuye temporalmente",
    },
    {
        "name":"HB",
        "core":"fusión estable de He, produciendo C y O",
        "burning":"He en núcleo",
        "surface":"L y T aproximadamente constantes en el resumen suministrado",
    },
    {
        "name":"He central agotado",
        "core":"núcleo inerte de C–O; vuelve a contraerse",
        "burning":"quema en capas de H y He",
        "surface":"prepara la estructura AGB",
    },
    {
        "name":"AGB",
        "core":"C–O degenerado",
        "burning":"dos capas: He y H",
        "surface":"R y L grandes, Teff baja; pulsos térmicos y pérdida de masa",
    },
]

SOLAR_EVOLVED_REFERENCE = {
    "age_gyr":9.8,
    "radius_rsun":1.27,
    "pc_pa":1.3e17,
    "tc_k":1.91e7,
    "lum_lsun":2.13,
    "xh_core":"≈ 0",
    "xh_envelope":"≈ 0.7",
    "energy_region":"0.1 < m/M⊙ < 0.3, según el documento",
    "outer_no_fusion":"m/M > 0.8",
    "inner_transport":"radiativo para m/M < 0.7",
    "outer_transport":"convectivo para m/M > 0.7",
}

def early_stage(index: int) -> dict:
    if not 0 <= index < len(EARLY_STAGES):
        raise IndexError(index)
    return EARLY_STAGES[index]

def advanced_stage(index: int) -> dict:
    if not 0 <= index < len(ADVANCED_STAGES):
        raise IndexError(index)
    return ADVANCED_STAGES[index]

def self_test():
    assert mirror_response(-0.1)["envelope"] == "expansión"
    assert mirror_response(+0.1)["envelope"] == "contracción"
    assert abs(normalized_gravitational_energy(0.5) + 2.0) < 1e-12

    q=sc_limit(0.62,1.34)
    assert 0.075 < q < 0.085, q  # direct evaluation of the source formula
    # The supplied document also prints ~0.12 for this numerical example;
    # that arithmetic discrepancy is handled explicitly in the UI/docs.

    assert early_stage(2)["name"].startswith("Agotamiento")
    assert advanced_stage(3)["name"] == "Flash de He"
    assert SOLAR_EVOLVED_REFERENCE["radius_rsun"] == 1.27

if __name__=="__main__":
    self_test()
    print("POST_ZAMS_CORE_SELF_TEST=PASS")
