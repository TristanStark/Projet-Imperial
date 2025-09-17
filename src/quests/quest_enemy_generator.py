from typing import List
from pathlib import Path
from src.models.quest_model import QuestModel
from src.models.monster import Monster
from src.monsters.monsters import MonsterPhysique


class QuestEnemyGenerator:
    def __init__(self, export_path: str, existing_monsters_dir: str = "export/monstres"):
        self.export_path = Path(export_path)
        self.monster_path = Path(existing_monsters_dir)
        self.monster_path.mkdir(parents=True, exist_ok=True)

    def monster_exists(self, nom: str) -> bool:
        filename = f"{nom.replace(' ', '_')}.json"
        return (self.monster_path / filename).exists()

    def generate_missing_monsters(self, quest: QuestModel) -> List[Monster]:
        generated: List[Monster] = []
        names_seen = set()

        for location in quest.lieux:
            for ennemi in location.ennemis:
                if ennemi.nom.lower() in names_seen:
                    continue
                names_seen.add(ennemi.nom.lower())

                if not self.monster_exists(ennemi.nom):
                    monster = MonsterPhysique.generate(nom=ennemi.nom)
                    MonsterPhysique.foundry(monster, folder=self.monster_path.name)
                    generated.append(monster)

        return generated
