import random
from collections import defaultdict
import string
import simplejson as json
from src.utils.parameters import PRINT_DEBUG

class MarkovChain:
    def __init__(self):
        self.chain = defaultdict(list)

    def train(self, text):
        # On parcourt le texte avec une fenêtre de taille 2 pour construire les paires de contexte (lettres précédentes) et les lettres suivantes
        for i in range(len(text) - 2):
            context = text[i:i + 2].lower()
            next_letter = text[i + 2]
            self.chain[context].append(next_letter.lower())

    def _generate(self, start, length) -> str:
        # Vérifie que le démarrage est dans le modèle
        if start not in self.chain:
            return None
        
        result = start
        current_context = start

        for _ in range(length - 2):
            next_letter_options = self.chain.get(current_context)
            if not next_letter_options:
                break  # Stop si on n'a pas d'options pour la lettre suivante
            
            # Choisir la prochaine lettre aléatoirement parmi les options disponibles
            next_letter = random.choice(next_letter_options)
            result += next_letter

            # Met à jour le contexte pour inclure les deux dernières lettres
            current_context = result[-2:]

        return result

    def generate(self) -> str:
        """Génère un nom"""
        # Débute la génération avec deux lettres (par exemple "Th")
        length = random.randint(3, 8)  # Longueur du texte généré
        for _ in range(80):
            start_sequence = ''.join(random.choices(string.ascii_letters, k=2))
            name = self._generate(start_sequence, length)
            if name is not None:
                return name.capitalize()
        raise Exception("Impossible de générer un nom en 20 essais")


    def save(self):
        """Save le truc sous format json?"""
        json_data = json.dumps(self.chain)
        with open("./data/markov/humains/markov_data.json", "a+") as f:
            f.write(json_data)

    def load(self):
        """Récupère le json pour se sauvegarder?"""
        if PRINT_DEBUG:
            print("Markov> Début du chargement")
        with open("./data/markov/humains/markov_data.json", "r") as fichier:
            data = json.load(fichier)
        self.chain = convertir_en_defaultdict(data)
        if PRINT_DEBUG:
            print("Markov> Fin du chargement")


def convertir_en_defaultdict(data):
    if isinstance(data, dict):
        # Recursion pour convertir les sous-dictionnaires en defaultdict(list)
        return defaultdict(list, {k: convertir_en_defaultdict(v) for k, v in data.items()})
    elif isinstance(data, list):
        # Appliquer la conversion sur chaque élément de la liste
        return [convertir_en_defaultdict(item) for item in data]
    else:
        return data  # Retourner la valeur si ce n'est ni un dict ni une liste

# Lecture du texte depuis un fichier pour l'entraînement
def load_text(filename):
    text = ""
    with open(filename, 'r', encoding='utf-8') as file:
        for lines in file.readlines():
            line = lines.split(",")
            text += f"{line[1]}"
    return text

if __name__ == "__main__":
    
    # Utilisation de la chaîne de Markov
    filename_prenom = './data/markov/humains/StateNames.csv'  # Remplacez par le chemin de votre fichier texte
    prenoms = load_text(filename_prenom)

    # Initialisation et entraînement
    markov_prenom = MarkovChain()
    markov_prenom.train(prenoms)
    markov_prenom.save()
    #markov_prenom.load()

    # Génération de texte
    start_sequence = letters = ''.join(random.choices(string.ascii_letters, k=2))
    # Débute la génération avec deux lettres (par exemple "Th")
    length = random.randint(3, 8)  # Longueur du texte généré

    #generated_text = markov_prenom.generate("ma", length)
    #print("Texte généré :", generated_text)
