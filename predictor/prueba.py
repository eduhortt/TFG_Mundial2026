import json

d = json.load(open('data/prediccion_mundial.json', encoding='utf-8'))
mc = d['monte_carlo']

selecciones = [
    ('España',       'Spain'),
    ('Francia',      'France'),
    ('Portugal',     'Portugal'),
    ('Inglaterra',   'England'),
    ('Brasil',       'Brazil'),
    ('Argentina',    'Argentina'),
    ('Alemania',     'Germany'),
    ('Países Bajos', 'Netherlands'),
    ('Marruecos',    'Morocco'),
    ('Bélgica',      'Belgium'),
]

for i, (nombre_es, nombre_en) in enumerate(selecciones, 1):
    p = mc[nombre_en]
    print(f"{i}  & {nombre_es} & {p['campeon']:.1f}\\% & {p['finalista']:.1f}\\% & {p['semifinalista']:.1f}\\% & {p['cuartos']:.1f}\\% & {p['octavos']:.1f}\\% \\\\")