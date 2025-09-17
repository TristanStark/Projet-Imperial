
import openai
import json
from time import gmtime, strftime
import uuid
import requests
import shutil
import random
import string
from src.utils.logger import log_function_call
import base64
import hashlib
from typing import Any


#openai.api_key = OPEN_AI_SECRET_KEY

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


class _ChatGpt:
    """Chat GPT"""
    def __init__(self) -> None:
        self.client = openai.OpenAI()
        self.batch_name = strftime("%Y-%m-%d-%H:%M", gmtime())
        self.contexte = self.loadContext()
        self.disable_details = "I NEED to test how the tool works with extremely simple prompts. DO NOT add any detail, just use it AS-IS:"

    def loadContext(self) -> str:
        """Renvoie le contexte"""
        data = ""
        with open(r"H:\github\Projet Impérial 4\data\contexte.txt", "r", encoding="utf-8") as f:
            for line in f.readlines():
                data += line
        return data
    
    @log_function_call
    def getNbTokens(self, message: str) -> int:
        """Renvoie le nombre de tokens du message"""
        num_tokens = len(self.encoding.encode(self.contexte + " " + message))
        return num_tokens

    def analyseImage(self, image_path: str, prompt: str) -> str:
        """Analyse une image et renvoie le résultat"""
        base64_image = encode_image(image_path)


        response = self.client.responses.create(
            model="gpt-4o",
            input=[
                {
                    "role": "user",
                    "content": [
                        { "type": "input_text", "text": prompt },
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    ],
                }
            ],
        )
        return response.output_text
    
    @log_function_call
    def getMessage(self, message: str) -> str:
        """Envoie un message à ChatGPT et renvoie le résultat"""
        response = openai.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[{"role": "system", "content": self.contexte},
                      {"role": "user", "content": message}]
        )
        return response.choices[0].message
    
    @log_function_call
    def getMessageWithJSON(self, message: str, format, context = True, temperature = 0.4):
        """Renvoie un objet JSON"""
        #print(f"[INFO] [ChatGPT] Envoi de la requête : {message}")
        # Todo: Log les usages de tokens entrée et tokens sortie

        if context:
            response = self.client.beta.chat.completions.parse(
                model="gpt-4.1-nano",
                messages=[{"role": "system", "content": self.contexte},
                        {"role": "user", "content": message}],
                response_format=format,
                top_p=temperature
            )
            return response.choices[0].message.parsed
        else:
            response = self.client.beta.chat.completions.parse(
                model="gpt-4.1-nano",
                messages=[{"role": "user", "content": message}],
                response_format=format,
                top_p=temperature
            )
            return response.choices[0].message.parsed
            
    @log_function_call
    def sanitize(self, message: str) -> str:
        """Renvoie le message expurgé de ses simples quotes"""
        return message.replace("'", " ")
    
    def sendByBatch(self, requete: str, format, batch_name: str, contexte = True) -> None:
        """Transforme la requête en batch"""
        r = {}
        if contexte:
            r = {
                "custom_id": f"{str(uuid.uuid4().hex)}", 
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model":"gpt-4.1-nano",
                    "messages":[{"role": "system", "content": contexte},
                            {"role": "user", "content": requete}],
                    "response_format": format,
                }
            }
        else:
            r = {
                "custom_id": f"{str(uuid.uuid4().hex)}", 
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model":"gpt-4o-mini",
                    "messages":[{"role": "user", "content": requete}],
                    "response_format": format().dict(),
                }
            }

        with open(f"./data/batches/{batch_name}.jsonl", "a+") as outputfile:
            json.dump(r, outputfile)
            outputfile.write("\n")

    @log_function_call
    def generateImage(self, requete: str) -> str:
        """Génère une image, la sauvegarde et renvoie le nom"""
        name = str(uuid.uuid4().hex)
        response = self.client.images.generate(
            model="dall-e-3",
            prompt=  requete,
            size="1024x1024",
            quality="hd",
            style="vivid"
        )
        image_url = response.data[0].url
        r = requests.get(image_url, stream=True)
        if r.status_code == 200:
            with open(f"./data/images/{name}.png", 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
        return name

    @log_function_call
    def generate_unique_id(self):
        characters = string.ascii_letters + string.digits  # Lettres majuscules, minuscules et chiffres
        unique_id = ''.join(random.choices(characters, k=16))  # Génère une chaîne de 16 caractères
        return unique_id
    
    @log_function_call
    def transcript(self, fileName: str) -> str:
        """Transcrit le fichier audio et renvoie la transcription"""
        audio_file = open(fileName, "rb")
        transcript = self.client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="verbose_json"
        )

        transcription = ""
        last_end_time = 0
        pause_threshold = 1.0  # Seuil de 1 seconde pour insérer un saut de ligne

        for segment in transcript.segments:
            start_time = segment.start
            end_time = segment.end
            text = segment.text

            # Ajout d'un saut de ligne si la pause est supérieure au seuil
            if start_time - last_end_time > pause_threshold:
                transcription += "\n"

            transcription += text.strip() + " "
            last_end_time = end_time

        return transcription

    def generate_entry_hash(self, entry_data: dict, ignore_fields: list[str] = None) -> str:
        """
        Calcule un hash SHA-1 stable basé sur le contenu d’un journal (hors champs volatiles).
        """
        if ignore_fields is None:
            ignore_fields = ["_stats", "ownership", "_id", "pages.0._stats"]

        def strip_ignored(data: Any, path: str = "") -> Any:
            if isinstance(data, dict):
                return {
                    k: strip_ignored(v, f"{path}.{k}" if path else k)
                    for k, v in data.items()
                    if f"{path}.{k}" not in ignore_fields
                }
            elif isinstance(data, list):
                return [strip_ignored(v, f"{path}[]") for v in data]
            return data

        stripped = strip_ignored(entry_data)
        as_json = json.dumps(stripped, sort_keys=True, separators=(",", ":"))
        return hashlib.sha1(as_json.encode("utf-8")).hexdigest()


ChatGPT = _ChatGpt()

