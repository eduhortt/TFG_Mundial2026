import pandas as pd
import numpy as np
import unicodedata
import re


class Seleccionador:

    LIGAS_TOP5 = {'LaLiga', 'Serie A', 'Ligue 1', 'Bundesliga', 'Premier League'}
    BONUS_LIGA = 3.0
    MIN_MINUTOS = 100
    PESO_2526 = 3.0
    PESO_2425 = 1.0
    MIN_REFERENCIA = 3000

    POSICIONES = {
        'LB':  ['LB', 'LWB'],
        'CB1': ['CB'],
        'CB2': ['CB'],
        'RB':  ['RB', 'RWB'],
        'CM1': ['CM', 'CDM', 'CAM'],
        'CM2': ['CM', 'CDM', 'CAM'],
        'CM3': ['CM', 'CDM', 'CAM'],
        'EI':  ['LW', 'LM', 'CAM', 'RW', 'RM'],
        'DC':  ['ST', 'CF'],
        'ED':  ['RW', 'RM', 'CAM', 'LW', 'LM'],
    }

    SUPLENTES_CONFIG = [
        {'slot': 'SUP_CB',  'label': 'CB',  'ref_slot': 'CB1'},
        {'slot': 'SUP_LB',  'label': 'LB',  'ref_slot': 'LB'},
        {'slot': 'SUP_RB',  'label': 'RB',  'ref_slot': 'RB'},
        {'slot': 'SUP_CDM', 'label': 'CDM', 'ref_slot': 'CM1'},
        {'slot': 'SUP_CM',  'label': 'CM',  'ref_slot': 'CM2'},
        {'slot': 'SUP_CAM', 'label': 'CAM', 'ref_slot': 'CM3'},
        {'slot': 'SUP_EI',  'label': 'EI',  'ref_slot': 'EI'},
        {'slot': 'SUP_ED',  'label': 'ED',  'ref_slot': 'ED'},
        {'slot': 'SUP_DC1', 'label': 'DC',  'ref_slot': 'DC'},
        {'slot': 'SUP_DC2', 'label': 'DC',  'ref_slot': 'DC'},
    ]

    SUPLENTES_POSICIONES = {
        'SUP_CB':  ['CB'],
        'SUP_LB':  ['LB', 'LWB'],
        'SUP_RB':  ['RB', 'RWB'],
        'SUP_CDM': ['CDM'],
        'SUP_CM':  ['CM'],
        'SUP_CAM': ['CAM'],
        'SUP_EI':  ['LW', 'LM'],
        'SUP_ED':  ['RW', 'RM'],
        'SUP_DC1': ['ST', 'CF'],
        'SUP_DC2': ['ST', 'CF'],
    }

    EXCLUIR_SI_PRIMERA = {
        'CM1': ['ST', 'CF', 'RW', 'LW', 'RM', 'LM'],
        'CM2': ['ST', 'CF', 'RW', 'LW', 'RM', 'LM'],
        'CM3': ['ST', 'CF', 'RW', 'LW', 'RM', 'LM'],
        'LB':  ['ST', 'CF', 'CM', 'CDM', 'RW', 'RM'],
        'RB':  ['ST', 'CF', 'CM', 'CDM', 'LW', 'LM'],
        'CB1': ['ST', 'CF', 'CM', 'CDM', 'CAM', 'LW', 'LM', 'RW', 'RM', 'LB', 'RB'],
        'CB2': ['ST', 'CF', 'CM', 'CDM', 'CAM', 'LW', 'LM', 'RW', 'RM', 'LB', 'RB'],
    }

    PESOS_POS = {
        'CB1': {
            'defending_marking_awareness': 5, 'defending_standing_tackle': 5,
            'defending_sliding_tackle': 4,    'mentality_interceptions': 4,
            'power_strength': 3,              'power_jumping': 3,
            'mentality_composure': 2,         'passing': 2,
        },
        'CB2': {
            'defending_marking_awareness': 5, 'defending_standing_tackle': 5,
            'defending_sliding_tackle': 4,    'mentality_interceptions': 4,
            'power_strength': 3,              'power_jumping': 3,
            'mentality_composure': 2,         'passing': 2,
        },
        'LB': {
            'defending_standing_tackle': 4,   'defending_marking_awareness': 4,
            'movement_acceleration': 4,       'pace': 4,
            'attacking_crossing': 3,          'power_stamina': 3,
            'movement_agility': 2,            'passing': 2,
        },
        'RB': {
            'defending_standing_tackle': 4,   'defending_marking_awareness': 4,
            'movement_acceleration': 4,       'pace': 4,
            'attacking_crossing': 3,          'power_stamina': 3,
            'movement_agility': 2,            'passing': 2,
        },
        'CM1': {
            'mentality_vision': 5,            'skill_ball_control': 4,
            'attacking_short_passing': 4,     'skill_long_passing': 4,
            'mentality_interceptions': 3,     'defending_marking_awareness': 3,
            'power_stamina': 3,               'mentality_composure': 2,
        },
        'CM2': {
            'mentality_vision': 5,            'skill_ball_control': 4,
            'attacking_short_passing': 4,     'skill_long_passing': 4,
            'mentality_interceptions': 3,     'defending_marking_awareness': 3,
            'power_stamina': 3,               'mentality_composure': 2,
        },
        'CM3': {
            'mentality_vision': 5,            'skill_ball_control': 4,
            'attacking_short_passing': 4,     'skill_long_passing': 4,
            'mentality_interceptions': 3,     'defending_marking_awareness': 3,
            'power_stamina': 3,               'mentality_composure': 2,
        },
        'EI': {
            'pace': 5,                        'skill_dribbling': 5,
            'movement_acceleration': 4,       'movement_agility': 4,
            'attacking_finishing': 3,         'attacking_crossing': 3,
            'power_long_shots': 2,
        },
        'ED': {
            'pace': 5,                        'skill_dribbling': 5,
            'movement_acceleration': 4,       'movement_agility': 4,
            'attacking_finishing': 3,         'attacking_crossing': 3,
            'power_long_shots': 2,
        },
        'DC': {
            'attacking_finishing': 5,         'mentality_positioning': 5,
            'movement_reactions': 4,          'power_shot_power': 4,
            'attacking_heading_accuracy': 3,  'power_strength': 3,
            'skill_dribbling': 2,             'pace': 2,
        },
    }

    PESOS_GK = {
        'goalkeeping_reflexes':    5,
        'goalkeeping_diving':      5,
        'goalkeeping_positioning': 4,
        'goalkeeping_handling':    4,
        'goalkeeping_kicking':     2,
        'goalkeeping_speed':       2,
    }

    # Equivalencias de nombres entre TM y FC para jugadores con nombre de camiseta
    # Clave: nombre corto FC  →  Valor: nombre completo TM
    EQUIVALENCIAS_NOMBRES = {
        'Moisés': 'Moisés Caicedo',
    }

    # Exclusiones por selección: jugadores que NO deben aparecer en esa selección
    # aunque tengan esa nacionalidad en el dataset (doble nacionalidad incorrecta)
    EXCLUSIONES = {
        'Ghana':    {'Kingsley Coman', 'Alexander Lind'},
        'Mexico':   {'Theo Hernández', 'Theo Hernandez'},
        'Colombia': {'Luis Suárez', 'Luis Suarez'},
    }

    # ── INIT ──────────────────────────────────────────────────────────────────

    def __init__(self, df_mundial: pd.DataFrame, df_fc: pd.DataFrame):
        self.df_mundial = df_mundial
        self.df_fc      = df_fc

    # ── HELPERS DE NOMBRE ─────────────────────────────────────────────────────

    @staticmethod
    def _norm_nombre(s: str) -> str:
        s = str(s or '').lower().strip()
        s = unicodedata.normalize('NFD', s)
        s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
        return re.sub(r'\s+', ' ', re.sub(r'[^a-z\s]', '', s)).strip()

    @staticmethod
    def _nombre_claves(nombre: str) -> set:
        """
        Genera variantes de un nombre para detectar duplicados.
        'Amine Gouiri' → {'amine gouiri', 'gouiri', 'a. gouiri', 'a gouiri'}
        'A. Gouiri'    → {'a. gouiri', 'a gouiri', 'gouiri'}
        También añade el nombre equivalente si existe en EQUIVALENCIAS_NOMBRES.
        """
        n = Seleccionador._norm_nombre(nombre)
        partes = n.replace('.', '').split()
        claves = {n}
        if partes:
            claves.add(partes[-1])
            claves.add(partes[0][0] + '. ' + partes[-1])
            claves.add(partes[0][0] + ' ' + partes[-1])
            if len(partes) >= 2:
                claves.add(partes[0] + ' ' + partes[-1])

        # Añadir equivalencia si existe
        for corto, completo in Seleccionador.EQUIVALENCIAS_NOMBRES.items():
            n_corto    = Seleccionador._norm_nombre(corto)
            n_completo = Seleccionador._norm_nombre(completo)
            if n == n_corto or n == n_completo:
                claves.add(n_corto)
                claves.add(n_completo)
                # Añadir también las claves del nombre completo
                p = n_completo.replace('.', '').split()
                if p:
                    claves.add(p[-1])
                    claves.add(p[0][0] + '. ' + p[-1])
                    claves.add(p[0] + ' ' + p[-1] if len(p) >= 2 else p[0])

        return claves

    # ── LÓGICA INTERNA ────────────────────────────────────────────────────────

    def _bonus_rendimiento(self, row, slot):
        goals_2526   = row.get('25/26_goals',   0) or 0
        assists_2526 = row.get('25/26_assists', 0) or 0
        goals_2425   = row.get('24/25_goals',   0) or 0
        assists_2425 = row.get('24/25_assists', 0) or 0
        mins_2425    = row.get('24/25_minutes', 0) or 0
        mins_2526    = row.get('25/26_minutes', 0) or 0

        # Combinar minutos de ambas temporadas con los mismos pesos que goles/asistencias
        # La temporada actual (25/26) pesa 3x más que la pasada (24/25)
        # Denominador: PESO_2526 * MIN_REFERENCIA = 3 * 3000 = 9000
        # Así una temporada completa en 25/26 (3000 min) da bonus máximo = 10
        mins_pond  = mins_2526 * self.PESO_2526 + mins_2425 * self.PESO_2425
        bonus_mins = min(mins_pond / (self.PESO_2526 * self.MIN_REFERENCIA), 1.0) * 10

        if slot in ['DC', 'EI', 'ED']:
            return ((goals_2526 * self.PESO_2526 + goals_2425 * self.PESO_2425) * 1.5
                  + (assists_2526 * self.PESO_2526 + assists_2425 * self.PESO_2425) * 0.5
                  + bonus_mins)
        elif slot in ['CM1', 'CM2', 'CM3']:
            return ((assists_2526 * self.PESO_2526 + assists_2425 * self.PESO_2425) * 1.5
                  + (goals_2526 * self.PESO_2526 + goals_2425 * self.PESO_2425) * 0.4
                  + bonus_mins * 1.5)
        elif slot in ['LB', 'RB']:
            return ((assists_2526 * self.PESO_2526 + assists_2425 * self.PESO_2425) * 1.0
                  + bonus_mins)
        else:
            return bonus_mins

    def _calcular_score(self, row, slot):
        pesos       = self.PESOS_POS[slot]
        total_peso  = sum(pesos.values())
        score_attrs = sum((row.get(a, 0) or 0) * w for a, w in pesos.items()) / total_peso
        overall     = row.get('overall', 0) or 0
        bonus_tm    = min(self._bonus_rendimiento(row, slot), 100)

        if slot in ['CM1', 'CM2', 'CM3']:
            score_base = score_attrs * 0.60 + overall * 0.25 + bonus_tm * 0.15
        elif slot in ['CB1', 'CB2']:
            score_base = score_attrs * 0.70 + overall * 0.25 + bonus_tm * 0.05
        elif slot in ['LB', 'RB']:
            score_base = score_attrs * 0.65 + overall * 0.25 + bonus_tm * 0.10
        else:
            score_base = score_attrs * 0.55 + overall * 0.20 + bonus_tm * 0.25

        liga = row.get('current_league', '') or ''
        return score_base + (self.BONUS_LIGA if liga in self.LIGAS_TOP5 else 0)

    def _puede_jugar(self, pos_str, slot):
        if not isinstance(pos_str, str): return False
        tags = [p.strip() for p in pos_str.split(',')]
        if not any(p in tags for p in self.POSICIONES[slot]): return False
        primera = tags[0] if tags else ''
        if primera in self.EXCLUIR_SI_PRIMERA.get(slot, []): return False
        return True

    def _puede_suplir(self, pos_str, sup_slot):
        if not isinstance(pos_str, str): return False
        primera = pos_str.split(',')[0].strip()
        return primera in self.SUPLENTES_POSICIONES[sup_slot]

    def _fc_fallback(self, seleccion, slot, ya_elegidos, ya_claves=None,
                     es_suplente=False, sup_slot=None):
        cands = self.df_fc[self.df_fc['nationality_name'] == seleccion].copy()
        col   = f'score_{slot}'

        if es_suplente:
            mascara = cands['player_positions'].apply(
                lambda p, ss=sup_slot: self._puede_suplir(p, ss))
        else:
            mascara = cands['player_positions'].apply(
                lambda p, s=slot: self._puede_jugar(p, s))

        cands = cands[mascara].copy()
        cands[col] = cands.apply(lambda r, s=slot: self._calcular_score(r, s), axis=1)
        cands = cands[~cands.index.isin(ya_elegidos)]

        # Filtrar también por claves de nombre si se proporcionan
        if ya_claves:
            cands = cands[~cands['name'].apply(
                lambda n: bool(self._nombre_claves(str(n)) & ya_claves))]

        if col not in cands.columns or cands.empty:
            return None, None

        cands = cands.sort_values(col, ascending=False)

        if len(cands) > 0:
            j = cands.iloc[0].copy()
            j['_fc_fallback'] = True
            return j, cands.index[0]
        return None, None

    def _buscar_candidato(self, df_eleg, df_sel, slot, col, ya, ya_claves=None):
        nombre_ok = df_eleg['name'].apply(
            lambda n: not bool(self._nombre_claves(str(n)) & ya_claves)
            if ya_claves else True)
        cands = df_eleg[df_eleg[col].notna() & ~df_eleg.index.isin(ya) & nombre_ok]\
                       .sort_values(col, ascending=False)
        if len(cands) > 0:
            return cands.iloc[0], cands.index[0]

        df2      = df_sel.copy()
        df2[col] = df2.apply(
            lambda r, s=slot: self._calcular_score(r, s)
            if self._puede_jugar(r['player_positions'], s) else np.nan, axis=1)
        nombre_ok2 = df2['name'].apply(
            lambda n: not bool(self._nombre_claves(str(n)) & ya_claves)
            if ya_claves else True)
        cands2 = df2[df2[col].notna() & ~df2.index.isin(ya) & nombre_ok2]\
                    .sort_values(col, ascending=False)
        if len(cands2) > 0:
            return cands2.iloc[0], cands2.index[0]

        return None, None

    # ── SELECCIÓN TITULAR ─────────────────────────────────────────────────────

    def elegir_titular(self, seleccion: str):
        sel       = self.df_mundial[self.df_mundial['nationality_name'] == seleccion].copy()
        # Aplicar exclusiones por selección
        excluidos = self.EXCLUSIONES.get(seleccion, set())
        if excluidos:
            sel = sel[~sel['name'].isin(excluidos)].copy()
        mins_2425 = pd.to_numeric(sel['24/25_minutes'], errors='coerce')
        mins_2526 = pd.to_numeric(sel['25/26_minutes'], errors='coerce')
        eleg = sel[
            (mins_2425 >= self.MIN_MINUTOS) |
            (mins_2526 >= self.MIN_MINUTOS) |
            mins_2425.isna()
        ].copy()

        for slot in self.POSICIONES:
            eleg[f'score_{slot}'] = eleg.apply(
                lambda r, s=slot: self._calcular_score(r, s)
                if self._puede_jugar(r['player_positions'], s) else np.nan, axis=1)

        once, ya, ya_claves = {}, set(), set()
        for slot in ['CB1', 'CB2', 'LB', 'RB', 'CM1', 'CM2', 'CM3', 'DC', 'EI', 'ED']:
            col = f'score_{slot}'
            j, idx = self._buscar_candidato(eleg, sel, slot, col, ya, ya_claves)
            if j is not None:
                once[slot] = j
                ya.add(idx)
                ya_claves |= self._nombre_claves(str(j.get('name', '')))
            else:
                j_fc, idx_fc = self._fc_fallback(seleccion, slot, ya, ya_claves)
                if j_fc is not None:
                    once[slot] = j_fc
                    ya.add(idx_fc)
                    ya_claves |= self._nombre_claves(str(j_fc.get('name', '')))

        return once, ya, ya_claves

    # ── SUPLENTES ─────────────────────────────────────────────────────────────

    def elegir_suplentes(self, seleccion: str, ya_elegidos: set, ya_claves: set = None):
        sel       = self.df_mundial[self.df_mundial['nationality_name'] == seleccion].copy()
        # Aplicar exclusiones por selección
        excluidos = self.EXCLUSIONES.get(seleccion, set())
        if excluidos:
            sel = sel[~sel['name'].isin(excluidos)].copy()
        mins_2425 = pd.to_numeric(sel['24/25_minutes'], errors='coerce')
        mins_2526 = pd.to_numeric(sel['25/26_minutes'], errors='coerce')
        eleg = sel[
            (mins_2425 >= self.MIN_MINUTOS) |
            (mins_2526 >= self.MIN_MINUTOS) |
            mins_2425.isna()
        ].copy()

        for ref in set(c['ref_slot'] for c in self.SUPLENTES_CONFIG):
            eleg[f'score_{ref}'] = eleg.apply(
                lambda r, s=ref: self._calcular_score(r, s)
                if self._puede_jugar(r['player_positions'], s) else np.nan, axis=1)

        ya_claves = set(ya_claves or set())
        suplentes, ya = {}, set(ya_elegidos)

        for cfg in self.SUPLENTES_CONFIG:
            sup_slot = cfg['slot']
            ref_slot = cfg['ref_slot']
            col      = f'score_{ref_slot}'

            mascara   = eleg['player_positions'].apply(
                lambda p, ss=sup_slot: self._puede_suplir(p, ss))
            nombre_ok = eleg['name'].apply(
                lambda n: not bool(self._nombre_claves(str(n)) & ya_claves))
            cands = eleg[
                mascara & eleg[col].notna() & ~eleg.index.isin(ya) & nombre_ok
            ].sort_values(col, ascending=False)

            if len(cands) == 0:
                sel2      = sel.copy()
                sel2[col] = sel2.apply(
                    lambda r, s=ref_slot: self._calcular_score(r, s)
                    if self._puede_jugar(r['player_positions'], s) else np.nan, axis=1)
                mascara2   = sel2['player_positions'].apply(
                    lambda p, ss=sup_slot: self._puede_suplir(p, ss))
                nombre_ok2 = sel2['name'].apply(
                    lambda n: not bool(self._nombre_claves(str(n)) & ya_claves))
                cands = sel2[
                    mascara2 & sel2[col].notna() & ~sel2.index.isin(ya) & nombre_ok2
                ].sort_values(col, ascending=False)

            if len(cands) > 0:
                j = cands.iloc[0]
                suplentes[sup_slot] = (j, cfg['label'], ref_slot)
                ya.add(cands.index[0])
                ya_claves |= self._nombre_claves(str(j.get('name', '')))
            else:
                j_fc, idx_fc = self._fc_fallback(
                    seleccion, ref_slot, ya, ya_claves,
                    es_suplente=True, sup_slot=sup_slot)
                if j_fc is not None:
                    suplentes[sup_slot] = (j_fc, cfg['label'], ref_slot)
                    ya.add(idx_fc)
                    ya_claves |= self._nombre_claves(str(j_fc.get('name', '')))

        return suplentes

    # ── PORTEROS ──────────────────────────────────────────────────────────────

    def _calcular_score_gk(self, row):
        pesos       = self.PESOS_GK
        total_peso  = sum(pesos.values())
        score_attrs = sum((row.get(a, 0) or 0) * w for a, w in pesos.items()) / total_peso
        overall     = row.get('overall', 0) or 0
        liga        = row.get('league_name', '') or ''
        score_base  = score_attrs * 0.70 + overall * 0.30
        return score_base + (self.BONUS_LIGA if liga in self.LIGAS_TOP5 else 0)

    def _portero_a_dict(self, row, slot='GK') -> dict:
        def safe_int(v):
            try: return int(v) if pd.notna(v) else 0
            except: return 0
        def safe_float(v):
            try: return round(float(v), 2) if pd.notna(v) else 0.0
            except: return 0.0
        liga = str(row.get('league_name', '') or '')
        return {
            'slot':         slot,
            'name':         str(row.get('short_name', '') or ''),
            'positions':    'GK',
            'overall':      safe_int(row.get('overall')),
            'score':        safe_float(row.get('score_gk', 0)),
            'goals_2526':   0, 'assists_2526': 0,
            'goals_2425':   0, 'assists_2425': 0,
            'minutes_2425': 0,
            'league':       liga,
            'top5_league':  liga in self.LIGAS_TOP5,
            'fc_fallback':  False,
            'photo_url':    str(row.get('player_face_url', '') or ''),
        }

    def elegir_portero(self, seleccion: str):
        gks = self.df_fc[
            (self.df_fc['nationality_name'] == seleccion) &
            (self.df_fc['player_positions'].str.contains('GK', na=False))
        ].copy()
        if gks.empty:
            return None
        gks['score_gk'] = gks.apply(self._calcular_score_gk, axis=1)
        best = gks.sort_values('score_gk', ascending=False).iloc[0]
        return self._portero_a_dict(best, 'GK')

    def elegir_portero_suplente(self, seleccion: str, titular_nombre: str):
        gks = self.df_fc[
            (self.df_fc['nationality_name'] == seleccion) &
            (self.df_fc['player_positions'].str.contains('GK', na=False)) &
            (self.df_fc['short_name'] != titular_nombre)
        ].copy()
        if gks.empty:
            return None
        gks['score_gk'] = gks.apply(self._calcular_score_gk, axis=1)
        best = gks.sort_values('score_gk', ascending=False).iloc[0]
        return self._portero_a_dict(best, 'GK')

    # ── SERIALIZACIÓN ─────────────────────────────────────────────────────────

    @staticmethod
    def _jugador_a_dict(j, score_col, slot_label, fc_fallback=False):
        def safe_int(v):
            try: return int(v) if pd.notna(v) else 0
            except: return 0
        def safe_float(v):
            try: return round(float(v), 2) if pd.notna(v) else 0.0
            except: return 0.0
        return {
            'slot':         slot_label,
            'name':         str(j.get('name', '') or ''),
            'positions':    str(j.get('player_positions', '') or ''),
            'overall':      safe_int(j.get('overall')),
            'score':        safe_float(j.get(score_col)),
            'goals_2526':   safe_int(j.get('25/26_goals')),
            'assists_2526': safe_int(j.get('25/26_assists')),
            'goals_2425':   safe_int(j.get('24/25_goals')),
            'assists_2425': safe_int(j.get('24/25_assists')),
            'minutes_2425': safe_int(j.get('24/25_minutes')),
            'minutes_2526': safe_int(j.get('25/26_minutes')),
            'league':       str(j.get('current_league', '') or ''),
            'top5_league':  str(j.get('current_league', '') or '') in Seleccionador.LIGAS_TOP5,
            'fc_fallback':  bool(fc_fallback),
            'photo_url':    str(j.get('player_face_url', '') or ''),
        }

    def generar_dict(self, seleccion: str) -> dict:
        once, ya_titular, ya_claves = self.elegir_titular(seleccion)
        suplentes = self.elegir_suplentes(seleccion, ya_titular, ya_claves)

        titulares_list = []
        for slot in ['LB', 'CB1', 'CB2', 'RB', 'CM1', 'CM2', 'CM3', 'EI', 'DC', 'ED']:
            if slot in once:
                j  = once[slot]
                sc = f'score_{slot}'
                titulares_list.append(
                    self._jugador_a_dict(j, sc, slot, fc_fallback=bool(j.get('_fc_fallback'))))

        suplentes_list = []
        for cfg in self.SUPLENTES_CONFIG:
            sup_slot = cfg['slot']
            if sup_slot in suplentes:
                j, label, ref_slot = suplentes[sup_slot]
                sc = f'score_{ref_slot}'
                suplentes_list.append(
                    self._jugador_a_dict(j, sc, label, fc_fallback=bool(j.get('_fc_fallback'))))

        # Porteros desde df_fc
        portero_t = self.elegir_portero(seleccion)
        portero_s = self.elegir_portero_suplente(
            seleccion, portero_t['name'] if portero_t else '')

        if portero_t:
            titulares_list.insert(0, portero_t)
        if portero_s:
            suplentes_list.insert(0, portero_s)

        def resumen(lst):
            if not lst: return {}
            return {
                'overall_mean':      round(sum(p['overall'] for p in lst) / len(lst), 1),
                'score_mean':        round(sum(p['score']   for p in lst) / len(lst), 1),
                'top5_count':        sum(1 for p in lst if p['top5_league']),
                'fc_fallback_count': sum(1 for p in lst if p['fc_fallback']),
            }

        return {
            'seleccion':         seleccion,
            'titulares':         titulares_list,
            'suplentes':         suplentes_list,
            'resumen_titulares': resumen(titulares_list),
            'resumen_suplentes': resumen(suplentes_list),
        }

    # ── PRINT EN CONSOLA ──────────────────────────────────────────────────────

    def imprimir(self, seleccion: str):
        data = self.generar_dict(seleccion)

        CABECERA  = (f"  {'SLOT':<6} {'JUGADOR':<25} {'POS':<20} {'OVR':<5} {'SCORE':<8} "
                     f"{'G 25/26':<8} {'A 25/26':<8} {'G 24/25':<8} {'A 24/25':<8} "
                     f"{'MIN 24/25':<10} {'LIGA':<20} {'SRC'}")
        SEPARADOR = f"  {'-'*100}"

        def print_group(titulo, jugadores, resumen):
            print(f"\n{'='*102}")
            print(f"  {titulo}")
            print(f"{'='*102}")
            print(CABECERA)
            print(SEPARADOR)
            for p in jugadores:
                top5 = '*' if p['top5_league'] else ' '
                src  = 'FC' if p['fc_fallback'] else '  '
                print(f"  {p['slot']:<6} {p['name'][:24]:<25} {p['positions'][:18]:<20} "
                      f"{p['overall']:<5} {p['score']:<8.1f} "
                      f"{p['goals_2526']:<8} {p['assists_2526']:<8} "
                      f"{p['goals_2425']:<8} {p['assists_2425']:<8} "
                      f"{p['minutes_2425']:<10} {top5} {p['league']:<18} {src}")
            if resumen:
                print(f"{'='*102}")
                print(f"  Overall: {resumen['overall_mean']}  Score: {resumen['score_mean']}  "
                      f"Top5: {resumen['top5_count']}")

        print_group(f"11 INICIAL - {seleccion.upper()}", data['titulares'], data['resumen_titulares'])
        print_group(f"11 SUPLENTES - {seleccion.upper()}", data['suplentes'], data['resumen_suplentes'])