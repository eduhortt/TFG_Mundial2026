import pandas as pd
import numpy as np
import json
import re
import time
import requests
import unicodedata
import webbrowser
from pathlib import Path

from seleccionador import Seleccionador
from predictor import Predictor

# ══════════════════════════════════════════════════════════════════════════════
#  CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════════════════════

PATH_MUNDIAL       = 'data/dataset_mundial.csv'
PATH_FC            = 'data/FC26_20250921.csv'
PATH_RESULTS       = 'data/results.csv'
PATH_SEL_JSON      = 'data/mundial_selecciones.json'
PATH_PRED_JSON     = 'data/prediccion_mundial.json'
PATH_RANKING_JSON  = 'data/prediccion_mundial_ranking.json'
PATH_HTML          = 'mundial2026.html'
PATH_FOTOS         = 'data/fotos'
N_SIMULACIONES     = 10_000

PAISES = {
    'Canada', 'Mexico', 'United States',
    'Australia', 'Iran', 'Japan', 'Jordan', 'Korea Republic',
    'Qatar', 'Saudi Arabia', 'Uzbekistan', 'Iraq',
    'Algeria', 'Cabo Verde', "Côte d'Ivoire", 'Egypt', 'Ghana',
    'Morocco', 'Senegal', 'South Africa', 'Tunisia', 'Congo DR',
    'Curacao', 'Haiti', 'Panama',
    'Argentina', 'Brazil', 'Colombia', 'Ecuador', 'Paraguay', 'Uruguay',
    'New Zealand',
    'Austria', 'Belgium', 'Bosnia and Herzegovina', 'Croatia', 'Czechia',
    'England', 'France', 'Germany', 'Netherlands', 'Norway',
    'Portugal', 'Scotland', 'Spain', 'Sweden', 'Switzerland', 'Türkiye',
}

HEADERS_HTTP = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://sofifa.com/',
}

SEP  = '=' * 70
SEP2 = '-' * 70

# ══════════════════════════════════════════════════════════════════════════════
#  PASO 1 — PLANTILLAS DE JUGADORES
# ══════════════════════════════════════════════════════════════════════════════

def paso1_plantillas(df_mundial, df_fc):
    print(f"\n{SEP}")
    print("  PASO 1/4 — Generando plantillas de selecciones")
    print(SEP)

    # Merge de fotos
    def _norm(s):
        s = str(s or '').lower().strip()
        s = unicodedata.normalize('NFD', s)
        s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
        s = re.sub(r'[^a-z\s]', '', s)
        return re.sub(r'\s+', ' ', s).strip()

    foto_map = {}
    for _, row in df_fc[['nationality_id','short_name','long_name','player_face_url']].dropna(
            subset=['player_face_url']).iterrows():
        nid = row['nationality_id']
        url = str(row['player_face_url'])
        sn  = _norm(str(row['short_name']))
        foto_map[(nid, sn)] = url
        sn_p = sn.replace('.', '').split()
        if sn_p and len(sn_p[0]) <= 2:
            apellidos = ' '.join(sn_p[1:])
            if apellidos:
                foto_map.setdefault((nid, apellidos), url)
        ln     = _norm(str(row['long_name']))
        foto_map[(nid, ln)] = url
        partes = ln.split()
        for k in range(len(partes) - 1):
            foto_map.setdefault((nid, f"{partes[k]} {partes[k+1]}"), url)
        if partes:
            foto_map.setdefault((nid, partes[0]),  url)
            foto_map.setdefault((nid, partes[-1]), url)

    def buscar_foto(row):
        nid    = row.get('nationality_id')
        nombre = _norm(str(row.get('name', '') or ''))
        partes = nombre.split()
        url = foto_map.get((nid, nombre))
        if not url:
            for k in range(len(partes) - 1):
                url = foto_map.get((nid, f"{partes[k]} {partes[k+1]}"))
                if url: break
        if not url and partes:
            url = foto_map.get((nid, partes[0]))
        if not url and partes:
            url = foto_map.get((nid, partes[-1]))
        return url or ''

    df_mundial['player_face_url'] = df_mundial.apply(buscar_foto, axis=1)
    enc = (df_mundial['player_face_url'] != '').sum()
    print(f"  Fotos encontradas en merge: {enc}/{len(df_mundial)}")

    # Correcciones manuales
    try:
        from correcciones_fotos import CORRECCIONES_FOTOS
        corregidos = 0
        for nombre, url in CORRECCIONES_FOTOS.items():
            mask = df_mundial['name'] == nombre
            if mask.any():
                df_mundial.loc[mask, 'player_face_url'] = url
                corregidos += 1
        if corregidos:
            print(f"  Correcciones manuales aplicadas: {corregidos}")
    except ImportError:
        pass

    # Generar plantillas
    selector   = Seleccionador(df_mundial, df_fc)
    resultados = {}
    total      = len(PAISES)

    for i, pais in enumerate(sorted(PAISES), 1):
        print(f"  [{i:>2}/{total}] {pais}...", end=' ', flush=True)
        try:
            resultados[pais] = selector.generar_dict(pais)
            r = resultados[pais]['resumen_titulares']
            print(f"OVR {r.get('overall_mean','?')} | Score {r.get('score_mean','?')}")
        except Exception as e:
            print(f"ERROR: {e}")
            resultados[pais] = {'seleccion': pais, 'error': str(e)}

    Path(PATH_SEL_JSON).parent.mkdir(parents=True, exist_ok=True)
    with open(PATH_SEL_JSON, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)

    ok = sum(1 for v in resultados.values() if 'error' not in v)
    print(f"\n  OK: {ok}/{total} selecciones generadas -> {PATH_SEL_JSON}")
    return resultados


