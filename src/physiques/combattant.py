from src.services.database_service import db
from dataclasses import dataclass
from pydantic import BaseModel
from src.services.chatgpt_service import ChatGPT
from src.physiques.items import Item, InventoryPhysique, Spell, SpellPhysique, Weapon

class DefenseProficiencyModel(BaseModel):
    type_of_armor: str
    ac_bonus: int
    proficiency: str

class AttackProficiencyModel(BaseModel):
    type_of_weapon: str
    attack_bonus: int
    damage_bonus: int
    proficiency: str

class SavingThrowModel(BaseModel):
    saving_throw_proficiency: str
    saving_throw_bonus: int

class WeaponModel(BaseModel):
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

class ItemModel(BaseModel):
    item_name: str
    item_price: float
    description: str
    level: str
    rarity: str

class SpellModel(BaseModel):
    spell_name: str
    spell_level: int

class CombattantModel(BaseModel):
    class_name: str
    class_hit_points: int
    attack: AttackProficiencyModel
    defense: DefenseProficiencyModel
    reflex_saving_throw: SavingThrowModel
    fortitude_saving_throw: SavingThrowModel
    will_saving_throw: SavingThrowModel
    weapon: WeaponModel
    armor: ItemModel
    loose_coins: float
    random_inventory: list[ItemModel]
    magical_tradition: str
    spell_list: list[SpellModel]

@dataclass
class DefenseProficiency:
    type_of_armor: str
    ac_bonus: int
    proficiency: str

@dataclass
class AttackProficiency:
    type_of_weapon: str
    attack_bonus: int
    damage_bonus: int
    proficiency: str

@dataclass
class SavingThrow:
    saving_throw_proficiency: str
    saving_throw_bonus: int

@dataclass
class Combattant:
    class_name: str
    class_hit_points: int
    total_hit_points: int
    attack: AttackProficiency
    defense: DefenseProficiency
    reflex_saving_throw: SavingThrow
    fortitude_saving_throw: SavingThrow
    will_saving_throw: SavingThrow
    weapon: Weapon
    armor: Item
    loose_coins: float
    random_inventory: list[Item]
    magical_tradition: str
    spell_list: list[Spell]
    perception: int



class _CombattantPhysique:
    def __init__(self) -> None:
        """Le physique pour un combattant"""
        pass

    def itemModelToItem(self, model: ItemModel) -> Item:
        """Transforme itemModel to item"""
        return Item(model.item_name, model.item_price, model.rarity, model.description, model.level, -1)
    
    def spellModelToSpell(self, model: SpellModel) -> Spell:
        """Transforme un spellModel en Spell"""
        return Spell(model.spell_name, model.spell_level)
    
    def savingThrowModelToSavingThrow(self, model: SavingThrowModel) -> SavingThrow:
        """Transforme un saving Throw Model en savingThrow"""
        return SavingThrow(model.saving_throw_proficiency, model.saving_throw_bonus)
    
    def defenseModelToDefense(self, model: DefenseProficiencyModel) -> DefenseProficiency:
        """Transforme un defense"""
        return DefenseProficiency(model.type_of_armor, model.ac_bonus + 10, model.proficiency)
    
    def attackModelToAttack(self, model: AttackProficiencyModel) -> AttackProficiency:
        """Transforme l'attaque"""
        return AttackProficiency(model.type_of_weapon, model.attack_bonus, model.damage_bonus, model.proficiency)
    
    def WeaponModelToWeapon(self, model: WeaponModel) -> Weapon:
        """..."""
        return Weapon(model.name, model.traits, model.bulk, model.hands, model.category, model.damage_number_of_dices, model.damage_type_die, model.damage_type, model.description, model.price)

    def generate(self, description: str, starting_hit_points: int, level: int, con_modifier: int, wis_modifier: int) -> Combattant:
        """Génère un combattant à partir d'un PNJ Complet"""
        message = f"""Transforme moi le pnj suivant en combattant pour Pathfinder 2e. 
                    Les raretés doivent faire parties de celles de Pathfinder 2e, tout comme la classe
                     et les sorts. Le type d'arme doit-faire partie de "Simple", "Martial", "Advanced". 
                      Le type d'armure doit faire partie de "unarmored" pour ceux qui n'en ont pas (pauvre ou
                       tout simplement une classe qui n'en utilise pas), "simple", "medium", "heavy".
                       Un combattant ne peut avoir de sort et une classe qui utilise la magie que
                        si celui-ci maîtrise la magie. Voici le pnj: \n{description}"""
        response = ChatGPT.getMessageWithJSON(message, CombattantModel)
        
        class_name = response.class_name
        hit_points = (response.class_hit_points + con_modifier) * level + starting_hit_points
        attack = self.attackModelToAttack(response.attack)
        defense = self.defenseModelToDefense(response.defense)
        reflex = self.savingThrowModelToSavingThrow(response.reflex_saving_throw)
        fortitude = self.savingThrowModelToSavingThrow(response.fortitude_saving_throw)
        will = self.savingThrowModelToSavingThrow(response.will_saving_throw)
        weapon = self.WeaponModelToWeapon(response.weapon)
        armor = self.itemModelToItem(response.armor)
        loose_coins = response.loose_coins
        perception = 10 + wis_modifier
        inventory = []
        for item in response.random_inventory:
            inventory.append(self.itemModelToItem(item))
        magical_tradition = response.magical_tradition
        spell_list = []
        for spell in response.spell_list:
            spell_list.append(self.spellModelToSpell(spell))
        combattant = Combattant(class_name, response.class_hit_points, hit_points, attack,
                                defense, reflex, fortitude, will, weapon,
                                armor, loose_coins, inventory, magical_tradition, spell_list, perception)
        #print(response)
        return combattant

    def insertCombattant(self, c: Combattant, pnj_id: int) -> None:
        """Insère le combattant"""
        requete = f"""insert into combattant values('{c.class_name}', {c.total_hit_points}, '{c.attack.proficiency}',
            {c.attack.attack_bonus}, {c.attack.damage_bonus}, '{c.attack.type_of_weapon}', '{c.defense.type_of_armor}',
            {c.defense.ac_bonus}, '{c.defense.proficiency}', '{c.reflex_saving_throw.saving_throw_proficiency}',
            {c.reflex_saving_throw.saving_throw_bonus}, '{c.fortitude_saving_throw.saving_throw_proficiency}', 
            {c.fortitude_saving_throw.saving_throw_bonus}, '{c.will_saving_throw.saving_throw_proficiency}', 
            {c.will_saving_throw.saving_throw_bonus}, '{c.magical_tradition}', {c.loose_coins}, {pnj_id});"""
        db.execute(requete)
        inventory = c.random_inventory
        #inventory.append(c.weapon)
        inventory.append(c.armor)
        InventoryPhysique.insert(pnj_id, inventory)

        if len(c.spell_list) != 0:
            SpellPhysique.insertSpellList(c.spell_list, pnj_id)

        db.commit()


CombattantPhysique = _CombattantPhysique()