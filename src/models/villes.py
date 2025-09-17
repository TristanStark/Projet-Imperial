from pydantic import BaseModel
from typing import List, Optional

class Quartier(BaseModel):
    nom: str
    description: str

class DirigeantActuel(BaseModel):
    titre: str
    nom: str
    description: str

class MaisonDirigeante(BaseModel):
    nom: str
    description: str
    blason: str
    devise: str

class Dirigeant(BaseModel):
    actuel: DirigeantActuel
    maison_dirigeante: MaisonDirigeante

class MembreGouvernance(BaseModel):
    nom: str
    role: str

class Gouvernance(BaseModel):
    type: str
    membres: List[MembreGouvernance]
    description: str
    nombre_de_sieges: int
    duree_du_mandat: str

class SecteurEconomique(BaseModel):
    nom: str
    description: str

class Economie(BaseModel):
    secteurs: List[SecteurEconomique]

class Faction(BaseModel):
    nom: str
    description: str

class LieuNotable(BaseModel):
    nom: str
    description: str

class City(BaseModel):
    nombre_habitants: int
    city_type: str
    image: str
    nom: str
    surnoms: List[str]
    old_name: str
    description: str
    quartiers: List[Quartier]
    dirigeant: Dirigeant
    gouvernance: Gouvernance
    economie: Economie
    factions: List[Faction]
    lieux_notables: List[LieuNotable]

class Data(BaseModel):
    city: City

class Ville(BaseModel):
    nom: str
    habitants: int
    type: str
    image: str
    data: Data
    def __repr__(self):
        c = self.data.city
        lignes = [
            f" Ville : {self.nom} ({self.type}, {self.habitants:,} habitants)",
            "",
            f" Détails sur {c.nom} ({c.city_type})",
            f"- Ancien nom : {c.old_name}",
            f"- Surnoms : {', '.join(c.surnoms)}",
            f"- Description : {c.description}",
            "",
            f" Dirigeant actuel : {c.dirigeant.actuel.titre} {c.dirigeant.actuel.nom}",
            f"  - Description : {c.dirigeant.actuel.description}",
            f"  - Maison dirigeante : {c.dirigeant.maison_dirigeante.nom}",
            f"    - Devise : {c.dirigeant.maison_dirigeante.devise}",
            f"    - Blason : {c.dirigeant.maison_dirigeante.blason}",
            f"    - Description : {c.dirigeant.maison_dirigeante.description}",
            "",
            f" Gouvernance : {c.gouvernance.type}",
            f"  - Description : {c.gouvernance.description}",
            f"  - Nombre de sièges : {c.gouvernance.nombre_de_sieges}",
            f"  - Durée du mandat : {c.gouvernance.duree_du_mandat}",
            f"  - Membres :"
        ]
        for membre in c.gouvernance.membres:
            lignes.append(f"    - {membre.nom}, {membre.role}")

        lignes.append("")
        lignes.append(" Économie :")
        for secteur in c.economie.secteurs:
            lignes.append(f"  - {secteur.nom} : {secteur.description}")

        lignes.append("")
        lignes.append(" Quartiers :")
        for q in c.quartiers:
            lignes.append(f"  - {q.nom} : {q.description}")

        lignes.append("")
        lignes.append(" Factions :")
        for f in c.factions:
            lignes.append(f"  - {f.nom} : {f.description}")

        lignes.append("")
        lignes.append(" Lieux notables :")
        for l in c.lieux_notables:
            lignes.append(f"  - {l.nom} : {l.description}")

        return "\n<br />".join(lignes)
