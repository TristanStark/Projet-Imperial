from src.core.factory import PNJFactory
from src.models.pnj import PNJQuery, PNJ
from src.core.description import PNJDescriptionService
from src.core.export_foundry import FoundryExporter
from src.physiques.combattant import CombattantPhysique
from src.utils.tokenizer import Tokenizer
from src.utils.logger import logger
from src.services.chatgpt_service import ChatGPT



class PNJPhysique:
    def __init__(self, export_path: str):
        self.factory = PNJFactory()
        self.description_service = PNJDescriptionService()
        self.exporter = FoundryExporter(export_path)
        self.export_path = export_path

    def change_export_path(self, new_path: str):
        logger.info(f"Changement du chemin d'exportation vers : {new_path}")
        self.export_path = new_path
        self.exporter.base_path = new_path
        self.exporter._ensure_directory("actors")
        logger.info("Chemin d'exportation mis à jour avec succès.")

    def generate(self, _metier=None, custom: PNJQuery | None = None) -> PNJ:
        logger.debug("Génération d’un PNJ physique en cours...")
        complet = self.factory.generate(_metier, custom)

        # Générer le bloc combattant
        summary = self.description_service.generate_summary(complet)
        combattant = CombattantPhysique.generate(
            summary,
            complet.race.hit_points,
            complet.level,
            round((complet.stats.con - 10) / 2),
            round((complet.stats.wis - 10) / 2),
        )
        complet.combattant = combattant

        # Générer les descriptions
        description_text = self.description_service.generate_equipment_description(complet)
        description_physique = self.description_service.generate_physical_description(description_text)
        token_prompt = self.description_service.generate_token_prompt(complet)

        # Générer image token
        #uuid = Tokenizer.generate_unique_id()
        #uuid = ChatGPT.generateImage(token_prompt)
        token_name = f"{complet.base.prenom} {complet.base.nom}"
        #Tokenizer.tokenize(token_name, uuid, "default", self.export_path)

        return PNJ(complet, token_prompt, token_name, description_text, description_physique)

    def export_to_foundry(self, pnj: PNJ) -> dict:
        return self.exporter.export(pnj)
