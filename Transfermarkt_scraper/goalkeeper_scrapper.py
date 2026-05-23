import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re

# ── CONFIGURACIÓN ─────────────────────────────────────────────────────────────
OUTPUT_FILE = 'porteros_ligas.csv'
TEMPORADA   = '2024'
PAUSA_MIN   = 4
PAUSA_MAX   = 8

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-GB,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Referer': 'https://www.transfermarkt.co.uk/',
}

# ── LIGAS: slug → código ──────────────────────────────────────────────────────
LIGAS = {
    'Major League Soccer':           ('major-league-soccer',           'MLS1'),
    'Campeonato Brasileiro Série A': ('campeonato-brasileiro-serie-a', 'BRA1'),
    'LaLiga':                        ('laliga',                        'ES1'),
    'Serie A':                       ('serie-a',                       'IT1'),
    'Premier League':                ('premier-league',                'GB1'),
    'Bundesliga':                    ('bundesliga',                    'L1'),
    'Ekstraklasa':                   ('ekstraklasa',                   'PL1'),
    'Süper Lig':                     ('super-lig',                     'TR1'),
    'Saudi Pro League':              ('saudi-professional-league',     'SA1'),
    'Liga Portugal':                 ('liga-nos',                      'PO1'),
    'Eredivisie':                    ('eredivisie',                    'NL1'),
    'Ligue 1':                       ('ligue-1',                       'FR1'),
    'Chance Liga':                   ('chance-liga',                   'TS1'),
    'Premier Liga':                  ('premier-liga',                  'RU1'),
    'Jupiler Pro League':            ('jupiler-pro-league',            'BE1'),
    'Super League 1':                ('super-league',                  'GR1'),
    'Premiership':                   ('scottish-premiership',          'SC1'),
    'Superliga':                     ('superliga',                     'DK1'),
}

# ── UTILIDADES ────────────────────────────────────────────────────────────────
def get_soup(url, reintentos=3):
    for intento in range(reintentos):
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            print(f"      Status: {r.status_code} | URL: {url}")
            if r.status_code == 200:
                return BeautifulSoup(r.content, 'html.parser')
        except Exception as e:
            print(f"      ❌ Intento {intento+1}: {e}")
        time.sleep(random.uniform(PAUSA_MIN, PAUSA_MAX))
    return None

def limpiar_num(texto):
    if not texto or texto.strip() in ['-', '']:
        return 0
    try:
        return int(re.sub(r'[^\d]', '', texto))
    except:
        return 0

# ── DIAGNÓSTICO: imprimir estructura de la primera página ────────────────────
def diagnosticar(slug, codigo):
    url  = f'https://www.transfermarkt.co.uk/{slug}/weisseweste/wettbewerb/{codigo}/saison_id/{TEMPORADA}'
    soup = get_soup(url)
    if not soup:
        print("❌ No se pudo cargar")
        return

    # Mostrar todas las tablas encontradas
    tablas = soup.find_all('table')
    print(f"\nTablas encontradas: {len(tablas)}")
    for i, t in enumerate(tablas):
        clases = t.get('class', [])
        filas  = t.find_all('tr')
        print(f"  Tabla {i}: class={clases}, filas={len(filas)}")
        # Mostrar cabeceras
        ths = t.find_all('th')
        if ths:
            print(f"    Cabeceras: {[th.get_text(strip=True) for th in ths[:15]]}")
        # Mostrar primera fila de datos
        for fila in filas[:3]:
            tds = fila.find_all('td')
            if tds:
                print(f"    Fila: {[td.get_text(strip=True)[:20] for td in tds[:12]]}")

# ── EJECUTAR DIAGNÓSTICO CON MLS ──────────────────────────────────────────────
print("=== DIAGNÓSTICO ESTRUCTURA TM ===")
diagnosticar('major-league-soccer', 'MLS1')