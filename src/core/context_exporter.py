"""

Qu'est-ce que je veux faire?
J'ai des villes, sous plusieurs formats. Ces villes j'ai dans contexte et dans data/villes. 
Dans le contexte:
- les villes sont reliées à des factions
- les villes sont reliées à des quêtes

Dans data/villes:
- les villes sont reliées à des images
- Elles ont également beaucoup plus de détails (habitants, type de ville, etc.)

In fine, je dois avoir:
- Une scène qui représente la ville
- Cette scène doit être lié à un JournalEntry
- Un journalEntry qui contient la ville
- Ce journalEntry doit être lié aux JournalEntriesFactions
- Ce journalEntry doit être lié aux JournalPersonns pour le gouvernements
- Avec les secteurs économiques j'aurais probablement des shops à générer

Les quêtes elles c'est des journalentries simples qui sont dans un dossier à part


J'ai aussi dans mon contexte des Places -> JournalEntriesPOI
Corresponds à villes["lieux-notables"] dans data/villes

J'ai également des factions -> JournalEntriesFactions
Corresponds à villes["factions"] dans data/villes mais aussi à des factions dans le contexte

"""


from PIL import Image
from src.models.scenes import SceneModel, Background



# Fonction de création de scène
def create_scene_from_image(image_path: str, name: str, real_path: str) -> SceneModel:
    """Fonction pour créer une scène à partir d'une image et d'un nom"""
    print(f"Création de la scène à partir de l'image : {image_path} et du nom : {name}")
    with Image.open(image_path) as img:
        width, height = img.size

    scene = SceneModel(
        folder="ejNj7kWMiIkbduqT",
        name=name,
        navName=name,
        background=Background(src=real_path),
        width=width,
        height=height
    )
    return scene

# Exemple (non exécuté ici) :
# scene = create_scene_from_image("path/to/image.jpg", "Le Laboratoire")
# print(scene.model_dump_json(indent=2))

