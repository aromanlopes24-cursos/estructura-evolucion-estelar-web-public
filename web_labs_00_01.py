from __future__ import annotations
import math
import matplotlib.pyplot as plt
import streamlit as st
from observables_core import *
from photometry_core import *

PAGE_HEADER=None
def set_page_header(fn):
    global PAGE_HEADER
    PAGE_HEADER=fn

def page_header(t,s):
    return PAGE_HEADER(t,s)

# M00 lab
# ----------------------------------------------------------------
def lab00():
    page_header("Laboratorio 00","PREDICE → MODIFICA → OBSERVA → EXPLICA")
    exp=st.selectbox("Experimento",[
        "1 · Luminosidad intrínseca","2 · Flujo y distancia",
        "3 · Mismo flujo, fuentes diferentes","4 · Intensidad y fuente resuelta",
        "5 · Síntesis"],key="lab00_exp")
    st.divider()

    if exp.startswith("1"):
        st.subheader("1 · Luminosidad intrínseca");st.latex(r"L=4\pi R^2\sigma T_{\rm eff}^4")
        c1,c2=st.columns(2)
        r=c1.slider("R / R☉",.2,10.,1.,.05,key="m00e1r")
        T=c2.slider("Teff [K]",2500,30000,int(T_SUN),50,key="m00e1t")
        Lr=luminosity_lsun(r,T)
        st.metric("L / L☉",f"{Lr:.4g}")
        Ts=[2500+i*(27500/180) for i in range(181)]
        fig,ax=plt.subplots();ax.plot(Ts,[luminosity_lsun(r,t) for t in Ts]);ax.scatter([T],[Lr])
        ax.set_yscale("log");ax.set_xlabel("Teff [K]");ax.set_ylabel("L/L☉");ax.grid(alpha=.25)
        st.pyplot(fig,clear_figure=True)

    elif exp.startswith("2"):
        st.subheader("2 · Flujo y distancia");st.latex(r"F=L/(4\pi d^2)")
        c1,c2,c3=st.columns(3)
        r=c1.slider("R/R☉",.2,8.,1.,.05,key="m00e2r")
        T=c2.slider("Teff [K]",2500,25000,int(T_SUN),50,key="m00e2t")
        logd=c3.slider("log10 d [pc]",-1.,4.,1.,.02,key="m00e2d")
        d=10**logd;L=luminosity_w(r,T);F=flux_wm2(L,d)
        st.metric("F",f"{F:.4e} W m⁻²")
        ds=[10**(-1+i*(5/180)) for i in range(181)]
        fig,ax=plt.subplots();ax.loglog(ds,[flux_wm2(L,x) for x in ds]);ax.scatter([d],[F])
        ax.set_xlabel("d [pc]");ax.set_ylabel("F [W m⁻²]");ax.grid(which="both",alpha=.25)
        st.pyplot(fig,clear_figure=True)

    elif exp.startswith("3"):
        st.subheader("3 · Mismo flujo, estrellas diferentes")
        c1,c2,c3=st.columns(3)
        LA=c1.slider("LA/L☉",.1,20.,1.,.1,key="m00e3la")
        dA=c2.slider("dA [pc]",1.,500.,10.,1.,key="m00e3da")
        LB=c3.slider("LB/L☉",.1,100.,4.,.1,key="m00e3lb")
        dB=distance_for_same_flux(LA*L_SUN,dA,LB*L_SUN)
        st.success(f"dB={dB:.3f} pc para conservar el mismo flujo.")

    elif exp.startswith("4"):
        st.subheader("4 · Intensidad y fuente resuelta")
        c1,c2,c3=st.columns(3)
        r=c1.slider("R/R☉",.2,8.,1.,.05,key="m00e4r")
        T=c2.slider("Teff [K]",2500,25000,int(T_SUN),50,key="m00e4t")
        logd=c3.slider("log10 d [pc]",-1.,4.,1.,.02,key="m00e4d")
        d=10**logd;I=isotropic_intensity_wm2sr(T);om=solid_angle_uniform_disk_sr(r,d)
        F=observed_flux_from_intensity(I,r,d)
        a,b,c=st.columns(3);a.metric("I",f"{I:.4e}");b.metric("Ω",f"{om:.4e} sr");c.metric("Fobs",f"{F:.4e}")
        ds=[10**(-1+i*(5/180)) for i in range(181)]
        om0=solid_angle_uniform_disk_sr(r,ds[0]);f0=observed_flux_from_intensity(I,r,ds[0])
        fig,ax=plt.subplots()
        ax.loglog(ds,[1]*len(ds),label="I/I0")
        ax.loglog(ds,[solid_angle_uniform_disk_sr(r,x)/om0 for x in ds],
                  "--",label="Ω/Ω0")
        ax.loglog(ds,[observed_flux_from_intensity(I,r,x)/f0 for x in ds],
                  ":",linewidth=2.5,label="F/F0")
        ax.text(.03,.05,"Ω/Ω0 = F/F0 ∝ d⁻²",transform=ax.transAxes)
        ax.set_xlabel("d [pc]");ax.set_ylabel("cantidad normalizada");ax.legend();ax.grid(which="both",alpha=.25)
        st.pyplot(fig,clear_figure=True)

    else:
        st.subheader("5 · Síntesis")
        c1,c2,c3=st.columns(3)
        r=c1.slider("R/R☉",.2,8.,1.,.05,key="m00e5r")
        T=c2.slider("Teff [K]",2500,25000,int(T_SUN),50,key="m00e5t")
        d=c3.slider("d [pc]",1.,500.,10.,1.,key="m00e5d")
        L=luminosity_w(r,T);F=flux_wm2(L,d);I=isotropic_intensity_wm2sr(T);om=solid_angle_uniform_disk_sr(r,d)
        st.table({"Cantidad":["R","Teff","L","F","I","Ω"],
                  "Valor":[f"{r:.3f} R☉",f"{T:.0f} K",f"{L/L_SUN:.4g} L☉",
                           f"{F:.4e}",f"{I:.4e}",f"{om:.4e} sr"]})

