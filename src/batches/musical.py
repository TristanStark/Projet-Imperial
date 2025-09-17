import warnings
import subprocess
import json
from pydub import AudioSegment
import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TRCK
import tensorflow_hub as hub
import numpy as np
import librosa
import requests
import time
warnings.filterwarnings('ignore')  # Désactive tous les warnings Python

"""Rechercher les musiques liées à un artiste ou OST :

Utiliser une bibliothèque comme yt-dlp pour rechercher des vidéos YouTube liées à l'artiste ou l'OST.
Optionnel : Croiser avec des API comme Spotify ou Genius pour enrichir les données.
Télécharger les musiques et les diviser par chapitres :

Récupérer les chapitres et les timestamps des vidéos pour découper chaque piste.
Découper automatiquement les musiques en utilisant les timestamps et pydub ou ffmpeg.
Supprimer les doublons :

Comparer les fichiers audio (ou les titres) pour détecter et supprimer les doublons en fonction de la similarité.
Classer les musiques par énergie et thème :

Utiliser des outils comme librosa pour extraire des caractéristiques audio (énergie, tempo, etc.).
Classifier les musiques automatiquement en utilisant un modèle d'apprentissage automatique.
Créer des playlists personnalisées :"""


class MusicalDownlaoder():
    def __init__(self):
        pass

    def get_playlist_ids(self, playlist_url):
        """Récupérer les ID de toutes les vidéos d'une playlist YouTube"""
        command = f'yt-dlp --flat-playlist --get-id "{playlist_url}"'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip().splitlines()


    def getListTitles(self, artist_name: str):
        """Récupérer une liste de titres à partir d'un artiste ou d'une OST"""
        command = f'yt-dlp "ytsearch10:{artist_name}" --get-id --get-title'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout
    
    def downloadMusic(self, url: str, title: str):
        """Télécharger une musique à partir d'une URL YouTube"""
        command = f'yt-dlp -x  -o "./data/Darktide/%(title)s.%(ext)s" --audio-format mp3 --add-metadata --embed-chapters {url}'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout
    
    def getID(self, list_titles: str):
        """Extraire les ID des vidéos YouTube et les titres associés"""
        liste = list_titles.split("\n")
        tuples_list = [(liste[i], liste[i + 1]) for i in range(0, len(liste) - 1, 2)]
        return tuples_list

    def checkMetadata(self, url: str, id: str):
        """Vérifier les métadonnées d'une musique"""
        print("  Vérification des métadonnées de la musique: ", id)
        command = f'yt-dlp --print-json "{url}"'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        with open(f"./data/{id}.json", "w") as f:
            f.write(result.stdout)
        return result.stdout

    def traitementSingleMusic(self, id: str, title: str, artist_name: str):
        """Traiter une musique"""
        print("  Téléchargement de la musique: ", title)
        url = f"https://www.youtube.com/watch?v={id}"
        #check les métadonnées pour vérifier si la musique a des chapitres
        self.checkMetadata(url, id)
        # Télécharger la musique
        self.downloadMusic(url, title)
        # Vérifier si la musique a des chapitres
        chapters = self.getChapters(id)
        # Si la musique a des chapitres, la découper
        if len(chapters) > 0:
            self.splitMusic(f'./data/{title}.mp3', chapters, id, artist_name)
            # Vu qu'on vient de le séparer en chapitre on supprime la grande
            os.remove(f'./data/{title}.mp3')

    def downloadAllMusic(self, artist_name: str):
        """Télécharger toutes les musiques d'un artiste"""
        print("Téléchargement de la musique de l'artiste: ", artist_name)
        list_titles = self.getListTitles(artist_name)
        list_titles = self.getID(list_titles)
        print("Liste des titres acquises")
        for music in list_titles:
            title, id = music
            try:
                self.traitementSingleMusic(id, title, artist_name)
            except Exception as e:
                print("Erreur lors du traitement de la musique: ", title)
                print(e)
        # On vire les doublons
        self.dedoublonne()

    def dedoublonne(self):
        """Supprimer les doublons dans un dossier de musiques"""
        # Dossier contenant les fichiers .mp3
        music_folder = "./data/"  # Remplace par ton dossier de musiques

        # Dictionnaire pour garder une trace des titres déjà vus
        seen_titles = {}
        print(" Vérification des doublons...")
        # Parcourir tous les fichiers .mp3 du dossier
        for filename in os.listdir(music_folder):
            if filename.endswith(".mp3"):
                filepath = os.path.join(music_folder, filename)
                
                # Charger les métadonnées
                audio = MP3(filepath, ID3=ID3)
                title = audio.tags.get("TIT2", None)  # TIT2 correspond au titre
                title_text = str(title.text[0]) if title else None

                if title_text:
                    # Vérifier si le titre est déjà présent
                    if title_text in seen_titles:
                        print(f"  Doublon détecté : {filename}. Supprimé.")
                        os.remove(filepath)  # Supprime le fichier doublon
                    else:
                        print("  Ajout du titre: ", title_text)
                        seen_titles[title_text] = filepath
        print("  Doublons vérifiés et supprimés !")

    def splitMusic(self, music_path: str, chapters: list, id: str, artist_name: str):
        """Découper une musique en fonction des chapitres"""
        print("  Découpage de la musique en chapitres...")
        audio = AudioSegment.from_file(music_path, format="mp3")
        # Découper l'audio en fonction des chapitres
        track_number = 1
        for chapter in chapters:
            title = chapter['title']
            start_time = chapter['start_time'] * 1000  # Convertir en millisecondes
            end_time = chapter['end_time'] * 1000  # Convertir en millisecondes

            # Découper le segment correspondant au chapitre
            segment = audio[start_time:end_time]

            # Sauvegarder le fichier audio découpé
            output_path = f"./data/{title}.mp3"
            segment.export(output_path, format="mp3")
            print(f"    Chapitre '{title}' exporté : {output_path}")
            self.addMetadata(output_path, title, artist_name, track_number)
            track_number += 1
        print("    Musique découpée avec succès !")

    def addMetadata(self, music_path: str, title: str, artist_name: str, track_number: int):
            """Ajouter des métadonnées à un fichier MP3"""
            # Charger le fichier MP3
            audio = MP3(music_path, ID3=ID3)

            # Ajouter des métadonnées
            audio["TIT2"] = TIT2(encoding=3, text=title)  # Titre
            audio["TALB"] = TALB(encoding=3, text="ALBUM")  # Album
            audio["TPE1"] = TPE1(encoding=3, text=artist_name)  # Artiste
            audio["TRCK"] = TRCK(encoding=3, text=str(track_number))  # Numéro de piste

            # Sauvegarder les métadonnées
            audio.save()


    def getChapters(self, id):
        """Extraire les chapitres d'une vidéo YouTube"""
        with open(f"./data/{id}.json", "r") as metadatas:
            metadata = json.load(metadatas)

        extracted_chapters = []
        # Extract chapters information
        if 'chapters' in metadata:
            chapters = metadata['chapters']
            if chapters is not None:
                for chapter in chapters:
                    start_time = chapter.get('start_time', None)
                    end_time = chapter.get('end_time', None)
                    title = chapter.get('title', None)
                    extracted_chapters.append({
                        'title': title,
                        'start_time': start_time,
                        'end_time': end_time
                    })
        os.remove(f"./data/{id}.json")
        return extracted_chapters

