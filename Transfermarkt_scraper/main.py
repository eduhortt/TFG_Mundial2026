import logging
import pandas as pd
from src.scraper import PageScraper, cache_db
from src.league import Leagues # Tu clase que me acabas de pasar

# Configuración de logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def run_tfg_scraper():
    # 1. Iniciamos el scraper con la nueva lógica de reintentos
    scraper = PageScraper(cache_db)
    
    print("🚀 Iniciando Scraper para el TFG...")
    
    # 2. Instanciamos tu clase Leagues
    # Esto ya dispara internamente parseLeagues() y parseLeague()
    # Gracias a los reintentos del scraper, ahora fallará mucho menos
    try:
        coleccion_ligas = Leagues(scraper)
        
        # 3. Exportamos los datos (Tu método export ya crea el CSV)
        coleccion_ligas.export("data/scoring_performance.csv")
        
    except Exception as e:
        print(f"❌ Error crítico durante la ejecución: {e}")

    # 4. GENERACIÓN DEL INFORME DE ERRORES
    # Vamos a leer la caché para ver qué URLs terminaron en error (None)
    print("\n" + "="*40)
    print("📊 RECUENTO DE EQUIPOS Y ERRORES")
    print("="*40)
    
    equipos_exitos = 0
    equipos_fallidos = []

    # Recorremos lo que se procesó en esta sesión
    for league in coleccion_ligas.leaguesData:
        # Si la liga no tiene equiposData, es que la liga falló
        if not league.teamsData:
            equipos_fallidos.append(f"LIGA COMPLETA: {league.leagueName}")
            continue
            
        for team in league.teamsData:
            # Si el equipo no tiene jugadores, lo contamos como error
            if not team.playersData:
                equipos_fallidos.append(f"{league.leagueName} - {team.url}")
            else:
                equipos_exitos += 1

    print(f"✅ Equipos procesados con éxito: {equipos_exitos}")
    
    if equipos_fallidos:
        print(f"❌ Equipos/Ligas con errores: {len(equipos_fallidos)}")
        # Guardamos la lista de fallos en un txt para que la revises
        with open("data/equipos_con_error.txt", "w", encoding="utf-8") as f:
            for fallo in equipos_fallidos:
                f.write(f"{fallo}\n")
        print("📂 Lista de errores guardada en: data/equipos_con_error.txt")
    else:
        print("🎉 ¡Perfecto! No se detectaron errores en ningún equipo.")

if __name__ == "__main__":
    run_tfg_scraper()