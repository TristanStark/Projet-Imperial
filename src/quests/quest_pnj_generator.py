from src.models.pnj import PNJQuery, PNJ
from src.app.pnj_physique import PNJPhysique
from src.models.quest_model import QuestModel, PNJBrief
from typing import List
from pathlib import Path


class QuestPNJGenerator:
    def __init__(self, export_path: str):
        self.engine = PNJPhysique(export_path)
        self.export_dir = Path(export_path)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def convert_brief_to_query(self, brief: PNJBrief) -> PNJQuery:
        return PNJQuery(
            nom=brief.nom,
            prenom="",
            genre=brief.genre,
            race=brief.race,
            job_name=brief.job_name,
            age=brief.age,
            magie=brief.magie
        )

    def generate_all_pnjs(self, quest: QuestModel) -> List[PNJ]:
        pnjs: List[PNJ] = []
        for brief in quest.pnjs:
            query = self.convert_brief_to_query(brief)
            pnj = self.engine.generate(custom=query)
            self.engine.export_to_foundry(pnj)
            pnjs.append(pnj)
        return pnjs
