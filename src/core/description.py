from src.services.chatgpt_service import ChatGPT
from src.models.pnj import PNJComplet
from src.utils.tokenizer import Tokenizer
from pydantic import BaseModel

# À adapter selon ton implémentation
class DescriptionPhysiqueModel(BaseModel):
    description: str

class BordureDetermination(BaseModel):
    moderne: bool
    nature: bool
    perse: bool


class PNJDescriptionService:
    @staticmethod
    def generate_summary(pnj: PNJComplet) -> str:
        return (
            f"{pnj.base.nom}, est un {pnj.base.genre} ({pnj.race.name}) de {pnj.base.age} ans\n"
            f"Il travaille comme: {pnj.job.name}.\n"
            f"Traits de personnalités: {', '.join(adj.nom for adj in pnj.adjectifs)}\n"
            f"Caractéristiques PF2e: STR: {pnj.stats.strength}, DEX: {pnj.stats.dex}, CON: {pnj.stats.con}, "
            f"WIS: {pnj.stats.wis}, INT: {pnj.stats.intelligence}, CHA: {pnj.stats.cha}\n"
            f"Maîtrise de la magie: {'oui' if pnj.base.magie else 'non'}\n"
            f"Niveau: {pnj.level}\n"
        )

    @staticmethod
    def generate_token_prompt(pnj: PNJComplet) -> str:
        genre = "masculin" if pnj.base.genre == "Homme" else "féminin"
        return f"Un splash art, full body frame of a {pnj.race.name} {genre} de {pnj.base.age} ans. C’est un {pnj.job.name}."

    @staticmethod
    def generate_equipment_description(pnj: PNJComplet) -> str:
        c = pnj.combattant
        if not c:
            return ""
        return (
            f"Nom Prénom: {pnj.base.nom}\n"
            f"Etat civil: {pnj.base.genre} ({pnj.race.name}) de {pnj.base.age} ans\n"
            f"Travail: {pnj.job.name} (Salaire {pnj.base.niveau_de_vie} / an)\n"
            f"Traits de personnalité: {', '.join(adj.nom for adj in pnj.adjectifs)}\n"
            f"Magie: {'oui' if pnj.base.magie else 'non'}\n"
            f"Niveau: {pnj.level}\n"
            f"Inventaire: Une {c.armor.item_name} ({c.armor.rarity}) et une {c.weapon.name}.\n"
            f"Objets: {', '.join(item.item_name for item in c.random_inventory)}."
        )

    @staticmethod
    def generate_physical_description(description: str) -> str:
        prompt = f"Décris l’apparence de ce personnage : {description}"
        result = ChatGPT.getMessageWithJSON(prompt, DescriptionPhysiqueModel)
        return result.description

    @staticmethod
    def simplify_description(description: str) -> str:
        prompt = f"Simplifie cette description : {description}"
        result = ChatGPT.getMessageWithJSON(prompt, DescriptionPhysiqueModel)
        return result.description

    @staticmethod
    def determine_border(description: str) -> str:
        prompt = f"Voici la description : {description}. Préfère-t-il une bordure moderne, nature ou perse ?"
        result = ChatGPT.getMessageWithJSON(prompt, BordureDetermination)
        if result.moderne:
            return Tokenizer.BORDURE_MODERNE
        elif result.nature:
            return Tokenizer.BORDURE_NATURE
        else:
            return Tokenizer.BORDURE_PERSE
