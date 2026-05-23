import pandas as pd
import unicodedata, re
from difflib import SequenceMatcher
from collections import defaultdict
import os

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_TM   = os.path.join(BASE_DIR, 'data', 'scoring_performance.csv')
FILE_FC   = os.path.join(BASE_DIR, 'data', 'FC26_20250921.csv')
OUT_MERGE = os.path.join(BASE_DIR, 'data', 'dataset_merged_final.csv')
OUT_SIN   = os.path.join(BASE_DIR, 'data', 'sin_match_final.csv')
THRESHOLD = 70

FC_COLS = [
    'short_name', 'long_name', 'player_positions', 'overall', 'potential',
    'value_eur', 'age', 'height_cm', 'weight_kg', 'nationality_id',
    'nationality_name', 'club_name', 'league_name', 'preferred_foot',
    'pace', 'shooting', 'passing', 'dribbling', 'defending', 'physic',
    'attacking_crossing', 'attacking_finishing', 'attacking_heading_accuracy',
    'attacking_short_passing', 'attacking_volleys',
    'skill_dribbling', 'skill_curve', 'skill_fk_accuracy',
    'skill_long_passing', 'skill_ball_control',
    'movement_acceleration', 'movement_sprint_speed', 'movement_agility',
    'movement_reactions', 'movement_balance',
    'power_shot_power', 'power_jumping', 'power_stamina', 'power_strength',
    'power_long_shots',
    'mentality_aggression', 'mentality_interceptions', 'mentality_positioning',
    'mentality_vision', 'mentality_penalties', 'mentality_composure',
    'defending_marking_awareness', 'defending_standing_tackle',
    'defending_sliding_tackle',
    'goalkeeping_diving', 'goalkeeping_handling', 'goalkeeping_kicking',
    'goalkeeping_positioning', 'goalkeeping_reflexes', 'goalkeeping_speed',
    'international_reputation', 'weak_foot', 'skill_moves',
]

CLUB_MAP = {
    'fluminense football club':'fluminense','sport club corinthians paulista':'corinthians',
    'clube atletico mineiro':'atletico mineiro','cr flamengo':'flamengo',
    'botafogo de futebol e regatas':'botafogo','sociedade esportiva palmeiras':'palmeiras',
    'sport club internacional':'internacional','clube de regatas vasco da gama':'vasco da gama',
    'esporte clube bahia':'bahia','esporte clube vitoria':'vitoria',
    'cruzeiro esporte clube':'cruzeiro','gremio foot ball porto alegrense':'gremio',
    'club athletico paranaense':'athletico paranaense',
    'associacao chapecoense de futebol':'chapecoense','clube do remo pa':'remo',
    'mirassol futebol clube sp':'mirassol','coritiba foot ball club':'coritiba',
    'santos fc':'santos','sao paulo futebol clube':'sao paulo',
    'red bull new york':'new york red bulls','zenit st petersburg':'zenit',
    'dynamo moscow':'dynamo moskva','spartak moscow':'spartak moskva',
    'cska moscow':'cska moskva','lokomotiv moscow':'lokomotiv moskva',
    'krylya sovetov samara':'krylia sovetov samara','fc pari nizhniy novgorod':'pari nn',
    'akron tolyatti':'akron','baltika kaliningrad':'baltika','rubin kazan':'rubin kazan',
    'akhmat grozny':'akhmat','fc orenburg':'orenburg','fc rostov':'rostov','fc sochi':'sochi',
    'paok thessaloniki':'paok','ae larisa':'larissa','asteras aktor':'asteras tripolis',
    'atromitos athens':'atromitos','aris thessaloniki':'aris','ofi crete':'ofi',
    'ae kifisia':'kifisia','volos nfc':'volos','ac sparta prague':'sparta prague',
    'sk sigma olomouc':'sigma olomouc','fk mlada boleslav':'mlada boleslav',
    'fk teplice':'teplice','fc banik ostrava':'banik ostrava','fc hradec kralove':'hradec kralove',
    'bohemians prague 1905':'bohemians 1905','fc slovan liberec':'slovan liberec',
    'sk slavia prague':'slavia prague','fc viktoria plzen':'viktoria plzen',
    'fk pardubice':'pardubice','fk jablonec':'jablonec','mfk karvina':'karvina',
    'fk dukla prague':'dukla prague','1fc slovacko':'slovacko',
    'al hilal sfc':'al hilal','al ittihad club':'al ittihad','al nassr fc':'al nassr',
    'al ettifaq fc':'al ettifaq','al taawoun fc':'al taawun','al riyadh sc':'al riyadh',
    'al kholood club':'al kholood','al fayha fc':'al fayha','al fateh sc':'al fateh',
    'al khaleej fc':'al khaleej','al qadsiah fc':'al qadsiah','al shabab fc':'al shabab',
    'al ahli sfc':'al ahli','neom sc':'neom','damac fc':'damac','al hazem sc':'al hazem',
    'al okhdood club':'al okhdood','al najma sc':'al najma',
    'los angeles galaxy':'la galaxy','houston dynamo fc':'houston dynamo',
    'inter miami cf':'inter miami','real salt lake city':'real salt lake',
    'st louis city sc':'st louis city','bayern munich':'fc bayern munchen',
}

