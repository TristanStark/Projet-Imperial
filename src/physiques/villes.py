from src.services.database_service import db
from dataclasses import dataclass
from numpy.random import choice

@dataclass
class Ville:
    """Une ville"""
    name: str
    id: int
    total_population: int
    current_population: int


class _VillePhysique:
    def __init__(self):
        self.villes = []
        self.load()
        self.last_commit = 0


    def load(self):
        requete = "select id, total_population, current_population, name from villes;"
        result = db.execute(requete)
        for res in result:
            id, total_population, current_population, name = res[0], int(res[1]), int(res[2]), res[3]
            place_libre = total_population - current_population
            if place_libre != 0:
                self.villes.append(Ville(name, id, total_population, current_population))

    def update(self, ville: Ville, force_commit = False) -> None:
        """Réalise un update de ladite ville pour son nombre d'habitants"""
        requete = f"update villes set current_population = {ville.current_population} where id = {ville.id};"
        db.execute(requete)
        self.commit(force_commit)


    def commit(self, force=False) -> None:
        """Commit si on a dépassé le temps"""
        self.last_commit += 1
        if (self.last_commit > 100 or force):
            db.commit()
            self.last_commit = 0

    def choose(self) -> Ville:
        """Renvoie une ville au hasard parmi ceux qui ont de la place!"""
        ville = choice(self.villes)
        ville.current_population += 1
        if ville.current_population >= ville.total_population:
            self.villes.remove(ville)
            self.update(ville, True)
        else:
            self.update(ville)


        return ville

    def insert_pnj(self, pnj_id: int, ville: Ville) -> None:
        """Insère une ville"""
        requete = f"insert into adresses(ville_id) values ({ville.id});"
        db.execute(requete)
        adresse_id = db.curseur.lastrowid
        requete = f"insert into pnj_adresses(adress_id, pnj_id) values({adresse_id}, {pnj_id});"
        db.execute(requete)
        self.commit()

VillePhysique = _VillePhysique()