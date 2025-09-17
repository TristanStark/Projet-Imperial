import argparse
from pathlib import Path
from src.quests.branched_quest_generator import BranchedQuestGenerator
from src.models.branched_quest import BranchedQuestModel
from src.utils.logger import logger
import json


def export_to_json(quest: BranchedQuestModel, export_path: str):
    path = Path(export_path) / quest.titre.replace(" ", "_")
    path.mkdir(parents=True, exist_ok=True)
    with open(path / "quest.json", "w", encoding="utf-8") as f:
        json.dump(quest.dict(), f, indent=2, ensure_ascii=False)
    logger.info(f"✅ Quête exportée dans {path / 'quest.json'}")
    return path / "quest.json"


def main():
    parser = argparse.ArgumentParser(description="Génère une quête à embranchements narratifs complets")
    parser.add_argument("--synopsis", type=str, required=True, help="Synopsis de la quête")
    parser.add_argument("--export-path", type=str, default="export/branched_quests", help="Chemin de sauvegarde")
    args = parser.parse_args()

    print("\n[1] Génération de la quête ramifiée...")
    quest = BranchedQuestGenerator.generate_from_synopsis(args.synopsis)

    print("\n[2] Export de la quête au format JSON...")
    export_to_json(quest, args.export_path)


if __name__ == "__main__":
    main()

