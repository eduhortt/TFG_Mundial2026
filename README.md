# Predicción Mundial de Fútbol 2026

Sistema automático de predicción del Mundial 2026 desarrollado como Trabajo de Fin de Grado en Ingeniería Informática (CUNEF Universidad, 2025-2026).

El sistema combina datos reales de rendimiento de **Transfermarkt** con atributos técnicos de **EA FC 26** para seleccionar automáticamente las mejores plantillas de las 48 selecciones participantes y predecir el resultado del torneo mediante un modelo estadístico de Poisson y simulación Monte Carlo.

---

## Instalación

```bash
pip install pandas numpy requests beautifulsoup4 lz4
```

---

## Uso

### 1. Scraping de Transfermarkt

```bash
cd scraper
python main.py
```

Genera `data/scoring_performance.csv` con el historial de más de 7.985 jugadores.

### 2. Cruce de datos

```bash
cd merge
python merge.py
```

Genera `data/dataset_mundial.csv` cruzando Transfermarkt con EA FC 26.

### 3. Predicción completa

```bash
cd predictor
python main.py
```

Ejecuta el pipeline completo en 4 pasos:
1. Genera las plantillas de las 48 selecciones
2. Descarga las fotografías de los jugadores
3. Ejecuta la predicción determinista y 10.000 simulaciones Monte Carlo
4. Incrusta los datos en `mundial2026.html`

Abre `mundial2026.html` en el navegador para ver los resultados.

---

## Resultados

| Posición | Selección | P. Campeón (MC) |
|----------|-----------|-----------------|
| 1º | España | 21.2% |
| 2º | Francia | 15.2% |
| 3º | Portugal | 14.2% |
| 4º | Inglaterra | 6.6% |
| 5º | Brasil | 6.5% |

---

## Datos necesarios

Los siguientes archivos **no están incluidos** en el repositorio por su tamaño y deben obtenerse por separado:

- `predictor/data/dataset_mundial.csv` → generado por el scraper + merge
- `predictor/data/FC26_20250921.csv` → disponible en [Kaggle](https://www.kaggle.com/datasets/rovnez/fc-26-fifa-26-player-data)
- `predictor/data/results.csv` → disponible en [Kaggle](https://www.kaggle.com/datasets/martj42/international-football-results-from-1872-to-2017)

---

## Tecnologías

- Python 3.12
- pandas, numpy, requests, beautifulsoup4, difflib, sqlite3, lz4
- HTML5, CSS3, JavaScript vanilla

---

## Autor

**Eduardo Hortelano Pérez**  
Trabajo Fin de Grado — Ingeniería Informática  
CUNEF Universidad · 2025-2026  
Director: Jesús Sánchez Allende
