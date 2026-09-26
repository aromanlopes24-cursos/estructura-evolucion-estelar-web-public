# Laboratorio 05 — Transporte de energía

## Base directa del material del curso

El material distingue:
- difusión radiativa;
- convección;
- conducción.

Sin embargo, las notas suministradas desarrollan cuantitativamente radiación y
convección, no conducción. Por eso este laboratorio no inventa una ley
conductiva adicional.

### Camino libre medio

    λ = 1/(κρ)

### Gradiente radiativo

Las transparencias presentan una derivación simplificada proporcional a:

    dT/dr ∝ -κρL/(T³r²)

El material complementario señala que esa derivación simplificada tiene un
error de aproximadamente 30% y entrega:

    (dT/dr)_rad = - 3 κρL / (64πσ T³ r²)

Ésta es la expresión usada para los cálculos del laboratorio.

### Gradiente adiabático

Para una burbuja de gas ideal:

    PV^γ = constante

    (dT/dr)_ad = -(1 - 1/γ) (m_av/k) g

con:

    m_av = μ m_H

y:

    ∇ad = (γ-1)/γ

### Criterio pedagógico

Como ambos gradientes físicos son negativos hacia afuera, el laboratorio
compara sus magnitudes:

    |grad_rad| > |grad_ad|  → tendencia convectiva

    |grad_rad| <= |grad_ad| → transporte radiativo estable posible

Esto evita ambigüedad de signo en la representación gráfica.

## Experimentos

1. Camino libre medio.
2. Gradiente radiativo y dependencias κ, ρ, L, T, r.
3. Burbuja adiabática.
4. Competencia radiación/convección.
5. Esquema de la estructura solar descrita en las notas:
   interior radiativo hasta ~0.7 R☉, región exterior convectiva.
6. Síntesis de una capa local.

## Puente al Módulo 06

El siguiente paso es seguir la radiación hasta las capas donde se forma el
espectro emergente: atmósferas estelares.
