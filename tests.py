from src.utils.parchemin import ParchmentFactory
from test_parchment import draw_text_in_mask_adaptive_font
from src.core.adaptative_context import City, ContextManager, Place
#from src.services.chatgpt_service import ChatGPT
from pprint import pprint
import os
import json
from collections import Counter, defaultdict
from typing import Any
from src.core.factory import PNJFactory
import csv
import glob
from src.batches.refactor_villes import refactor_villes
from src.core.context_exporter import create_scene_from_image
from src.core.faction_exporter import create_journal_entry_faction
from src.core.faction_exporter import load_and_inject_relationships as load_and_inject_relationships_faction
from src.core.poi_exporter import poi_create_journal_entry
from src.core.place_exporter import create_journal_entry_place
from src.core.place_exporter import load_and_inject_relationships_place
from src.models.villes import Ville
from src.core.person_exporter import create_journal_entry_personn
from src.core.person_exporter import load_and_inject_relationships as load_and_inject_relationships_person
from typing import Union
from src.core.get_foundry_id import IDGetter
from src.models.factions_foundry import Relationship as FactionRelationship
from src.models.place_foundry import Relationship as PlaceRelationship
from rich import print as print_rich
from src.models.person_foundry import Relationship as PersonRelationship


def print_red(text: str):
    print_rich(f"[bold red]{text}[/bold red]")  # Rouge clair + reset propre


def calculer_total_input_tokens(dossier):
    """
    Calcule le total des input_tokens dans tous les fichiers CSV valides d'un dossier.

    Args:
        dossier (str): Chemin vers le dossier contenant les fichiers CSV

    Returns:
        int: Total des input_tokens ou None si aucun fichier valide trouvé
    """
    total_input = 0
    total_output = 0
    total_requests = 0
    fichiers_valides = 0

    # Recherche tous les fichiers CSV dans le dossier
    fichiers_csv = glob.glob(os.path.join(dossier, '*.csv'))

    if not fichiers_csv:
        print("Aucun fichier CSV trouvé dans le dossier.")
        return None

    for fichier in fichiers_csv:
        try:
            with open(fichier, mode='r', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader)  # Lit la première ligne (en-têtes)

                # Vérifie la structure du fichier
                if headers != [
                    "start_time", "end_time", "input_tokens", "output_tokens",
                    "num_model_requests", "project_id", "user_id", "api_key_id",
                    "model", "batch", "service_tier", "input_cached_tokens",
                    "input_uncached_tokens", "input_audio_tokens", "output_audio_tokens"
                ]:
                    print(f"Structure incorrecte dans le fichier: {fichier}")
                    continue

                # Compte les lignes (sans l'en-tête)
                num_lignes = sum(1 for _ in reader)
                print(f"Fichier valide: {fichier} ({num_lignes} lignes de données)")

                # Recommence la lecture pour additionner les input_tokens
                f.seek(0)
                next(reader)  # Saute l'en-tête
                for ligne in reader:
                    try:
                        total_input += float(ligne[2])  # Troisième colonne (index 2)
                        total_output += float(ligne[3])  # Troisième colonne (index 2)
                        total_requests += float(ligne[4])  # Troisième colonne (index 2)
                    except (IndexError, ValueError) as e:
                        total_input += 0
                        total_output += 0
                        total_requests += 0
                        continue

                fichiers_valides += 1

        except Exception as e:
            print(f"Erreur lors de la lecture du fichier {fichier}: {e}")
            continue

    if fichiers_valides == 0:
        print("Aucun fichier CSV valide trouvé.")
        return None

    total_input_formatte = "{:,}".format(total_input).replace(",", " ")
    total_output_formatte = "{:,}".format(total_output).replace(",", " ")
    total_requests_formatte = "{:,}".format(total_requests).replace(",", " ")
    print(f"\nTotal des input_tokens dans {fichiers_valides} fichiers valides: {total_input_formatte}")
    print(f"\nTotal des outputs_tokens dans {fichiers_valides} fichiers valides: {total_output_formatte}")
    print(f"\nTotal des requests dans {fichiers_valides} fichiers valides: {total_requests_formatte}")
    return total_input_formatte



