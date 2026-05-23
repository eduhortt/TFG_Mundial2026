# ══════════════════════════════════════════════════════════════════════════════
#  CALENDARIO OFICIAL MUNDIAL 2026
#  Extraído del fixture oficial FIFA.
#  Nombres en formato JSON/seleccionador.
# ══════════════════════════════════════════════════════════════════════════════

# ── GRUPOS ────────────────────────────────────────────────────────────────────

GRUPOS = {
    'A': ['Mexico', 'South Africa', 'Korea Republic', 'Czechia'],
    'B': ['Canada', 'Bosnia and Herzegovina', 'Qatar', 'Switzerland'],
    'C': ['Brazil', 'Morocco', 'Haiti', 'Scotland'],
    'D': ['United States', 'Paraguay', 'Australia', 'Türkiye'],
    'E': ['Germany', 'Curacao', "Côte d'Ivoire", 'Ecuador'],
    'F': ['Netherlands', 'Japan', 'Sweden', 'Tunisia'],
    'G': ['Belgium', 'Egypt', 'Iran', 'New Zealand'],
    'H': ['Spain', 'Cabo Verde', 'Saudi Arabia', 'Uruguay'],
    'I': ['France', 'Senegal', 'Iraq', 'Norway'],
    'J': ['Argentina', 'Algeria', 'Austria', 'Jordan'],
    'K': ['Portugal', 'Congo DR', 'Uzbekistan', 'Colombia'],
    'L': ['England', 'Croatia', 'Ghana', 'Panama'],
}

# ── FIXTURES DE GRUPOS (orden oficial FIFA) ───────────────────────────────────
# Cada partido: (local, visitante, fecha, estadio)

