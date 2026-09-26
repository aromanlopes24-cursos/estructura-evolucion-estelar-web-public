#!/usr/bin/env python3
"""Núcleo numérico/conceptual — Módulo 07: Secuencia principal.

Este módulo se apoya directamente en la tabla del material
"Estructura de las Estrellas en la Secuencia Principal":

0.08–0.3 Msun  -> p-p, totalmente convectivas
0.3–1.2 Msun   -> p-p, atmósfera convectiva / interior radiativo
1.2–100 Msun   -> CNO, atmósfera radiativa / interior convectivo

También se usa la relación de la clase de evolución:
t_n = E_n / L

No se introduce una relación masa-luminosidad ni una relación Tc(M)
porque esos vínculos cuantitativos no aparecen en el material suministrado.
"""

from __future__ import annotations

def mass_regime(m_msun: float) -> dict:
    if m_msun < 0:
        raise ValueError("La masa debe ser no negativa")
    if m_msun < 0.08:
        return {
            "label": "subestelar / enana marrón",
            "fusion": "sin fusión estable de H",
            "transport": "fuera de la tabla de SP",
            "core": "—",
            "envelope": "—",
            "main_sequence": False,
            "note": "T central insuficiente para iniciar la fusión del H según el material."
        }
    if m_msun < 0.30:
        return {
            "label": "SP de muy baja masa",
            "fusion": "ciclo p–p",
            "transport": "totalmente convectiva",
            "core": "convectivo",
            "envelope": "convectivo",
            "main_sequence": True,
            "note": "Rango 0.08–0.3 Msun del cuadro de clase."
        }
    if m_msun < 1.20:
        return {
            "label": "SP de baja/intermedia masa",
            "fusion": "ciclo p–p",
            "transport": "interior radiativo + región externa convectiva",
            "core": "radiativo",
            "envelope": "convectivo",
            "main_sequence": True,
            "note": "Rango 0.3–1.2 Msun del cuadro de clase."
        }
    if m_msun <= 100.0:
        return {
            "label": "SP masiva",
            "fusion": "ciclo CNO",
            "transport": "interior convectivo + región externa radiativa",
            "core": "convectivo",
            "envelope": "radiativo",
            "main_sequence": True,
            "note": "Rango 1.2–100 Msun del cuadro de clase."
        }
    return {
        "label": "por encima del rango estable resumido",
        "fusion": "no clasificado por la tabla del módulo",
        "transport": "fuera del rango 0.08–100 Msun",
        "core": "—",
        "envelope": "—",
        "main_sequence": False,
        "note": "El material destaca presión de radiación, pérdida de masa y vientos intensos para >100 Msun."
    }

def fusion_from_temperature_mk(Tc_MK: float) -> dict:
    """Only source-supported temperature statements; intermediate range is marked transitional."""
    if Tc_MK <= 0:
        raise ValueError("Tc debe ser > 0")
    if Tc_MK < 10:
        return {
            "label": "por debajo del intervalo p–p citado",
            "source_statement": "El material cita 10–15 MK para el régimen p–p de baja masa."
        }
    if Tc_MK <= 15:
        return {
            "label": "régimen p–p citado",
            "source_statement": "Ciclo p–p: temperaturas centrales de 10–15 MK."
        }
    if Tc_MK < 20:
        return {
            "label": "zona intermedia no cuantificada en las notas",
            "source_statement": "Las notas no asignan un umbral único entre 15 y 20 MK."
        }
    return {
        "label": "régimen CNO citado",
        "source_statement": "Ciclo CNO: Tc > 20 MK en el material."
    }

def cno_relative_sensitivity(T_ratio: float, exponent: float=19.0) -> float:
    """Didactic use of the source statement epsilon_CNO ∝ T^(18–20); exponent=19 midpoint."""
    if T_ratio <= 0:
        raise ValueError("T_ratio debe ser > 0")
    return T_ratio**exponent

def relative_nuclear_lifetime(energy_ratio: float, luminosity_ratio: float) -> float:
    """From t_n = E_n/L, normalized to an arbitrary reference."""
    if energy_ratio <= 0 or luminosity_ratio <= 0:
        raise ValueError("energy_ratio y luminosity_ratio > 0")
    return energy_ratio/luminosity_ratio

def self_test():
    assert mass_regime(0.05)["main_sequence"] is False
    assert mass_regime(0.10)["transport"] == "totalmente convectiva"
    assert mass_regime(1.0)["core"] == "radiativo"
    assert mass_regime(5.0)["core"] == "convectivo"
    assert mass_regime(120)["main_sequence"] is False

    assert "p–p" in fusion_from_temperature_mk(12)["label"]
    assert "intermedia" in fusion_from_temperature_mk(17)["label"]
    assert "CNO" in fusion_from_temperature_mk(25)["label"]

    # CNO sensitivity around a 10% T increase with exponent 19.
    x=cno_relative_sensitivity(1.1,19)
    assert 6.0 < x < 6.2

    assert abs(relative_nuclear_lifetime(2,4)-0.5) < 1e-12

if __name__=="__main__":
    self_test()
    print("MAIN_SEQUENCE_CORE_SELF_TEST=PASS")