class MusicalClassifier():
    def __init__(self):
        self.yamnet_model = hub.load('https://tfhub.dev/google/yamnet/1')
        self.download_ontology()
        with open("./data/ontology.json") as f:
            self.ontology = json.load(f)
        # Filtrer uniquement les catégories liées à la musique
        self.music_labels = [
            entry["name"] for entry in self.ontology if "/m/04rlf" in entry.get("restrictions", [])
        ]
        self.labels = [entry["name"] for entry in self.ontology]


    def download_ontology(self):
        ontology_url = "https://raw.githubusercontent.com/audioset/ontology/master/ontology.json"
        ontology_file = "./data/ontology.json"

        # Vérifier si le fichier JSON existe déjà localement, sinon le télécharger
        if not os.path.exists(ontology_file):
            print("Téléchargement de l'ontologie AudioSet...")
            response = requests.get(ontology_url)
            if response.status_code == 200:
                with open(ontology_file, "wb") as f:
                    f.write(response.content)
                print("Ontologie téléchargée avec succès.")
            else:
                print(f"Erreur lors du téléchargement : {response.status_code}")


    # Fonction pour prédire les classes d'un fichier audio
    def classify_audio(self, file_path):
        # Charger le fichier audio avec librosa
        waveform, sr = librosa.load(file_path, sr=16000)  # YAMNet attend un échantillonnage à 16 kHz

        # Prédiction
        scores, embeddings, spectrogram = self.yamnet_model(waveform)
        scores = scores.numpy()
        
        music_predictions = {
            self.labels[i]: scores.mean(axis=0)[i]
            for i in range(len(self.labels)) if self.labels[i] in self.music_labels
        }

        # Trier les catégories musicales par probabilité
        sorted_predictions = sorted(music_predictions.items(), key=lambda x: x[1], reverse=True)[:5]
        return sorted_predictions

    def classify_all_music(self, music_folder):
        all_themes = {}
        for audio_file in os.listdir(music_folder):
            if audio_file.endswith(".mp3"):
                print(f"Classification de {audio_file}...")
                predicted_theme = self.getAudioFeatures("./data/" + audio_file)
                # Bouge la musique dans le dossier correspondant
                os.rename(f"./data/{audio_file}", f"./data/{predicted_theme}/{audio_file}")
                if predicted_theme in all_themes:
                    all_themes[predicted_theme] += 1
                else:
                    all_themes[predicted_theme] = 1
        print("Résultats de la classification :")
        for theme, count in all_themes.items():
            print(f"  {theme}: {count} musiques")
           
    def classify_theme(self, energy, tempo, spectral_centroid, spectral_bandwidth, mfcc):
        mfcc_0 = mfcc[0]
        mfcc_variance = np.var(mfcc[1:])  # Variance des autres MFCC

        # Thème Triste : Faible énergie, tempo lent, fréquence basse, MFCC bas
        if energy < 0.1:
            if tempo < 80 and spectral_centroid < 2000 and mfcc_0 < -300:
                return "Triste"
            elif tempo < 120 and mfcc_variance < 100:
                return "Exploration calme"
            else:
                return "Exploration rapide"
        
        # Thème Dramatique : Énergie moyenne, tempo modéré, brillance moyenne, MFCC complexe
        elif energy < 0.3:
            if tempo < 120 and spectral_centroid < 2500 and mfcc_variance > 150:
                return "Dramatique"
            elif spectral_bandwidth > 3000 and mfcc_variance > 100:
                return "Suspense"
            else:
                return "Action modérée"
        
        # Thème Combat : Énergie élevée, tempo rapide, fréquences riches, MFCC élevé
        else:
            if tempo > 120 and spectral_bandwidth > 3500 and mfcc_0 > -200:
                return "Combat"
            elif spectral_centroid > 2500 and mfcc_variance > 200:
                return "Action intense"
            else:
                return "Dramatique intense"

    def getAudioFeatures(self, music_path: str):
        """Extraire les caractéristiques audio d'une musique"""
        # Charger l'audio
        y, sr = librosa.load(music_path)

        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        energy = sum(abs(y)) / len(y)
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
        spectral_bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))
        mfcc = np.mean(librosa.feature.mfcc(y=y, sr=sr), axis=1)

        # Afficher les résultats
        print(f"    Tempo: {tempo}")
        print(f"    Énergie: {energy}")
        theme = self.classify_theme(energy, tempo, spectral_centroid, spectral_bandwidth, mfcc)
        print("    Thème musical: ", theme)
        return theme




