# Laboratorio 01 — Fotometría y extinción

## Objetivo

Transformar las relaciones fotométricas de las clases en experimentos
interactivos y conectar flujo, magnitud, distancia, espesor óptico, extinción
y color.

## Experimento 1 — Magnitud y flujo

    Δm = -2.5 log10(F1/F2)

Se explora la escala logarítmica de Pogson.

## Experimento 2 — Módulo de distancia

    m - M = 5 log10(d/10 pc)

Se verifica que:
- a 10 pc, m=M;
- una década en distancia añade 5 mag.

## Experimento 3 — Espesor óptico

    F/F0 = e^(-τ)

Se visualiza la atenuación exponencial.

## Experimento 4 — Extinción en magnitudes

Del material del curso:

    m - M = 5 log10(d/10 pc) + A

y, para una atenuación e^-τ:

    A = 2.5 log10(e) τ ≈ 1.086 τ

## Experimento 5 — Color y enrojecimiento

    B-V = (B-V)0 + E(B-V)

Se usa la relación adoptada en las clases:

    A_V / E(B-V) ≈ 3.0

por tanto:

    A_V ≈ 3.0 E(B-V)

## Experimento 6 — Síntesis

Entradas:
- M_V
- d
- (B-V)0
- E(B-V)

Derivadas:
- μ
- A_V
- A_B
- M_B
- V
- B
- B-V

Chequeo interno:

    B-V = (B-V)0 + E(B-V)

## Puente

El siguiente módulo pregunta cómo el interior estelar puede producir y
sostener las propiedades globales observadas:

Módulo 02 — Estructura mecánica.
