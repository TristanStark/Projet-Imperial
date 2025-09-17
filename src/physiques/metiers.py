from src.services.database_service import db
from dataclasses import dataclass
from numpy.random import randint, choice
from src.physiques.stats import PNJStats
from src.utils.logger import log_function_call

@dataclass
class Metier:
    """Un Métier"""
    name: str
    id: int
    remuneration: float
    rarete: float
    magie: bool
    quota_id: int

@dataclass
class MetierRequirement:
    """Les pré-requis pour postuler à ce job!"""
    job_id: int
    skill_required: str
    skill_level: str
    carac_required: str
    carac_level: int
    adj_prefered: int
    adj_incompatible: int

class _MetierPhysique:
    """L'accesseur physique pour tout ce qui est métier"""
    def __init__(self) -> None:
        self.metiers = self.getListMetiers()

        self.metier_no_magie = []
        self.metier_magie = []
        self.metiers_quota = {}

        # Les coûts pour les randoms
        self.total_random_cost = 0
        self.random_magie_cost = 0
        self.random_no_magie_cost = 0
        self.metiers_names = ", ".join([metier.name for metier in self.metiers])

        for metier in self.metiers:
            self.total_random_cost += metier.rarete * 100
            if metier.magie:
                self.random_magie_cost += metier.rarete * 100
                self.metier_magie.append(metier)
            else:
                self.random_no_magie_cost += metier.rarete * 100
                self.metier_no_magie.append(metier)
        
        self.loadQuotas()


    def loadQuotas(self) -> None:
        """Load tous les quotas"""
        liste_villes_id_requete = f"select id from villes;"
        r = db.execute(liste_villes_id_requete)
        for res in r:
            requete = f"select group_id, percentage from jobs_quotas where ville_id = {res[0]};"
            results_requete = db.execute(requete)
            d = {}
            for quota in results_requete:
                d[quota[0]] = quota[1]
            self.metiers_quota[res[0]] = d   

    def getListMetiers(self) -> list[Metier]:
        """Renvoie la liste de tous les métiers"""
        result = []
        requete = "select * from jobs;"
        r = db.execute(requete)
        for res in r:
            result.append(Metier(res[0], res[1], res[2], res[3], res[4] == 1, res[5]))
        return result
    

    @log_function_call
    def _getRandom(self, cost: float, liste: list) -> Metier:
        """Renvoie un métier aléatoire parmi la liste et le coût"""
        result = randint(0, cost)
        total = 0
        for metier in liste:
            total += metier.rarete * 100
            if result < total:
                return metier
        return None
    
    @log_function_call
    def getMetier(self, id: int) -> Metier:
        """Renvoie un métier à partir de son id"""
        for metier in self.metiers:
            if metier.id == id:
                return metier
        return None

    @log_function_call
    def getSpecificMetierByName(self, name: str) -> Metier:
        """Renvoie un métier à partir de son nom"""
        for metier in self.metiers:
            if metier.name == name:
                return metier
        return self.getRandomMetier()

    @log_function_call
    def getRandomMetierNoMagie(self) -> Metier:
        """Renvoie un métier aléatoire parmi ceux ne requérant pas la magie pour opérer"""
        return self._getRandom(self.random_no_magie_cost, self.metier_no_magie)
    
    @log_function_call
    def getRandomMetierMagie(self) -> Metier:
        """Renvoie un métier aléatoire nécessitant d'être magicien"""
        return self._getRandom(self.random_magie_cost, self.metier_magie)
    
    @log_function_call
    def getRandomMetier(self) -> Metier:
        """Renvoie un métier aléatoire, magie ou pas"""
        return self._getRandom(self.total_random_cost, self.metiers)
    
    @log_function_call
    def insertMetier(self, metier: Metier) -> int:
        """Insère un métier"""
        requete = f"insert into jobs(name, remuneration, rarete, magie) values('{metier.name}', {metier.remuneration}, {metier.rarete}, {1 if metier.magie else 0});"
        db.execute(requete)
        return db.curseur.lastrowid
    
    @log_function_call
    def commit(self) -> None:
        """Commit la database"""
        db.commit()

    def getQuotas(self, ville_id: int) -> dict:
        """Renvoie le dictionnaire des multiplicateurs de quota par villes"""
        return self.metiers_quota.get(ville_id, {})

    def getWeightForJobAndCity(self, metier: Metier, ville_id: int) -> float:
        """Renvoie le multiplicateur de chance de ce métier pour cette ville"""
        jobs_quota = self.getQuotas(ville_id)
        return jobs_quota.get(metier.quota_id, 1)
        

    @log_function_call
    def getMetierWithRequirement(self, magie: bool, stats: PNJStats, adjectifs_id: list[int], ville_id) -> Metier:
        """Si t'as les prérequis, on t'envois un métier mon frère"""
        liste_metiers = self.metier_magie if magie else self.metier_no_magie
        new_list = []
        new_weight = []
        for metier in liste_metiers:
            job_requirement = MetierRequirementPhysique.getRequirementOfJob(metier)
            weight = MetierRequirementPhysique.checkIfPossible(job_requirement, stats, adjectifs_id)
            city_weight = self.getWeightForJobAndCity(metier, ville_id)
            if (weight != -1 and city_weight != 0):
                new_list.append(metier)
                new_weight.append(weight * city_weight)
        total_sum = sum(new_weight)
        normalized_array = [x / total_sum for x in new_weight]  # Diviser chaque élément par la somme

        return choice(new_list, 1, p=normalized_array)

