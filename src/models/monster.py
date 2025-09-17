from typing import List, Optional, Literal, Dict
from pydantic import BaseModel


class Attack(BaseModel):
    name: str
    bonus: int
    traits: List[str]
    type_: Literal["melee", "ranged"]
    damage: str
    damage_type: str

class DamageType(BaseModel):
    damage_type: str
    value: int

class Action(BaseModel):
    category: Literal["interaction", "defensive", "offensive"]
    action_type: Literal["passive", "action"]
    number_of_action: Literal["OneAction", "TwoAction", "ThreeAction", "Passive"]
    name: str
    description: str
    traits: Optional[List[str]]

class Monster(BaseModel):
    # Informations générales
    name: str
    level: int  # Niveau de danger
    size: Literal["Tiny", "Small", "Medium", "Large", "Huge", "Gargantuan"]
    traits: List[str]  # Liste des traits (par ex. "Fiend", "Dragon", etc.)

    # Caractéristiques principales
    ac: int  # Classe d'armure
    hp: int  # Points de vie
    perception: int  # Jet de perception

    # Jets de sauvegarde
    fortitude_bonus: int
    reflex_bonus: int
    will_bonus: int

    #description
    description: str

    # Valeurs de caractéristiques
    strength_modifier: int
    dexterity_modifier: int
    constitution_modifier: int
    intelligence_modifier: int
    wisdom_modifier: int
    charisma_modifier: int

    # Attaques et actions
    attacks: Optional[List[Attack]]  # Liste d'attaques spécifiques
    actions: Optional[List[Action]]  # Liste des actions spéciales

    # Résistances, immunités, et faiblesses
    resistances: Optional[List[DamageType]]
    immunities: Optional[List[str]]
    weaknesses: Optional[List[DamageType]]

    # Capacités spéciales
    passive_abilities: Optional[List[Action]]
    auras: Optional[List[Action]]

    # Vitesse et déplacements
    speed: int  # Vitesse principale
    other_speeds: Optional[Dict[str, int]]

    # Compétences
    skills: Optional[Dict[str, int]]

    # Sens
    senses: Optional[List[str]]

    # Réactions
    reactions: Optional[List[Action]]

    # Langues
    languages: Optional[List[str]]
    rarity: Literal["common", "uncommon", "rare", "unique"]

    class Config:
        json_schema_extra = {
            "required": [
                "name", "level", "size", "traits", "ac", "hp", "perception", 
                "fortitude", "reflex", "will", "strength", "dexterity", 
                "constitution", "intelligence", "wisdom", "charisma", 
                "speed"
            ]
        }

class Monsters(BaseModel):
    variations: list[Monster]
