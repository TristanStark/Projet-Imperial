import glob
from src.monsters.monsters import MonsterPhysique
from math import ceil
from shutil import copyfile
from os import makedirs
from src.utils.logger import log_function_call
from tqdm import tqdm

class _too_many_tokens:
    def __init__(self, nb_variations_per_tokens = 5) -> None:
        """l'accesseur physique des nouveaux monstres de type too_many_tokens"""
        self.nbVariations = nb_variations_per_tokens
        self.path = "./data/Tokens/too_many_tokens/Tokens/"

    @log_function_call
    def determinate_how_many_variations(self, directory: str) -> int:
        """Détermine combien de variations de tokens on doit faire"""
        return ceil(len(glob.glob(self.path + f"{directory}/*.webp")) / self.nbVariations)
    
    @log_function_call
    def getNames(self) -> list[str]:
        """Renvoie la liste des monstres à générer"""
        names = []
        with open("./data/Tokens/too_many_tokens/names.txt", "r", encoding="utf-8") as f:
            for line in f.readlines():
                line = line.strip("\n")
                if line != "Commoner" and line != "Gnome Bard":
                    names.append(line.strip("\n"))
        return names


    @log_function_call
    def generate(self, nb = -1) -> list[(str, str)]:
        """Génère"""
        names = self.getNames()
        result = []
        i = 0
        progress_bar = tqdm(total=min(len(names), nb), desc="Generating monsters", unit="monster")
        nb_modules = 0
        
        for name in names:
            if nb != -1 and i < nb:
                # Génères les stats
                monsters = self.generateOne(name)
                result.append((name, monsters))
                # Pour chaque monstre on le foundryse
                token_variation = 0
                for variations in monsters.variations:
                    #f.write("[")
                    name2 = variations.name.replace(" ", "_")
                    foundry_json, id = MonsterPhysique.foundry(variations, str(token_variation), name.replace(" ", "_"))
                    with open(f"./data/foundry/les-reliques-des-ainees/packs/monsters_0/_source/{name2}_{id}.json", "a+", encoding="utf-8") as f:
                        token_variation = 0
                        #message += foundry_json
                        #message += ","
                        token_variation += 1
                        f.write(foundry_json)
                    #message = message[:-1]
                    #f.write("]")
            if nb_modules % 50 == 0:
                nb_modules += 1
            i += 1
            progress_bar.update(1)
        progress_bar.close()
        """
        for name in names:
            if nb != -1 and i < nb:
                # Génères les stats
                monsters = self.generateOne(name)
                result.append((name, monsters))
                # Pour chaque monstre on le foundryse
                with open(f"./data/foundry/les-reliques-des-ainees/monsters_{nb_modules}/_source/{name}.json", "a+", encoding="utf-8") as f:
                    for variations in monsters.variations:
                        f.write(MonsterPhysique.foundry(variations, str(i), name))
                        i += 1

            i += 1
        return result
        """



    @log_function_call
    def moveImages(self) -> None:
        """bouge toutes les images dans les folders correspondants"""
        names = self.getNames()
        for name in names:
            nb_variations = self.determinate_how_many_variations(name)
            files = glob.glob(self.path + f"{name}/*.webp")
            nb_files = len(files)
            new_name = name.replace(" ", "")
            makedirs(f"./data/foundry/les-reliques-des-ainees/monstres/{new_name}")
            k = 0
            for i in range(nb_variations):
                for j in range(self.nbVariations):
                    if k < nb_files:
                        copyfile(files[k], f"./data/foundry/les-reliques-des-ainees/monstres/{new_name}/{new_name}_{i}_{j}.webp")
                    k += 1

    @log_function_call
    def getNombreTotalDeVariation(self) -> int:
        """Détermine le nombre total de variations générées"""
        total_variations = 0
        names = self.getNames()
        for name in names:
            total_variations +=  self.determinate_how_many_variations(name)
        print("Nombre de monstres   >", len(names))
        print("Nombre de variations >", total_variations)
        print(f"Moyenne Var / Monstre>{total_variations/len(names):.2f}")
        return total_variations


    @log_function_call
    def generateOne(self, name: str):
        """Pass"""
        nb_variations = self.determinate_how_many_variations(name)
        monstre = MonsterPhysique.generate(name, nb_variations)
        # Chaque variation a 10 tokens, donc on doit renommer les tokens en "variation_1_nb_{1; }"
        # Ensuite: pour chaque variation, faut le jsoniser pour foundry
        # en token: glob sur les variations
        # en data: on jsonise
        return monstre

BatchTooManyTokens = _too_many_tokens()