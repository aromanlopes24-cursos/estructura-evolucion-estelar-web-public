#!/usr/bin/env python3
from functools import lru_cache
import numpy as np
from scipy.integrate import solve_ivp

G = 6.67430e-11
M_JUP = 1.89813e27
R_JUP = 7.1492e7
M_SUN = 1.98847e30
R_SUN = 6.96e8
L_SUN = 3.839e26
SIGMA_SB = 5.670374419e-8
K_B = 1.380649e-23
M_H = 1.6735575e-27


def _rhs(xi, y, n):
    theta, u = y
    t = max(theta, 0.0)
    return [u, -(2.0 / xi) * u - t**n]


def _surface(xi, y, n):
    return y[0]


_surface.terminal = True
_surface.direction = -1


@lru_cache(maxsize=256)
def solve_lane_emden_cached(n_rounded, npoints=1001):
    n = float(n_rounded)
    if not (0.0 < n < 5.0):
        raise ValueError("Se requiere 0 < n < 5.")

    eps = 1e-7
    sol = solve_ivp(
        _rhs,
        (eps, 200.0),
        [1.0 - eps**2 / 6.0, -eps / 3.0],
        args=(n,),
        events=_surface,
        dense_output=True,
        max_step=0.02,
        rtol=1e-9,
        atol=1e-11,
    )
    if len(sol.t_events[0]) == 0:
        raise RuntimeError(f"No se encontró superficie para n={n}.")

    xi1 = float(sol.t_events[0][0])
    xi = np.linspace(eps, xi1, int(npoints))
    theta, u = sol.sol(xi)
    theta = np.maximum(theta, 0.0)
    omega = -xi1**2 * float(sol.sol(xi1)[1])
    q = -xi**2 * u
    mfrac = q / omega
    return n, xi, xi1, theta, u, omega, mfrac


def solve_lane_emden(n, npoints=1001):
    key = round(float(n), 4)
    n, xi, xi1, theta, u, omega, mfrac = solve_lane_emden_cached(key, npoints)
    return {
        "n": n,
        "xi": xi.copy(),
        "xi1": xi1,
        "theta": theta.copy(),
        "u": u.copy(),
        "omega": omega,
        "mfrac": mfrac.copy(),
    }


def scale_polytrope(mass_mjup, radius_rjup, n=1.5, npoints=1001):
    M = float(mass_mjup) * M_JUP
    R = float(radius_rjup) * R_JUP
    le = solve_lane_emden(n, npoints=npoints)

    a = R / le["xi1"]
    rho_c = M / (4.0 * np.pi * a**3 * le["omega"])
    K = 4.0 * np.pi * G * a**2 / (n + 1.0) * rho_c ** (1.0 - 1.0 / n)
    P_c = K * rho_c ** (1.0 + 1.0 / n)

    r = a * le["xi"]
    rho = rho_c * le["theta"] ** n
    P = K * rho ** (1.0 + 1.0 / n)
    rho_mean = 3.0 * M / (4.0 * np.pi * R**3)

    I = (8.0 * np.pi / 3.0) * np.trapz(rho * r**4, r)
    inertia_coeff = I / (M * R**2)
    m50 = float(np.interp(0.5, r / R, le["mfrac"]))

    return {
        **le,
        "M": M,
        "R": R,
        "r": r,
        "rnorm": r / R,
        "rho": rho,
        "P": P,
        "rho_c": rho_c,
        "rho_mean": rho_mean,
        "concentration": rho_c / rho_mean,
        "K": K,
        "P_c": P_c,
        "inertia_coeff": inertia_coeff,
        "m50": m50,
        "gamma_pol": 1.0 + 1.0 / n,
        "nabla_pol": 1.0 / (n + 1.0),
        "logg_calc": np.log10((G * M / R**2) * 100.0),
    }


def match_bhac(catalog_row, bhac_rows):
    if not bhac_rows:
        return None, np.nan

    M_sun = float(catalog_row["mass_evo"]) * M_JUP / M_SUN
    R_sun = float(catalog_row["radius_evo"]) * R_JUP / R_SUN
    T = float(catalog_row["teff_evo"])
    logL = float(catalog_row["log_lbol_lsun"])
    logg = float(catalog_row["logg_evo"])

    best = None
    bestd = np.inf
    for b in bhac_rows:
        d = (
            (np.log10(b["mass_msun"] / M_sun) / 0.08) ** 2
            + (np.log10(b["radius_rsun"] / R_sun) / 0.08) ** 2
            + ((b["teff_K"] - T) / 150.0) ** 2
            + ((b["logL_lsun"] - logL) / 0.15) ** 2
            + ((b["logg_cgs"] - logg) / 0.15) ** 2
        )
        if d < bestd:
            bestd = d
            best = b
    return best, float(bestd)


def transport_proxy(
    model,
    teff,
    logL_lsun,
    bhac_row=None,
    mu_eff=0.61,
    kappa_cgs=1.0,
    alpha_lum=1.0,
    nabla_ad=0.4,
):
    # Modelo docente para explorar Schwarzschild.
    teff = float(teff)
    Lsurf = 10 ** float(logL_lsun) * L_SUN
    mu_eff = float(mu_eff)
    kappa_cgs = float(kappa_cgs)
    alpha_lum = float(alpha_lum)

    if bhac_row is not None and np.isfinite(bhac_row.get("logTc_K", np.nan)):
        Tc = 10 ** float(bhac_row["logTc_K"])
        tc_source = "BHAC15"
    else:
        Tc = model["P_c"] * mu_eff * M_H / (model["rho_c"] * K_B)
        tc_source = "gas ideal central"

    Tc = max(Tc, teff * 1.01)
    T = teff + (Tc - teff) * model["theta"]

    mfrac = np.clip(model["mfrac"], 1e-18, 1.0)
    mass = model["M"] * mfrac
    Lr = Lsurf * mfrac**alpha_lum

    # 1 cm^2/g = 0.1 m^2/kg
    kappa_si = kappa_cgs * 0.1
    denom = 64.0 * np.pi * SIGMA_SB * G * mass * T**4
    grad_rad = 3.0 * kappa_si * Lr * model["P"] / np.maximum(denom, 1e-300)
    grad_rad = np.nan_to_num(grad_rad, nan=0.0, posinf=1e9, neginf=0.0)
    grad_rad = np.maximum(grad_rad, 0.0)

    conv = grad_rad > float(nabla_ad)

    if conv[0]:
        rrad_frac = 0.0
        mrad_frac = 0.0
    else:
        idx = np.where(conv)[0]
        if len(idx) == 0:
            rrad_frac = 1.0
            mrad_frac = 1.0
        else:
            j = int(idx[0])
            rrad_frac = float(model["rnorm"][j])
            mrad_frac = float(model["mfrac"][j])

    return {
        "T": T,
        "Tc": Tc,
        "tc_source": tc_source,
        "Lr": Lr,
        "Lsurf": Lsurf,
        "kappa_cgs": kappa_cgs,
        "alpha_lum": alpha_lum,
        "mu_eff": mu_eff,
        "grad_rad": grad_rad,
        "grad_ad": float(nabla_ad),
        "grad_pol": model["nabla_pol"],
        "convective": conv,
        "rrad_frac": rrad_frac,
        "mrad_frac": mrad_frac,
    }
