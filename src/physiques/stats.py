from src.services.database_service import db
from dataclasses import dataclass
import random

def generer_nombre_aleatoire() -> int:
    # Générer un nombre pour décider de la distribution
    tirage = random.random()
    
    if tirage < 0.9:  # 90% des cas, entre -3 et +3
        return round(random.uniform(-3, 3) + 10)
    elif tirage < 0.95:  # 5% des cas, entre -5 et -3
        return round(random.uniform(-5, -3) + 10)
    else:  # 5% restant, entre +5 et +8
        return round(random.uniform(5, 8) + 10)


@dataclass
class PNJStats:
    """Les caractéristiques des PNJ"""
    pnj_id: int
    strength: int
    dex: int
    con: int
    wis: int
    intelligence: int
    cha: int

class _PNJStatsAccesseurPhysique:
    def __init__(self) -> None:
        """L'accesseur physique pour les statistiques des pnj"""
        pass

    def generate(self) -> PNJStats:
        """Génère un PNJStats à partir de rien"""
        return PNJStats(0, generer_nombre_aleatoire(), generer_nombre_aleatoire(),
                        generer_nombre_aleatoire(), generer_nombre_aleatoire(),
                        generer_nombre_aleatoire(), generer_nombre_aleatoire())

    def applyModification(self, stats: PNJStats, modif: str) -> PNJStats:
        """Applique les modifications de {modif} (peut venir d'un adjectif ou autre) à stats"""
        r = []
        for character in modif:
            modifier = int(character) - 4
            r.append(modifier)
        newPNJ = PNJStats(stats.pnj_id, stats.strength + r[0],
                          stats.dex + r[1], stats.con + r[2],
                          stats.wis + r[3], stats.intelligence + r[4],
                          stats.cha + r[5])
        return newPNJ
    
    def insert(self, stats: PNJStats) -> None:
        """Insère les stats pour le pnj"""
        requete = f"insert into pnj_stats values({stats.pnj_id}, {stats.strength}, {stats.dex}, {stats.con}, {stats.wis}, {stats.intelligence}, {stats.cha});"
        db.execute(requete)
        
PNJStatsPhysique = _PNJStatsAccesseurPhysique()


