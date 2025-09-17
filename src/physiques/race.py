from src.services.database_service import db
from dataclasses import dataclass
from numpy.random import randint

@dataclass
class Race:
    """une RACE"""
    name: str
    id: int
    proportion: float
    hit_points: int
    lifespan: int
    sexual_majority: int
    mean_number_of_children: int
    legal_majority: int
    percentage_magie: int
    speed: int



class _RacePhysique:
    """Accesseur physique des races"""
    def __init__(self):
        self.races = self.getListRaces()
        self.races_names = ", ".join([race.name for race in self.races])
        self.total = 0
        for race in self.races:
            self.total += race.proportion * 100

    def getListRaces(self) -> list:
        """Renvoie la liste de toutes les races (objets races)"""
        requete = "select * from people_race_descriptions;"
        result = db.execute(requete)
        tab = []
        for res in result:
            tab.append(Race(res[0], res[1], res[2], res[3], res[4], res[5], res[6], res[7], res[8], res[9]))

        return tab
    
    def getSpecificRace(self, race_id: int) -> Race:
        """Renvoie la race concernée"""
        for race in self.races:
            if race.id == race_id:
                return race
        return None
    
    def getSpecificRaceByName(self, name: str) -> Race:
        """Renvoie la race concernée ou une aléatoier si non trouvée"""
        for race in self.races:
            if race.name == name:
                return race
        return self.getRandomRace()

    def getRandomRace(self) -> Race:
        """Renvoie une race aléatoire suivant les proportions"""
        result = randint(0, self.total)
        total = 0
        for race in self.races:
            total += race.proportion * 100
            if result < total:
                return race
        return None


RacePhysique = _RacePhysique()