# ----------------------------------------------------------------
# M01 lab
# ----------------------------------------------------------------
def lab01():
    page_header("Laboratorio 01","flujo → magnitud → distancia → extinción → color")
    exp=st.selectbox("Experimento",[
        "1 · Magnitud y flujo","2 · Módulo de distancia","3 · Espesor óptico",
        "4 · Extinción en magnitudes","5 · Color y enrojecimiento","6 · Síntesis"
    ],key="lab01_exp")
    st.divider()

    if exp.startswith("1"):
        st.subheader("1 · Magnitud y flujo")
        dm=st.slider("Δm=m1-m2 [mag]",-7.5,7.5,1.0,.05,key="m01e1dm")
        ratio=flux_ratio_from_mag_difference(dm)
        st.metric("F1/F2",f"{ratio:.5g}")
        ds=[-7.5+i*(15/160) for i in range(161)]
        fig,ax=plt.subplots();ax.semilogy(ds,[flux_ratio_from_mag_difference(x) for x in ds]);ax.scatter([dm],[ratio])
        ax.set_xlabel("Δm [mag]");ax.set_ylabel("F1/F2");ax.grid(which="both",alpha=.25)
        st.pyplot(fig,clear_figure=True)

    elif exp.startswith("2"):
        st.subheader("2 · Módulo de distancia")
        c1,c2=st.columns(2)
        logd=c1.slider("log10 d [pc]",-1.,4.,1.,.02,key="m01e2d")
        M=c2.slider("M [mag]",-10.,15.,0.,.05,key="m01e2m")
        d=10**logd;mu=distance_modulus(d);m=M+mu
        a,b,c=st.columns(3);a.metric("d",f"{d:.3g} pc");b.metric("m-M",f"{mu:+.3f}");c.metric("m",f"{m:+.3f}")
        ds=[10**(-1+i*(5/160)) for i in range(161)]
        fig,ax=plt.subplots();ax.semilogx(ds,[distance_modulus(x) for x in ds]);ax.scatter([d],[mu])
        ax.axvline(10,linestyle="--",alpha=.5);ax.set_xlabel("d [pc]");ax.set_ylabel("m-M [mag]");ax.grid(which="both",alpha=.25)
        st.pyplot(fig,clear_figure=True)

    elif exp.startswith("3"):
        st.subheader("3 · Espesor óptico")
        tau=st.slider("τ",0.,6.,.5,.01,key="m01e3tau")
        tr=transmission_from_tau(tau)
        st.metric("F/F0",f"{tr:.5f}")
        ts=[i*(6/160) for i in range(161)]
        fig,ax=plt.subplots();ax.plot(ts,[transmission_from_tau(x) for x in ts]);ax.scatter([tau],[tr])
        ax.set_xlabel("τ");ax.set_ylabel("F/F0");ax.grid(alpha=.25)
        st.pyplot(fig,clear_figure=True)

    elif exp.startswith("4"):
        st.subheader("4 · Extinción en magnitudes")
        c1,c2,c3=st.columns(3)
        tau=c1.slider("τ",0.,4.,.5,.01,key="m01e4tau")
        logd=c2.slider("log10 d [pc]",-1.,4.,1.,.02,key="m01e4d")
        M=c3.slider("M [mag]",-10.,15.,0.,.05,key="m01e4m")
        d=10**logd;A=extinction_mag_from_tau(tau);mu=distance_modulus(d)
        m=M+mu+A
        a,b,c=st.columns(3);a.metric("A",f"{A:.3f} mag");b.metric("m sin ext.",f"{M+mu:.3f}");c.metric("m observada",f"{m:.3f}")
        ts=[i*(4/160) for i in range(161)]
        fig,ax=plt.subplots();ax.plot(ts,[M+mu+extinction_mag_from_tau(x) for x in ts]);ax.scatter([tau],[m])
        ax.set_xlabel("τ");ax.set_ylabel("m observada");ax.grid(alpha=.25)
        st.pyplot(fig,clear_figure=True)

    elif exp.startswith("5"):
        st.subheader("5 · Color y enrojecimiento")
        c1,c2=st.columns(2)
        bv0=c1.slider("(B-V)0 [mag]",-.4,2.,0.,.01,key="m01e5bv0")
        ebv=c2.slider("E(B-V) [mag]",0.,2.,.2,.01,key="m01e5ebv")
        obs=observed_bv(bv0,ebv);Av=av_from_ebv(ebv,3.)
        a,b=st.columns(2);a.metric("B-V observado",f"{obs:+.3f}");b.metric("AV",f"{Av:.3f} mag")
        es=[i*(2/160) for i in range(161)]
        fig,ax=plt.subplots();ax.plot(es,[observed_bv(bv0,x) for x in es]);ax.scatter([ebv],[obs])
        ax.set_xlabel("E(B-V)");ax.set_ylabel("B-V observado");ax.grid(alpha=.25)
        st.pyplot(fig,clear_figure=True)

    else:
        st.subheader("6 · Síntesis fotométrica")
        c1,c2,c3,c4=st.columns(4)
        Mv=c1.slider("MV [mag]",-10.,15.,0.,.05,key="m01e6mv")
        logd=c2.slider("log10 d [pc]",-1.,4.,1.,.02,key="m01e6d")
        bv0=c3.slider("(B-V)0",-0.4,2.,0.,.01,key="m01e6bv0")
        ebv=c4.slider("E(B-V)",0.,2.,.2,.01,key="m01e6ebv")
        s=synthesis(Mv,bv0,10**logd,ebv,3.)
        st.table({"Cantidad":["μ","AV","AB","MV","MB","V","B","(B-V)0","B-V","E(B-V)"],
                  "Valor":[f"{s[k]:+.3f} mag" for k in ["mu","Av","Ab","Mv","Mb","V","B","bv0","bv_obs","ebv"]]})
        st.success("Chequeo: B-V = (B-V)0 + E(B-V).")

def laboratory_page():
    if MID=="00": lab00()
    else: lab01()

# ----------------------------------------------------------------
