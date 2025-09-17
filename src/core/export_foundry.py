from src.utils.logger import logger
from src.models.pnj import PNJ
from pathlib import Path
from os.path import relpath
import json
from src.services.chatgpt_service import ChatGPT
from src.physiques.items import FoundryItems

class FoundryExporter:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        print(f"Initialisation de l'exportateur Foundry avec le chemin de base : {self.base_path}")

    def _ensure_directory(self, folder: str):
        p = Path("C:\\Users\\thoma\\AppData\\Local\\FoundryVTT\\Data")
        full_path = self.base_path / folder
        print("FULL PATH = ", full_path)
        return full_path

    def _build_prototype_token(self, pnj: PNJ, folder: str) -> dict:
        return {
            "prototypeToken": {
                "displayName": 20,
                "displayBars": 20,
                "actorLink": True,
                "name": pnj.token_name,
                "texture": {
                    "src": f"{folder}/{pnj.token_name.replace(' ', '%20')}.png",
                    "anchorX": 0.5,
                    "anchorY": 0.5
                },
                "bar1": {"attribute": "attributes.hp"},
                "bar2": {"attribute": None},
                "disposition": -1,
                "width": 1,
                "height": 1
            }
        }

    def _build_attributes(self, pnj: PNJ) -> dict:
        return {
            "attributes": {
                "hp": {
                    "value": pnj.pnj.combattant.total_hit_points,
                    "temp": 0,
                    "max": pnj.pnj.combattant.total_hit_points,
                    "details": ""
                },
                "speed": {"value": pnj.pnj.race.speed, "otherSpeeds": [], "details": ""},
                "ac": {"value": pnj.pnj.combattant.defense.ac_bonus, "details": ""},
                "allSaves": {"value": ""},
                "initiative": {"statistic": "perception"}
            }
        }

    def _build_abilities(self, pnj: PNJ) -> dict:
        s = pnj.pnj.stats
        return {
            "abilities": {
                "str": {"mod": s.strength - 10},
                "dex": {"mod": s.dex - 10},
                "con": {"mod": s.con - 10},
                "int": {"mod": s.intelligence - 10},
                "wis": {"mod": s.wis - 10},
                "cha": {"mod": s.cha - 10},
            }
        }

    def _build_items(self, pnj: PNJ, folder: str) -> list:
        items = []

        for item in pnj.pnj.combattant.random_inventory:
            foundry_item = FoundryItems.foundry(item)
            if isinstance(foundry_item, str):
                try:
                    foundry_item = json.loads(foundry_item)
                except json.JSONDecodeError:
                    print(f"Objet JSON mal formé ignoré : {foundry_item}")
                    continue

            if foundry_item and isinstance(foundry_item, dict) and "name" in foundry_item and "type" in foundry_item:
                items.append(foundry_item)
            else:
                print(f"Item Foundry invalide ignoré: {foundry_item}")

        weapon_item = FoundryItems.Weapon(pnj.pnj.combattant.weapon)
        if isinstance(weapon_item, str):
            try:
                weapon_item = json.loads(weapon_item)
            except json.JSONDecodeError:
                print(f"Arme JSON mal formée ignorée : {weapon_item}")
                weapon_item = None

        if weapon_item and isinstance(weapon_item, dict) and "name" in weapon_item and "type" in weapon_item:
            items.append(weapon_item)
        else:
            print(f"Arme Foundry invalide ignorée: {weapon_item}")

        return items
    
    def _build_details(self, pnj: PNJ) -> dict:
        return   {"details": {
                "languages": {
                    "value": [],
                    "details": ""
                },
                "level": {
                    "value": 1
                },
                "blurb": "",
                "publicNotes": f"<p>{pnj.token_prompt}",
                "privateNotes": f"<p>{pnj.equipment_description}</p>"
            }
        }


    def _build_system(self, pnj: PNJ) -> dict:
        perception = {
            "perception": {
                "details": "",
                "mod": pnj.pnj.combattant.perception,
                "senses": [],
                "vision": True
            }
        }
        saves = {
            "saves": {
                "fortitude": {"value": pnj.pnj.combattant.fortitude_saving_throw.saving_throw_bonus},
                "reflex": {"value": pnj.pnj.combattant.reflex_saving_throw.saving_throw_bonus},
                "will": {"value": pnj.pnj.combattant.will_saving_throw.saving_throw_bonus}
            }
        }
        traits = {"traits": {"value": [], "rarity": "common", "size": {"value": "med"}}}
        customModifiers = { "customModifiers": { "all": [ { "slug": "proficiency-without-level",
          "label": "Proficiency Without Level", "domains": [], "modifier": 0, "type": "untyped",
          "ability": None, "adjustments": [], "force": False, "enabled": False,
          "ignored": False, "source": None,
          "custom": True, "damageType": None,
          "damageCategory": None, "critical": None, "tags": [],
          "hideIfDisabled": False, "kind": "modifier",
          "predicate": [] } ] } }

        return {
            **self._build_attributes(pnj),
            **self._build_details(pnj),
            **self._build_abilities(pnj),
            **perception,
            **saves,
            **traits,
            **customModifiers
        }

    def export(self, pnj: PNJ) -> dict:
        relative_path = relpath(self.base_path, Path("C:\\Users\\thoma\\AppData\\Local\\FoundryVTT\\Data"))
        data = {
            **self._build_prototype_token(pnj, relative_path),
            "folder": "GKgEkImp9p0e3Ni8",
            "name": pnj.token_name,
            "type": "npc",
            "system": self._build_system(pnj),
            "items": self._build_items(pnj, relative_path),
            "img": f"{relative_path}/{pnj.token_name.replace(' ', '%20')}_RAW.png",
            "_id": ChatGPT.generate_unique_id(),
            "sort": 100000,
            "flags": {},
            "ownership": {"default": 0},
            "effects": [],
            "_stats": {
                "coreVersion": "12.331",
                "systemId": "pf2e",
                "systemVersion": "6.6.2"
            }
        }

        with open(f"{self.base_path}\\{pnj.pnj.base.nom}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return data

