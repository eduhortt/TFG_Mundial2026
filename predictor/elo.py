import pandas as pd
import numpy as np


# ══════════════════════════════════════════════════════════════════════════════
#  ELO DINÁMICO
#  Calcula el rating ELO de cada selección a partir del historial de partidos.
#  El campo 'peso' del CSV se usa para escalar el K-factor.
# ══════════════════════════════════════════════════════════════════════════════

# K-factor base — se multiplica por (peso / 50) para dar más peso a partidos
# importantes (Mundial = 50, Amistoso = 10, etc.)
K_BASE       = 32
ELO_INICIAL  = 1000
# Factor de ventaja local — se establece a 0 porque en partidos entre selecciones
# nacionales casi nunca hay un local real (Mundiales, Eurocopas y eliminatorias
# se juegan en sedes neutrales o con escasa ventaja real demostrable).
HOME_ADV     = 0


def calcular_elo(path_csv: str) -> dict[str, float]:
    """
    Lee el CSV de resultados y devuelve un dict {seleccion: elo_final}.
    Solo procesa partidos que ya tienen resultado (home_score y away_score rellenos).
    """
    df = pd.read_csv(path_csv, sep=';', decimal=',', encoding='cp1252')

    # Filtrar solo partidos con resultado
    df = df.dropna(subset=['home_score', 'away_score']).copy()
    df['home_score'] = pd.to_numeric(df['home_score'], errors='coerce')
    df['away_score'] = pd.to_numeric(df['away_score'], errors='coerce')
    df = df.dropna(subset=['home_score', 'away_score'])

    # Ordenar por fecha
    df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
    df = df.sort_values('date').reset_index(drop=True)

    elo: dict[str, float] = {}

    def get_elo(team: str) -> float:
        return elo.get(team, ELO_INICIAL)

    for _, row in df.iterrows():
        home  = row['home_team']
        away  = row['away_team']
        hs    = int(row['home_score'])
        as_   = int(row['away_score'])
        peso  = float(row.get('peso', 10) or 10)

        r_home = get_elo(home)
        r_away = get_elo(away)

        # Probabilidad esperada (con ventaja local en historial)
        exp_home = 1 / (1 + 10 ** ((r_away - (r_home + HOME_ADV)) / 400))
        exp_away = 1 - exp_home

        # Resultado real
        if hs > as_:
            s_home, s_away = 1.0, 0.0
        elif hs < as_:
            s_home, s_away = 0.0, 1.0
        else:
            s_home, s_away = 0.5, 0.5

        # Margen de goles como multiplicador (suavizado con log)
        margen = abs(hs - as_)
        mult   = np.log1p(margen) + 1.0

        k = K_BASE * (peso / 50) * mult

        elo[home] = r_home + k * (s_home - exp_home)
        elo[away] = r_away + k * (s_away - exp_away)

    return elo


def normalizar_elo(elo: dict[str, float]) -> dict[str, float]:
    """Reescala ELO a rango 0-100 para usarlo como feature junto a otros scores."""
    if not elo:
        return {}
    vals  = list(elo.values())
    mn, mx = min(vals), max(vals)
    if mx == mn:
        return {k: 50.0 for k in elo}
    return {k: (v - mn) / (mx - mn) * 100 for k, v in elo.items()}


def get_elo_table(path_csv: str) -> pd.DataFrame:
    """Devuelve un DataFrame ordenado por ELO descendente."""
    elo  = calcular_elo(path_csv)
    rows = [{'seleccion': k, 'elo': round(v, 1)} for k, v in elo.items()]
    return pd.DataFrame(rows).sort_values('elo', ascending=False).reset_index(drop=True)