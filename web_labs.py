from __future__ import annotations
from pathlib import Path
import math
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/"core"))

from structure_core import *
from energy_core import *
import transport_core as tr
import atmosphere_core as atm
from main_sequence_core import *
from post_zams_core import *
from lane_emden_core import solve_lane_emden, scale_polytrope, M_SUN, R_SUN, M_JUP, R_JUP

DATA=ROOT/"data"/"BHAC15_tracks_structure_normalizado.csv"

def _plot():
    return plt.subplots()

def lab02():
    st.header("Laboratorio 02 — Estructura mecánica")
    exp=st.selectbox("Experimento",[
        "1 · Masa encerrada","2 · Equilibrio hidrostático","3 · Presión central",
        "4 · Cierre del sistema","5 · Síntesis radial"],key="lab02")
    if exp.startswith("1"):
        m=st.slider("M/M☉",.1,20.,1.,.05,key="02m1"); x=st.slider("r/R",0.,1.,.5,.005,key="02x1")
        mf=enclosed_mass_fraction(x)
        st.metric("M(r)/M",f"{mf:.5f}")
        xs=np.linspace(0,1,200)
        fig,ax=_plot();ax.plot(xs,[enclosed_mass_fraction(v) for v in xs]);ax.scatter([x],[mf]);ax.set(xlabel="r/R",ylabel="M(r)/M");ax.grid(alpha=.25);st.pyplot(fig)
    elif exp.startswith("2"):
        c1,c2,c3=st.columns(3);m=c1.slider("M/M☉",.1,20.,1.,.05,key="02m2");r=c2.slider("R/R☉",.1,10.,1.,.05,key="02r2");x=c3.slider("r/R",0.,1.,.5,.005,key="02x2")
        g=gravity_ms2(m,r,x);grad=hydrostatic_gradient_pa_per_m(m,r,x);P=pressure_uniform_pa(m,r,x);Pc=central_pressure_uniform_pa(m,r)
        a,b,c=st.columns(3);a.metric("g(r)",f"{g:.3e} m s⁻²");b.metric("dP/dr",f"{grad:.3e} Pa m⁻¹");c.metric("P/Pc",f"{P/Pc:.4f}")
        xs=np.linspace(0,1,200);fig,ax=_plot();ax.plot(xs,[pressure_uniform_pa(m,r,v)/Pc for v in xs]);ax.scatter([x],[P/Pc]);ax.set(xlabel="r/R",ylabel="P/Pc");ax.grid(alpha=.25);st.pyplot(fig)
    elif exp.startswith("3"):
        c1,c2=st.columns(2);m=c1.slider("M/M☉",.1,20.,1.,.05,key="02m3");r=c2.slider("R/R☉",.1,10.,1.,.05,key="02r3")
        pc=central_pressure_uniform_pa(m,r);pe=central_pressure_class_estimate_pa(m,r)
        st.metric("Pc esfera uniforme",f"{pc:.3e} Pa");st.metric("Estimación GMρ/R",f"{pe:.3e} Pa")
        st.caption(f"Razón estimación/exacto = {pe/pc:.3f}")
    elif exp.startswith("4"):
        st.info("Dos ecuaciones mecánicas: dP/dr y dM/dr. Funciones principales: P(r), M(r), ρ(r).")
        st.latex(r"\frac{dP}{dr}=-\frac{GM(r)\rho}{r^2},\qquad \frac{dM}{dr}=4\pi r^2\rho")
        st.success("Hace falta una relación adicional. Aquí el benchmark usa ρ=constante; el Módulo 03 usa P=Kρ^(1+1/n).")
    else:
        c1,c2,c3=st.columns(3);m=c1.slider("M/M☉",.1,20.,1.,.05,key="02m5");r=c2.slider("R/R☉",.1,10.,1.,.05,key="02r5");x=c3.slider("r/R",0.,1.,.5,.005,key="02x5")
        Pc=central_pressure_uniform_pa(m,r);gs=surface_gravity_ms2(m,r);xs=np.linspace(0,1,200)
        fig,ax=_plot();ax.plot(xs,[enclosed_mass_fraction(v) for v in xs],label="M/Mtot");ax.plot(xs,[pressure_uniform_pa(m,r,v)/Pc for v in xs],label="P/Pc");ax.plot(xs,[gravity_ms2(m,r,v)/gs for v in xs],label="g/gR");ax.axvline(x,ls="--");ax.legend();ax.grid(alpha=.25);st.pyplot(fig)

