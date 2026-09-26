# Laboratorio 08 — Evolución post-ZAMS

## Regla metodológica

Este módulo NO fabrica una trayectoria evolutiva numérica L(t), Teff(t) o R(t)
si el material suministrado no proporciona esos datos.

Se cuantifican sólo relaciones explícitas de las notas; el resto se presenta
como secuencia de estados físicos.

## Secuencia temprana

Del material post-ZAMS:

1. ZAMS: fusión estable de H.
2. H → He en el núcleo: μ aumenta; núcleo se reajusta.
3. Agotamiento de H central: núcleo de He inerte, contracción, SGB.
4. H en capa alrededor del núcleo.
5. RGB: R ↑, Teff ↓, L ↑; envoltura expandida.

## Principio del espejo

El material enuncia:

    núcleo se contrae -> envoltura se expande
    núcleo se expande -> envoltura se contrae

y relaciona el proceso con el virial:

    Egrav ∝ -GM²/R

Para masa fija, el laboratorio visualiza sólo la proporcionalidad:

    Egrav ∝ -1/Rcore.

No se asigna una amplitud artificial a la respuesta de la envoltura.

## Límite de Schönberg–Chandrasekhar

Se implementa la fórmula escrita en el material:

    qSC = Mc/M* = 0.37 (μe/μc)²

### Auditoría interna importante

El mismo documento presenta el ejemplo:

    μe = 0.62
    μc = 1.34
    qSC ≈ 0.12

Sin embargo, evaluando literalmente la fórmula escrita:

    0.37 (0.62/1.34)² ≈ 0.079

Por tanto, existe una discrepancia aritmética interna en el material.
El laboratorio:
- conserva la fórmula tal como está escrita;
- calcula su valor matemático;
- muestra explicitamente la discrepancia;
- no força o resultado para 0.12.

## Estrella solar evolucionada — referencia del material

Para una estrella de 1 M☉ a 9.8 Gyr el documento suministra:

    R = 1.27 R☉
    Pc = 1.3×10^17 Pa
    Tc = 1.91×10^7 K
    L = 2.13 L☉
    XH(núcleo) ≈ 0
    XH(envoltura) ≈ 0.7

También identifica:
- mayor contribución energética en 0.1 < m/M☉ < 0.3;
- ausencia de fusión activa en m/M > 0.8;
- interior radiativo para m/M < 0.7;
- región externa convectiva para m/M > 0.7.

Estos números se muestran como un punto de referencia y NO se interpolan para
fabricar una evolución temporal.

## Evolución avanzada

La secuencia del material es:

- fin SP / subgigante;
- primer dredge-up;
- RGB;
- flash de He, con Tc ≈ 1.3×10^8 K;
- HB con quema estable de He;
- agotamiento de He y núcleo C–O;
- AGB con capas de He y H, pulsos térmicos y pérdida de masa.

## Experimentos

1. ZAMS → SGB → RGB.
2. Principio del espejo.
3. Límite SC.
4. Referencia solar evolucionada.
5. RGB → flash de He → HB → AGB.
6. Síntesis final do curso.
