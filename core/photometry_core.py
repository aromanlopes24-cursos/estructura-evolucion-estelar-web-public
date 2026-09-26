#!/usr/bin/env python3
"""Núcleo numérico — Módulo 01: Fotometría y extinción.

Las relaciones siguen la convención usada en el material del curso:
m = -2.5 log10(F/F0)
m-M = 5 log10(d/10 pc) + A
F/F0 = exp(-tau)
E(B-V) = (B-V) - (B-V)_0
A_V ≈ 3.0 E(B-V)
"""

from __future__ import annotations
import math

LOGE10 = math.log10(math.e)
A_PER_TAU = 2.5 * LOGE10  # ≈ 1.085736 mag

def magnitude_from_flux_ratio(flux_ratio: float) -> float:
    """Δm relative to a reference flux: -2.5 log10(F/F0)."""
    if flux_ratio <= 0:
        raise ValueError("flux_ratio debe ser > 0")
    return -2.5 * math.log10(flux_ratio)

def flux_ratio_from_mag_difference(delta_m: float) -> float:
    """F1/F2 from Δm = m1-m2."""
    return 10.0 ** (-0.4 * delta_m)

def distance_modulus(distance_pc: float) -> float:
    """μ = m-M = 5 log10(d/10 pc), without extinction."""
    if distance_pc <= 0:
        raise ValueError("distance_pc debe ser > 0")
    return 5.0 * math.log10(distance_pc / 10.0)

def distance_from_modulus(mu: float) -> float:
    """d [pc] from μ = 5 log10(d/10 pc)."""
    return 10.0 * 10.0 ** (mu / 5.0)

def transmission_from_tau(tau: float) -> float:
    if tau < 0:
        raise ValueError("tau debe ser >= 0")
    return math.exp(-tau)

def extinction_mag_from_tau(tau: float) -> float:
    """A = 2.5 log10(e) tau."""
    if tau < 0:
        raise ValueError("tau debe ser >= 0")
    return A_PER_TAU * tau

def apparent_magnitude(M_abs: float, distance_pc: float, A_mag: float = 0.0) -> float:
    if A_mag < 0:
        raise ValueError("A_mag debe ser >= 0")
    return M_abs + distance_modulus(distance_pc) + A_mag

def color_excess(observed_bv: float, intrinsic_bv: float) -> float:
    return observed_bv - intrinsic_bv

def observed_bv(intrinsic_bv: float, ebv: float) -> float:
    return intrinsic_bv + ebv

def av_from_ebv(ebv: float, R: float = 3.0) -> float:
    """Course convention: A_V ≈ 3.0 E(B-V)."""
    if ebv < 0:
        raise ValueError("ebv debe ser >= 0 para el laboratorio")
    return R * ebv

def synthesis(Mv: float, intrinsic_bv: float, distance_pc: float, ebv: float, Rv: float = 3.0):
    """Return internally consistent V, B, A_V, A_B, μ, observed B-V."""
    mu = distance_modulus(distance_pc)
    Av = av_from_ebv(ebv, Rv)
    Ab = Av + ebv  # E(B-V)=A_B-A_V
    Mb = Mv + intrinsic_bv
    V = Mv + mu + Av
    B = Mb + mu + Ab
    return {
        "mu": mu,
        "Av": Av,
        "Ab": Ab,
        "Mv": Mv,
        "Mb": Mb,
        "V": V,
        "B": B,
        "bv0": intrinsic_bv,
        "bv_obs": B - V,
        "ebv": ebv,
    }

def self_test():
    # Pogson: 5 mag = factor 100 in flux.
    assert abs(flux_ratio_from_mag_difference(5.0) - 0.01) < 1e-12
    assert abs(magnitude_from_flux_ratio(0.01) - 5.0) < 1e-12

    # Distance modulus anchors.
    assert abs(distance_modulus(10.0)) < 1e-12
    assert abs(distance_modulus(100.0) - 5.0) < 1e-12
    assert abs(distance_from_modulus(5.0) - 100.0) < 1e-10

    # Optical depth / magnitudes.
    assert abs(transmission_from_tau(1.0) - math.e**-1) < 1e-12
    assert abs(extinction_mag_from_tau(1.0) - A_PER_TAU) < 1e-12

    # Course reddening relation.
    assert abs(av_from_ebv(0.2) - 0.6) < 1e-12

    # Synthesis identity.
    s = synthesis(Mv=1.0, intrinsic_bv=0.3, distance_pc=100.0, ebv=0.2)
    assert abs(s["bv_obs"] - 0.5) < 1e-12
    assert abs(s["V"] - (1.0 + 5.0 + 0.6)) < 1e-12
    assert abs((s["B"] - s["V"]) - (0.3 + 0.2)) < 1e-12

if __name__ == "__main__":
    self_test()
    print("PHOTOMETRY_CORE_SELF_TEST=PASS")