def lab03():
    st.header("Laboratorio 03 — Polítropos y Lane–Emden")
    exp=st.selectbox("Experimento",[
        "1 · Solución Lane–Emden","2 · Perfiles","3 · Escalamiento M–R",
        "4 · Dependencia con n","5 · BHAC15 real"],key="lab03")
    if exp.startswith("1"):
        n=st.slider("n",0.5,4.5,1.5,.05,key="03n1");le=solve_lane_emden(n)
        st.metric("ξ1",f"{le['xi1']:.5f}");st.metric("ωn",f"{le['omega']:.5f}")
        fig,ax=_plot();ax.plot(le["xi"],le["theta"]);ax.axhline(0,ls="--");ax.set(xlabel="ξ",ylabel="θ");ax.grid(alpha=.25);st.pyplot(fig)
    elif exp.startswith("2"):
        n=st.slider("n",0.5,4.5,1.5,.05,key="03n2");le=solve_lane_emden(n)
        fig,ax=_plot();ax.plot(le["xi"]/le["xi1"],le["theta"]**n,label="ρ/ρc");ax.plot(le["xi"]/le["xi1"],le["mfrac"],label="M(r)/M");ax.legend();ax.set(xlabel="r/R",ylabel="normalizado");ax.grid(alpha=.25);st.pyplot(fig)
    elif exp.startswith("3"):
        c1,c2,c3=st.columns(3);n=c1.slider("n",.5,4.5,1.5,.05,key="03n3");mj=c2.slider("M [MJup]",5.,100.,50.,1.,key="03m3");rj=c3.slider("R [RJup]",.7,2.,1.,.01,key="03r3")
        m=scale_polytrope(mj,rj,n)
        a,b,c=st.columns(3);a.metric("ρc",f"{m['rho_c']:.3e} kg m⁻³");b.metric("Pc",f"{m['P_c']:.3e} Pa");c.metric("I/(MR²)",f"{m['inertia_coeff']:.4f}")
        st.info("M y R son entradas del escalamiento; no cuentan como predicciones independientes.")
    elif exp.startswith("4"):
        ns=np.linspace(.5,4.5,25);conc=[]
        for n in ns:
            mm=scale_polytrope(50,1,n);conc.append(mm["concentration"])
        n0=st.slider("n seleccionado",.5,4.5,1.5,.05,key="03n4")
        m0=scale_polytrope(50,1,n0)
        st.metric("ρc/ρmedia",f"{m0['concentration']:.3f}")
        fig,ax=_plot();ax.semilogy(ns,conc);ax.scatter([n0],[m0["concentration"]]);ax.set(xlabel="n",ylabel="ρc/ρmedia");ax.grid(which="both",alpha=.25);st.pyplot(fig)
    else:
        df=pd.read_csv(DATA)
        masses=sorted(df.mass_msun.unique())
        mass=st.selectbox("Masa BHAC15 [M☉]",masses,index=min(8,len(masses)-1),key="03bhm")
        d=df[df.mass_msun==mass].reset_index(drop=True)
        rowi=st.slider("Índice temporal BHAC15",0,len(d)-1,min(20,len(d)-1),1,key="03bhi")
        row=d.iloc[rowi]
        mj=row.mass_msun*M_SUN/M_JUP;rj=row.radius_rsun*R_SUN/R_JUP
        pol=scale_polytrope(mj,rj,1.5)
        rho_b=10**row.log_rhoc_gcc*1000
        I_b=row.kconv**2+row.krad**2
        st.table({"Cantidad":["M","R","Teff","ρc BHAC","ρc n=1.5","I/(MR²) BHAC","I/(MR²) n=1.5"],
                  "Valor":[f"{row.mass_msun:.3f} M☉",f"{row.radius_rsun:.3f} R☉",f"{row.teff_K:.0f} K",f"{rho_b:.3e}",f"{pol['rho_c']:.3e}",f"{I_b:.4f}",f"{pol['inertia_coeff']:.4f}"]})
        st.caption("Comparación real: BHAC15 no se usa para fijar ρc ni el coeficiente de inercia del polítropo.")

