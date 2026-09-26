#!/usr/bin/env python3
"""Núcleo numérico — Módulo 05: Transporte de energía.

Base del material:
- camino libre medio: lambda = 1/(kappa rho)
- gradiente radiativo correcto del material complementario:
  dT/dr = - 3 kappa rho L / (64 pi sigma T^3 r^2)
- gradiente adiabático para gas ideal:
  (dT/dr)_ad = -(1 - 1/gamma) (m_av/k_B) g
- competencia radiación/convección por comparación de magnitudes.

No se modela conducción porque el material suministrado la menciona como
mecanismo posible, pero no desarrolla una ecuación cuantitativa para ella.
"""

from __future__ import annotations
import math

SIGMA = 5.670374419e-8
G = 6.67430e-11
K_B = 1.380649e-23
M_H = 1.6735575e-27
M_SUN = 1.98847e30
R_SUN = 6.957e8
L_SUN = 3.828e26

def mean_free_path_m(kappa_m2kg: float, rho_kgm3: float) -> float:
    if kappa_m2kg <= 0 or rho_kgm3 <= 0:
        raise ValueError("kappa y rho deben ser > 0")
    return 1.0/(kappa_m2kg*rho_kgm3)

def radiative_gradient_k_per_m(
    kappa_m2kg: float,
    rho_kgm3: float,
    luminosity_lsun: float,
    temperature_k: float,
    radius_rsun: float,
) -> float:
    """Correct expression quoted in the complementary material."""
    if min(kappa_m2kg,rho_kgm3,luminosity_lsun,temperature_k,radius_rsun) <= 0:
        raise ValueError("Todos los parámetros deben ser > 0")
    L = luminosity_lsun*L_SUN
    r = radius_rsun*R_SUN
    return -3.0*kappa_m2kg*rho_kgm3*L/(64.0*math.pi*SIGMA*temperature_k**3*r**2)

def radiative_gradient_class_simplified_k_per_m(
    kappa_m2kg: float,
    rho_kgm3: float,
    luminosity_lsun: float,
    temperature_k: float,
    radius_rsun: float,
) -> float:
    """Simplified proportionality from the class slides: -k rho L/(16 pi sigma T^3 r^2)."""
    L=luminosity_lsun*L_SUN
    r=radius_rsun*R_SUN
    return -kappa_m2kg*rho_kgm3*L/(16.0*math.pi*SIGMA*temperature_k**3*r**2)

def gravity_ms2(mass_inside_msun: float, radius_rsun: float) -> float:
    if mass_inside_msun <= 0 or radius_rsun <= 0:
        raise ValueError("masa y radio deben ser > 0")
    M=mass_inside_msun*M_SUN
    r=radius_rsun*R_SUN
    return G*M/r**2

def adiabatic_gradient_k_per_m(
    gamma: float,
    mu: float,
    mass_inside_msun: float,
    radius_rsun: float,
) -> float:
    """Material complementario: -(1-1/gamma) m_av/k * g, with m_av=mu*m_H."""
    if gamma <= 1 or mu <= 0:
        raise ValueError("gamma>1 y mu>0")
    g=gravity_ms2(mass_inside_msun,radius_rsun)
    m_av=mu*M_H
    return -(1.0-1.0/gamma)*(m_av/K_B)*g

def transport_ratio(
    kappa_m2kg: float,
    rho_kgm3: float,
    luminosity_lsun: float,
    temperature_k: float,
    radius_rsun: float,
    gamma: float,
    mu: float,
    mass_inside_msun: float,
) -> float:
    """|grad_rad|/|grad_ad|."""
    gr=abs(radiative_gradient_k_per_m(kappa_m2kg,rho_kgm3,luminosity_lsun,temperature_k,radius_rsun))
    ga=abs(adiabatic_gradient_k_per_m(gamma,mu,mass_inside_msun,radius_rsun))
    return gr/ga

def transport_regime(ratio: float) -> str:
    # Pedagogical implementation of the criterion in magnitude form.
    return "convectivo" if ratio > 1.0 else "radiativo estable posible"

def nabla_ad(gamma: float) -> float:
    return (gamma-1.0)/gamma

def self_test():
    # Mean free path.
    assert abs(mean_free_path_m(2.0,100.0)-0.005) < 1e-14

    # Scaling checks of grad_rad.
    g0=abs(radiative_gradient_k_per_m(1,100,1,2e6,0.7))
    gk=abs(radiative_gradient_k_per_m(2,100,1,2e6,0.7))
    grho=abs(radiative_gradient_k_per_m(1,200,1,2e6,0.7))
    gL=abs(radiative_gradient_k_per_m(1,100,2,2e6,0.7))
    gT=abs(radiative_gradient_k_per_m(1,100,1,4e6,0.7))
    assert abs(gk/g0-2) < 1e-12
    assert abs(grho/g0-2) < 1e-12
    assert abs(gL/g0-2) < 1e-12
    assert abs(gT/g0-1/8) < 1e-12

    # Slides simplified expression differs by factor 4/3 from correct expression.
    gs=abs(radiative_gradient_class_simplified_k_per_m(1,100,1,2e6,0.7))
    assert abs(gs/g0 - 4/3) < 1e-12

    # Monatomic gas nabla_ad.
    assert abs(nabla_ad(5/3)-0.4) < 1e-12

    # Adiabatic gradient independent of luminosity by construction.
    ga=adiabatic_gradient_k_per_m(5/3,0.61,0.98,0.7)
    assert ga < 0

if __name__=="__main__":
    self_test()
    print("TRANSPORT_CORE_SELF_TEST=PASS")