strings = "Salutations, voyageurs. Je suis Elda, la Chasseresse du village de Brindel, et je vous implore d’aider notre communauté à résoudre un malentendu. Depuis plusieurs semaines, nos caravanes ont disparu dans la forêt, laissant derrière elles des traces de lutte et un silence pesant. La peur grandit, et seul un groupe courageux comme le vôtre pourra découvrir ce qui se cache dans l’ombre. La menace est invisible mais réelle, et le danger élevé, alors faites preuve de vigilance. En échange de votre bravoure, je vous offre la gratitude du village, ainsi qu’une récompense précieuse : de quoi assurer votre voyage lors de prochaines aventures. Acceptez-vous cette sombre mission pour rétablir la paix ?"
parchment = "./data/tavernes/parchment/Parchemin1.png"
mask = "./data/tavernes/masks/mask2.png"
"""
#draw_text_in_mask_adaptive_font(parchment, mask, strings, "Les Ombres de la Route", output_path="./data/tests/quete1_result.png")
#ParchmentFactory.draw_quest("Les Ombres de la Route", strings, "./data/tests/test_factory.png")
#print(ContextManager.context_summary())
#print("-" * 50)
message = "Donne moi un village forestier au nord de la ville de Caledorne"
result = ChatGPT.getMessageWithJSON(message, City)
#pprint(result.model_dump())
ContextManager.add_city(result)

message = "Donne moi une chaîne de collines à l'est du village de Vailloncourt"
result = ChatGPT.getMessageWithJSON(message, Place)
#pprint(result.model_dump())
ContextManager.add_place(result)

ContextManager.synchronize_missing_factions_from_quests()
print("-" * 50)
elements = ContextManager.get_elements_with_tag_to_faire()
for city in elements["cities"]:
    print(f"Ville à faire : {city.nom}")

for place in elements["places"]:
    print(f"Place à faire : {place.nom}")

incomplete_factions = ContextManager.get_incomplete_factions()
for faction in incomplete_factions:
    print(f"Faction à compléter : {faction.nom}")

#print(ContextManager.context_summary())
"""

def collect_key_usages(data: Any, fichier: str, tracker: dict, path: str = ""):
    if isinstance(data, dict):
        for key, value in data.items():
            full_key = f"{path}.{key}" if path else key
            tracker[full_key]["présence"] += 1
            tracker[full_key]["fichiers"].add(fichier)
            collect_key_usages(value, fichier, tracker, full_key)
    elif isinstance(data, list):
        for item in data:
            collect_key_usages(item, fichier, tracker, path)

