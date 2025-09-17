from src.services.chatgpt_service import ChatGPT
from src.models.branched_quest import BranchedQuestModel
from pydantic import TypeAdapter
import json

adapter = TypeAdapter(BranchedQuestModel)
schema = adapter.json_schema()
del schema['required']  # Supprime la clé problématique si présente
clean_schema = json.dumps(schema, indent=2)


class BranchedQuestGenerator:
    @staticmethod
    def generate_from_synopsis(synopsis: str) -> BranchedQuestModel:
        prompt = f"""
            Tu es un maître de jeu expérimenté en narration interactive. 
            À partir du synopsis ci-dessous, génère une quête interactive à embranchements (avec plusieurs étapes, choix multiples et chemins alternatifs).

            Réponds au format JSON strict en suivant ce modèle Pydantic :

            {clean_schema}

            Règles à respecter :
            - Commence par une introduction courte (champ synopsis).
            - Chaque QuestNode doit contenir un ou plusieurs choix.
            - Chaque choix mène à un autre QuestNode (next_node_id) ou à une fin (None).
            - Génère entre 4 et 8 nœuds avec des branches divergentes et convergentes.
            - Inclus des PNJ et ennemis crédibles dans les scènes.
            - Sois immersif, crédible et donne une saveur unique à chaque segment.

            Synopsis de base :
            ---
            {synopsis}
            ---

            Ne retourne que le JSON.
            """
        return ChatGPT.getMessageWithJSON(prompt, BranchedQuestModel)
