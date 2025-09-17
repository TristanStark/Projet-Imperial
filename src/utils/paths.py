from pathlib import Path

# Répertoire d'export des images et JSON Foundry
EXPORT_BASE_PATH = Path("modules/les-reliques-des-ainees/actors")

# Répertoire source des images générées par l'IA
IMAGE_SOURCE_PATH = Path("./data/images")

# Répertoire des bordures
BORDURE_PATHS = {
    "nature": Path("./data/Tokens/bordure_arbres_vide.png"),
    "moderne": Path("./data/Tokens/bordure_moderne_vide.png"),
    "perse": Path("./data/Tokens/bordure_persian_vide.png"),
    "default": Path("./data/Tokens/token_vide_2.png"),
}

# Bordure spéciale pour détection dans l'image
BORDURE_CODE = (255, 0, 82, 255)
