from typing import Optional
from numpy.random import randint, choice
from src.utils.name import MarkovChain
from src.models.pnj import PNJBase, PNJComplet, PNJQuery
from src.physiques.race import RacePhysique
from src.physiques.adjectifs import AdjectifPhysique
from src.physiques.stats import PNJStatsPhysique
from src.physiques.metiers import MetierPhysique, Metier
from src.services.pnj_database import PNJDatabaseService
from src.physiques.villes import Ville, VillePhysique


def get_custom_or_generate(custom_request, attr, generator, empty_value=""):
    value = getattr(custom_request, attr, None) if custom_request else None
    if value not in (None, empty_value):
        return value
    return generator()


class PNJFactory:
    def __init__(self):
        self.markov = MarkovChain()
        self.loaded = False

    def _load_once(self):
        if not self.loaded:
            self.markov.load()
            self.loaded = True

    def _generate_nom(self):
        return self.markov.generate()

    def _generate_prenom(self):
        return self.markov.generate()

    def _generate_genre(self):
        return choice(["Homme", "Femme"])

    def _generate_race(self):
        return RacePhysique.getRandomRace()

    def _generate_magie(self, pourcentage: int) -> bool:
        return randint(0, 100) < pourcentage

    def _generate_age(self, race) -> int:
        if randint(0, 100) < 20:
            #print("PNJFactory: Génération d'un PNJ jeune")
            return randint(1, race.legal_majority)
        return randint(race.legal_majority, race.lifespan)

    def _generate_adjectifs(self):
        nb_adj = randint(1, 5)
        list_adj = [AdjectifPhysique.getRandomAdjectif().id]
        for _ in range(nb_adj):
            a = AdjectifPhysique.getRandomAdjectifWithPrerequisites(list_adj)
            if a:
                list_adj.append(a)
            else:
                break
        return [AdjectifPhysique.getAdjectifWithID(i) for i in list_adj]

    def _generate_stats(self, adj):
        stats = PNJStatsPhysique.generate()
        for a in adj:
            stats = PNJStatsPhysique.applyModification(stats, a.modif)
        return stats

    def _generate_metier(self, magie, stats, adj, ville_id):
        list_id = [a.id for a in adj]
        metiers = MetierPhysique.getMetierWithRequirement(magie, stats, list_id, ville_id)
        return metiers[0]

    def _generate_niveau_de_vie(self, metier, stats):
        bonus = randint(-5, 5)
        for seuil, gain in [(14, 2), (16, 5), (18, 10)]:
            if stats.intelligence > seuil:
                bonus += gain
            if stats.cha > seuil:
                bonus += gain
        return metier.remuneration + bonus

    def _generate_level(self):
        table = [
            (19, 20, 0.000001),
            (16, 18, 0.000009),
            (14, 15, 0.00009),
            (10, 13, 0.0009),
            (8, 9, 0.014),
            (3, 5, 0.7),
            (1, 7, 0.985)
        ]
        tirage = randint(0, 1000000) / 1000000
        cumul = 0
        for mini, maxi, proba in table:
            cumul += proba
            if tirage <= cumul:
                return randint(mini, maxi)
        return 1
    
    def _generate_ville(self) -> Ville:
        """Récupère l'une des ville existante"""
        return VillePhysique.choose()
        

    def generate(self, _metier: Optional[Metier] = None, custom: Optional[PNJQuery] = None) -> PNJComplet:
        self._load_once()

        nom = get_custom_or_generate(custom, "nom", self._generate_nom)
        prenom = get_custom_or_generate(custom, "prenom", self._generate_prenom)
        genre = get_custom_or_generate(custom, "genre", self._generate_genre)
        race_name = get_custom_or_generate(custom, "race", self._generate_race)
        race = RacePhysique.getSpecificRaceByName(race_name) if isinstance(race_name, str) else race_name
        age = custom.age if custom and custom.age != 0 else self._generate_age(race)
        magie = custom.magie if custom else self._generate_magie(race.percentage_magie)

        adjectifs = self._generate_adjectifs()
        stats = self._generate_stats(adjectifs)
        ville = self._generate_ville()

        if _metier:
            metier = _metier
        elif custom and custom.job_name:
            metier = MetierPhysique.getSpecificMetierByName(custom.job_name)
        else:
            metier = self._generate_metier(magie, stats, adjectifs, ville.id)

        niveau_de_vie = self._generate_niveau_de_vie(metier, stats)
        level = self._generate_level()

        base = PNJBase(nom, prenom, -1, metier.id, genre, niveau_de_vie, magie, race.id, age)

        pnj_id = PNJDatabaseService.insert_pnj(base)
        base.id = pnj_id
        PNJDatabaseService.insert_adjectifs(adjectifs, pnj_id)
        PNJDatabaseService.insert_stats(stats, pnj_id)
        PNJDatabaseService.commit()
        VillePhysique.insert_pnj(pnj_id, ville)

        return PNJComplet(base, level, stats, race, metier, adjectifs)
