import re
import logging
import pandas as pd
from collections import namedtuple
from config import CURRENT_YEAR, N_SEASON_HISTORY

# Configuración del logger para este módulo
logger = logging.getLogger(__name__)

# Definición de la estructura para filas de rendimiento
perfRow = namedtuple("PerformanceRow", ["year", "games_played", "goals_scored", "assists", "minutes_played"])

# Patrones Regex para la extracción
PATTERN_PLAYER_ATTRIBUTE = re.compile(r"info-table__content")

class PlayerProfile:
    def __init__(self, playerName, playerUrl, scraper):
        self.playerUrl = playerUrl
        # Generar URL de estadísticas detalladas a partir del perfil
        self.urlPerfPage = playerUrl.replace("profil", "leistungsdatendetails")
        self.scraper = scraper
        self.playerName = playerName
        self.playerData = {}
        self.parsePlayer()

    def parsePlayer(self):
        # 1. Scraping de la página de perfil (Atributos físicos/personales)
        soup = self.scraper(self.playerUrl)
        
        playerAttributes = {}
        playerAttributes["name"] = self.playerName
        
        # Atributos de interés
        StoredAttributes = {"Age:", "Height:", "Nationality:", "Position:", "Foot:", "Current club:"}
        
        entries = soup.find_all("span", class_=PATTERN_PLAYER_ATTRIBUTE)
        
        # Recorrer etiquetas span de dos en dos (llave: valor)
        for key_tag, val_tag in zip(entries[::2], entries[1::2]):
            key = key_tag.text.strip()
            val = val_tag.text.strip()
            if key in StoredAttributes:
                # Guardar como 'age', 'height', etc.
                playerAttributes[key[:-1].lower()] = val.strip()

        # Limpieza de datos (Data Cleaning)
        if "height" in playerAttributes:
            try:
                # Normalizar formato de altura (1,85m -> 185)
                clean_height = playerAttributes["height"].replace("\xa0", " ")
                match = re.search(r"(\d),(\d+)", clean_height)
                if match:
                    meter, centimeters = match.groups()
                    playerAttributes["height"] = int(meter) * 100 + int(centimeters)
            except Exception:
                playerAttributes["height"] = None

        if "nationality" in playerAttributes:
            playerAttributes["nationality"] = playerAttributes["nationality"].replace("\xa0", " ")
            
        if "position" in playerAttributes:
            # Quedarse con la posición principal tras el guión
            playerAttributes["position"] = playerAttributes["position"].split("-")[-1].lstrip()
            
        if "age" in playerAttributes:
            try:
                playerAttributes["age"] = int(playerAttributes["age"])
            except ValueError:
                playerAttributes["age"] = None

        # 2. Scraping de la página de rendimiento (Estadísticas históricas)
        soup = self.scraper(self.urlPerfPage)
        performanceColumns = ("season", "games", "goals", "assists", "minutes")
        performanceRows = []

        try:
            table_container = soup.find("div", class_="responsive-table")
            if table_container and table_container.find("tbody"):
                for row in table_container.find("tbody").find_all("tr"):
                    p_row = self.parsePerformanceRow(row)
                    
                    # Control de profundidad histórica (N_SEASON_HISTORY)
                    # p_row.year tiene formato "23/24"
                    try:
                        start_year = int(p_row.year.split('/')[0])
                        if start_year < (CURRENT_YEAR - N_SEASON_HISTORY):
                            break
                    except (ValueError, IndexError):
                        pass
                        
                    performanceRows.append(p_row)

            # Convertir a DataFrame para agrupar y aplanar
            if performanceRows:
                performanceDF = pd.DataFrame(data=performanceRows, columns=performanceColumns).groupby("season", sort=False).sum()
                # Aplanar el DataFrame: "23/24 goals": 15, "23/24 assists": 5...
                performanceSeries = {
                    f"{season} {col}": performanceDF.at[season, col] 
                    for season in performanceDF.index 
                    for col in performanceDF.columns
                }
            else:
                performanceSeries = {}

        except Exception as e:
            logger.error(f"Error parseando rendimiento de {self.playerName}: {e}")
            performanceSeries = {}

        # Unir diccionarios (Sintaxis Python 3.9+)
        self.playerData = playerAttributes | performanceSeries
        logger.info(f"\tPlayer: {self.playerName} processed")

    @staticmethod
    def parsePerformanceRow(row):
        cells = row.find_all("td")
        # Limpiar texto de cada celda
        cells = list(map(lambda x: x.text.replace("\xa0", " ").strip(), cells))
        
        # Estructura típica de TM: Temporada, Competición, Club, ..., Goles, Asistencias, etc.
        # Ajustamos los índices según la estructura de la tabla de 'leistungsdatendetails'
        year, *_, games_played, goals_scored, assists, _, minutes_played = cells
        
        # Formatear el año
        if re.match(r"\d{4}", year):
            short_year = int(year[2:])
            year = f"{short_year-1:02d}/{short_year:02d}"
        
        # Convertir a enteros tratando el guión "-" de TM como cero
        def to_int(val):
            if val == "-" or not val:
                return 0
            # Eliminar puntos de miles y el símbolo de minutos '
            clean_val = val.replace(".", "").replace("'", "").strip()
            return int(clean_val)

        return perfRow(
            year, 
            to_int(games_played), 
            to_int(goals_scored), 
            to_int(assists), 
            to_int(minutes_played)
        )