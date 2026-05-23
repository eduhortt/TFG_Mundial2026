import re
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import MAX_WORKERS
from src.player import PlayerProfile

# Configuración del logger
logger = logging.getLogger(__name__)

# Patrón para identificar si un jugador es portero (para saltárselos si solo buscas goleadores)
PATTERN_PLAYER_POS = re.compile(r"zentriert rueckennummer")

class Team:
    def __init__(self, url, league_name, scraper):
        self.url = url
        self.leagueName = league_name
        self.scraper = scraper
        self.playersData = []
        self.parseTeam()

    def parseTeam(self):
        """
        Extrae los perfiles de todos los jugadores de campo del equipo usando multithreading.
        """
        try:
            team_soup = self.scraper(self.url)
            player_table = team_soup.find("table", class_="items")
            
            if not player_table:
                logger.warning(f"No se encontró tabla de jugadores en {self.url}")
                return

            # Extraer todos los contenedores de jugadores
            # TM suele repetir el nombre en dos celdas, seleccionamos saltando de dos en dos
            player_cells = player_table.find_all("td", class_="hauptlink")[::2]
            
            # Identificar posiciones para filtrar porteros
            # Buscamos en el div que contiene la posición (clase 'zentriert rueckennummer')
            position_tags = player_table.find_all("td", class_=PATTERN_PLAYER_POS)
            
            # Verificación de seguridad
            if len(position_tags) != len(player_cells):
                # A veces la estructura varía ligeramente, intentamos procesar de todos modos
                logger.debug(f"Desajuste de etiquetas en {self.url}. Procesando con precaución.")
            
            # Crear lista de tuplas (nombre, url) filtrando porteros
            players_to_process = {}
            for i, cell in enumerate(player_cells):
                try:
                    is_goalkeeper = "goalkeeper" in position_tags[i].get("title", "").lower()
                    if not is_goalkeeper:
                        link = cell.find("a")
                        if link:
                            players_to_process[link.text.strip()] = link["href"]
                except IndexError:
                    continue

            # --- PARALELIZACIÓN CON THREADS ---
            def instantiate_player(p_name, p_url):
                """Función auxiliar para ejecutar en hilos"""
                try:
                    return PlayerProfile(p_name, p_url, self.scraper)
                except Exception as exc:
                    logger.error(f"Error procesando a {p_name}: {exc}")
                    return None

            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                # Lanzar todas las peticiones a la vez
                future_to_player = {
                    executor.submit(instantiate_player, name, url): name 
                    for name, url in players_to_process.items()
                }
                
                # Recoger los resultados a medida que terminan
                for future in as_completed(future_to_player):
                    player_instance = future.result()
                    if player_instance:
                        # Inyectar la liga actual en los datos del jugador
                        player_instance.playerData["current league"] = self.leagueName
                        self.playersData.append(player_instance)

        except Exception as e:
            logger.error(f"Error general en el equipo {self.url}: {e}")