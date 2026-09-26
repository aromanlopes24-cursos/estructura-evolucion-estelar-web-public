#!/usr/bin/env python3
"""Núcleo numérico — Módulo 04: Fuentes de energía estelar."""

from __future__ import annotations
import math

G = 6.67430e-11
C = 299792458.0
K_B = 1.380649e-23
M_P = 1.67262192369e-27
M_SUN = 1.98847e30
R_SUN = 6.957e8
L_SUN = 3.828e26
YEAR = 365.25*24*3600
EV_J = 1.602176634e-19
ALPHA = 7.2973525693e-3
MEV_J = 1e6*EV_J
KEV_J = 1e3*EV_J

def gravitational_potential_uniform_j(m_msun: float, r_rsun: float) -> float:
    """Ug = -3/5 GM^2/R for a uniform sphere."""
    M=m_msun*M_SUN; R=r_rsun*R_SUN
    return -(3.0/5.0)*G*M*M/R

def virial_available_energy_j(m_msun: float, r_rsun: float) -> float:
    """Energy radiated in collapse from Ri>>R using course virial estimate: 3/10 GM^2/R."""
    M=m_msun*M_SUN; R=r_rsun*R_SUN
    return (3.0/10.0)*G*M*M/R

def kelvin_helmholtz_years(m_msun: float, r_rsun: float, l_lsun: float) -> float:
    E=virial_available_energy_j(m_msun,r_rsun)
    L=l_lsun*L_SUN
    return E/L/YEAR

def chemical_energy_j(m_msun: float, ev_per_atom: float=10.0) -> float:
    """Pedagogical estimate from class: pure H, electronic energy per atom."""
    N=m_msun*M_SUN/M_P
    return N*ev_per_atom*EV_J

def chemical_timescale_years(m_msun: float, l_lsun: float, ev_per_atom: float=10.0) -> float:
    return chemical_energy_j(m_msun,ev_per_atom)/(l_lsun*L_SUN)/YEAR

def nuclear_energy_j(m_msun: float, burn_fraction: float=0.10, efficiency: float=0.007) -> float:
    """Course estimate: fraction of stellar mass participating * 0.7% mass conversion."""
    return efficiency*burn_fraction*m_msun*M_SUN*C*C

def nuclear_timescale_years(m_msun: float, l_lsun: float, burn_fraction: float=0.10, efficiency: float=0.007) -> float:
    return nuclear_energy_j(m_msun,burn_fraction,efficiency)/(l_lsun*L_SUN)/YEAR

def coulomb_potential_mev(r_fm: float, z1: int=1, z2: int=1) -> float:
    if r_fm <= 0: raise ValueError("r_fm > 0")
    return 1.44*z1*z2/r_fm

def classical_turning_radius_fm(E_keV: float, z1: int=1, z2: int=1) -> float:
    if E_keV <= 0: raise ValueError("E_keV > 0")
    E_MeV=E_keV/1000.0
    return 1.44*z1*z2/E_MeV

def reduced_mass_kg(a1: float=1.0, a2: float=1.0) -> float:
    m1=a1*M_P; m2=a2*M_P
    return m1*m2/(m1+m2)

def relative_velocity_ms(E_keV: float, mu_kg: float|None=None) -> float:
    if mu_kg is None: mu_kg=reduced_mass_kg()
    E=E_keV*KEV_J
    return math.sqrt(2.0*E/mu_kg)

def gamow_factor(E_keV: float, z1: int=1, z2: int=1, mu_kg: float|None=None) -> float:
    if mu_kg is None: mu_kg=reduced_mass_kg()
    v=relative_velocity_ms(E_keV,mu_kg)
    eta=ALPHA*z1*z2*C/v
    return math.exp(-2.0*math.pi*eta)

def gamow_exponent(E_keV: float, z1: int=1, z2: int=1, mu_kg: float|None=None) -> float:
    if mu_kg is None: mu_kg=reduced_mass_kg()
    v=relative_velocity_ms(E_keV,mu_kg)
    eta=ALPHA*z1*z2*C/v
    return 2.0*math.pi*eta

def kT_keV(T_K: float) -> float:
    return K_B*T_K/KEV_J

def maxwell_factor(E_keV: float, T_K: float) -> float:
    """Only the exponential Boltzmann factor exp(-E/kT), as used in the Gamow-window argument."""
    return math.exp(-E_keV/kT_keV(T_K))

def gamow_product(E_keV: float, T_K: float, z1: int=1, z2: int=1, mu_kg: float|None=None) -> float:
    return maxwell_factor(E_keV,T_K)*gamow_factor(E_keV,z1,z2,mu_kg)

def gamow_peak_keV(T_K: float, z1: int=1, z2: int=1, mu_kg: float|None=None) -> float:
    """E0 = [mu c^2 (pi alpha Z1 Z2)^2 (kT)^2 / 2]^(1/3)."""
    if mu_kg is None: mu_kg=reduced_mass_kg()
    kT=K_B*T_K
    E0=((mu_kg*C*C*(math.pi*ALPHA*z1*z2)**2*(kT**2))/2.0)**(1.0/3.0)
    return E0/KEV_J

def self_test():
    tkh=kelvin_helmholtz_years(1,1,1)
    assert 0.8e7 < tkh < 1.2e7, tkh
    tch=chemical_timescale_years(1,1,10)
    assert 1.0e5 < tch < 2.0e5, tch
    tn=nuclear_timescale_years(1,1,0.10,0.007)
    assert 0.8e10 < tn < 1.2e10, tn
    assert abs(classical_turning_radius_fm(10)-144.0) < 1e-10
    pg=gamow_factor(10)
    assert 8e-4 < pg < 1.0e-3, pg
    e0=gamow_peak_keV(1.55e7)
    assert 5.5 < e0 < 6.5, e0

if __name__=="__main__":
    self_test()
    print("ENERGY_CORE_SELF_TEST=PASS")