def lab04():
    st.header("Laboratorio 04 — Fuentes de energía")
    exp=st.selectbox("Experimento",["1 · Reservorios","2 · Kelvin–Helmholtz","3 · Nuclear","4 · Enlace","5 · Barrera","6 · Gamow"],key="lab04")
    if exp.startswith("1"):
        c1,c2,c3=st.columns(3);m=c1.slider("M/M☉",.2,5.,1.,.02,key="04m1");r=c2.slider("R/R☉",.2,5.,1.,.02,key="04r1");l=c3.slider("L/L☉",.05,50.,1.,.05,key="04l1")
        vals=[chemical_timescale_years(m,l,10),kelvin_helmholtz_years(m,r,l),nuclear_timescale_years(m,l,.1,.007)]
        fig,ax=_plot();ax.bar(["química","gravedad","nuclear"],vals);ax.set_yscale("log");ax.set_ylabel("años");ax.grid(axis="y",which="both",alpha=.25);st.pyplot(fig)
    elif exp.startswith("2"):
        c1,c2,c3=st.columns(3);m=c1.slider("M/M☉",.2,5.,1.,.02,key="04m2");r=c2.slider("R/R☉",.1,8.,1.,.02,key="04r2");l=c3.slider("L/L☉",.05,50.,1.,.05,key="04l2")
        st.metric("tKH",f"{kelvin_helmholtz_years(m,r,l):.3e} años");st.metric("E radiable",f"{virial_available_energy_j(m,r):.3e} J")
    elif exp.startswith("3"):
        c1,c2,c3=st.columns(3);m=c1.slider("M/M☉",.2,5.,1.,.02,key="04m3");f=c2.slider("fracción f",.01,.5,.1,.005,key="04f3");eta=c3.slider("η",.001,.01,.007,.0001,key="04e3")
        st.metric("E nuclear",f"{nuclear_energy_j(m,f,eta):.3e} J")
    elif exp.startswith("4"):
        st.info("La curva de enlace del material tiene máximo cerca de Fe–Ni. Reacciones que aumentan Eb/A son exotérmicas.")
        st.bar_chart(pd.DataFrame({"Q [MeV]":[26.7,17.6,200]},index=["4p→He","D+T","fisión U235"]))
    elif exp.startswith("5"):
        E=st.slider("E [keV]",.5,50.,10.,.1,key="04E5");rc=classical_turning_radius_fm(E)
        st.metric("rc",f"{rc:.2f} fm");st.metric("PG",f"{gamow_factor(E):.3e}")
        rs=np.logspace(0,3,250);fig,ax=_plot();ax.loglog(rs,[coulomb_potential_mev(x) for x in rs]);ax.axhline(E/1000,ls="--");ax.axvline(rc,ls=":");ax.set(xlabel="r [fm]",ylabel="MeV");ax.grid(which="both",alpha=.25);st.pyplot(fig)
    else:
        T=10**st.slider("log10 T [K]",6.,8.,math.log10(1.55e7),.005,key="04T6");E0=gamow_peak_keV(T)
        st.metric("E0",f"{E0:.3f} keV");Es=np.linspace(.2,30,300);mb=np.array([maxwell_factor(e,T) for e in Es]);pg=np.array([gamow_factor(e) for e in Es]);prod=mb*pg
        fig,ax=_plot();ax.semilogy(Es,mb/mb.max(),label="MB");ax.semilogy(Es,pg/pg.max(),label="Gamow");ax.semilogy(Es,prod/prod.max(),label="producto");ax.axvline(E0,ls="--");ax.legend();ax.set_ylim(1e-8,1.2);ax.grid(which="both",alpha=.25);st.pyplot(fig)

