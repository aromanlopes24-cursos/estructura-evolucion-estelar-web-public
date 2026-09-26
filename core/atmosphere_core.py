#!/usr/bin/env python3
"""Núcleo numérico — Módulo 06: Atmósferas estelares."""

from __future__ import annotations
import math

H = 6.62607015e-34
C = 299792458.0
K_B = 1.380649e-23
SIGMA = 5.670374419e-8
A_RAD = 4.0*SIGMA/C
M_H = 1.6735575e-27

def planck_lambda_w_m3_sr(lam_nm: float, T_K: float) -> float:
    """B_lambda [W m^-3 sr^-1]."""
    if lam_nm <= 0 or T_K <= 0:
        raise ValueError("lambda y T deben ser > 0")
    lam = lam_nm*1e-9
    x = H*C/(lam*K_B*T_K)
    return (2.0*H*C*C/lam**5) / math.expm1(x)

def radiation_energy_density_j_m3(T_K: float) -> float:
    """u = a T^4."""
    if T_K <= 0:
        raise ValueError("T debe ser > 0")
    return A_RAD*T_K**4

def mean_free_path_m(kappa_m2kg: float, rho_kgm3: float) -> float:
    if kappa_m2kg <= 0 or rho_kgm3 <= 0:
        raise ValueError("kappa y rho deben ser > 0")
    return 1.0/(kappa_m2kg*rho_kgm3)

def optical_depth_uniform(kappa_m2kg: float, rho_kgm3: float, path_m: float) -> float:
    if min(kappa_m2kg,rho_kgm3,path_m) < 0:
        raise ValueError("parámetros no negativos")
    return kappa_m2kg*rho_kgm3*path_m

def transmitted_fraction(tau: float) -> float:
    if tau < 0:
        raise ValueError("tau debe ser >= 0")
    return math.exp(-tau)

def airmass_sec(z_deg: float) -> float:
    """Plane-parallel sec(z), used in the class notes."""
    if not (0 <= z_deg < 90):
        raise ValueError("0 <= z < 90")
    return 1.0/math.cos(math.radians(z_deg))

def atmospheric_transmission(tau0: float, z_deg: float) -> float:
    """I/I0 = exp(-tau0 sec z)."""
    if tau0 < 0:
        raise ValueError("tau0 >= 0")
    return math.exp(-tau0*airmass_sec(z_deg))

def photon_escape_steps(tau: float) -> float:
    """Class random-walk scaling for tau >> 1: n ~ tau^2."""
    if tau < 0:
        raise ValueError("tau >= 0")
    return tau*tau

def doppler_width_nm(lam0_nm: float, T_K: float, particle_mass_kg: float=M_H) -> float:
    """Width quoted before FWHM in notes: Δλ = 2 λ/c sqrt(2 k T/m)."""
    if min(lam0_nm,T_K,particle_mass_kg) <= 0:
        raise ValueError("parámetros > 0")
    lam = lam0_nm*1e-9
    dlam = (2.0*lam/C)*math.sqrt(2.0*K_B*T_K/particle_mass_kg)
    return dlam*1e9

def doppler_fwhm_nm(
    lam0_nm: float,
    T_K: float,
    particle_mass_kg: float=M_H,
    vturb_kms: float=0.0,
) -> float:
    """FWHM from the formula in the notes."""
    if min(lam0_nm,T_K,particle_mass_kg) <= 0 or vturb_kms < 0:
        raise ValueError("parámetros inválidos")
    lam=lam0_nm*1e-9
    vt=vturb_kms*1000.0
    term=(2.0*K_B*T_K/particle_mass_kg + vt*vt)*math.log(2.0)
    return (2.0*lam/C)*math.sqrt(term)*1e9

def gaussian_equivalent_width_nm(depth: float, fwhm_nm: float) -> float:
    """Toy Gaussian absorption line, explicitly an educational extension."""
    if not (0 <= depth <= 1) or fwhm_nm < 0:
        raise ValueError("depth in [0,1], fwhm >= 0")
    return depth*fwhm_nm*math.sqrt(math.pi)/(2.0*math.sqrt(math.log(2.0)))

def gaussian_normalized_flux(lam_nm: float, lam0_nm: float, depth: float, fwhm_nm: float) -> float:
    if fwhm_nm <= 0:
        return 1.0
    x=(lam_nm-lam0_nm)/fwhm_nm
    return 1.0-depth*math.exp(-4.0*math.log(2.0)*x*x)

def self_test():
    # Solar-ish mean free path example from the notes.
    l=mean_free_path_m(0.03,2.1e-4)
    assert 1.5e5 < l < 1.7e5, l

    # tau=1 means e^-1 transmission.
    assert abs(transmitted_fraction(1)-math.e**-1) < 1e-12

    # Plane-parallel airmass.
    assert abs(airmass_sec(60)-2.0) < 1e-12

    # Notes quote Δλ~0.0427 nm for Halpha at 5770 K.
    d=doppler_width_nm(656.3,5770)
    assert abs(d-0.0427) < 0.001, d

    # Blackbody intensity positive and increases strongly with T at fixed lambda.
    b1=planck_lambda_w_m3_sr(500,5000)
    b2=planck_lambda_w_m3_sr(500,6000)
    assert b2>b1>0

    # u=aT^4.
    u1=radiation_energy_density_j_m3(5000)
    u2=radiation_energy_density_j_m3(10000)
    assert abs(u2/u1-16.0) < 1e-12

if __name__=="__main__":
    self_test()
    print("ATMOSPHERE_CORE_SELF_TEST=PASS")