FIXTURES_GRUPOS = [
    # Jornada 1
    ('Mexico',                  'South Africa',           'J11-06', 'Estadio Ciudad de México',      'A'),
    ('Korea Republic',          'Czechia',                'J11-06', 'Estadio Guadalajara',            'A'),
    ('Canada',                  'Bosnia and Herzegovina', 'V12-06', 'Estadio Toronto',                'B'),
    ('United States',           'Paraguay',               'V12-06', 'Estadio Los Ángeles',            'D'),
    ('Qatar',                   'Switzerland',            'S13-06', 'Estadio Bahía de San Francisco', 'B'),
    ('Brazil',                  'Morocco',                'S13-06', 'Estadio Nueva York Nueva Jersey','C'),
    ('Haiti',                   'Scotland',               'S13-06', 'Estadio Boston',                 'C'),
    ('Australia',               'Türkiye',                'S13-06', 'Estadio BC Place Vancouver',     'D'),
    ('Germany',                 'Curacao',                'D14-06', 'Estadio Houston',                'E'),
    ('Netherlands',             'Japan',                  'D14-06', 'Estadio Dallas',                 'F'),
    ("Côte d'Ivoire",           'Ecuador',                'D14-06', 'Estadio Filadelfia',             'E'),
    ('Sweden',                  'Tunisia',                'D14-06', 'Estadio Monterrey',              'F'),
    ('Spain',                   'Cabo Verde',             'L15-06', 'Estadio Atlanta',                'H'),
    ('Belgium',                 'Egypt',                  'L15-06', 'Estadio Seattle',                'G'),
    ('Saudi Arabia',            'Uruguay',                'L15-06', 'Estadio Miami',                  'H'),
    ('Iran',                    'New Zealand',            'L15-06', 'Estadio Los Ángeles',            'G'),
    ('France',                  'Senegal',                'Ma16-06','Estadio Nueva York Nueva Jersey','I'),
    ('Iraq',                    'Norway',                 'Ma16-06','Estadio Boston',                 'I'),
    ('Argentina',               'Algeria',                'Ma16-06','Estadio Kansas City',            'J'),
    ('Austria',                 'Jordan',                 'Ma16-06','Estadio Bahía de San Francisco', 'J'),
    ('Portugal',                'Congo DR',               'Mi17-06','Estadio Houston',                'K'),
    ('England',                 'Croatia',                'Mi17-06','Estadio Dallas',                 'L'),
    ('Ghana',                   'Panama',                 'Mi17-06','Estadio Toronto',                'L'),
    ('Uzbekistan',              'Colombia',               'Mi17-06','Estadio Ciudad de México',       'K'),

    # Jornada 2
    ('Czechia',                 'South Africa',           'J18-06', 'Estadio Atlanta',                'A'),
    ('Switzerland',             'Bosnia and Herzegovina', 'J18-06', 'Estadio Los Ángeles',            'B'),
    ('Canada',                  'Qatar',                  'J18-06', 'Estadio BC Place Vancouver',     'B'),
    ('Mexico',                  'Korea Republic',         'J18-06', 'Estadio Guadalajara',            'A'),
    ('United States',           'Australia',              'V19-06', 'Estadio Seattle',                'D'),
    ('Scotland',                'Morocco',                'V19-06', 'Estadio Boston',                 'C'),
    ('Brazil',                  'Haiti',                  'V19-06', 'Estadio Filadelfia',             'C'),
    ('Türkiye',                 'Paraguay',               'V19-06', 'Estadio Bahía de San Francisco', 'D'),
    ('Netherlands',             'Sweden',                 'S20-06', 'Estadio Houston',                'F'),
    ('Germany',                 "Côte d'Ivoire",          'S20-06', 'Estadio Toronto',                'E'),
    ('Ecuador',                 'Curacao',                'S20-06', 'Estadio Kansas City',            'E'),
    ('Tunisia',                 'Japan',                  'S20-06', 'Estadio Monterrey',              'F'),
    ('Spain',                   'Saudi Arabia',           'D21-06', 'Estadio Atlanta',                'H'),
    ('Belgium',                 'Iran',                   'D21-06', 'Estadio Los Ángeles',            'G'),
    ('Uruguay',                 'Cabo Verde',             'D21-06', 'Estadio Miami',                  'H'),
    ('New Zealand',             'Egypt',                  'D21-06', 'Estadio BC Place Vancouver',     'G'),
    ('Argentina',               'Austria',                'L22-06', 'Estadio Dallas',                 'J'),
    ('France',                  'Iraq',                   'L22-06', 'Estadio Filadelfia',             'I'),
    ('Norway',                  'Senegal',                'L22-06', 'Estadio Nueva York Nueva Jersey','I'),
    ('Jordan',                  'Algeria',                'L22-06', 'Estadio Bahía de San Francisco', 'J'),
    ('Portugal',                'Uzbekistan',             'Ma23-06','Estadio Houston',                'K'),
    ('England',                 'Ghana',                  'Ma23-06','Estadio Boston',                 'L'),
    ('Panama',                  'Croatia',                'Ma23-06','Estadio Toronto',                'L'),
    ('Colombia',                'Congo DR',               'Ma23-06','Estadio Guadalajara',            'K'),

    # Jornada 3 (simultáneos por grupo)
    ('Switzerland',             'Canada',                 'Mi24-06','Estadio BC Place Vancouver',     'B'),
    ('Bosnia and Herzegovina',  'Qatar',                  'Mi24-06','Estadio Seattle',                'B'),
    ('Scotland',                'Brazil',                 'Mi24-06','Estadio Miami',                  'C'),
    ('Morocco',                 'Haiti',                  'Mi24-06','Estadio Atlanta',                'C'),
    ('Czechia',                 'Mexico',                 'Mi24-06','Estadio Ciudad de México',       'A'),
    ('South Africa',            'Korea Republic',         'Mi24-06','Estadio Monterrey',              'A'),
    ('Curacao',                 "Côte d'Ivoire",          'J25-06', 'Estadio Filadelfia',             'E'),
    ('Ecuador',                 'Germany',                'J25-06', 'Estadio Nueva York Nueva Jersey','E'),
    ('Japan',                   'Sweden',                 'J25-06', 'Estadio Dallas',                 'F'),
    ('Tunisia',                 'Netherlands',            'J25-06', 'Estadio Kansas City',            'F'),
    ('Türkiye',                 'United States',          'J25-06', 'Estadio Los Ángeles',            'D'),
    ('Paraguay',                'Australia',              'J25-06', 'Estadio Bahía de San Francisco', 'D'),
    ('Norway',                  'France',                 'V26-06', 'Estadio Boston',                 'I'),
    ('Senegal',                 'Iraq',                   'V26-06', 'Estadio Toronto',                'I'),
    ('Cabo Verde',              'Saudi Arabia',           'V26-06', 'Estadio Houston',                'H'),
    ('Uruguay',                 'Spain',                  'V26-06', 'Estadio Guadalajara',            'H'),
    ('Egypt',                   'Iran',                   'V26-06', 'Estadio Seattle',                'G'),
    ('New Zealand',             'Belgium',                'V26-06', 'Estadio BC Place Vancouver',     'G'),
    ('Panama',                  'England',                'S27-06', 'Estadio Nueva York Nueva Jersey','L'),
    ('Croatia',                 'Ghana',                  'S27-06', 'Estadio Filadelfia',             'L'),
    ('Colombia',                'Portugal',               'S27-06', 'Estadio Miami',                  'K'),
    ('Congo DR',                'Uzbekistan',             'S27-06', 'Estadio Atlanta',                'K'),
    ('Algeria',                 'Austria',                'S27-06', 'Estadio Kansas City',            'J'),
    ('Jordan',                  'Argentina',              'S27-06', 'Estadio Dallas',                 'J'),
]

