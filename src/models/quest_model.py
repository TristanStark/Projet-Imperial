from typing import List, Literal, Optional
from pydantic import BaseModel


class PNJBrief(BaseModel):
    nom: str
    genre: Literal["Homme", "Femme"]
    race: str
    job_name: str
    age: int
    magie: bool
    role: Optional[str] 
    faction: Optional[str]


class EnnemiBrief(BaseModel):
    nom: str
    type: Literal["monstre", "humanoïde", "bête", "créature magique"]
    description: Optional[str]
    niveau_estime: Optional[int]
    localisation: Optional[str]
    faction: Optional[str] 

class LocationBrief(BaseModel):
    nom: str
    type: Literal["ville", "taverne", "ruines", "forêt", "abbaye", "donjon", "campement", "village", "inconnu"]
    description: str
    ambiance: Optional[str]
    danger: Optional[str]
    pnj_associes: List[str] 
    illustration_prompt: Optional[str]
    ennemis: List[EnnemiBrief]
    musique_theme: Optional[str]

class QuestStep(BaseModel):
    titre: str
    resume: str
    lieu: Optional[str]
    musique_suggestion: Optional[str] 

class QuestModel(BaseModel):
    titre: str
    synopsis: str
    long_description: str
    objectif: str
    type: Literal["exploration", "enquête", "intrigue", "combat", "diplomatie", "quête d'objet"]
    niveau_recommande: int
    tags: List[str]
    giver: PNJBrief

    pnjs: List[PNJBrief]
    lieux: List[LocationBrief]
    etapes: List[QuestStep]
    rebondissements: List[str]
    consequences: List[str]
    factions_associees: List[str]

    def collect_factions(self) -> List[str]:
        """Collecte toutes les factions associées aux PNJs et lieux de la quête."""
        factions = set()

        # Giver
        if self.giver.faction:
            factions.add(self.giver.faction)

        # PNJ
        for pnj in self.pnjs:
            if pnj.faction:
                factions.add(pnj.faction)

        # Ennemis humanoïdes uniquement
        for loc in self.lieux:
            for ennemi in loc.ennemis:
                if ennemi.type in ("humanoïde", "humain") and ennemi.faction:
                    factions.add(ennemi.faction)

        return sorted(factions)