def analyser_champs_par_fichier(dossier: str) -> dict:
    tracker = defaultdict(lambda: {"présence": 0, "fichiers": set()})

    for filename in os.listdir(dossier):
        if filename.endswith(".json"):
            chemin_fichier = os.path.join(dossier, filename)
            try:
                with open(chemin_fichier, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    collect_key_usages(data, filename, tracker)
            except Exception as e:
                print(f"⚠️ Erreur dans {filename} : {e}")

    # Convertir les ensembles en listes triées pour l’export JSON
    resultats = {
        cle: {
            "présence": valeur["présence"],
            "fichiers": sorted(valeur["fichiers"])
        }
        for cle, valeur in tracker.items()
    }

    return resultats



def calculer_habitants_totaux(dossier="./data/villes/villes_refactor"):
    total = 0
    for fichier in os.listdir(dossier):
        if fichier.endswith(".json"):
            chemin = os.path.join(dossier, fichier)
            try:
                with open(chemin, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    habitants = data.get("nombre_habitants", 0)
                    if isinstance(habitants, int):
                        total += habitants
            except Exception as e:
                print_red(f"[!] Erreur avec le fichier {fichier} : {e}")
    return total

def proportions_par_ville(dossier="./data/villes/villes_refactor"):
    habitants_par_ville = {}

    # Lire chaque fichier JSON et extraire le nombre d'habitants
    for fichier in os.listdir(dossier):
        if fichier.endswith(".json"):
            chemin = os.path.join(dossier, fichier)
            try:
                with open(chemin, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    nom = data.get("nom", os.path.splitext(fichier)[0])
                    habitants = data.get("nombre_habitants", 0)
                    if isinstance(habitants, int) and habitants > 0:
                        habitants_par_ville[nom] = habitants
            except Exception as e:
                print_red(f"[!] Erreur avec le fichier {fichier} : {e}")

    total = sum(habitants_par_ville.values())
    if total == 0:
        return []

    # Calcul des proportions
    proportions = [
        (ville, habitants, round((habitants / total) * 100, 2))
        for ville, habitants in habitants_par_ville.items()
    ]

    # Tri du plus grand au plus petit
    proportions.sort(key=lambda x: x[0])

    return proportions

def get_villes_to_faire(dossier="./data/villes"):
    print("-" * 50)
    print("[!] Vérification des villes passé au data...")
    total_to_do = 0
    for fichier in os.listdir(dossier):
        if fichier.endswith(".json"):
            chemin = os.path.join(dossier, fichier)
            try:
                with open(chemin, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    datas = data.get("data", None)
                    if datas is None:
                        total_to_do += 1
                        print(f"[!] La ville {data["nom"]} doit encore être traité pour data!")
            except Exception as e:
                print(f"[!] Erreur avec le fichier {fichier} : {e}")
    print(f"[!] Total de villes à faire : {total_to_do}")
    return total_to_do


def get_villes_to_purifier(dossier="./data/villes"):
    print("-" * 50)
    print("[!] Vérification des villes à purifier...")
    total_to_do = 0
    for fichier in os.listdir(dossier):
        if fichier.endswith(".json"):
            chemin = os.path.join(dossier, fichier)
            try:
                with open(chemin, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    datas = data.get("purifier", None)
                    if datas is None:
                        total_to_do += 1
                        print(f"[!] La ville {data["nom"]} doit encore être purifié de toute hérésie!")
            except Exception as e:
                print(f"[!] Erreur avec le fichier {fichier} : {e}")
    print(f"[!] Total de villes à purifier : {total_to_do}")
    return total_to_do

"""
# Tests de la modification de fonctions
elements = ContextManager.get_elements_with_tag_to_faire()
for city in elements["cities"]:
    print("-" * 50)
    print(f"Ville à faire : {city.name}")
    old_factions = city.factions.copy()
    city.factions = []"""
    #message = f"""Donne moi beaucoup plus de détails sur {city.name}. Rajoute un gouvernement local, des landmarks,
    # des ressources, une population cohérente avec la taille de la ville.
    #Voici ce qu'on sait: {city.summary()}"""
    #result = ChatGPT.getMessageWithJSON(message, City)
    #pprint(result.model_dump())
    #result.factions = old_factions
    #ContextManager.modify_element("cities", result)


def create_scenes_from_json(input_dossier: str, output_dossier: str):
    """
    Crée des scènes à partir des fichiers JSON dans le dossier spécifié.

    Args:
        dossier (str): Chemin vers le dossier contenant les fichiers JSON
    """
    for fichier in os.listdir(input_dossier):
        if fichier.endswith(".json"):
            chemin = os.path.join(input_dossier, fichier)
            try:
                with open(chemin, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    image = data.get("image", None)
                    pos1 = image.rfind("/") + 1
                    image = image[pos1:] if pos1 > 0 else image
                    image = "H:\\github\\Projet Impérial 4\\data\\Bastion Impérial\\" + image

                    # Créer une scène à partir de l'image et du nom
                    scene = create_scene_from_image(image, data["nom"], data["image"])
                    # Enregistrer la scène ou effectuer d'autres opérations
                    with open(os.path.join(output_dossier, f"{data['nom']}.json"), "w", encoding="utf-8") as out:
                        out.write(scene.model_dump_json(indent=2))
                    #print(scene.model_dump_json(indent=2))
            except Exception as e:
                print(f"[!] Erreur avec le fichier {fichier} : {e}")

def create_factions_from_json(output_dossier: str):
    """
    """
    for faction in ContextManager.get_factions():
        try:
            jef = create_journal_entry_faction(faction.name, faction.description)
            # Enregistrer la scène ou effectuer d'autres opérations
            with open(os.path.join(output_dossier, f"FACTION_{faction.name}.json"), "w", encoding="utf-8") as out:
                out.write(jef.model_dump_json(indent=2))
            #print(scene.model_dump_json(indent=2))
        except Exception as e:
            print(f"[!] Erreur avec la faction {faction.name} : {e}")


class faction_temp:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def __repr__(self):
        return f"Faction(name={self.name}, description={self.description})"

def get_faction(data: dict) -> list:
    result = []
    if "factions" not in data:
        return None
    for faction in data["factions"]:
        if isinstance(faction, dict):
            name = faction.get("nom")
            description = faction.get("description")
            if name and description:
                result.append(faction_temp(name, description))
    return result

def create_factions_from_scenes(input_dossier: str, output_dossier: str):
    """
    """
    for fichier in os.listdir(input_dossier):
        if fichier.endswith(".json"):
            chemin = os.path.join(input_dossier, fichier)
            try:
                with open(chemin, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Créer une scène à partir de l'image et du nom
                    factions = get_faction(data)
                    if factions is None:
                        print(f"[!] Aucune faction trouvée dans le fichier {fichier}")
                        continue
                    for faction in factions:
                        print(f"[!] Création de la faction {faction.name}...")
                        jef = create_journal_entry_faction(faction.name, faction.description)
                        # Enregistrer la scène ou effectuer d'autres opérations
                        with open(os.path.join(output_dossier, f"FACTION_{faction.name}.json"), "w", encoding="utf-8") as out:
                            out.write(jef.model_dump_json(indent=2))
                    #print(scene.model_dump_json(indent=2))
            except Exception as e:
                print(f"[!] Erreur avec le fichier {fichier} : {e}")

def get_pois(data: dict) -> list:
    result = []
    if "lieux_notables" not in data:
        return None
    for poi in data["lieux_notables"]:
        if isinstance(poi, dict):
            name = poi.get("nom")
            description = poi.get("description")
            if name and description:
                result.append(faction_temp(name, description))
    return result

def create_poi_from_scenes(input_dossier: str, output_dossier: str):
    """
    """
    for fichier in os.listdir(input_dossier):
        if fichier.endswith(".json"):
            chemin = os.path.join(input_dossier, fichier)
            try:
                with open(chemin, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Créer une scène à partir de l'image et du nom
                    pois = get_pois(data)
                    if pois is None:
                        print(f"[!] Aucun POI trouvée dans le fichier {fichier}")
                        continue
                    for poi in pois:
                        print(f"[!] Création du poi {poi.name}...")
                        jef = poi_create_journal_entry(poi.name, "TODO", poi.description)
                        # Enregistrer la scène ou effectuer d'autres opérations
                        with open(os.path.join(output_dossier, f"POI_{poi.name}.json"), "w", encoding="utf-8") as out:
                            out.write(jef.model_dump_json(by_alias=True, indent=2))
                    #print(scene.model_dump_json(indent=2))
            except Exception as e:
                print_red(f"[!] Erreur avec le fichier {fichier} : {e}")

def load_ville_from_json(source: Union[str, dict]) -> Ville:
    if isinstance(source, str):
        with open(source, encoding='utf-8') as f:
            data = json.load(f)
    elif isinstance(source, dict):
        data = source
    else:
        raise TypeError("source doit être un chemin str ou un dict JSON")

    # Auto-wrap si c'est un city brut
    if "nombre_habitants" in data and "nom" in data:
        data = {
            "nom": data["nom"],
            "habitants": data["nombre_habitants"],
            "type": data.get("city_type", "Inconnu"),
            "image": data.get("image", ""),
            "data": {
                "city": data
            }
        }

    return Ville.model_validate(data)


def create_place_from_scenes(input_dossier: str, output_dossier: str):
    """
    Crée des lieux à partir des fichiers JSON dans le dossier spécifié.

    Args:
        input_dossier (str): Chemin vers le dossier contenant les fichiers JSON
        output_dossier (str): Chemin vers le dossier de sortie pour les fichiers créés
    """
    for fichier in os.listdir(input_dossier):
        if fichier.endswith(".json"):
            chemin = os.path.join(input_dossier, fichier)
            try:
                with open(chemin, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    ville = load_ville_from_json(data)
                    # Créer un lieu à partir des données
                    place = create_journal_entry_place(
                        name=data["nom"],
                        description=data.get("description", "Aucune description fournie"),
                        size=data.get("city_type", "Inconnue"),
                        government=data.get("dirigeant", {}).get("actuel", {}).get("nom", "Inconnu"),
                        inhabitants=data.get("nombre_habitants", 0),
                        image_path=data.get("image", "Aucune image fournie"),
                        MEGADescription=ville.__repr__()
                    )
                    # Enregistrer le lieu ou effectuer d'autres opérations
                    with open(os.path.join(output_dossier, f"PLACE_{data['nom']}.json"), "w", encoding="utf-8") as out:
                        out.write(place.model_dump_json(indent=2, by_alias=True))
            except Exception as e:
                print_red(f"[!] Erreur avec le fichier {fichier} : {e}")


def create_persons_from_scenes(input_dossier: str, output_dossier: str):
    """
    Crée des personnages à partir des fichiers JSON dans le dossier spécifié.

    Args:
        input_dossier (str): Chemin vers le dossier contenant les fichiers JSON
        output_dossier (str): Chemin vers le dossier de sortie pour les fichiers créés
    """
    for fichier in os.listdir(input_dossier):
        if fichier.endswith(".json"):
            chemin = os.path.join(input_dossier, fichier)
            try:
                with open(chemin, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Créer un lieu à partir des données
                    person = load_ville_from_json(data)

                    jep = create_journal_entry_personn(
                        name=person.data.city.dirigeant.actuel.nom,
                        role=person.data.city.dirigeant.actuel.titre,
                        description=person.data.city.dirigeant.actuel.description,
                        location=person.data.city.nom,
                    )
                    # Enregistrer le lieu ou effectuer d'autres opérations
                    with open(os.path.join(output_dossier, f"PERSONN_{person.data.city.dirigeant.actuel.nom}.json"), "w", encoding="utf-8") as out:
                        out.write(jep.model_dump_json(indent=2, by_alias=True))
                    for membre in person.data.city.gouvernance.membres:
                        jep = create_journal_entry_personn(
                            name=membre.nom,
                            role=membre.role,
                            description="",
                            location=person.data.city.nom,
                        )
                        # Enregistrer le lieu ou effectuer d'autres opérations
                        with open(os.path.join(output_dossier, f"PERSONN_{membre.nom}.json"), "w", encoding="utf-8") as out:
                            out.write(jep.model_dump_json(indent=2, by_alias=True))

            except Exception as e:
                print_red(f"[!] Erreur avec le fichier {fichier} : {e}")


def get_persons_relationships(input_dossier: str, output_dossier_place: str, output_dossier_faction: str, output_dossier_person: str, id_getter: IDGetter):
    """
    Crée des relations entre les personnes à partir des fichiers JSON dans le dossier spécifié.
    On lui donne le dossiers des villes refactor. On load donc toutes les villes et 
    on extrait les personnes. On créé une relation entre la personne et la Ville, ainsi qu'entre
    la personne et la faction.

    Args:
        input_dossier (str): Chemin vers le dossier contenant les fichiers JSON
        output_dossier (str): Chemin vers le dossier de sortie pour les fichiers créés
    """
    for fichier in os.listdir(input_dossier):
        if fichier.endswith(".json"):
            chemin = os.path.join(input_dossier, fichier)
            try:
                with open(chemin, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # Créer un lieu à partir des données
                ville = load_ville_from_json(data)
                ville_id = id_getter.get("places", ville.data.city.nom)
                dirigeant_id = id_getter.get("persons", ville.data.city.dirigeant.actuel.nom)
                maison_dirigeante_id = id_getter.get("factions", ville.data.city.dirigeant.maison_dirigeante.nom)
                if ville.data.city.dirigeant.actuel.nom == "":
                    print(f"[!] La ville {ville.data.city.nom} n'a pas de dirigeant, on passe.")
                    continue  # Si pas de dirigeant, on passe
                # Relation entre la ville et le chef du gouvernement
                relationship = PlaceRelationship(
                        type="person",
                        name=ville.data.city.dirigeant.actuel.nom,
                        role="Chef du gouvernement",
                        hidden=False,
                        relationship=f"{ville.data.city.dirigeant.actuel.nom} est le chef du gouvernement de  {ville.data.city.nom}",
                        img="modules/monks-enhanced-journal/assets/place.png",
                        uuid=f"JournalEntry.{dirigeant_id}",
                        id=dirigeant_id,
                        alias_id=dirigeant_id
                    )
                load_and_inject_relationships_place(
                    os.path.join(output_dossier_place, f"PLACE_{ville.data.city.nom}.json"), [relationship])
                relationship = PersonRelationship(
                        type="place",
                        name=ville.data.city.nom,
                        role="Gouvernement local",
                        hidden=False,
                        relationship=f"{ville.data.city.dirigeant.actuel.nom} est le chef du gouvernement de  {ville.data.city.nom}",
                        img="modules/monks-enhanced-journal/assets/place.png",
                        uuid=f"JournalEntry.{ville_id}",
                        id=ville_id,
                        alias_id=ville_id
                )
                load_and_inject_relationships_person(
                    os.path.join(output_dossier_person, f"PERSONN_{ville.data.city.dirigeant.actuel.nom}.json"),
                    [relationship]
                )
                # Relation entre le chef du gouv et sa faction
                relationship = FactionRelationship(
                        type="person",
                        name=ville.data.city.dirigeant.actuel.nom,
                        role="Chef du gouvernement",
                        hidden=False,
                        relationship=f"{ville.data.city.dirigeant.actuel.nom} fais partie de {ville.data.city.dirigeant.maison_dirigeante.nom}",
                        img="modules/monks-enhanced-journal/assets/place.png",
                        uuid=f"JournalEntry.{dirigeant_id}",
                        id=dirigeant_id,
                        alias_id=dirigeant_id
                )
                load_and_inject_relationships_faction(
                    os.path.join(output_dossier_faction, f"FACTION_{ville.data.city.dirigeant.maison_dirigeante.nom}.json"), [relationship])
                # Relation entre la faction et le chef de la ville
                relationship = FactionRelationship(
                        type="organization",
                        name=ville.data.city.dirigeant.maison_dirigeante.nom,
                        role="Gouvernement local",
                        hidden=False,
                        relationship=f"{ville.data.city.dirigeant.actuel.nom} fais partie de {ville.data.city.dirigeant.maison_dirigeante.nom} [CHEF]",
                        img="modules/monks-enhanced-journal/assets/place.png",
                        uuid=f"JournalEntry.{maison_dirigeante_id}",
                        id=maison_dirigeante_id,
                        alias_id=maison_dirigeante_id
                )
                load_and_inject_relationships_person(
                    os.path.join(output_dossier_person, f"PERSONN_{ville.data.city.dirigeant.actuel.nom}.json"),
                    [relationship]
                )

                for person in ville.data.city.gouvernance.membres:
                    person_id = id_getter.get("persons", person.nom)
                    relationship = PlaceRelationship(
                            type="person",
                            name=person.nom,
                            role=f"Membre du gouvernement local {person.role}",
                            hidden=False,
                            relationship=f"{person.nom} fais partie du gouv de {ville.data.city.nom} ({person.role})",
                            img="modules/monks-enhanced-journal/assets/place.png",
                            uuid=f"JournalEntry.{person_id}",
                            id=person_id,
                            alias_id=person_id
                        )
                    load_and_inject_relationships_place(
                        os.path.join(output_dossier_place, f"PLACE_{ville.data.city.nom}.json"), [relationship])
                    relationship = PersonRelationship(
                            type="place",
                            name=ville.data.city.nom,
                            role="Gouvernement local",
                            hidden=False,
                            relationship=f"{person.nom} est la {person.role} du gouv de {ville.data.city.nom}",
                            img="modules/monks-enhanced-journal/assets/place.png",
                            uuid=f"JournalEntry.{ville_id}",
                            id=ville_id,
                            alias_id=ville_id
                    )
                    load_and_inject_relationships_person(
                        os.path.join(output_dossier_person, f"PERSONN_{person.nom}.json"),
                        [relationship]
                    )
            except Exception as e:
                print_red(f"[!] Erreur avec le fichier {fichier} : {e.with_traceback(None)}")

def populate_foundry_ids(output_dossier: str):
    """
    Popule les IDs Foundry à partir des fichiers JSON dans le dossier spécifié.

    Args:
        input_dossier (str): Chemin vers le dossier contenant les fichiers JSON
        output_dossier (str): Chemin vers le dossier de sortie pour les fichiers créés
    """
    id_getter = IDGetter()
    id_getter.collect_from_folder("factions")
    id_getter.collect_from_folder("persons")
    id_getter.collect_from_folder("places")
    id_getter.collect_from_folder("pois")
    #id_getter.collect_from_folder("scenes")

    with open(os.path.join(output_dossier, "foundry_ids.json"), "w", encoding="utf-8") as out:
        json.dump(id_getter.list_of_ids, out, indent=2, ensure_ascii=False)
    
    return id_getter


def get_factions_relationships(input_dossier: str, output_dossier: str, output_dossier2: str, id_getter: IDGetter):
    """
    Crée des relations entre les factions à partir des fichiers JSON dans le dossier spécifié.
    On lui donne le dossiers des villes refactor. On load donc toutes les villes et 
    on extrait les factions. On créé une relation entre la faction et la Ville, ainsi qu'entre
    la faction et la personne.

    Args:
        input_dossier (str): Chemin vers le dossier contenant les fichiers JSON
        output_dossier (str): Chemin vers le dossier de sortie pour les fichiers créés
    """
    for fichier in os.listdir(input_dossier):
        if fichier.endswith(".json"):
            chemin = os.path.join(input_dossier, fichier)
            try:
                with open(chemin, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # Créer un lieu à partir des données
                ville = load_ville_from_json(data)
                ville_id = id_getter.get("places", ville.data.city.nom)
                ville_relationships = []
                for faction in ville.data.city.factions:
                    # Créer une relation entre la faction et la ville
                    relationship = FactionRelationship(
                        type="place",
                        name=ville.data.city.nom,
                        role="Lieu d'influence",
                        hidden=False,
                        relationship=f"Relation entre {faction.nom} et {ville.data.city.nom}",
                        img="modules/monks-enhanced-journal/assets/place.png",
                        uuid=f"JournalEntry.{ville_id}",
                        id=ville_id,
                        alias_id=ville_id
                    )

                    # Charger la faction et injecter la relation
                    load_and_inject_relationships_faction(
                        os.path.join(output_dossier, f"FACTION_{faction.nom}.json"),
                        [relationship]
                    )

                    faction_id = id_getter.get("factions", faction.nom)
                    relationship = PlaceRelationship(
                        type="organization",
                        name=faction.nom,
                        role="Faction locale",
                        hidden=False,
                        relationship=f"Relation entre {ville.data.city.nom} et {faction.nom}",
                        img="modules/monks-enhanced-journal/assets/organization.png",
                        uuid=f"JournalEntry.{faction_id}",
                        id=faction_id,
                        alias_id=faction_id
                    )
                    ville_relationships.append(relationship)
                load_and_inject_relationships_place(
                    os.path.join(output_dossier2, f"PLACE_{ville.data.city.nom}.json"),
                    ville_relationships
                )
            except Exception as e:
                print_red(f"[!] Erreur avec le fichier {fichier} : {e}")


def clear():
    """
    Efface le contenu du dossier de sortie.
    """
    output_dossier = ["./data/foundry/factions", 
                      "./data/foundry/places", 
                      "./data/foundry/persons", 
                      "./data/foundry/pois",
                      "./data/foundry/scenes"]
    for dossier in output_dossier:
        for fichier in os.listdir(dossier):
            chemin = os.path.join(dossier, fichier)
            try:
                if os.path.isfile(chemin):
                    os.remove(chemin)
                elif os.path.isdir(chemin):
                    os.rmdir(chemin)
            except Exception as e:
                print_red(f"[!] Erreur lors de la suppression du fichier {fichier} : {e}")

def get_all_notes():
    input_dossier = "./data/foundry/places"
    with open("./new_contexte.txt", "w", encoding="utf-8") as f2:
        for fichier in os.listdir(input_dossier):
            if fichier.endswith(".json"):
                chemin = os.path.join(input_dossier, fichier)
                try:
                    with open(chemin, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        # Créer un lieu à partir des données
                        notes = data["pages"][0]["flags"]["monks-enhanced-journal"]["5e25BVKy2W9e3XQq"]["notes"].replace("<br />", "").replace("<p>", "").replace("</p>", "")
                        f2.write(f"\n------\n")
                        f2.write(notes)
                except Exception as e:
                    print_red(f"[!] Erreur avec le fichier {fichier} : {e}")



def create():
    clear()
    dossier = "./data/villes/villes_refactor"
    output_dossier = "./data/foundry/scenes"
    create_scenes_from_json(dossier, output_dossier)
    create_factions_from_json("./data/foundry/factions")
    print("OK Factions créées à partir des fichiers JSON.")
    print("-" * 50)
    create_factions_from_scenes(dossier, "./data/foundry/factions")
    print("OK Factions créées à partir des villes.")
    print("-" * 50)
    create_place_from_scenes(dossier, "./data/foundry/places")
    print("OK Scènes créées à partir des villes.")
    print("-" * 50)
    #create_poi_from_scenes(dossier, "./data/foundry/pois")
    #create_place_from_scenes(dossier, "./data/foundry/places")  
    create_persons_from_scenes(dossier, "./data/foundry/persons")
    print("OK Personnages créés à partir des villes.")
    print("-" * 50)
    ids = populate_foundry_ids("./data/foundry")
    get_factions_relationships(dossier, "./data/foundry/factions", "./data/foundry/places", ids)
    print("OK Factions et relations créées.")
    print("-" * 50)
    get_persons_relationships(dossier, "./data/foundry/places", "./data/foundry/factions", "./data/foundry/persons", ids)
    print("OK Relations entre personnes et lieux créées.")

def analyze_error():
    errors = []
    with open("./erreurs.txt", "r") as f:
        for line in f:
            if line.strip():
                if "No such file or directory" in line:
                    errors.append(line.strip())
    print("Nous n'avons pas pu trouver les fichiers suivants :")
    for error in errors:
        print(f" - {error}")


def create_pnjs_en_masse(nb):
    factory = PNJFactory()
    for _ in range(nb):
        factory.generate()

if __name__ == "__main__":
    #get_all_notes()
    create_pnjs_en_masse(500000)



    # Exemple d'utilisation
    #total_habitants = calculer_habitants_totaux()
    #print(f"Total des habitants dans le dossier 'villes' : {total_habitants}")
    #for ville, habitants, pourcentage in proportions_par_ville():
    #    print(f"{ville} : {habitants} habitants ({pourcentage}%)")
    #print(ChatGPT.analyseImage("./data/Bastion Impérial/120.jpeg", "Décris moi cette image"))
    #get_villes_to_faire()
    #get_villes_to_purifier()
    #create()
    #nalyze_error()
    """
    resultats = analyser_champs_par_fichier(dossier)
    
    with open("résumé_unifié.json", "w", encoding="utf-8") as out:
        json.dump(resultats, out, indent=2, ensure_ascii=False)

    print("OK Fusion terminée. Résultat dans 'résumé_unifié.json'")
    #total = calculer_total_input_tokens("./data/api_cost")
    refactor_villes(dossier)
    """