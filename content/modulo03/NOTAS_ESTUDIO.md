# Módulo 03 — Polítropos y Lane–Emden
## Resumen para estudiar

### 0. Dónde estamos en el curso

Este módulo parte de la estructura mecánica introducida previamente.

CONTENIDO DE CLASE:
- equilibrio hidrostático;
- continuidad de la masa;
- ecuación de estado;
- presión, densidad y masa como funciones del radio.

EXTENSIÓN DIDÁCTICA DEL LABORATORIO:
- relación politrópica;
- ecuación de Lane–Emden;
- índice politrópico continuo;
- comparación con objetos reales y BHAC15.

La distinción es importante: el politropo es una forma sencilla de cerrar el
sistema mecánico y explorar sus consecuencias. No significa que toda estrella
real esté descrita por un único índice n.

---

## 1. Equilibrio hidrostático

La condición mecánica fundamental es

    dP/dr = - G M(r) ρ(r) / r²

Símbolos:

    P(r)   presión local
    r      distancia al centro
    M(r)   masa encerrada dentro de r
    ρ(r)   densidad local
    G      constante gravitacional

Interpretación:
el gradiente de presión neutraliza la atracción gravitacional. El signo
negativo indica que la presión disminuye al aumentar el radio.

IDEA PARA MEMORIZAR:
    gravedad hacia adentro ↔ gradiente de presión hacia afuera

---

## 2. Continuidad de la masa

La distribución de masa satisface

    dM/dr = 4 π r² ρ(r)

Una capa esférica delgada tiene volumen

    dV = 4 π r² dr

y por tanto

    dM = ρ dV.

IDEA PARA MEMORIZAR:
    geometría de la capa × densidad = masa añadida

Condición central:

    M(0) = 0.

---

## 3. ¿Qué falta para cerrar el problema?

Las ecuaciones mecánicas contienen varias funciones desconocidas. Necesitamos
una relación que conecte la presión con el estado de la materia.

En una estrella real, la ecuación de estado puede depender de

    P = P(ρ, T, composición, ionización, degeneración, ...)

Para construir un laboratorio sencillo, introducimos una aproximación
politrópica.

---

## 4. Relación politrópica

EXTENSIÓN DEL LABORATORIO:

    P = K ρ^(1 + 1/n)

donde

    n       índice politrópico
    K       constante politrópica
    γpol    1 + 1/n

El índice n controla la forma de la estructura.

Casos útiles:

    n = 1.5  → γpol = 5/3
    n = 3.0  → γpol = 4/3

No debe memorizarse sólo el número. Debe recordarse qué cambia cuando n
cambia: la concentración central y la distribución de masa.

---

## 5. Variables adimensionales de Lane–Emden

Escribimos

    ρ(r) = ρc θ(ξ)^n

y

    r = a ξ

donde

    ρc      densidad central
    θ(ξ)    función adimensional
    ξ       radio adimensional
    a       escala de longitud

La escala a satisface

    a² = [(n+1) K / (4πG)] ρc^(1/n - 1)

Con estas definiciones, las ecuaciones mecánicas se reducen a la ecuación
de Lane–Emden:

    (1/ξ²) d/dξ [ ξ² dθ/dξ ] = - θ^n

Condiciones centrales:

    θ(0) = 1
    θ'(0) = 0

---

## 6. La superficie y la primera raíz

La superficie del politropo está definida por la primera raíz:

    θ(ξ1) = 0.

Entonces

    R = a ξ1

y la masa total es

    M = 4π a³ ρc [-ξ1² θ'(ξ1)].

ξ1 NO es el radio físico. Es el radio adimensional de la superficie.

---

## 7. Concentración central

Una cantidad muy útil es

    Cρ = ρc / ρmedia

con

    ρmedia = 3M / (4πR³).

A medida que n aumenta, el politropo se vuelve más centralmente concentrado.

Otros diagnósticos:

    r50/R
        radio que contiene 50% de la masa

    I/(MR²)
        coeficiente adimensional de momento de inercia

Lectura conjunta:

    ρc/ρmedia grande
    r50/R pequeño
    I/(MR²) pequeño

→ masa más concentrada hacia el centro.

---

## 8. Qué ocurre cuando n se aproxima a 5

Para n < 5 existe una primera raíz finita.

Cuando n → 5:

    ξ1 crece fuertemente
    ρc/ρmedia crece fuertemente

Para n = 5, la solución no alcanza θ=0 a radio finito.

Por eso el laboratorio permite aproximarse a 5, pero no utiliza n=5 como una
estrella de radio finito.

---

## 9. n = 1.5 y objetos de muy baja masa

EXTENSIÓN / APLICACIÓN:

Para n=1.5:

    P ∝ ρ^(5/3)
    γpol = 5/3
    ∇pol = 1/(n+1) = 0.4

La dependencia ρ^(5/3) aparece en contextos físicamente relevantes para
objetos de muy baja masa, como un gas monoatómico adiabático y la
degeneración electrónica no relativista.

Esto motiva usar n≈1.5 como primera aproximación pedagógica para ciertas
enanas marrones.

NO significa:
“toda enana marrón real es exactamente un politropo n=1.5”.

---

## 10. Escalar el politropo a un objeto real

En la aplicación real usamos M y R del catálogo para fijar la escala física.

Esto permite obtener:

    ρc
    Pc
    K
    ρ(r)
    P(r)
    m(r)

Pero atención:

    M y R son ENTRADAS.

Por tanto, comprobar después que el modelo tiene la misma M y el mismo R no
es una validación independiente.

---

## 11. Comparación con BHAC15

BHAC15 aporta información estructural más detallada.

Comparamos, por ejemplo:

    ρc(polítropo)  vs  ρc(BHAC15)

    [I/(MR²)]pol   vs  [I/(MR²)]BHAC15

y la presencia o ausencia de una región radiativa.

Estas comparaciones contienen más información que volver a comparar M y R.

---

## 12. Pregunta de salida del módulo

Al terminar, el estudiante debe poder responder:

“Si dos modelos tienen la misma masa y el mismo radio, ¿por qué pueden tener
estructuras internas diferentes?”

La respuesta debe mencionar la relación P–ρ, la distribución radial de masa y
algún diagnóstico como ρc/ρmedia, r50/R o I/(MR²).

---

## Puente al módulo siguiente

Este módulo construye una estructura mecánica.

La siguiente pregunta es:

    ¿de dónde proviene la energía que mantiene L(r)?

Eso abre el Módulo 04 — Fuentes de energía.
