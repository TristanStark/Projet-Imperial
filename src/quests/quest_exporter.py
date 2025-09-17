import json
from pathlib import Path
from src.models.quest_model import QuestModel
from src.utils.logger import logger
from src.services.chatgpt_service import ChatGPT
from src.utils.parchemin import ParchmentFactory

class QuestExporter:
    @staticmethod
    def export_as_journal(quest: QuestModel, export_path: str) -> Path:
        export_path = Path(export_path)
        quest_dir = export_path / quest.titre.replace(" ", "_")
        quest_dir.mkdir(parents=True, exist_ok=True)

        journal = {
            "name": quest.titre,
            "pages": [],
            "folder": "AeYjbyEIrNgvvPJI",
            "flags": {
                "core": {"sheetClass": ""},
                "scene-packer": {"sourceId": f"JournalEntry.{quest.titre.replace(' ', '_')[:16]}"},
                "exportSource": {
                    "world": "la-couronne-des-immortels",
                    "system": "pf2e",
                    "coreVersion": "12.331",
                    "systemVersion": "6.11.1"
                }
            },
            "_stats": {
                "systemId": "pf2e",
                "systemVersion": "6.11.1",
                "coreVersion": "12.331",
                "createdTime": 0,
                "modifiedTime": 0,
                "lastModifiedBy": "5e25BVKy2W9e3XQq"
            }
        }

        def new_page(title: str, content: str, sort_index: int, pid: str) -> dict:
            return {
                "sort": sort_index,
                "name": title,
                "type": "text",
                "_id": pid,
                "title": {"show": True, "level": 1},
                "image": {},
                "text": {
                    "format": 1,
                    "content": f"<p>{content}</p>",
                    "markdown": ""
                },
                "video": {"controls": True, "volume": 0.5},
                "src": None,
                "system": {},
                "ownership": {"default": -1},
                "flags": {},
                "_stats": journal["_stats"].copy()
            }

        sort_index = 100000
        journal["pages"].append(new_page("Synopsis", quest.synopsis, sort_index, ChatGPT.generate_unique_id()))

        for step in quest.etapes:
            sort_index += 100000
            journal["pages"].append(new_page(step.titre, step.resume, sort_index, ChatGPT.generate_unique_id()))

        for lieu in quest.lieux:
            sort_index += 100000
            contenu = f"<strong>Type :</strong> {lieu.type}<br>"
            contenu += f"<strong>Description :</strong> {lieu.description}<br>"
            if lieu.ambiance:
                contenu += f"<strong>Ambiance :</strong> {lieu.ambiance}<br>"
            if lieu.danger:
                contenu += f"<strong>Danger :</strong> {lieu.danger}<br>"
            if lieu.musique_theme:
                contenu += f"<strong>Musique :</strong> {lieu.musique_theme}<br>"
            journal["pages"].append(new_page(f"Lieu - {lieu.nom}", contenu, sort_index, ChatGPT.generate_unique_id()))

        if quest.rebondissements:
            sort_index += 100000
            html = "<ul>" + "".join([f"<li>{r}</li>" for r in quest.rebondissements]) + "</ul>"
            journal["pages"].append(new_page("Rebondissements", html, sort_index, ChatGPT.generate_unique_id()))

        if quest.consequences:
            sort_index += 100000
            html = "<ul>" + "".join([f"<li>{c}</li>" for c in quest.consequences]) + "</ul>"
            journal["pages"].append(new_page("Conséquences", html, sort_index, ChatGPT.generate_unique_id()))

        json_path = quest_dir / f"{quest.titre.replace(' ', '_')}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(journal, f, indent=2, ensure_ascii=False)

        logger.info(f"Journal Foundry exporté : {json_path}")
        return quest_dir

    @staticmethod
    def create_parchemin(title: str, description: str, export_path: str) -> Path:
        ParchmentFactory.draw_quest(title, description, export_path)