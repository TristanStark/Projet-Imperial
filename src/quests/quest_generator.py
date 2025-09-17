from src.services.chatgpt_service import ChatGPT
from src.models.quest_model import QuestModel


class QuestGenerator:
    @staticmethod
    def generate_from_synopsis(synopsis: str) -> QuestModel:
        prompt = f"""
            Tu es un créateur de campagnes pour un jeu de rôle fantastique. 
            À partir du synopsis suivant, génère une quête complète au format JSON en respectant ce modèle Pydantic :

            {QuestModel.model_json_schema()}

            Synopsis :
            ---
            {synopsis}
            ---

            Assure-toi d'inventer :
            - un titre original,
            - des PNJ pertinents (avec leur métier, race, genre, âge, magie...)
            - des lieux cohérents avec ambiance, danger, suggestions musicales
            - des étapes de quête avec musique
            - un ou plusieurs ennemis bien intégrés
            - et une structure complète de quête (tags, conséquences...)

            Réponds uniquement avec le JSON valide.
            """
        return ChatGPT.getMessageWithJSON(prompt, QuestModel)

    @staticmethod
    def transform_prompt(questModel: QuestModel) -> str:
        prompt = f"""
        Tu es un donneur de quête dans un univers de fantasy sombre. On te demande d'écrire un très court texte (5 à 10 lignes) que l'on affichera sur un parchemin pour inviter des aventuriers à accomplir une mission.

        Tu dois :
        - Expliquer pourquoi tu as besoin d’aide
        - Décrire très brièvement le danger ou la difficulté
        - Mentionner ce que tu offres en échange (récompense)

        Voici les informations de la quête sous forme de données structurées. Inspire-toi-en pour écrire ton message :

        ```json
        {questModel.model_dump_json(indent=2)}
        ```
        Écris uniquement le texte qu'écrirait le donneur de quête, de manière naturelle, sans nommer la structure des données ni le mot "quest_model".
        Le texte doit être adapté à un parchemin que l'on trouverait sur un panneau d'affichage . Évite les phrases trop longues et les détails superflus.
        """
        return ChatGPT.getMessage(prompt)
