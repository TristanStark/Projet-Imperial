from typing import List, Optional
from pydantic import BaseModel


class QuestChoice(BaseModel):
    texte: str  # Le choix proposé au joueur
    consequence: str  # Résultat narratif du choix
    next_node_id: Optional[str]  # Id du nœud suivant (peut être None pour une fin)


class QuestNode(BaseModel):
    id: str
    titre: str
    description: str
    lieu: Optional[str]
    pnj: List[str]
    ennemis: List[str]
    choix: List[QuestChoice]


class BranchedQuestModel(BaseModel):
    titre: str
    synopsis: str
    niveau_recommande: int
    tags: List[str]
    start_id: str  # ID du point de départ
    nodes: List[QuestNode]  # tous les nœuds de la quête
    rebondissements: List[str]
    consequences: List[str]