def L(t):
    if not isinstance(t,str): return ''
    t=t.lower(); t=unicodedata.normalize('NFD',t)
    t=''.join(c for c in t if unicodedata.category(c)!='Mn')
    return re.sub(r'[^a-z ]','',t).strip()

def tsr(a,b):
    return SequenceMatcher(None,' '.join(sorted(a.split())),' '.join(sorted(b.split()))).ratio()*100

def tset(a,b):
    sa,sb=set(a.split()),set(b.split()); inter=sa&sb
    i=' '.join(sorted(inter))
    return max(tsr(i,' '.join(sorted(sa))),tsr(i,' '.join(sorted(sb))),
               tsr(' '.join(sorted(sa)),' '.join(sorted(sb))))

def partial_contains(short,long_):
    return set(short.split()).issubset(set(long_.split()))

print("Cargando datos...")
try:
    df_tm = pd.read_csv(FILE_TM, sep=';', decimal=',', encoding='utf-8-sig')
except:
    df_tm = pd.read_csv(FILE_TM, sep=';', decimal=',', encoding='latin-1')

df_fc = pd.read_csv(FILE_FC, low_memory=False)
df_tm.columns = df_tm.columns.str.strip().str.lower().str.replace(' ','_')
df_fc.columns = df_fc.columns.str.strip().str.lower().str.replace(' ','_')

print(f"TM:   {len(df_tm)} jugadores")
print(f"FC26: {len(df_fc)} jugadores")

# ── EXCLUIR PORTEROS ANTES DEL MERGE ─────────────────────────────────────────
df_fc = df_fc[~df_fc['player_positions'].str.contains('GK', na=False)].copy().reset_index(drop=True)
print(f"FC26 sin porteros: {len(df_fc)}")

# ── QUEDARSE SOLO CON COLUMNAS RELEVANTES DE FC26 ─────────────────────────────
fc_cols_usar = [c for c in FC_COLS if c in df_fc.columns]
df_fc = df_fc[fc_cols_usar].copy()

# ── PREPARAR CLAVES ───────────────────────────────────────────────────────────
df_tm['_k']  = df_tm['name'].apply(L)
df_fc['_kl'] = df_fc['long_name'].apply(L)
df_fc['_ks'] = df_fc['short_name'].apply(L)
df_fc['_kc'] = df_fc['club_name'].apply(L)

kl_arr = df_fc['_kl'].values
ks_arr = df_fc['_ks'].values
kc_arr = df_fc['_kc'].values

exact_l = {v:i for i,v in enumerate(kl_arr) if v}
exact_s = {v:i for i,v in enumerate(ks_arr) if v}

club_idx = defaultdict(list)
for i,c in enumerate(kc_arr): club_idx[c].append(i)
all_clubs = list(club_idx.keys())

ap_idx = defaultdict(list)
for i,kl in enumerate(kl_arr):
    parts=kl.split()
    if parts:
        ap=parts[-1]; ap_idx[ap].append(i)
        if len(ap)>=4: ap_idx[ap[:4]].append(i)