# ── BRACKET ELIMINATORIAS ─────────────────────────────────────────────────────
# Formato: partido_id: (fuente_local, fuente_visitante, fecha, estadio)
# Fuentes: '1A'=primero grupo A, '2B'=segundo grupo B,
#          '3ABCDF'=mejor tercero de esos grupos, 'W73'=ganador P73, 'L101'=perdedor P101

BRACKET_INFO = {
    # 16avos
    73:  ('2A',    '2B',     'D28-06', 'Estadio Los Ángeles'),
    74:  ('1E',    '3ABCDF', 'L29-06', 'Estadio Boston'),
    75:  ('1F',    '2C',     'L29-06', 'Estadio Monterrey'),
    76:  ('1C',    '2F',     'L29-06', 'Estadio Houston'),
    77:  ('1I',    '3CDFGH', 'Ma30-06','Estadio Nueva York Nueva Jersey'),
    78:  ('2E',    '2I',     'Ma30-06','Estadio Dallas'),
    79:  ('1A',    '3CEFHI', 'Ma30-06','Estadio Ciudad de México'),
    80:  ('1L',    '3EHIJK', 'Mi01-07','Estadio Atlanta'),
    81:  ('1D',    '3BEFIJ', 'Mi01-07','Estadio Bahía de San Francisco'),
    82:  ('1G',    '3AEHIJ', 'Mi01-07','Estadio Seattle'),
    83:  ('2K',    '2L',     'J02-07', 'Estadio Toronto'),
    84:  ('1H',    '2J',     'J02-07', 'Estadio Los Ángeles'),
    85:  ('1B',    '3EFGIJ', 'J02-07', 'Estadio BC Place Vancouver'),
    86:  ('1J',    '2H',     'V03-07', 'Estadio Miami'),
    87:  ('1K',    '3DEIJL', 'V03-07', 'Estadio Kansas City'),
    88:  ('2D',    '2G',     'V03-07', 'Estadio Dallas'),
    # Octavos
    89:  ('W74',   'W77',    'S04-07', 'Estadio Filadelfia'),
    90:  ('W73',   'W75',    'S04-07', 'Estadio Houston'),
    91:  ('W76',   'W78',    'D05-07', 'Estadio Nueva York Nueva Jersey'),
    92:  ('W79',   'W80',    'D05-07', 'Estadio Ciudad de México'),
    93:  ('W83',   'W84',    'L06-07', 'Estadio Dallas'),
    94:  ('W81',   'W82',    'L06-07', 'Estadio Seattle'),
    95:  ('W86',   'W88',    'Ma07-07','Estadio Atlanta'),
    96:  ('W85',   'W87',    'Ma07-07','Estadio BC Place Vancouver'),
    # Cuartos
    97:  ('W89',   'W90',    'J09-07', 'Estadio Boston'),
    98:  ('W93',   'W94',    'V10-07', 'Estadio Los Ángeles'),
    99:  ('W91',   'W92',    'S11-07', 'Estadio Miami'),
    100: ('W95',   'W96',    'S11-07', 'Estadio Kansas City'),
    # Semis
    101: ('W97',   'W98',    'Ma14-07','Estadio Dallas'),
    102: ('W99',   'W100',   'Mi15-07','Estadio Atlanta'),
    # 3er puesto
    103: ('L101',  'L102',   'S18-07', 'Estadio Miami'),
    # Final
    104: ('W101',  'W102',   'D19-07', 'Estadio Nueva York Nueva Jersey'),
}

# Solo fuentes para compatibilidad con predictor
BRACKET = {pid: (v[0], v[1]) for pid, v in BRACKET_INFO.items()}