if __name__ == "__main__":
    debut = time.time()
    downloader = MusicalDownlaoder()
    #downloader.downloadAllMusic("Monster Hunter Wild OST")
    #downloader.traitementSingleMusic("OblT91aXQ5c", "Frieren", "Frieren OST")
    ids = downloader.get_playlist_ids("https://www.youtube.com/playlist?list=PLtlUVhDQX5vvGhE5j5d_qu_wPyTemf4Mu")
    for id in ids:
        downloader.downloadMusic(id, id)
    """
    downloader.downloadAllMusic("Darkest Dungeon OST")
    downloader.downloadAllMusic("Gwent OST")
    downloader.downloadAllMusic("StoneShard OST")
    downloader.downloadAllMusic("The Witcher OST")
    downloader.downloadAllMusic("Thronebreaker OST")
    downloader.dedoublonne()
    """
    #classifier = MusicalClassifier()
    #classifier.classify_all_music("./data/")
    print("Temps d'exécution: ", time.time() - debut)
    #downloader.downloadMusic("https://www.youtube.com/watch?v=1lWJXDG2i0A")
    #downloader.getListTitles("Ludovico Einaudi")
    #downloader.downloadMusic("1lWJXDG2i0A")


"""
1. Caractéristique : Énergie
Définition :
L'énergie est calculée comme la moyenne des amplitudes absolues du signal audio.
Elle reflète l'intensité globale du morceau : des morceaux calmes auront une énergie faible, tandis que des morceaux forts et rythmés auront une énergie élevée.
Ce que l'énergie peut t'apprendre :
Faible énergie : Indique souvent des morceaux calmes, relaxants ou introspectifs. Exemple : exploration, triste, mystérieux.
Énergie moyenne : Correspond généralement à des morceaux équilibrés ou modérément dynamiques. Exemple : découverte, espoir, ambiance dramatique légère.
Haute énergie : Souvent associée à des morceaux intenses, rapides et excitants. Exemple : combat, action, suspense dramatique.
2. Caractéristique : Tempo
Définition :
Le tempo, mesuré en battements par minute (BPM), correspond à la vitesse perçue de la musique.
Il est directement lié à la dynamique et peut donner des indices sur l'ambiance générale.
Ce que le tempo peut t'apprendre :
Tempo lent (< 80 BPM) : Convient aux thèmes calmes, tristes ou contemplatifs. Exemple : exploration lente, tristesse, désolation.
Tempo modéré (80-120 BPM) : Évoque des ambiances équilibrées, souvent utilisées pour des scènes d'exploration ou des moments dramatiques. Exemple : mystère, découverte, dramatique.
Tempo rapide (> 120 BPM) : Associé à l'énergie, la vitesse et le dynamisme. Exemple : combat, action intense, urgence.
3. Approche pour classifier par thème
Combinaison énergie + tempo
En combinant énergie et tempo, tu peux commencer à définir des zones thématiques. Voici un guide pour classifier des morceaux en fonction de ces deux caractéristiques :

Thème	Énergie	Tempo
Exploration	Faible à moyenne	Lent à modéré (< 120 BPM)
Combat	Élevée	Rapide (> 120 BPM)
Dramatique	Moyenne	Modéré (80-120 BPM)
Triste	Faible	Lent (< 80 BPM)
Suspense	Moyenne	Variable (avec des variations abruptes)

Spectral Centroid
Indique où se situe le "centre" de la fréquence dominante dans le spectre.
Valeurs typiques :
< 2000 Hz : Sons graves et doux → Triste, Exploration.
2000-2500 Hz : Équilibré → Dramatique, Mystère.
> 2500 Hz : Sons aigus, brillants → Combat, Action.
Spectral Bandwidth
Mesure la "largeur" spectrale, indiquant la diversité des fréquences.
Valeurs typiques :
< 3000 Hz : Sons simples, doux → Triste, Exploration calme.
3000-4000 Hz : Sons riches et dynamiques → Dramatique, Suspense.
> 4000 Hz : Sons complexes et intenses → Combat, Action intense.
MFCC
Les coefficients MFCC capturent la texture du son.
Utilisation :
Analyse la variation des premiers coefficients (par exemple, MFCC[0]) pour différencier les textures musicales :
MFCC[0] faible (valeurs négatives élevées) : Sons graves, introspectifs → Triste, Exploration.
MFCC[0] élevé (valeurs proches de zéro) : Sons aigus et dynamiques → Action, Combat.




"""