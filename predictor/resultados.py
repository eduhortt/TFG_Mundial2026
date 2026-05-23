import json

d = json.load(open('data/mundial_selecciones.json', encoding='utf-8'))

for sel in ['Spain', 'France', 'Argentina']:
    print(f'\n=== {sel} ===')
    for j in d[sel]['titulares']:
        print(f"{j['slot']:<6} {j['name']:<25} {j['overall']} {j['score']:.1f}  {j['league']}")