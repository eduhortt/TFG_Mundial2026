import sqlite3
import requests
import logging
from time import sleep, time
from threading import Lock
from bs4 import BeautifulSoup
from lz4.frame import compress, decompress
from config import BASE_URL, DELAY_BETWEEN_QUERIES, USER_AGENT

logger = logging.getLogger(__name__)
cache_db = sqlite3.connect("data/page.db", check_same_thread=False)

class PageScraper:
    def __init__(self, db_conn):
        self.lastQuery = -666
        self.cache_db = db_conn
        self.db_mutex = Lock()
        
        with self.db_mutex, self.cache_db:
            self.cache_db.execute(
                "CREATE TABLE IF NOT EXISTS pages (url text PRIMARY KEY, content blob)"
            )

    def getSoup(self, url, retries=3):
        if not url.startswith("http"):
            url = BASE_URL + (url if url.startswith("/") else "/" + url)
        
        # 1. Intentar Caché
        with self.db_mutex, self.cache_db:
            hit = self.cache_db.execute(
                "SELECT content FROM pages WHERE url = ? LIMIT 1;", (url,)
            ).fetchone()
        
        if hit:
            return BeautifulSoup(decompress(hit[0]), "lxml")
        
        # 2. Petición Externa con Reintentos
        for i in range(retries):
            waiting_time = self.lastQuery + DELAY_BETWEEN_QUERIES - time()
            if waiting_time > 0:
                sleep(waiting_time)
                
            try:
                logger.info(f"Petición externa (Intento {i+1}): {url}")
                # Aumentamos timeout a 30s
                response = requests.get(url, headers={"User-agent": USER_AGENT}, timeout=30)
                response.raise_for_status() 
                
                self.lastQuery = time()
                content = response.content
                
                # Guardar solo si ha funcionado
                with self.db_mutex, self.cache_db:
                    self.cache_db.execute(
                        "INSERT OR IGNORE INTO pages (url, content) VALUES (?, ?)", 
                        (url, compress(content))
                    )
                return BeautifulSoup(content, "lxml")
                
            except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
                logger.warning(f"⚠️ Error {url}: {e}")
                if i < retries - 1:
                    sleep(2 ** (i + 2)) # Espera exponencial: 4s, 8s...
                else:
                    logger.error(f"❌ Fallo definitivo en {url}")
                    return None

    def __call__(self, url):
        return self.getSoup(url)