class _MetierRequirementPhysique:
    def __init__(self) -> None:
        """L'accesseur physique des pré-requis des jobs!"""
        self.memoize = {}

    @log_function_call
    def insert(self, requirement: MetierRequirement) -> None:
        """Insère un enregistrement"""
        requete = f"insert into jobs_requirement values ({requirement.job_id}, '{requirement.skill_required}', '{requirement.skill_level}', '{requirement.carac_required}', {requirement.carac_level}, {requirement.adj_prefered}, {requirement.adj_incompatible});"
        db.execute(requete)
        db.commit()

    @log_function_call
    def getRequirementOfJob(self, job: Metier) -> MetierRequirement:
        """Récupère les requirement pour le job"""
        self.memoize.setdefault(job.id, {})
        if "requirement" not in self.memoize[job.id]:
            requete = f"select * from jobs_requirement where job_id = {job.id};"
            results = db.execute(requete)
            result = results[0]
            self.memoize[job.id]["requirement"] = MetierRequirement(result[0], result[1], result[2], result[3], result[4], result[5], result[6])
        return self.memoize[job.id]["requirement"]

    @log_function_call
    def checkIfPossible(self, requirement: MetierRequirement, stats: PNJStats, adjectifs: list[int]) -> float:
        """Détermine si c'est possible tel requirement avec tels stats et tel adjectifs et renvoie le poids"""
        #Step 1: on check les adj
        if requirement.adj_incompatible in adjectifs:
            return -1
        
        if (requirement.carac_required == "Strength") and ((requirement.carac_level * 2) + 10) < stats.strength:
            return -1
        if (requirement.carac_required == "Dexterity") and ((requirement.carac_level * 2) + 10) < stats.dex:
            return -1
        if (requirement.carac_required == "Constitution") and ((requirement.carac_level * 2) + 10) < stats.con:
            return -1
        if (requirement.carac_required == "Wisdom") and ((requirement.carac_level * 2) + 10) < stats.wis:
            return -1
        if (requirement.carac_required == "Intelligence") and ((requirement.carac_level * 2) + 10) < stats.intelligence:
            return -1
        if (requirement.carac_required == "Charisma") and ((requirement.carac_level * 2) + 10) < stats.cha:
            return -1
        
        if requirement.adj_prefered in adjectifs:
            return 2
        
        return 1


MetierPhysique = _MetierPhysique()
MetierRequirementPhysique = _MetierRequirementPhysique()