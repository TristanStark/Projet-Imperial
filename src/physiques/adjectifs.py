from src.services.database_service import db
from dataclasses import dataclass
from numpy.random import choice

@dataclass
class Adjectif:
    nom: str
    id: int
    description: str
    modif: str

@dataclass
class Relation:
    adjectif_a: Adjectif
    est: int
    adjectif_b: Adjectif

class _AdjectifPhysique:
    def __init__(self) -> None:
        """Accesseur physique pour les adjectifs"""
        self.adjectifs = self.getListAdjectifs()

    def getListAdjectifs(self) -> list:
        """Renvoie la liste de tous les adjectifs"""
        adj = []
        requete = "select * from adjectifs;"
        results = db.execute(requete)
        for result in results:
            adj.append(Adjectif(result[0], result[1], result[2], result[3]))
        return adj
    
    def getRandomAdjectif(self) -> Adjectif:
        """Renvoie un adjectif aléatoire"""
        return choice(self.adjectifs)
    
    def insertAdjectif(self, adj: Adjectif) -> int:
        """Insère un adjectif et renvoie son id"""
        requete = f"insert into adjectifs(nom, description, modif) values('{adj.nom}', '{adj.description}', '{adj.modif}');"
        db.execute(requete)
        db.commit()
        return db.curseur.lastrowid
    
    def getAdjectif(self, adj_name: str) -> Adjectif:
        """Récupère l'adjectif qui a pour nom adj_name. Si non trouvé renvoie None"""
        requete = f"select * from adjectifs where nom = '{adj_name}';"
        result = db.execute(requete)
        if (len(result) == 0):
            return Adjectif("", -1, "", "")
        result = result[0]
        return Adjectif(result[0], result[1], result[2], result[3])
    
    def getAdjectifWithID(self, id: int) -> Adjectif:
        """Renvoie un adjectif qui a tel id"""
        requete = f"select * from adjectifs where id = {id};"
        result = db.execute(requete)
        if (len(result) == 0):
            return None
        result = result[0]
        return Adjectif(result[0], result[1], result[2], result[3])
    
    def Dedoublonner(self):
        """se dédoublonne soit-même! Incroyable!"""
        liste_name = []
        liste_id = []
        for adjectif in self.adjectifs:
            liste_name.append(adjectif.nom)
            liste_id.append(adjectif.id)
        return liste_name[:40], liste_id[:40]


    def SupprimerDoublons(self, list_id: list[int]) -> None:
        """Supprime les doublons de liste_id"""
        pass

    def getRandomAdjectifWithPrerequisites(self, present: list[int]) -> int:
        """Renvoie un random adjectif qui meet les prerequisites"""
        #Todo: populer les adjectifs relations avec l'inverse 
        liste_incompatibles_with = AdjectifRelationPhysique.getListRelations(present, _AdjectifsRelationPhysique.INCOMPATIBLE_WITH)
        liste_opposed_with = AdjectifRelationPhysique.getListRelations(present, _AdjectifsRelationPhysique.OPPOSED_WITH)
        list_often_paired_with = AdjectifRelationPhysique.getListRelations(present, _AdjectifsRelationPhysique.OFTEN_PAIRED_WITH)

        new_adj = []
        new_adj_weight = []
        for adj in self.adjectifs:
            if (adj.id in liste_incompatibles_with):
                continue
            if (adj.id in liste_opposed_with):
                new_adj.append(adj.id)
                new_adj_weight.append(0.5)
            elif adj.id in list_often_paired_with:
                new_adj.append(adj.id)
                new_adj_weight.append(2)
            else:
                new_adj_weight.append(1)
                new_adj.append(adj.id)

        total_sum = sum(new_adj_weight)
        normalized_array = [x / total_sum for x in new_adj_weight]  # Diviser chaque élément par la somme

        return int(choice(new_adj, 1, p=normalized_array)[0])

    def insert(self, list_adj: list[Adjectif], pnj_id: int) -> None:
        """Insère pour le pnj {pnj_id} les adjectifs de {list_adj}"""
        for adj in list_adj:
            requete = f"insert into pnj_adjectifs(pnj_id, adj_id) values ({pnj_id}, {adj.id});"
            db.execute(requete)


class _AdjectifsRelationPhysique:
    UPGRADE_OF = 4
    OFTEN_PAIRED_WITH = 3
    OPPOSED_WITH = 2
    INCOMPATIBLE_WITH = 1

    def __init__(self) -> None:
        """Accesseur physique pour les relations entre les adjectifs"""
        pass

    def insertRelation(self, rel: Relation) -> None:
        """Insère la relation"""
        requete = f"insert into adjectifs_relations(id_one, id_two, relation) values ({rel.adjectif_a.id}, {rel.adjectif_b.id}, {rel.est});"
        db.execute(requete)
        db.commit()
    
    def insertRelations(self, id_one: int, id_two: int, relation_type: int) -> None:
        """Insère la relation"""
        requete = f"insert into adjectifs_relations(id_one, id_two, relation) values ({id_one}, {id_two}, {relation_type});"
        db.execute(requete)
        db.commit()

    def getListRelation(self, id_one: int, relation: int) -> list[int]:
        """pass"""
        pass

    def getListRelations(self, list_adj: list[int], relation: int) -> list[int]:
        """Renvoie la liste des relations"""
        m = ""
        for p in list_adj:
            m += f" {p},"
        m = m[:-1]
        requete = f"select id_two from adjectifs_relations where id_one in ({m}) and relation = {relation};"
        results = db.execute(requete)
        tab = []
        for result in results:
            tab.append(result[0])
        return tab


AdjectifPhysique = _AdjectifPhysique()
AdjectifRelationPhysique = _AdjectifsRelationPhysique()