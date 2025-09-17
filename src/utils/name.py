import random
import json
import os
from collections import defaultdict
from typing import List, Dict

MODEL_FILE = "./data/markov/humains/markov_models.json"
CORPUS_FILE = "./data/markov/humains/StateNames.csv"

class MarkovChain:
    def __init__(self, prob_order2=0.5):
        self.prob_order2 = prob_order2
        self.model1 = defaultdict(list)
        self.model2 = defaultdict(list)

    def train(self, names: List[str]):
        for name in names:
            name = name.strip().lower()
            padded = "~~" + name + "\0"

            # Ordre 1
            for i in range(len(padded) - 2):
                key1 = padded[i+1]
                self.model1[key1].append(padded[i+2])

            # Ordre 2
            for i in range(len(padded) - 2):
                key2 = padded[i:i+2]
                self.model2[key2].append(padded[i+2])

    def generate(self, max_length=15) -> str:
        key = "~~"
        result = ""

        while True:
            if len(result) == 0:
                next_chars = self.model1.get("~", [])
            else:
                use_order2 = random.random() < self.prob_order2 and len(result) >= 1
                if use_order2:
                    context = key[-2:]
                    next_chars = self.model2.get(context, [])
                else:
                    context = key[-1]
                    next_chars = self.model1.get(context, [])

            if not next_chars:
                break

            next_char = random.choice(next_chars)
            if next_char == "\0" or len(result) >= max_length:
                break

            result += next_char
            key = key[1:] + next_char
        #print("GENERATE! -> ", result)
        # C'est cassé, donc on renvoie un todo :p
        result = "TODO!!!!!"
        return result.capitalize()

    def save(self, path=MODEL_FILE):
        with open(path, "w", encoding="utf-8") as f:
            json.dump({
                "model1": dict(self.model1),
                "model2": dict(self.model2)
            }, f)

    def load(self, path=MODEL_FILE):
        if not os.path.exists(path):
            print("ERREUR LOADING MARKOV!!!!")
            print("[TRAIN] Entraînement du modèle...")
            with open(CORPUS_FILE, encoding="utf-8") as f:
                noms = f.read().splitlines()
            self.train(noms)
            self.save()
            print("[OK] Modèle entraîné et sauvegardé.")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.model1 = defaultdict(list, {k: v for k, v in data["model1"].items()})
            self.model2 = defaultdict(list, {k: v for k, v in data["model2"].items()})
        return True

# Exemple d'utilisation
if __name__ == "__main__":
    markov = MarkovChain(prob_order2=0.5)

    if not markov.load():
        print("🔄 Entraînement du modèle...")
        with open(CORPUS_FILE, encoding="utf-8") as f:
            noms = f.read().splitlines()
        markov.train(noms)
        markov.save()
        print("✅ Modèle entraîné et sauvegardé.")
    else:
        print("✅ Modèle chargé depuis le fichier.")

    print("\n🌱 Noms générés :")
    for _ in range(20):
        print("-", markov.generate())
