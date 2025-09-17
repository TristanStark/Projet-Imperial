from dataclasses import dataclass
from src.services.database_service import db
from src.services.chatgpt_service import ChatGPT

@dataclass
class Weapon:
    name: str
    traits: list[str]
    bulk: int
    hands: int
    category: str
    damage_number_of_dices: int
    damage_type_die: str
    damage_type: str
    description: str
    price: int

@dataclass
class Item:
    item_name: str
    item_price: float
    rarity: str
    description: str
    level: int
    id: int

@dataclass
class Spell:
    spell_name: str
    spell_level: int


class _ItemPhysique:
    def __init__(self) -> None:
        """Physique pour les items"""
        pass

    def insert(self, item: Item) -> int:
        """Insère l'item"""
        message = f"""insert into item(name, price, rarity) values(
                    '{ChatGPT.sanitize(item.item_name)}', {item.item_price}, '{item.rarity}');"""
        db.execute(message)
        db.commit()
        return db.curseur.lastrowid
    
ItemPhysique = _ItemPhysique()

class _SpellPhysique:
    def __init__(self) -> None:
        """L'accesseur physique pour les spells"""
        pass

    def insert(self, spell: Spell) -> int:
        """Insère le spell et renvoie son id"""
        requete = f"insert into spell(name, level) values('{spell.spell_name}', {spell.spell_level});"
        db.execute(requete)
        return db.curseur.lastrowid
    
    def insertSpellList(self, spellList: list[Spell], pnj_id: int) -> None:
        """Insère la spell list correspondante"""
        for spell in spellList:
            id = self.insert(spell)
            requete = f"insert pnj_spells(pnj_id, spell_id) values ({pnj_id}, {id});"
            db.execute(requete)
        db.commit()        

class _InventoryPhysique:
    def __init__(self) -> None:
        """L'inventaire"""
        pass

    def insert(self, pnj_id: int, list_items: list[Item]) -> None:
        """insère l'inventaire"""
        for item in list_items:
            id = ItemPhysique.insert(item)
            message = f"insert into pnj_item(pnj_id, item_id) values ({pnj_id}, {id});"
            db.execute(message)
        db.commit()



class _FoundryItems:
    def __init__(self) -> None:
        """L'accesseur physique des items"""
        pass

    def foundry(self, item: Item) -> str:
        """Foundryse l'item"""
        id = ChatGPT.generate_unique_id()
        message = f""" {{ "name": "{item.item_name}", "type": "equipment", "effects": [], 
        "system": {{ "description": {{ "gm": "", "value": "<p> {item.description} </p>"
            }}, "rules": [ ], "slug": null, "_migration": {{ "version": 0.933, "lastMigration": null, "previous": {{
                "schema": 0.932, "foundry": "12.331", "system": "6.5.0" }} }}, "traits": {{
              "otherTags": [], "value": [], "rarity": "{item.rarity}" }}, "publication": {{ "title": "", "authors": "",
              "license": "OGL", "remaster": false }}, "level": {{ "value": {item.level} }}, "quantity": 1, "baseItem": null,
            "bulk": {{ "value": 0 }}, "hp": {{ "value": 0, "max": 0 }}, "hardness": 0, "price": {{ "value": {{ 
                "gp": {int(item.item_price)} }} }}, "equipped": {{ "carryType": "worn", "invested": null }}, "containerId": null,
            "size": "med", "material": {{ "type": null, "grade": null }}, "identification": {{
              "status": "identified", "unidentified": {{ "name": "Unusual Object", 
                "img": "systems/pf2e/icons/unidentified_item_icons/adventuring_gear.webp",
                "data": {{ "description": {{ "value": "" }} }} }}, "misidentified": {{}} }},
            "usage": {{ "value": "worn" }}, "subitems": [] }}, "img": "systems/pf2e/icons/default-icons/equipment.svg",
          "folder": "tPxLcPiDXMuWnftY", "sort": 100000, "ownership": {{ "default": 0}},
          "flags": {{}}, "_stats": {{ "compendiumSource": "Item.{id}", "duplicateSource": null,
            "coreVersion": "12.331", "systemId": "pf2e", "systemVersion": "6.6.2", "createdTime": 1731507665810,
            "modifiedTime": 1731507665810}}, "_id": "{id}" }} """
        return message

    def Weapon(self, arme: Weapon) -> str:
        """Foundryse l'arme et son attaque associée"""
        id = ChatGPT.generate_unique_id()
        message_weapon = f""" {{ "img": "icons/weapons/swords/greatsword-crossguard-silver.webp", 
        "name": "{arme.name}", "system": {{ "description": {{ "gm": "", "value": "<p>{arme.description}</p>"
            }}, "rules": [], "slug": "", "_migration": {{ "version": 0.933, "lastMigration": null,
            "previous": null }}, "traits": {{ "otherTags": [], "value": [ "versatile-p" ], "rarity": "common"
            }}, "publication": {{ "title": "Pathfinder Player Core", "authors": "", "license": "ORC",
            "remaster": true }}, "level": {{ "value": 0 }}, "quantity": 1, "baseItem": "greatsword", "bulk": {{
            "value": {arme.bulk} }}, "hp": {{ "value": 0, "max": 0 }}, "hardness": 0, "price": {{ "value": {{ "gp": {arme.price}
            }} }}, "equipped": {{ "carryType": "held", "invested": null, "handsHeld": {arme.hands} }}, "containerId": null,
            "size": "med", "material": {{ "type": null, "grade": null }}, "identification": {{
            "status": "identified", "unidentified": {{ "name": "", "img": "", "data": {{ "description": {{
                    "value": "" }} }} }}, "misidentified": {{}} }}, "usage": {{ "value": "held-in-two-hands"
            }}, "category": "{arme.category}", "group": "sword", "bonus": {{ "value": 0 }}, "damage": {{ "dice": {arme.damage_number_of_dices},
            "die": "{arme.damage_type_die}", "damageType": "{arme.damage_type}", "persistent": null }}, "bonusDamage": {{ "value": 0
            }}, "splashDamage": {{ "value": 0 }}, "range": null, "reload": {{ "value": "" }}, "runes": {{
            "potency": 0, "striking": 0, "property": [] }}, "specific": null, "subitems": [],
            "property1": {{ "value": "", "dice": 0, "die": "", "damageType": "", "critDice": 0,
            "critDie": "", "critDamage": "", "critDamageType": "" }} }}, "type": "weapon", "_stats": {{
            "compendiumSource": "Compendium.pf2e.equipment-srd.Item.UX71GkWBL9g41VwM", "duplicateSource": null,
            "coreVersion": "12.331", "systemId": "pf2e", "systemVersion": "6.6.2", "createdTime": 1731533838811,
            "modifiedTime": 1731533841455}}, "effects": [], "folder": null,
        "sort": 0, "ownership": {{ "default": 0}}, "flags": {{}}, "_id": "{id}"
        }} """
        return message_weapon

FoundryItems = _FoundryItems()
InventoryPhysique = _InventoryPhysique()
SpellPhysique = _SpellPhysique()

        