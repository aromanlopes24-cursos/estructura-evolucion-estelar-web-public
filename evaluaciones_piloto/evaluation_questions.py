"""Banco de práctica. No contiene claves de corrección ni soluciones."""

EXAM_ID = 'EEE-P3-PRAC-131'
VERSION = '1.3.1-piloto.1'
TITLE = 'Simulación de la Prueba N.º 3'
DEMO_MINUTES = 15
QUESTIONS = [
    {
        'id': 'P01', 'type': 'choice', 'title': 'Agotamiento del hidrógeno central',
        'prompt': '¿Qué ocurre inicialmente con el núcleo de helio de una estrella de baja masa al agotarse el hidrógeno central?',
        'options': [
            {'id': 'o1', 'text': 'Permanece en el mismo estado termodinámico.'},
            {'id': 'o2', 'text': 'Se contrae y se calienta.'},
            {'id': 'o3', 'text': 'Se expande y se enfría inmediatamente.'},
            {'id': 'o4', 'text': 'Desaparece y deja una cavidad central.'},
        ],
    },
    {
        'id': 'P02', 'type': 'choice', 'title': 'Lectura de un diagrama H–R', 'figure': 'hr',
        'prompt': 'En el desplazamiento esquemático desde A hasta B, ¿cómo cambian la luminosidad y la temperatura efectiva?',
        'options': [
            {'id': 'o1', 'text': 'Aumentan ambas.'},
            {'id': 'o2', 'text': 'Disminuyen ambas.'},
            {'id': 'o3', 'text': 'Aumenta la luminosidad y disminuye la temperatura efectiva.'},
            {'id': 'o4', 'text': 'Disminuye la luminosidad y aumenta la temperatura efectiva.'},
        ],
    },
    {
        'id': 'P03', 'type': 'numeric', 'title': 'Relación entre radio y luminosidad',
        'prompt': 'Dos estrellas tienen la misma temperatura efectiva. El radio de la estrella B es tres veces el radio de A. Determine el cociente L_B/L_A (sin unidades).',
        'unit': 'L_B/L_A', 'formula': r'L=4\pi R^2\sigma T_{\mathrm{eff}}^4',
    },
    {
        'id': 'P04', 'type': 'text', 'title': 'Evolución post-secuencia principal',
        'prompt': 'Explique brevemente cómo puede responder la envoltura de una estrella cuando su núcleo se contrae después de la secuencia principal. Escriba dos o tres frases.',
    },
    {
        'id': 'P05', 'type': 'choice', 'title': 'Estructura interna esquemática', 'figure': 'layers',
        'prompt': 'El esquema representa una estrella de baja masa con núcleo inerte de helio (A), una capa delgada circundante (B) y una envoltura (C). ¿En qué región se concentra la fusión de hidrógeno por capas?',
        'options': [
            {'id': 'o1', 'text': 'En la región A.'},
            {'id': 'o2', 'text': 'En la región C de manera uniforme.'},
            {'id': 'o3', 'text': 'En las tres regiones por igual.'},
            {'id': 'o4', 'text': 'En la región B.'},
        ],
    },
]
