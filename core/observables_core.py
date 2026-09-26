#!/usr/bin/env python3
"""Núcleo numérico del Laboratorio 00 — Observables estelares."""

from __future__ import annotations
import math

SIGMA_SB = 5.670374419e-8      # W m^-2 K^-4
L_SUN = 3.828e26               # W
R_SUN = 6.957e8                # m
PC = 3.085677581491367e16      # m
T_SUN = 5772.0                 # K

def luminosity_w(radius_rsun: float, teff_k: float) -> float:
    """L = 4*pi*R^2*sigma*T^4."""
    r = radius_rsun * R_SUN
    return 4.0 * math.pi * r * r * SIGMA_SB * teff_k**4

def luminosity_lsun(radius_rsun: float, teff_k: float) -> float:
    return luminosity_w(radius_rsun, teff_k) / L_SUN

def flux_wm2(luminosity_watt: float, distance_pc: float) -> float:
    """F = L/(4*pi*d^2)."""
    d = distance_pc * PC
    return luminosity_watt / (4.0 * math.pi * d * d)

def flux_ratio_from_distance(d1_pc: float, d2_pc: float) -> float:
    """F2/F1 for the same isotropic luminosity."""
    return (d1_pc / d2_pc) ** 2

def distance_for_same_flux(
    luminosity_a_w: float,
    distance_a_pc: float,
    luminosity_b_w: float,
) -> float:
    """Distance of source B needed to match the flux of source A."""
    return distance_a_pc * math.sqrt(luminosity_b_w / luminosity_a_w)

def angular_radius_rad(radius_rsun: float, distance_pc: float) -> float:
    """Small-angle angular radius R/d."""
    return radius_rsun * R_SUN / (distance_pc * PC)

def solid_angle_uniform_disk_sr(radius_rsun: float, distance_pc: float) -> float:
    """Small-angle solid angle of a circular stellar disk: pi*(R/d)^2."""
    a = angular_radius_rad(radius_rsun, distance_pc)
    return math.pi * a * a

def surface_flux_wm2(teff_k: float) -> float:
    """Emergent bolometric surface flux for a blackbody: sigma*T^4."""
    return SIGMA_SB * teff_k**4

def isotropic_intensity_wm2sr(teff_k: float) -> float:
    """For an isotropically radiating surface hemisphere, F_surface = pi I."""
    return surface_flux_wm2(teff_k) / math.pi

def observed_flux_from_intensity(
    intensity_wm2sr: float, radius_rsun: float, distance_pc: float
) -> float:
    """Uniform unresolved disk: F_obs = I * Omega (small-angle, face-on approximation)."""
    return intensity_wm2sr * solid_angle_uniform_disk_sr(radius_rsun, distance_pc)

def scientific(x: float, digits: int = 3) -> str:
    if x == 0:
        return "0"
    return f"{x:.{digits}e}"

def self_test() -> None:
    # Solar Stefan-Boltzmann should be close to adopted Lsun.
    ls = luminosity_lsun(1.0, T_SUN)
    assert abs(ls - 1.0) < 0.01, ls

    # Inverse square.
    f1 = flux_wm2(L_SUN, 10.0)
    f2 = flux_wm2(L_SUN, 20.0)
    assert abs(f2 / f1 - 0.25) < 1e-12

    # Same-flux degeneracy: 4L at twice the distance.
    db = distance_for_same_flux(L_SUN, 10.0, 4.0 * L_SUN)
    assert abs(db - 20.0) < 1e-12

    # F=I Omega is consistent with L/(4pi d2) for blackbody sphere.
    I = isotropic_intensity_wm2sr(T_SUN)
    fi = observed_flux_from_intensity(I, 1.0, 10.0)
    fs = flux_wm2(luminosity_w_w := luminosity_w(1.0, T_SUN), 10.0)
    assert abs(fi / fs - 1.0) < 1e-12

if __name__ == "__main__":
    self_test()
    print("OBSERVABLES_CORE_SELF_TEST=PASS")
