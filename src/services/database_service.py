import sqlite3
from sqlite3 import Connection, Cursor
from typing import Optional, Union
from src.utils.logger import logger

DB_PATH = "./data/db/database_test.db"

class _DataBase:
    def __init__(self):
        self.connection: Connection = sqlite3.connect(DB_PATH)
        self.connection.row_factory = sqlite3.Row
        self.curseur: Cursor = self.connection.cursor()
        logger.debug(f"Connexion ouverte à la base de données : {DB_PATH}")

    def execute(self, request: str, params: Optional[Union[tuple, dict]] = None) -> list:
        try:
            logger.debug(f"Requête SQL : {request} | Params: {params}")
            if params:
                res = self.curseur.execute(request, params)
            else:
                res = self.curseur.execute(request)
            return res.fetchall()
        except Exception as e:
            logger.error(f"ERREUR REQUETE SQL: {request}\nException: {e}")
            return []

    def commit(self) -> None:
        logger.debug("Commit de la transaction")
        self.connection.commit()

    def close(self) -> None:
        logger.debug("Fermeture de la base de données")
        self.connection.close()


db = _DataBase()
