from dataclasses import dataclass
from pydantic import BaseModel
from typing import Optional, List

from src.physiques.race import Race
from src.physiques.metiers import Metier
from src.physiques.adjectifs import Adjectif
from src.physiques.stats import PNJStats
from src.physiques.combattant import Combattant


class PNJQuery(BaseModel):
    nom: str = ""
    prenom: str = ""
    job_name: str = ""
    race: str = ""
    age: int = 0
    genre: str = ""
    magie: bool = False


@dataclass
class PNJBase:
    nom: str
    prenom: str
    id: int
    job_id: int
    genre: str
    niveau_de_vie: float
    magie: bool
    race_id: int
    age: int


@dataclass
class PNJComplet:
    base: PNJBase
    level: int
    stats: PNJStats
    race: Race
    job: Metier
    adjectifs: List[Adjectif]
    combattant: Optional[Combattant] = None


@dataclass
class PNJ:
    pnj: PNJComplet
    description: str
    token_name: str
    equipment_description: str = ""
    token_prompt: str = ""