# ══════════════════════════════════════════════════════════════════════════════
#  PASO 2 — DESCARGAR FOTOS
# ══════════════════════════════════════════════════════════════════════════════

def paso2_fotos(df_fc):
    print(f"\n{SEP}")
    print("  PASO 2/4 — Descargando fotos de jugadores")
    print(SEP)

    Path(PATH_FOTOS).mkdir(parents=True, exist_ok=True)

    with open(PATH_SEL_JSON, encoding='utf-8') as f:
        datos = json.load(f)

    nid_por_sel = (df_fc[['nationality_name','nationality_id']]
                   .drop_duplicates()
                   .set_index('nationality_name')['nationality_id']
                   .to_dict())

    def _norm(s):
        s = str(s or '').lower().strip()
        s = unicodedata.normalize('NFD', s)
        s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
        s = re.sub(r'[^a-z\s]', '', s)
        return re.sub(r'\s+', ' ', s).strip()

    def url_a_filename(url):
        parts = str(url).rstrip('/').split('/')
        try:    return '_'.join(parts[-4:-1]) + '.png'
        except: return parts[-1]

    # Construir índice
    idx = {}
    for _, row in df_fc[['nationality_id','short_name','long_name','player_face_url']].dropna(
            subset=['player_face_url']).iterrows():
        nid = row['nationality_id']
        url = str(row['player_face_url'])
        for campo in ['short_name', 'long_name']:
            n = _norm(str(row[campo]))
            idx[(nid, n)] = url
            partes = n.split()
            for k in range(len(partes) - 1):
                idx.setdefault((nid, f"{partes[k]} {partes[k+1]}"), url)
            if partes:
                idx.setdefault((nid, partes[0]),  url)
                idx.setdefault((nid, partes[-1]), url)
        sn_p = _norm(str(row['short_name'])).replace('.', '').split()
        if sn_p and len(sn_p[0]) <= 2:
            ap = ' '.join(sn_p[1:])
            if ap: idx.setdefault((nid, ap), url)

    def buscar_url(nombre, nid):
        partes = _norm(nombre).split()
        for clave in ([_norm(nombre)] +
                      [f"{partes[k]} {partes[k+1]}" for k in range(len(partes)-1)] +
                      ([partes[0]] if partes else []) +
                      ([partes[-1]] if partes else [])):
            if (nid, clave) in idx:
                return idx[(nid, clave)]
        return None

    # Cargar correcciones manuales
    try:
        from correcciones_fotos import CORRECCIONES_FOTOS
    except ImportError:
        CORRECCIONES_FOTOS = {}

    # Recopilar descargas necesarias
    descargas = {}
    for seleccion, data in datos.items():
        if 'error' in data: continue
        nid = nid_por_sel.get(seleccion)
        for grupo in ['titulares', 'suplentes']:
            for j in data.get(grupo, []):
                nombre = j.get('name', '')

                # Corrección manual tiene prioridad
                if nombre in CORRECCIONES_FOTOS:
                    url   = CORRECCIONES_FOTOS[nombre]
                    fname = url_a_filename(url)
                    j['photo_url'] = f"data/fotos/{fname}"
                    descargas[fname] = url
                    continue

                # Si ya tiene ruta local válida, usarla
                foto = j.get('photo_url', '')
                if foto.startswith('data/fotos/'):
                    fname = Path(foto).name
                    url   = buscar_url(nombre, nid)
                    if url:
                        descargas[fname] = url
                    j['photo_url'] = f"data/fotos/{fname}"
                else:
                    url = buscar_url(nombre, nid)
                    if url:
                        fname = url_a_filename(url)
                        j['photo_url'] = f"data/fotos/{fname}"
                        descargas[fname] = url
                    else:
                        j['photo_url'] = ''

    total  = len(descargas)
    ok = err = skip = 0
    for i, (fname, url) in enumerate(descargas.items(), 1):
        dest = Path(PATH_FOTOS) / fname
        if dest.exists():
            skip += 1
            continue
        try:
            r = requests.get(url, headers=HEADERS_HTTP, timeout=10)
            if r.status_code == 200:
                dest.write_bytes(r.content)
                ok += 1
                if ok % 50 == 0:
                    print(f"  Descargadas: {ok+skip}/{total}...")
            else:
                err += 1
        except Exception:
            err += 1
        time.sleep(0.03)

    print(f"  Nuevas: {ok}  |  Ya existian: {skip}  |  Errores: {err}")

    with open(PATH_SEL_JSON, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    print(f"  OK -> {PATH_SEL_JSON} actualizado con rutas locales")


# ══════════════════════════════════════════════════════════════════════════════
#  PASO 3 — PREDICCIÓN DEL TORNEO
# ══════════════════════════════════════════════════════════════════════════════

def paso3_prediccion():
    print(f"\n{SEP}")
    print(f"  PASO 3/4 — Generando prediccion del torneo ({N_SIMULACIONES:,} simulaciones)")
    print(SEP)

    from calendario import GRUPOS

    predictor = Predictor(PATH_RESULTS, PATH_SEL_JSON)

    print("  Prediccion determinista (104 partidos)...")
    torneo = predictor.predecir_torneo_completo()

    print(f"  Monte Carlo ({N_SIMULACIONES:,} simulaciones)...")
    probs = predictor.monte_carlo(n=N_SIMULACIONES)

    # Ranking
    LABEL = {
        1: 'Campeon',       2: 'Subcampeon',
        3: 'Tercer puesto', 4: 'Cuarto puesto',
        5: 'Semifinalista', 6: 'Cuartofinalista',
        7: 'Octavos',       8: 'Dieciseisavos',
        9: 'Fase de grupos',
    }
    ronda = {}
    ronda[torneo['campeon']]       = 1
    ronda[torneo['subcampeon']]    = 2
    ronda[torneo['tercer_puesto']] = 3
    ronda[torneo['cuarto_puesto']] = 4
    for fase, nivel in [('semifinal',5),('cuartos',6),('octavos',7),('16avos',8)]:
        for p in torneo['eliminatorias'].get(fase, []):
            if p['perdedor'] not in ronda:
                ronda[p['perdedor']] = nivel
    todos = [e for g in GRUPOS.values() for e in g]
    for e in todos:
        if e not in ronda: ronda[e] = 9

    ordenados = sorted(todos, key=lambda e: (ronda.get(e,9), -probs.get(e,{}).get('campeon',0)))
    ranking = []
    pos = 1
    for i, e in enumerate(ordenados):
        if i > 0 and ronda.get(e) != ronda.get(ordenados[i-1]):
            pos = i + 1
        ranking.append({
            'pos': pos, 'seleccion': e,
            'ronda_alcanzada': LABEL.get(ronda.get(e,9), 'Fase de grupos'),
            'p_campeon': probs.get(e,{}).get('campeon', 0.0),
        })

    Path(PATH_PRED_JSON).parent.mkdir(parents=True, exist_ok=True)
    with open(PATH_PRED_JSON, 'w', encoding='utf-8') as f:
        json.dump({'n_simulaciones': N_SIMULACIONES,
                   'prediccion_torneo': torneo,
                   'monte_carlo': probs}, f, ensure_ascii=False, indent=2)
    with open(PATH_RANKING_JSON, 'w', encoding='utf-8') as f:
        json.dump(ranking, f, ensure_ascii=False, indent=2)

    print(f"  Campeon predicho: {torneo['campeon']}")
    print(f"  Top 5 Monte Carlo:")
    for i, (pais, p) in enumerate(list(probs.items())[:5], 1):
        print(f"    {i}. {pais:<25} {p['campeon']:.1f}%")
    print(f"  OK -> {PATH_PRED_JSON}")


# ══════════════════════════════════════════════════════════════════════════════
#  PASO 4 — INCRUSTAR EN HTML
# ══════════════════════════════════════════════════════════════════════════════

def paso4_html():
    print(f"\n{SEP}")
    print("  PASO 4/4 — Incrustando datos en el HTML")
    print(SEP)

    with open(PATH_PRED_JSON,  encoding='utf-8') as f:
        datos_pred = json.load(f)
    with open(PATH_SEL_JSON, encoding='utf-8') as f:
        datos_sel  = json.load(f)
    with open(PATH_HTML, encoding='utf-8') as f:
        html = f.read()

    pred_str = json.dumps(datos_pred, ensure_ascii=False)

    # Eliminar TODAS las ocurrencias de const DATOS_EJEMPLO = {...};
    html_nuevo = re.sub(
        r'const DATOS_EJEMPLO\s*=\s*\{.*?\};',
        '',
        html, flags=re.DOTALL
    )

    # Insertar UNA sola vez antes de async function cargarDatos
    pos = html_nuevo.find('async function cargarDatos')
    if pos != -1:
        html_nuevo = html_nuevo[:pos] + f'const DATOS_EJEMPLO = {pred_str};\n\n' + html_nuevo[pos:]
    else:
        print("  ERROR: no se encontró async function cargarDatos")
        return

    # Limpiar _selData anteriores y añadir nuevo
    MARKER = 'window._selData = {'
    while MARKER in html_nuevo:
        idx_s = html_nuevo.find(MARKER)
        idx_e = html_nuevo.find(';\n', idx_s)
        if idx_e == -1: break
        html_nuevo = html_nuevo[:idx_s] + html_nuevo[idx_e+2:]

    sel_str = json.dumps(datos_sel, ensure_ascii=False)
    pos = html_nuevo.rfind('</script>')
    html_nuevo = html_nuevo[:pos] + f'\nwindow._selData = {sel_str};\n' + html_nuevo[pos:]

    with open(PATH_HTML, 'w', encoding='utf-8') as f:
        f.write(html_nuevo)

    campeon = datos_pred.get('prediccion_torneo', {}).get('campeon', '?')
    print(f"  Campeon incrustado: {campeon}")
    print(f"  Selecciones incrustadas: {len(datos_sel)}")
    print(f"  OK -> {PATH_HTML}")


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print(f"\n{SEP}")
    print("  MUNDIAL 2026 — GENERADOR COMPLETO")
    print(SEP)

    print("\nCargando datasets...")
    df_mundial = pd.read_csv(PATH_MUNDIAL, sep=';', decimal=',', encoding='cp1252')
    df_fc      = pd.read_csv(PATH_FC, sep=',', decimal='.', encoding='utf-8-sig', low_memory=False)
    df_fc['name'] = df_fc['short_name']
    print(f"  Mundial: {len(df_mundial)} jugadores")
    print(f"  FC:      {len(df_fc)} jugadores")

    paso1_plantillas(df_mundial, df_fc)
    paso2_fotos(df_fc)
    paso3_prediccion()
    paso4_html()

    print(f"\n{SEP}")
    print("  PROCESO COMPLETADO")
    print(SEP)
    print(f"  Abre el HTML en el navegador:")
    print(f"  {Path(PATH_HTML).absolute()}")

    # Abrir HTML automáticamente
    try:
        webbrowser.open(Path(PATH_HTML).absolute().as_uri())
        print("  Abriendo navegador...")
    except Exception:
        pass


if __name__ == '__main__':
    main()