def lab05():
    st.header("Laboratorio 05 — Transporte de energía")
    exp=st.selectbox("Experimento",["1 · Camino libre","2 · Gradiente radiativo","3 · Adiabático","4 · Competencia","5 · Sol","6 · Síntesis"],key="lab05")
    if exp.startswith("1"):
        c1,c2=st.columns(2);k=c1.slider("κ [m²/kg]",.01,5.,1.,.01,key="05k1");rho=c2.slider("ρ [kg/m³]",1.,1000.,200.,1.,key="05r1")
        st.metric("λ",f"{tr.mean_free_path_m(k,rho):.3e} m")
    elif exp.startswith("2"):
        c1,c2,c3=st.columns(3);k=c1.slider("κ",.01,5.,1.,.01,key="05k2");rho=c2.slider("ρ",1.,1000.,200.,1.,key="05r2");T=10**c3.slider("log10 T",5.5,7.5,6.3,.005,key="05T2")
        g=tr.radiative_gradient_k_per_m(k,rho,1,T,.7);st.metric("|dT/dr|rad",f"{abs(g):.3e} K/m")
    elif exp.startswith("3"):
        c1,c2,c3=st.columns(3);gam=c1.slider("γ",1.1,1.8,5/3,.005,key="05g3");mu=c2.slider("μ",.5,1.3,.61,.005,key="05u3");mr=c3.slider("M(r)/M☉",.05,2.,.98,.005,key="05m3")
        ga=tr.adiabatic_gradient_k_per_m(gam,mu,mr,.7);st.metric("|dT/dr|ad",f"{abs(ga):.3e} K/m");st.metric("∇ad",f"{tr.nabla_ad(gam):.4f}")
    elif exp.startswith("4"):
        k=st.slider("κ",.01,5.,1.5,.01,key="05k4");T=10**st.slider("log10 T",5.5,7.5,6.3,.005,key="05T4")
        ratio=tr.transport_ratio(k,200,1,T,.7,5/3,.61,.98);st.metric("|rad|/|ad|",f"{ratio:.3f}");st.success(tr.transport_regime(ratio) if ratio<=1 else tr.transport_regime(ratio))
    elif exp.startswith("5"):
        st.info("Según el material complementario: interior solar aproximadamente radiativo hasta 0.7 R☉ y región externa convectiva.")
        xs=np.linspace(0,1,200);fig,ax=_plot();ax.axvspan(0,.7,alpha=.25,label="radiativo");ax.axvspan(.7,1,alpha=.25,label="convectivo");ax.set(xlabel="r/R☉",yticks=[]);ax.legend();st.pyplot(fig)
    else:
        k=st.slider("κ",.01,5.,1.5,.01,key="05k6");rho=st.slider("ρ",1.,1000.,200.,1.,key="05r6");T=10**st.slider("log10 T",5.5,7.5,6.3,.005,key="05T6")
        lam=tr.mean_free_path_m(k,rho);gr=abs(tr.radiative_gradient_k_per_m(k,rho,1,T,.7));ga=abs(tr.adiabatic_gradient_k_per_m(5/3,.61,.98,.7));st.table({"Cantidad":["λ","|grad_rad|","|grad_ad|","razón"],"Valor":[f"{lam:.3e}",f"{gr:.3e}",f"{ga:.3e}",f"{gr/ga:.3f}"]})

def lab06():
    st.header("Laboratorio 06 — Atmósferas estelares")
    exp=st.selectbox("Experimento",["1 · Planck","2 · u=aT⁴","3 · τλ","4 · Atmósfera terrestre","5 · Fotosfera","6 · Líneas"],key="lab06")
    if exp.startswith("1"):
        T=st.slider("T [K]",2500,20000,5770,50,key="06T1");lam=st.slider("λ [nm]",100,2500,500,1,key="06l1")
        B=atm.planck_lambda_w_m3_sr(lam,T);st.metric("Bλ",f"{B:.3e} W m⁻³ sr⁻¹");ls=np.linspace(100,2500,300);fig,ax=_plot();ax.plot(ls,[atm.planck_lambda_w_m3_sr(x,T) for x in ls]);ax.scatter([lam],[B]);ax.set(xlabel="nm",ylabel="Bλ");st.pyplot(fig)
    elif exp.startswith("2"):
        T=st.slider("T [K]",2500,20000,5770,50,key="06T2");st.metric("u",f"{atm.radiation_energy_density_j_m3(T):.3e} J/m³")
    elif exp.startswith("3"):
        c1,c2,c3=st.columns(3);k=c1.slider("κ",.001,.2,.03,.001,key="06k3");rho=c2.slider("ρ [kg/m³]",1e-5,1e-3,2.1e-4,1e-5,key="06r3");s=c3.slider("s [km]",1,1000,160,1,key="06s3")
        tau=atm.optical_depth_uniform(k,rho,s*1000);st.metric("τ",f"{tau:.4f}");st.metric("I/I0",f"{atm.transmitted_fraction(tau):.4f}")
    elif exp.startswith("4"):
        tau0=st.slider("τ0",0.,1.,.15,.005,key="06t4");z=st.slider("z [deg]",0.,70.,30.,.5,key="06z4");st.metric("sec z",f"{atm.airmass_sec(z):.3f}");st.metric("I/I0",f"{atm.atmospheric_transmission(tau0,z):.4f}")
    elif exp.startswith("5"):
        tau=st.slider("τ",0.,10.,2/3,.01,key="06t5");st.metric("n≈τ²",f"{atm.photon_escape_steps(tau):.3f}");st.caption("El material cita τ≈2/3 como profundidad fotosférica característica.")
    else:
        T=st.slider("T [K]",2500,20000,5770,50,key="06T6");vt=st.slider("v_turb [km/s]",0.,20.,0.,.1,key="06v6");dep=st.slider("profundidad",.05,.95,.5,.01,key="06d6")
        fwhm=atm.doppler_fwhm_nm(656.3,T,atm.M_H,vt);ew=atm.gaussian_equivalent_width_nm(dep,fwhm);st.metric("FWHM",f"{fwhm:.5f} nm");st.metric("W gaussiano didáctico",f"{ew:.5f} nm")
        span=max(.25,6*fwhm);ls=np.linspace(656.3-span/2,656.3+span/2,300);fig,ax=_plot();ax.plot(ls,[atm.gaussian_normalized_flux(x,656.3,dep,fwhm) for x in ls]);ax.set(xlabel="λ [nm]",ylabel="F/Fc");st.pyplot(fig)