nm_idx = defaultdict(list)
for i,kl in enumerate(kl_arr):
    if len(kl)>=4: nm_idx[kl[:4]].append(i)

def get_club(raw):
    ck=L(raw)
    if ck in CLUB_MAP and CLUB_MAP[ck] in club_idx: return CLUB_MAP[ck],100
    if ck in club_idx: return ck,100
    best,bs=None,0
    for c in all_clubs:
        s=tset(ck,c)
        if s>bs: bs=s; best=c
    return best,bs

def nombre_score(key,i):
    kl,ks=kl_arr[i],ks_arr[i]
    s1=max(tsr(key,kl),tsr(key,ks))
    s2=max(tset(key,kl),tset(key,ks))
    s3=85 if partial_contains(key,kl) else 0
    return max(s1,s2,s3)

def match(key_tm, club_raw):
    if key_tm in exact_l: return exact_l[key_tm],100
    if key_tm in exact_s: return exact_s[key_tm],100
    club_key,cs=get_club(club_raw)
    bi,bs=None,0
    if cs>=70 and club_key in club_idx:
        for i in club_idx[club_key]:
            s=nombre_score(key_tm,i)
            if s>bs: bs=s; bi=i
        if bi is not None and bs>=THRESHOLD: return bi,bs
    parts=key_tm.split(); ap=parts[-1] if parts else ''
    pref=ap[:4] if len(ap)>=4 else ap
    cands=set(ap_idx.get(ap,[])+ap_idx.get(pref,[]))
    if len(key_tm)>=4: cands.update(nm_idx.get(key_tm[:4],[]))
    for i in cands:
        s=nombre_score(key_tm,i)
        if s>bs: bs=s; bi=i
    if bi is None: return None,0
    if bs>=90: return bi,bs
    if bs>=THRESHOLD:
        club_fc=tset(L(club_raw),kc_arr[bi])
        if club_fc>=55: return bi,bs
        pf=kl_arr[bi].split()
        if len(parts)>=2 and len(pf)>=2 and SequenceMatcher(None,parts[-1],pf[-1]).ratio()>=0.8:
            return bi,bs
    if bs>=85: return bi,bs
    return None,0

print("Procesando merge...")
resultados, sin_match = [], []
for i,(_, row) in enumerate(df_tm.iterrows()):
    if i%1000==0: print(f"  {i}/{len(df_tm)}...")
    key = row['_k']
    if not key: continue
    idx, score = match(key, row.get('current_club',''))
    if idx is not None and score>=THRESHOLD:
        combined = {**row.to_dict(), **df_fc.iloc[idx].to_dict(), 'match_quality': round(score,1)}
        resultados.append(combined)
    else:
        sin_match.append({'name_tm': row['name'], 'club_tm': row.get('current_club',''),
                          'league_tm': row.get('current_league',''), 'score': round(score,1) if score else 0})

print("Guardando...")
DROP = ['_k','_kl','_ks','_kc']
df_final = pd.DataFrame(resultados).fillna(0)
df_final.drop(columns=[c for c in DROP if c in df_final.columns], inplace=True)
df_final.to_csv(OUT_MERGE, sep=';', decimal=',', index=False, encoding='utf-8-sig')
pd.DataFrame(sin_match).to_csv(OUT_SIN, sep=';', index=False, encoding='utf-8-sig')

total = len(df_tm)
print(f"\n{'─'*45}")
print(f"Total TM:           {total}")
print(f"✅ Unidos:          {len(resultados):4d}  ({len(resultados)/total*100:.1f}%)")
print(f"❌ Sin match:       {len(sin_match):4d}  ({len(sin_match)/total*100:.1f}%)")
print(f"Porteros:           {len(df_final[df_final['player_positions'].str.contains('GK',na=False)])}")
print(f"Columnas finales:   {len(df_final.columns)}")
print(f"Match quality avg:  {df_final['match_quality'].mean():.1f}")
print(f"'overall' presente: {'overall' in df_final.columns}")