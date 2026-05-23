import numpy as np
import json
from scipy.stats import poisson

from elo import calcular_elo, normalizar_elo
from calendario import GRUPOS, FIXTURES_GRUPOS, BRACKET, BRACKET_INFO


# ══════════════════════════════════════════════════════════════════════════════
#  MAPEO DE NOMBRES
#  JSON/Predictor  →  CSV (results.csv)
# ══════════════════════════════════════════════════════════════════════════════

JSON_A_CSV = {
    'Czechia':          'Czech Republic',
    'Congo DR':         'DR Congo',
    'Cabo Verde':       'Cape Verde',
    'Türkiye':          'Turkey',
    'Korea Republic':   'South Korea',
    "Côte d'Ivoire":    'Ivory Coast',
}

CSV_A_JSON = {v: k for k, v in JSON_A_CSV.items()}


# ══════════════════════════════════════════════════════════════════════════════
#  CLASE PREDICTOR
# ══════════════════════════════════════════════════════════════════════════════

class Predictor:

    # Pesos de cada feature en la fuerza final
    W_ELO        = 0.35   # historial competitivo
    W_OVR        = 0.20   # overall medio de la plantilla
    W_TOP5       = 0.15   # ratio jugadores en top5 ligas
    W_POSICIONES = 0.15   # equilibrio defensivo vs ofensivo
    W_RECENT     = 0.15   # racha reciente


    def __init__(self, path_results: str, path_json: str):
        # ELO calculado con nombres del CSV
        self.elo_raw  = calcular_elo(path_results)
        self.elo_norm = normalizar_elo(self.elo_raw)

        # Features del JSON (nombres en formato JSON)
        with open(path_json, encoding='utf-8') as f:
            self.json_data = json.load(f)

        self.overall_norm   = self._extraer_overall()       # overall medio normalizado
        self.top5_norm      = self._extraer_top5()          # ratio top5 ligas normalizado
        self.balance_norm   = self._extraer_balance()       # equilibrio def/of normalizado
        self.racha_norm     = self._calcular_racha(path_results, n=10)

        # Medias globales para fallback
        self._elo_medio    = float(np.mean(list(self.elo_norm.values())))    if self.elo_norm    else 50.0
        self._ovr_medio    = float(np.mean(list(self.overall_norm.values()))) if self.overall_norm else 50.0
        self._top5_medio   = float(np.mean(list(self.top5_norm.values())))   if self.top5_norm   else 50.0
        self._balance_medio= float(np.mean(list(self.balance_norm.values()))) if self.balance_norm else 50.0
        self._racha_media  = float(np.mean(list(self.racha_norm.values())))  if self.racha_norm  else 50.0

        self._debug_features()

    # ── EXTRACCIÓN DE FEATURES ────────────────────────────────────────────────

    @staticmethod
    def _normalizar(d: dict) -> dict:
        if not d: return d
        mn, mx = min(d.values()), max(d.values())
        rng = mx - mn if mx != mn else 1
        return {k: (v - mn) / rng * 100 for k, v in d.items()}

    def _extraer_overall(self) -> dict[str, float]:
        """Overall medio de los 10 titulares (0-100 FIFA)."""
        raw = {}
        for pais, data in self.json_data.items():
            if 'error' in data or not data.get('titulares'):
                continue
            raw[pais] = float(np.mean([p['overall'] for p in data['titulares']]))
        return self._normalizar(raw)

    def _extraer_top5(self) -> dict[str, float]:
        """
        Ratio de jugadores (titulares + suplentes) que militan en top5 ligas.
        Penaliza selecciones con muchos jugadores de ligas menores o FC fallback.
        """
        raw = {}
        for pais, data in self.json_data.items():
            if 'error' in data:
                continue
            todos = data.get('titulares', []) + data.get('suplentes', [])
            if not todos:
                continue
            # Penalización por FC fallback: cuenta como 0 top5 aunque juegue en liga top
            top5  = sum(1 for p in todos if p.get('top5_league') and not p.get('fc_fallback'))
            total = len(todos)
            raw[pais] = top5 / total
        return self._normalizar(raw)

    def _extraer_balance(self) -> dict[str, float]:
        """
        Score de equilibrio posicional: combina la fuerza defensiva (CB, LB, RB)
        y ofensiva (DC, EI, ED) de forma independiente.
        Devuelve la media armónica entre ambas → penaliza equipos muy desequilibrados.
        """
        raw = {}
        SLOTS_DEF = {'CB1', 'CB2', 'LB', 'RB'}
        SLOTS_MED = {'CM1', 'CM2', 'CM3'}
        SLOTS_ATQ = {'DC', 'EI', 'ED'}

        for pais, data in self.json_data.items():
            if 'error' in data or not data.get('titulares'):
                continue

            por_slot = {p['slot']: p['score'] for p in data['titulares']}

            def media_slots(slots):
                vals = [por_slot[s] for s in slots if s in por_slot]
                return float(np.mean(vals)) if vals else 0.0

            s_def = media_slots(SLOTS_DEF)
            s_med = media_slots(SLOTS_MED)
            s_atq = media_slots(SLOTS_ATQ)

            # Media armónica de las 3 líneas → equipos con línea floja bajan más
            if s_def > 0 and s_med > 0 and s_atq > 0:
                raw[pais] = 3 / (1/s_def + 1/s_med + 1/s_atq)
            else:
                raw[pais] = (s_def + s_med + s_atq) / 3

        return self._normalizar(raw)

    def _calcular_racha(self, path_results: str, n: int = 10) -> dict[str, float]:
        import pandas as pd
        df = pd.read_csv(path_results, sep=';', decimal=',', encoding='cp1252')
        df = df.dropna(subset=['home_score', 'away_score']).copy()
        df['home_score'] = pd.to_numeric(df['home_score'], errors='coerce')
        df['away_score'] = pd.to_numeric(df['away_score'], errors='coerce')
        df = df.dropna(subset=['home_score', 'away_score'])
        df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
        df = df.sort_values('date')

        puntos: dict[str, list] = {}
        for _, row in df.iterrows():
            home, away = row['home_team'], row['away_team']
            hs, as_ = int(row['home_score']), int(row['away_score'])
            for team in [home, away]:
                puntos.setdefault(team, [])
            if hs > as_:
                puntos[home].append(1.0); puntos[away].append(0.0)
            elif hs < as_:
                puntos[home].append(0.0); puntos[away].append(1.0)
            else:
                puntos[home].append(0.5); puntos[away].append(0.5)

        racha = {}
        for team, pts in puntos.items():
            ultimos = pts[-n:]
            pesos_r = np.linspace(1, 2, len(ultimos))
            racha[team] = float(np.average(ultimos, weights=pesos_r) * 100)

        mn, mx = min(racha.values()), max(racha.values())
        rng = mx - mn if mx != mn else 1
        return {k: (v - mn) / rng * 100 for k, v in racha.items()}

    def _to_csv_name(self, team: str) -> str:
        return JSON_A_CSV.get(team, team)

    def _to_json_name(self, team: str) -> str:
        return CSV_A_JSON.get(team, team)

    def _get_elo(self, team: str) -> float:
        csv_name = self._to_csv_name(team)
        return self.elo_norm.get(csv_name, self.elo_norm.get(team, self._elo_medio))

    def _get_overall(self, team: str) -> float:
        return self.overall_norm.get(team, self._ovr_medio)

    def _get_top5(self, team: str) -> float:
        return self.top5_norm.get(team, self._top5_medio)

    def _get_balance(self, team: str) -> float:
        return self.balance_norm.get(team, self._balance_medio)

    def _get_racha(self, team: str) -> float:
        csv_name = self._to_csv_name(team)
        return self.racha_norm.get(csv_name, self.racha_norm.get(team, self._racha_media))

    def _fuerza(self, team: str) -> float:
        return (
            self.W_ELO        * self._get_elo(team)     +
            self.W_OVR        * self._get_overall(team)  +
            self.W_TOP5       * self._get_top5(team)     +
            self.W_POSICIONES * self._get_balance(team)  +
            self.W_RECENT     * self._get_racha(team)
        )

    def _debug_features(self):
        print(f"\n{'─'*96}")
        print(f"  {'SELECCIÓN':<28} {'ELO':>6} {'OVR':>6} {'TOP5':>6} {'BAL':>6} {'RACHA':>6} {'FUERZA':>7}")
        print(f"  {'─'*94}")
        todos = [e for g in GRUPOS.values() for e in g]
        for team in sorted(todos):
            e  = self._get_elo(team)
            o  = self._get_overall(team)
            t  = self._get_top5(team)
            b  = self._get_balance(team)
            r  = self._get_racha(team)
            f  = self._fuerza(team)
            fe = '⚠' if self._to_csv_name(team) not in self.elo_norm and team not in self.elo_norm else ' '
            fo = '⚠' if team not in self.overall_norm  else ' '
            ft = '⚠' if team not in self.top5_norm     else ' '
            fb = '⚠' if team not in self.balance_norm  else ' '
            fr = '⚠' if self._to_csv_name(team) not in self.racha_norm and team not in self.racha_norm else ' '
            print(f"  {team:<28} {e:>5.1f}{fe} {o:>5.1f}{fo} {t:>5.1f}{ft} {b:>5.1f}{fb} {r:>5.1f}{fr} {f:>7.2f}")
        print(f"{'─'*96}\n")

    # ── PREDICCIÓN DE PARTIDO ─────────────────────────────────────────────────

    # Rango empírico de goles por equipo en Mundiales:
    #   equipo muy débil  → ~0.6 goles/partido
    #   equipo muy fuerte → ~2.2 goles/partido
    LAMBDA_MIN = 0.2   # equipo muy débil  → puede marcar 0
    LAMBDA_MAX = 3.2   # equipo muy fuerte → puede llegar a 3-4

    def _lambdas(self, home: str, away: str) -> tuple[float, float]:
        """
        Lambda escalada de forma no lineal (cuadrática) para que los equipos
        débiles tengan lambdas mucho más bajas y puedan marcar 0 goles.
        fuerza=100 → lambda=3.2
        fuerza=50  → lambda=~1.0
        fuerza=0   → lambda=0.2
        """
        f_home = self._fuerza(home)
        f_away = self._fuerza(away)

        # Escala cuadrática: penaliza más a los equipos débiles
        def f_to_lambda(f):
            t = (f / 100) ** 1.8  # exponente >1 = curva que baja rápido en valores bajos
            return self.LAMBDA_MIN + (self.LAMBDA_MAX - self.LAMBDA_MIN) * t

        return float(f_to_lambda(f_home)), float(f_to_lambda(f_away))

    def predecir_partido(self, home: str, away: str, max_goles: int = 8) -> dict:
        lam_h, lam_a = self._lambdas(home, away)

        prob_matrix = np.outer(
            [poisson.pmf(i, lam_h) for i in range(max_goles + 1)],
            [poisson.pmf(j, lam_a) for j in range(max_goles + 1)],
        )

        p_home = float(np.sum(np.tril(prob_matrix, -1)))
        p_draw = float(np.sum(np.diag(prob_matrix)))
        p_away = float(np.sum(np.triu(prob_matrix, 1)))

        # resultado_esperado = round(lambda) de cada equipo
        # mucho más representativo que el máximo de la matriz Poisson (siempre 1-1)
        gh_esp = int(round(lam_h))
        ga_esp = int(round(lam_a))

        return {
            'home':              home,
            'away':              away,
            'goles_esp_home':    round(lam_h, 2),
            'goles_esp_away':    round(lam_a, 2),
            'resultado_esperado': f"{gh_esp}-{ga_esp}",
            'p_home':            round(p_home, 4),
            'p_draw':            round(p_draw, 4),
            'p_away':            round(p_away, 4),
        }

    def simular_partido(self, home: str, away: str,
                        eliminatoria: bool = False) -> tuple[str, int, int]:
        lam_h, lam_a = self._lambdas(home, away)
        gh = int(np.random.poisson(lam_h))
        ga = int(np.random.poisson(lam_a))

        if gh > ga:
            return home, gh, ga
        elif ga > gh:
            return away, gh, ga
        else:
            if eliminatoria:
                ganador = home if np.random.random() < 0.5 else away
                return ganador, gh, ga
            return 'draw', gh, ga

    # ── FASE DE GRUPOS ────────────────────────────────────────────────────────

    def simular_grupos(self) -> dict[str, list]:
        clasificacion = {}
        for grupo, equipos in GRUPOS.items():
            tabla = {e: {'pts': 0, 'gf': 0, 'gc': 0} for e in equipos}
            partidos_grupo = [(h, a) for h, a, *_, g in FIXTURES_GRUPOS if g == grupo]
            for home, away in partidos_grupo:
                ganador, gh, ga = self.simular_partido(home, away)
                tabla[home]['gf'] += gh; tabla[home]['gc'] += ga
                tabla[away]['gf'] += ga; tabla[away]['gc'] += gh
                if ganador == home:
                    tabla[home]['pts'] += 3
                elif ganador == away:
                    tabla[away]['pts'] += 3
                else:
                    tabla[home]['pts'] += 1; tabla[away]['pts'] += 1

            orden = sorted(
                equipos,
                key=lambda e: (tabla[e]['pts'],
                               tabla[e]['gf'] - tabla[e]['gc'],
                               tabla[e]['gf']),
                reverse=True,
            )
            clasificacion[grupo] = orden
        return clasificacion

    def _resolver_terceros(self, clasificacion: dict[str, list]) -> list[str]:
        terceros = [(orden[2], grupo)
                    for grupo, orden in clasificacion.items() if len(orden) >= 3]
        terceros.sort(key=lambda x: self._fuerza(x[0]), reverse=True)
        return [t[0] for t in terceros[:8]]

    # ── ELIMINATORIAS ─────────────────────────────────────────────────────────

    def simular_eliminatorias(self, clasificacion: dict[str, list]) -> dict:
        terceros = self._resolver_terceros(clasificacion)
        terceros_iter = iter(terceros)
        resultados: dict[int, dict] = {}

        def resolver_fuente(fuente: str) -> str:
            if fuente.startswith('W'):
                return resultados[int(fuente[1:])]['ganador']
            if fuente.startswith('L'):
                return resultados[int(fuente[1:])]['perdedor']
            pos = int(fuente[0])
            grp = fuente[1:]
            if pos <= 2:
                return clasificacion[grp][pos - 1]
            return next(terceros_iter)

        for pid in sorted(BRACKET.keys()):
            f1, f2   = BRACKET[pid]
            home     = resolver_fuente(f1)
            away     = resolver_fuente(f2)
            ganador, gh, ga = self.simular_partido(home, away, eliminatoria=True)
            perdedor = away if ganador == home else home
            resultados[pid] = {
                'partido': pid, 'home': home, 'away': away,
                'goles_home': gh, 'goles_away': ga,
                'ganador': ganador, 'perdedor': perdedor,
            }
        return resultados

    # ── MONTE CARLO ───────────────────────────────────────────────────────────

    def monte_carlo(self, n: int = 10_000) -> dict:
        np.random.seed(42)  # Semilla fija para garantizar reproducibilidad (RNF-05)
        contadores: dict[str, dict[str, int]] = {
            pais: {'campeon': 0, 'finalista': 0, 'semifinalista': 0,
                   'cuartos': 0, 'octavos': 0, '16avos': 0}
            for pais in [e for g in GRUPOS.values() for e in g]
        }

        for _ in range(n):
            clas = self.simular_grupos()
            elim = self.simular_eliminatorias(clas)

            for pid in range(73, 89):
                if pid in elim:
                    contadores[elim[pid]['home']]['16avos'] += 1
                    contadores[elim[pid]['away']]['16avos'] += 1
            for pid in range(89, 97):
                if pid in elim:
                    contadores[elim[pid]['home']]['octavos'] += 1
                    contadores[elim[pid]['away']]['octavos'] += 1
            for pid in range(97, 101):
                if pid in elim:
                    contadores[elim[pid]['home']]['cuartos'] += 1
                    contadores[elim[pid]['away']]['cuartos'] += 1
            for pid in [101, 102]:
                if pid in elim:
                    contadores[elim[pid]['home']]['semifinalista'] += 1
                    contadores[elim[pid]['away']]['semifinalista'] += 1
            if 104 in elim:
                contadores[elim[104]['home']]['finalista'] += 1
                contadores[elim[104]['away']]['finalista'] += 1
                contadores[elim[104]['ganador']]['campeon'] += 1

        probs = {
            pais: {k: round(v / n * 100, 2) for k, v in cnts.items()}
            for pais, cnts in contadores.items()
        }
        return dict(sorted(probs.items(),
                           key=lambda x: x[1]['campeon'], reverse=True))

    def predecir_fase_grupos(self) -> dict[str, list[dict]]:
        """Usa FIXTURES_GRUPOS (lista plana) con fecha y estadio del calendario oficial."""
        resultado = {}
        for home, away, fecha, estadio, grupo in FIXTURES_GRUPOS:
            pred = self.predecir_partido(home, away)
            pred['fecha']   = fecha
            pred['estadio'] = estadio
            pred['grupo']   = grupo
            resultado.setdefault(grupo, []).append(pred)
        return resultado

    def _ganador_probable(self, home: str, away: str) -> str:
        pred = self.predecir_partido(home, away)
        p_h = pred['p_home'] + pred['p_draw'] * 0.5
        p_a = pred['p_away'] + pred['p_draw'] * 0.5
        return home if p_h >= p_a else away

    def _clasificacion_grupo_determinista(self) -> dict[str, list]:
        """Clasifica cada grupo usando el resultado esperado del calendario oficial."""
        clasificacion = {}
        for grupo, equipos in GRUPOS.items():
            tabla = {e: {'pts': 0, 'gf': 0, 'gc': 0} for e in equipos}
            partidos_grupo = [(h, a) for h, a, *_ , g in FIXTURES_GRUPOS if g == grupo]
            for home, away in partidos_grupo:
                pred = self.predecir_partido(home, away)
                gh, ga = map(int, pred['resultado_esperado'].split('-'))
                tabla[home]['gf'] += gh; tabla[home]['gc'] += ga
                tabla[away]['gf'] += ga; tabla[away]['gc'] += gh
                if gh > ga:
                    tabla[home]['pts'] += 3
                elif ga > gh:
                    tabla[away]['pts'] += 3
                else:
                    tabla[home]['pts'] += 1; tabla[away]['pts'] += 1

            orden = sorted(
                equipos,
                key=lambda e: (tabla[e]['pts'],
                               tabla[e]['gf'] - tabla[e]['gc'],
                               tabla[e]['gf']),
                reverse=True,
            )
            clasificacion[grupo] = orden
        return clasificacion

    def predecir_torneo_completo(self) -> dict:
        """
        Predice los 104 partidos del torneo de forma determinista:
        - Fase de grupos: usa resultado_esperado de cada partido
        - Eliminatorias: en cada cruce avanza el equipo con mayor P(ganar)
        Devuelve un dict con todos los partidos organizados por fase.
        """
        # ── Fase de grupos ────────────────────────────────────────────────────
        fase_grupos = self.predecir_fase_grupos()
        clasificacion = self._clasificacion_grupo_determinista()

        # Mejores terceros por fuerza
        terceros = [(orden[2], grupo)
                    for grupo, orden in clasificacion.items() if len(orden) >= 3]
        terceros.sort(key=lambda x: self._fuerza(x[0]), reverse=True)
        mejores_terceros = [t[0] for t in terceros[:8]]
        terceros_iter = iter(mejores_terceros)

        # Tablas de grupos para el JSON
        tablas_grupos = {}
        for grupo, orden in clasificacion.items():
            tablas_grupos[grupo] = [
                {'pos': i+1, 'equipo': e}
                for i, e in enumerate(orden)
            ]

        # ── Eliminatorias ─────────────────────────────────────────────────────
        partidos_elim: dict[int, dict] = {}

        def resolver_fuente(fuente: str) -> str:
            if fuente.startswith('W'):
                return partidos_elim[int(fuente[1:])]['ganador']
            if fuente.startswith('L'):
                return partidos_elim[int(fuente[1:])]['perdedor']
            pos = int(fuente[0])
            grp = fuente[1:]
            if pos <= 2:
                return clasificacion[grp][pos - 1]
            return next(terceros_iter)

        for pid in sorted(BRACKET.keys()):
            f1, f2   = BRACKET[pid]
            home     = resolver_fuente(f1)
            away     = resolver_fuente(f2)
            pred     = self.predecir_partido(home, away)
            ganador  = self._ganador_probable(home, away)
            perdedor = away if ganador == home else home
            _, _, fecha, estadio = BRACKET_INFO[pid]

            # Fase
            if pid <= 88:   fase = '16avos'
            elif pid <= 96: fase = 'octavos'
            elif pid <= 100: fase = 'cuartos'
            elif pid <= 102: fase = 'semifinal'
            elif pid == 103: fase = 'tercer_puesto'
            else:            fase = 'final'

            partidos_elim[pid] = {
                'partido_id':         pid,
                'fase':               fase,
                'fecha':              fecha,
                'estadio':            estadio,
                'home':               home,
                'away':               away,
                'goles_esp_home':     pred['goles_esp_home'],
                'goles_esp_away':     pred['goles_esp_away'],
                'resultado_esperado': pred['resultado_esperado'],
                'p_home':             pred['p_home'],
                'p_draw':             pred['p_draw'],
                'p_away':             pred['p_away'],
                'ganador':            ganador,
                'perdedor':           perdedor,
            }

        # Organizar eliminatorias por fase
        fases = ['16avos', 'octavos', 'cuartos', 'semifinal', 'tercer_puesto', 'final']
        eliminatorias = {f: [] for f in fases}
        for p in partidos_elim.values():
            eliminatorias[p['fase']].append(p)

        campeon = partidos_elim[104]['ganador']
        tercero = partidos_elim[103]['ganador']

        return {
            'tablas_grupos':  tablas_grupos,
            'fase_grupos':    fase_grupos,
            'eliminatorias':  eliminatorias,
            'campeon':        campeon,
            'subcampeon':     partidos_elim[104]['perdedor'],
            'tercer_puesto':  tercero,
            'cuarto_puesto':  partidos_elim[103]['perdedor'],
        }