def lab07():
    st.header("Laboratorio 07 — Secuencia principal")
    exp=st.selectbox("Experimento",["1 · Mapa de masa","2 · Fusión","3 · Estructura","4 · Límites","5 · Tiempo nuclear","6 · Síntesis"],key="lab07")
    if exp.startswith("1"):
        m=st.slider("M/M☉",.02,120.,1.,.02,key="07m1");r=mass_regime(m);st.json(r)
    elif exp.startswith("2"):
        Tc=st.slider("Tc [MK]",5.,35.,15.,.1,key="07T2");st.info(fusion_from_temperature_mk(Tc)["label"])
        rr=st.slider("T/T0",.8,1.3,1.1,.005,key="07r2");st.metric("εCNO/ε0 (T^19)",f"{cno_relative_sensitivity(rr,19):.3f}")
    elif exp.startswith("3"):
        m=st.slider("M/M☉",.08,20.,1.,.01,key="07m3");r=mass_regime(m);st.table({"Zona":["núcleo","región externa","fusión"],"Estado":[r["core"],r["envelope"],r["fusion"]]})
    elif exp.startswith("4"):
        m=st.slider("M/M☉",.02,120.,.08,.02,key="07m4");st.info(mass_regime(m)["note"])
    elif exp.startswith("5"):
        e=st.slider("En/En0",.1,5.,1.,.01,key="07e5");l=st.slider("L/L0",.1,10.,1.,.01,key="07l5");st.metric("tn/tn0",f"{relative_nuclear_lifetime(e,l):.4f}")
    else:
        m=st.slider("M/M☉",.02,120.,1.,.02,key="07m6");r=mass_regime(m);st.table({"Aspecto":["régimen","SP","fusión","núcleo","envoltura"],"Resultado":[r["label"],str(r["main_sequence"]),r["fusion"],r["core"],r["envelope"]]})

def lab08():
    st.header("Laboratorio 08 — Evolución post-ZAMS")
    exp=st.selectbox("Experimento",["1 · Salida de SP","2 · Espejo","3 · Límite SC","4 · Referencia solar","5 · RGB→AGB","6 · Síntesis"],key="lab08")
    if exp.startswith("1"):
        i=st.slider("etapa",0,len(EARLY_STAGES)-1,0,1,key="08i1");st.json(early_stage(i))
    elif exp.startswith("2"):
        d=st.slider("ΔR núcleo",-.5,.5,-.2,.01,key="08d2");rr=st.slider("Rcore/Rref",.4,1.6,.8,.01,key="08r2");st.json(mirror_response(d));st.metric("Egrav/Eref",f"{normalized_gravitational_energy(rr):.3f}")
    elif exp.startswith("3"):
        me=st.slider("μ envoltura",.5,.8,.62,.005,key="08e3");mc=st.slider("μ núcleo",1.,1.6,1.34,.005,key="08c3");q=st.slider("qcore",.02,.25,.08,.002,key="08q3");st.json(sc_state(q,me,mc));st.warning("Auditoría: 0.37(0.62/1.34)^2≈0.079, aunque el documento imprime ~0.12.")
    elif exp.startswith("4"):
        st.table({"Cantidad":list(SOLAR_EVOLVED_REFERENCE.keys()),"Valor":[str(v) for v in SOLAR_EVOLVED_REFERENCE.values()]})
    elif exp.startswith("5"):
        i=st.slider("etapa avanzada",0,len(ADVANCED_STAGES)-1,0,1,key="08i5");st.json(advanced_stage(i))
    else:
        st.markdown("**Cadena física:** agotamiento central → contracción → respuesta en espejo → quema en capa → RGB → He → HB → AGB.")
