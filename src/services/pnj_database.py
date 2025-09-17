from src.utils.logger import log_function_call
from src.services.database_service import db
from src.physiques.stats import PNJStatsPhysique
from src.physiques.adjectifs import AdjectifPhysique
from src.models.pnj import PNJBase


class PNJDatabaseService:
    """Service pour gérer les accès BDD liés aux PNJs."""

    @staticmethod
    @log_function_call
    def insert_pnj(pnj: PNJBase) -> int:
        query = """
        INSERT INTO pnj(nom, prenom, job_id, genre, niveau_de_vie, magie, race_id, age)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """
        genre_int = 1 if pnj.genre == "Homme" else 0
        magie_int = 1 if pnj.magie else 0
        values = (
            pnj.nom, pnj.prenom, pnj.job_id, genre_int,
            pnj.niveau_de_vie, magie_int, pnj.race_id, pnj.age
        )
        db.execute(query, values)
        return db.curseur.lastrowid

    @staticmethod
    @log_function_call
    def insert_adjectifs(adjectifs: list, pnj_id: int):
        AdjectifPhysique.insert(adjectifs, pnj_id)

    @staticmethod
    @log_function_call
    def insert_stats(stats, pnj_id: int):
        stats.pnj_id = pnj_id
        PNJStatsPhysique.insert(stats)

    @staticmethod
    @log_function_call
    def commit():
        db.commit()
