from src.services.chatgpt_service import ChatGPT
from src.models.monster import Monsters, Monster, Action, Attack
from src.utils.logger import log_function_call
from pathlib import Path
import json
import os


class _MonsterPhysique:
    def __init__(self) -> None:
        self.monster_folder_id = "GKgEkImp9p0e3Ni8"
        self.foundry_root = Path(os.getenv("FOUNDRY_EXPORT_PATH", r"C:\\Users\\thoma\\AppData\\Local\\FoundryVTT\\Data\\modules\\les-reliques-des-ainees\\quests"))

    @log_function_call
    def generateSeveral(self, nom: str, nb: int = 1) -> Monsters:
        message = f"""
You are a Pathfinder 2e game master who creates challenging and interesting enemies.
Generate {nb} variation(s) of the following monster: {nom}.
Reply in English with complete details.
"""
        return ChatGPT.getMessageWithJSON(message, Monsters, False)

    @log_function_call
    def generate(self, nom: str) -> Monster:
        message = f"""
You are a Pathfinder 2e game master who creates challenging and interesting enemies.
Generate a complete description of the following monster: {nom}.
Reply in English with complete details.
"""
        return ChatGPT.getMessageWithJSON(message, Monster, False)


    def add_actions(self, monstre: Monster) -> list:
        items = []
        for action in monstre.actions:
            items.append({
                "type": "action",
                "name": action.name,
                "img": f"systems/pf2e/icons/actions/{action.number_of_action}.webp",
                "system": {
                    "description": {"value": action.description or ""},
                    "traits": {"value": []},
                    "actionType": {"value": action.action_type},
                    "actions": {"value": f"{action.number_of_action}"},
                },
                "flags": {},
                "effects": []
            })
        for atk in monstre.attacks:
            items.append({
                "type": "melee",
                "name": atk.name,
                "img": "systems/pf2e/icons/equipment/weapons/sword.webp",
                "system": {
                    "bonus": {"value": atk.bonus},
                    "damageRolls": [{"damage": atk.damage}],
                    "traits": {"value": atk.traits or []},
                },
                "flags": {},
                "effects": []
            })
        return items

    def extract_traits(self, monstre: Monster) -> list:
        keywords = ["undead", "fey", "construct", "aberration", "dragon", "fiend", "beast", "plant", "ooze", "elemental"]
        result = []
        name_desc = f"{monstre.name.lower()} {monstre.description.lower()}"
        for trait in keywords:
            if trait in name_desc:
                result.append(trait)
        return result

    @log_function_call
    def foundry(self, monstre: Monster, folder: str = "monstres", quest_name: str = "") -> Path:
        base_name = monstre.name.replace(" ", "_")
        token_variation = "var1"
        id = ChatGPT.generate_unique_id()

        foundry_data = {
            "name": monstre.name,
            "type": "npc",
            "img": f"modules/les-reliques-des-ainees/monstres/{base_name}_{token_variation}_1_0.webp",
            "prototypeToken": {
                "name": monstre.name,
                "texture": {
                    "src": f"modules/les-reliques-des-ainees/monstres/{base_name}_{token_variation}*.webp"
                },
                "width": 1,
                "height": 1,
                "displayName": 20,
                "displayBars": 20,
                "disposition": -1,
                "bar1": {"attribute": "attributes.hp"},
                "bar2": {"attribute": None},
                "flags": {
                    "pf2e": {"linkToActorSize": True, "autoscale": True}
                },
                "randomImg": True
            },
            "system": {
                "traits": {"value": self.extract_traits(monstre)}
            },
            "items": self.add_actions(monstre),
            "folder": self.monster_folder_id,
            "_id": id,
            "_stats": {
                "coreVersion": "12.331",
                "systemId": "pf2e",
                "systemVersion": "6.6.2"
            },
            "effects": []
        }

        output_folder = self.foundry_root / quest_name / folder
        output_folder.mkdir(parents=True, exist_ok=True)
        output_file = output_folder / f"{base_name}.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(foundry_data, f, indent=2, ensure_ascii=False)

        return output_file


MonsterPhysique = _MonsterPhysique()
