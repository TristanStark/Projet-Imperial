from PIL import Image
import numpy as np
from uuid import uuid4
from os import makedirs
from src.utils.logger import log_function_call
from src.utils.paths import IMAGE_SOURCE_PATH, EXPORT_BASE_PATH, BORDURE_PATHS, BORDURE_CODE
from pathlib import Path


class _TokenIzer:
    def __init__(self):
        self.bordures = {
            key: self.load_image(path)
            for key, path in BORDURE_PATHS.items()
        }

    def load_image(self, path: str) -> list:
        image = Image.open(path)
        pixels = image.load()
        width, height = image.size
        result = []
        for y in range(height):
            row = [pixels[x, y] for x in range(width)]
            result.append(row)
        return result

    @log_function_call
    def tokenize(self, token_name: str, base_image: str, bordure_key: str, output_folder: str, midjourney: False) -> str:
        image_path = f"{base_image}.png"
        save_dir = Path(output_folder)
        if not midjourney:
            image_path = IMAGE_SOURCE_PATH / f"{base_image}.png"
            save_dir = EXPORT_BASE_PATH / output_folder
            if not save_dir.exists():
                makedirs(save_dir)
        image = Image.open(image_path)
        pixels = image.load()
        width, height = image.size


        raw_path = save_dir
        if not midjourney:
            raw_path = save_dir / f"{token_name}_RAW.png"
        image.save(raw_path)

        bordure = self.bordures.get(bordure_key, self.bordures["default"])
        new_image = []
        for y in range(height):
            row = []
            for x in range(width):
                base_pixel = bordure[y][x]
                cpixel = pixels[x, y]
                if base_pixel == BORDURE_CODE:
                    row.append((cpixel[0], cpixel[1], cpixel[2], 255))
                else:
                    row.append(base_pixel)
            new_image.append(row)

        array = np.array(new_image, dtype=np.uint8)
        new_image = Image.fromarray(array)

        final_path = save_dir 
        if not midjourney:
            final_path = save_dir / f"{token_name}.png"
        new_image.save(final_path)

        return str(final_path)

    def generate_unique_id(self) -> str:
        return str(uuid4())


Tokenizer = _TokenIzer()
