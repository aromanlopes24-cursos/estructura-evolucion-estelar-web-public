# Laboratorio 02 — Estructura mecánica

## Base directa en el material del curso

Las dos ecuaciones mecánicas usadas son:

    dP/dr = -G M(r) ρ(r) / r²

    dM/dr = 4π r² ρ(r)

El material de clases interpreta la primera como la condición en que el
gradiente de presión neutraliza la atracción gravitacional y usa una
estimación solar de orden de magnitud:

    Pc ~ G M ρ / R

## Extensión didáctica explícita

Para poder integrar las ecuaciones de forma analítica y transparente se adopta
un benchmark de densidad constante:

    ρ(r) = constante

Entonces:

    M(r)/M = (r/R)³

    P(r) = Pc [1 - (r/R)²]

    Pc = 3 G M² / (8π R⁴)

Esta esfera uniforme es un benchmark pedagógico, no un modelo solar realista.

## Experimentos

1. Capa esférica: interpretar dM/dr.
2. Masa encerrada: integrar M(r).
3. Equilibrio hidrostático: relacionar g(r), dP/dr y P(r).
4. Presión central: comparar la estimación de clase con la solución exacta
   del benchmark uniforme.
5. Cierre: mostrar por qué las ecuaciones mecánicas no determinan solas
   P(r), M(r) y ρ(r).
6. Síntesis radial: visualizar M(r)/M, P(r)/Pc y g(r)/g(R).

## Puente al Módulo 03

El siguiente cierre abandona ρ=constante y adopta una relación P–ρ:

    P = K ρ^(1+1/n)

lo que conduce a los polítropos y a la ecuación de Lane–Emden.
