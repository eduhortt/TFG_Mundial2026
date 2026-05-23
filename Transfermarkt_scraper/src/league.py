import re
import logging
import pandas as pd
from tqdm import tqdm
from config import N_LEAGUES, LEAGUES_URL
from src.team import Team

# Configuración del logger
logger = logging.getLogger(__name__)

class Leagues:
    def __init__(self, scraper):
        self.scraper = scraper
        self.leaguesData = []
        self.failedTeams=[]
        self.parseLeagues()

    def parseLeagues(self):
        """
        Obtiene la lista de ligas principales y añade ligas extra internacionales.
        """
        logger.info("Iniciando el parseo de ligas...")
        leagues_soup = self.scraper.getSoup(LEAGUES_URL)
        
        try:
            league_table = leagues_soup.find("table", class_="items").find("tbody")
            league_links = league_table.find_all("a", href=re.compile(r"wettbewerb/[A-Z]{1,2}1"), title=re.compile(r"\w"))
            
            # 1. Obtener las ligas automáticas de Europa
            league_links = league_links[:N_LEAGUES]
            league_url_dic = {league.text: league["href"] for league in league_links}
            
            # --- SECCIÓN: INYECTAR LIGAS EXTRA (MLS, ARABIA, BRASIL) ---
            # Añadimos manualmente las ligas que no están en la tabla de Europa
            extra_leagues = {
                "Major League Soccer": "/major-league-soccer/startseite/wettbewerb/MLS1",
                "Saudi Pro League": "/saudi-pro-league/startseite/wettbewerb/SA1",
                "Campeonato Brasileiro Série A": "/campeonato-brasileiro-serie-a/startseite/wettbewerb/BRA1"
            }
            
            # Las unimos al diccionario original
            league_url_dic.update(extra_leagues)
            # ----------------------------------------------------------
            
            logger.info(f"Ligas totales a procesar: {list(league_url_dic.keys())}")
            
            # Barra de progreso principal para las ligas
            for league_name, league_url in (pbar := tqdm(league_url_dic.items())):
                pbar.set_description(f"Procesando Liga: {league_name:<20}")
                self.leaguesData.append(League(league_name, league_url, self.scraper))
                
        except Exception as e:
            logger.error(f"Error crítico al obtener la lista de ligas: {e}")

            
    def export(self, filename="data/scoring_performance.csv"):
        """
        Recopila todos los datos de los jugadores de todas las ligas y equipos y los exporta a CSV.
        """
        logger.info(f"Exportando datos a {filename}...")
        
        player_profiles = []
        for league in self.leaguesData:
            for team in league.teamsData:
                for player in team.playersData:
                    player_profiles.append(player.playerData)
        
        if not player_profiles:
            logger.warning("No se han encontrado perfiles de jugadores para exportar.")
            return

        df = pd.DataFrame(player_profiles)
        
        # Ordenar columnas alfabéticamente de forma inversa para consistencia

        df = pd.DataFrame(player_profiles)
        
        # 1. Rellenar celdas vacías con 0 (lo que pediste al principio)
        df = df.fillna(0)
        
        # 2. Ordenar columnas y filas
        df = df[sorted(df.columns, reverse=True)]
        goal_columns = [col for col in df.columns if col.endswith("goals")]
        if goal_columns:
            total_goals = df[goal_columns].sum(axis=1)
            df = df.iloc[total_goals.sort_values(ascending=False).index]
        
        # 3. GUARDADO CORRECTO (Usa utf-8-sig y separador ;)
        # Esto evitará que Morata salga con la A rara
        df.to_csv(filename, index=False, encoding='utf-8-sig', sep=';', decimal=',')
        if self.failedTeams:
            failed_df = pd.DataFrame(self.failedTeams)
            failed_filename = "data/equipos_fallidos_scraper.csv"
            failed_df.to_csv(failed_filename, index=False, sep=';', encoding='utf-8-sig')
            logger.info(f"Reporte de errores guardado en {failed_filename}")
        
        logger.info(f"Exportación completada. Se han guardado {len(df)} jugadores.")


class League:
    def __init__(self, name, url, scraper):
        self.leagueName = name
        self.scraper = scraper
        self.teamsData = []
        # tm(url) es un atajo si el scraper implementa __call__
        self.leagueSoup = scraper(url)
        self.parseLeague()

    def parseLeague(self):
        """
        Extrae todos los equipos de la liga actual.
        """
        try:
            teams_table = self.leagueSoup.find("table", class_="items")
            if not teams_table:
                logger.warning(f"No se encontró tabla de equipos para la liga {self.leagueName}")
                return

            # TM usa celdas 'hauptlink no-border-links' para los nombres de equipos
            team_cells = teams_table.find_all("td", class_="hauptlink no-border-links")
            team_links = [cell.find("a") for cell in team_cells if cell.find("a")]
            
            # Diccionario de nombre_equipo: url
            team_urls = {link.text.strip(): link["href"] for link in team_links}
            
            # Barra de progreso secundaria para los equipos (leave=False para no ensuciar la consola)
            for team_name, team_url in (pbar := tqdm(team_urls.items(), leave=False)):
                pbar.set_description(f"  Equipo: {team_name:<25}")
                self.teamsData.append(Team(team_url, self.leagueName, self.scraper))
                
        except Exception as e:
            logger.error(f"Error parseando la liga {self.leagueName}: {e}")