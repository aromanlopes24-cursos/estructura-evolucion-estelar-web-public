# Laboratorio 06 — Atmósferas estelares

## Base del material suministrado

El curso introduce la intensidad específica Iλ y, para radiación isotrópica
de cuerpo negro:

    <Iλ> = Bλ(T)

con la función de Planck.

La densidad de energía específica satisface:

    uλ = (4π/c) <Iλ>

y para cuerpo negro, integrada en longitud de onda:

    u = a T⁴

El material define absorción/opacidad mediante:

    dIλ = -κλ ρ Iλ ds

y profundidad óptica:

    τλ = ∫ κλ ρ ds

de forma que:

    Iλ = Iλ,0 exp(-τλ)

También distingue:
    τλ >> 1  → ópticamente grueso
    τλ << 1  → ópticamente delgado

## Ejemplo fotosférico de las notas

Para λ=500 nm, ρ=2.1×10^-4 kg m^-3 y κλ=0.03 m² kg^-1:

    camino libre medio ≈160 km.

Las notas señalan que los fotones observables de una fotosfera se caracterizan
por una profundidad óptica aproximada:

    τλ ≈ 2/3.

## Atmósfera terrestre

En la aproximación plana de las notas:

    τλ = τλ,0 sec z

    Iλ = Iλ,0 exp(-τλ,0 sec z)

    ln Iλ = ln Iλ,0 - τλ,0 sec z

lo que permite recuperar la intensidad por encima de la atmósfera.

## Líneas espectrales

El ancho equivalente se define como:

    W = ∫ (Fc-Fl)/Fc dλ

y se introduce FWHM.

Para ensanchamiento Doppler térmico:

    Δλ = (2λ/c) sqrt(2kT/m)

y, incluyendo turbulencia, las notas dan una expresión para FWHM.

Para Hα a T=5770 K, el material cita:

    Δλ ≈ 0.0427 nm.

## Extensión pedagógica explícita

Para visualizar simultáneamente FWHM y W, el laboratorio genera un perfil
gaussiano sintético de absorción. Esa forma de línea es una herramienta
didáctica añadida y se identifica como tal; no se presenta como una
reconstrucción de una línea observada ni de una atmósfera real.

## Experimentos

1. Cuerpo negro: Bλ(T).
2. Densidad de energía: u=aT⁴.
3. Opacidad, camino libre y τλ.
4. Extinción por la atmósfera terrestre.
5. Profundidad óptica y fotosfera.
6. Línea Hα sintética: ensanchamiento, FWHM y ancho equivalente.

## Puente al Módulo 07

El espectro y la atmósfera permiten conectar los parámetros observados con
estrellas de distintas masas en la secuencia principal.
