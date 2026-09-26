#!/usr/bin/env python3
"""Núcleo numérico — Módulo 02: Estructura mecánica.

Base del curso:
    dP/dr = -G M(r) rho(r) / r^2
    dM/dr = 4 pi r^2 rho(r)

Extensión didáctica usada para obtener una solución analítica:
    estrella de densidad constante.

Para rho = constante:
    M(r) = M (r/R)^3
    P(r) = Pc [1 - (r/R)^2]
    Pc = 3 G M^2 / (8 pi R^4)

La estimación de orden de magnitud usada en las notas de clase es:
    Pc,est ~ G M rho_mean / R
que, para una esfera uniforme, es exactamente 2 Pc.
"""

from __future__ import annotations
import math

G = 6.67430e-11
M_SUN = 1.98847e30
R_SUN = 6.957e8

def mean_density_kgm3(mass_msun: float, radius_rsun: float) -> float:
    M = mass_msun * M_SUN
    R = radius_rsun * R_SUN
    return 3.0 * M / (4.0 * math.pi * R**3)

def enclosed_mass_fraction(x: float) -> float:
    """Uniform-density sphere: m(r)/M = x^3, x=r/R."""
    x = min(max(x, 0.0), 1.0)
    return x**3

def enclosed_mass_kg(mass_msun: float, x: float) -> float:
    return mass_msun * M_SUN * enclosed_mass_fraction(x)

def dm_dr_kgm(mass_msun: float, radius_rsun: float, x: float) -> float:
    """dM/dr = 4 pi r^2 rho for uniform density."""
    rho = mean_density_kgm3(mass_msun, radius_rsun)
    R = radius_rsun * R_SUN
    r = min(max(x,0.0),1.0) * R
    return 4.0 * math.pi * r*r * rho

def central_pressure_uniform_pa(mass_msun: float, radius_rsun: float) -> float:
    M = mass_msun * M_SUN
    R = radius_rsun * R_SUN
    return 3.0 * G * M*M / (8.0 * math.pi * R**4)

def central_pressure_class_estimate_pa(mass_msun: float, radius_rsun: float) -> float:
    """Course order-of-magnitude estimate Pc ~ G M rho_mean / R."""
    M = mass_msun * M_SUN
    R = radius_rsun * R_SUN
    rho = mean_density_kgm3(mass_msun, radius_rsun)
    return G * M * rho / R

def pressure_uniform_pa(mass_msun: float, radius_rsun: float, x: float) -> float:
    x = min(max(x,0.0),1.0)
    return central_pressure_uniform_pa(mass_msun, radius_rsun) * (1.0 - x*x)

def gravity_ms2(mass_msun: float, radius_rsun: float, x: float) -> float:
    """g(r)=G m(r)/r^2. For uniform density, finite and linear in x."""
    x = min(max(x,0.0),1.0)
    if x == 0:
        return 0.0
    M = mass_msun * M_SUN
    R = radius_rsun * R_SUN
    r = x * R
    m = enclosed_mass_kg(mass_msun, x)
    return G * m / (r*r)

def surface_gravity_ms2(mass_msun: float, radius_rsun: float) -> float:
    M = mass_msun * M_SUN
    R = radius_rsun * R_SUN
    return G*M/(R*R)

def hydrostatic_gradient_pa_per_m(mass_msun: float, radius_rsun: float, x: float) -> float:
    """dP/dr = -rho*g."""
    rho = mean_density_kgm3(mass_msun, radius_rsun)
    return -rho * gravity_ms2(mass_msun, radius_rsun, x)

def pressure_from_integrated_gradient_pa(mass_msun: float, radius_rsun: float, x: float) -> float:
    """Analytic integral from surface P(R)=0 inward for uniform density."""
    return pressure_uniform_pa(mass_msun, radius_rsun, x)

def scientific(x: float, digits: int = 3) -> str:
    if x == 0:
        return "0"
    return f"{x:.{digits}e}"

def self_test():
    # Solar mean density near 1408 kg/m3 using adopted constants.
    rho = mean_density_kgm3(1.0,1.0)
    assert 1390 < rho < 1430, rho

    # Uniform sphere mass profile.
    assert abs(enclosed_mass_fraction(0.5)-0.125) < 1e-14
    assert abs(enclosed_mass_fraction(1.0)-1.0) < 1e-14

    # Pressure boundary conditions.
    pc = central_pressure_uniform_pa(1.0,1.0)
    assert 1.30e14 < pc < 1.40e14, pc
    assert abs(pressure_uniform_pa(1.0,1.0,0.0)-pc) < 1e-8*pc
    assert abs(pressure_uniform_pa(1.0,1.0,1.0)) < 1e-12*pc

    # Course estimate is exactly 2x for a uniform sphere.
    pest = central_pressure_class_estimate_pa(1.0,1.0)
    assert abs(pest/pc - 2.0) < 1e-12

    # Hydrostatic gradient has the correct sign away from center.
    assert hydrostatic_gradient_pa_per_m(1.0,1.0,0.5) < 0

    # Surface gravity.
    gs = surface_gravity_ms2(1.0,1.0)
    assert 270 < gs < 280

if __name__ == "__main__":
    self_test()
    print("STRUCTURE_CORE_SELF_TEST=PASS")
