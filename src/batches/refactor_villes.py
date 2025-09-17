from src.models.villes import City
from src.services.chatgpt_service import ChatGPT
import os
import json


def refactor_villes(dossier="./data/villes"):
    """
    Refactor the city data to match the new model.
    """
    for fichier in os.listdir(dossier):
        if fichier.endswith(".json"):
            chemin = os.path.join(dossier, fichier)
            chemin_refactor = os.path.join(dossier + "/villes_refactor", fichier)
            print("[*] Refactorisation du fichier : ", fichier)
            print(f"[+] Fichier : {chemin}")
            print(f"[+] Fichier refactorisé : {chemin_refactor}")
            try:
                with open(chemin, "r", encoding="utf-8") as f:
                    message = f"""Convertis moi les données suivantes au nouveau format. Si tu ne sais pas, renvoie un champs vide.
                     Voici les données: \n ---- \n {f.read()}\n"""
                    response = ChatGPT.getMessageWithJSON(message, City)
                    with open(chemin_refactor, "a+", encoding="utf-8") as f2:
                        json.dump(response.model_dump(), f2, ensure_ascii=False, indent=2)
                    print(f"[+] Fichier {fichier} refactorisé avec succès.")
            except Exception as e:
                print(f"[!] Erreur avec le fichier {fichier} : {e}")
                import sys
                sys.exit(1)
