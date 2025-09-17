import json
import os


class IDGetter:
    FACTION = "FACTION_"
    PERSON = "PERSON_"
    PLACE = "PLACE_"
    POI = "POI_"
    SCENE = "SCENE_"

    def __init__(self):
        self.list_of_ids = []


    def deep_get(self, d: dict, keys: str, sep="."):
        for key in keys.split(sep):
            if isinstance(d, dict):
                d = d.get(key)
            else:
                return None
        return d


    def collect(self, folder: str, type: str):
        """Collects all IDs from the given folder."""
        try:
            with open(folder, 'r', encoding='utf-8') as file:
                data = json.load(file)
                id = self.deep_get(data, "flags.scene-packer.sourceId")
                if id:
                    id = id.split(".")[-1]
                    self.list_of_ids.append({"type": type, "id": id, "name": data.get("name", "Unknown")})
                else:
                    print(f"No ID found in {folder}.")
        except FileNotFoundError:
            print(f"File {folder} not found.")
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {folder}.")

    def get(self, type: str, name: str) -> str:
        """Returns the ID for the given type and name."""
        for item in self.list_of_ids:
            if item["type"] == type and item["name"] == name:
                return item["id"]
        return None

    def collect_from_folder(self, type: str):
        """Collects all IDs from all files in the given folder."""
        folder_path = f"./data/foundry/{type.lower()}/"
        for filename in os.listdir(folder_path):
            if filename.endswith(".json"):
                self.collect(os.path.join(folder_path, filename), type)
        return self.list_of_ids
    



