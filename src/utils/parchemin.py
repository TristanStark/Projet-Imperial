from PIL import Image, ImageFont, ImageDraw
from random import choice
import unicodedata
from pathlib import Path
import os
import numpy as np

def get_max_red_height(mask_array, zone_start, zone_end, y_start, max_search=200, tolerance=30):
    """
    Retourne la hauteur maximale commune de rouge sous la ligne y_start, entre zone_start et zone_end.
    """
    height = mask_array.shape[0]
    for y_offset in range(max_search):
        y = y_start + y_offset
        if y >= height:
            return y_offset  # dépassé

        for x in range(zone_start, zone_end):
            pixel = mask_array[y, x]
            if not np.all(np.abs(pixel - [125, 125, 125]) < tolerance):
                return y_offset  # première colonne non rouge trouvée

    return max_search  # zone rouge complète sur max_search px


class Mask:
    def __init__(self, path, seal=True, titre=True):
        self.path = path
        self.image = Image.open(path).convert("L")
        self.array = np.array(self.image)
        self.titre = titre
        self.width, self.height = self.array.shape[1], self.array.shape[0]
        self.seal = seal


    def __repr__(self):
        return f"Mask(path={self.path}, seal={self.seal}, titre={self.titre})"

class FontStyle:
    def __init__(self, name, title_size, text_size, max_length, line_height, allow_upper=True, title_bonus=-8, max_lines=10):
        path = f"./data/tavernes/fonts/{name}.ttf"
        self.name = name
        self.font_title = ImageFont.truetype(path, title_size)
        self.font_text = ImageFont.truetype(path, text_size)
        self.path = path
        self.title_size = title_size
        self.text_size = text_size
        self.max_length = max_length
        self.line_height = line_height
        self.allow_upper = allow_upper
        self.title_bonus = title_bonus
        self.max_lines = max_lines

    def font(self, is_title):
        return self.font_title if is_title else self.font_text

    def line_limit(self, is_title):
        return self.max_length + (self.title_bonus if is_title else 0)

    def __repr__(self):
        return f"FontStyle(name={self.name}, title_size={self.title_size}, text_size={self.text_size})"

def remove_accents(text):
    normalized = unicodedata.normalize('NFD', text)
    return ''.join(c for c in normalized if not unicodedata.combining(c))

class Box:
    def __init__(self, x, y, width, height, is_title=False):
        self.is_title = is_title
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __repr__(self):
        return f"Box(x={self.x}, y={self.y}, width={self.width}, height={self.height})"

class Layout:
    def __init__(self, liste_boxes: list):
        self.liste_boxes = liste_boxes

class Parchment:
    def __init__(self, image_name, listMask, x_text, y_text, x_price, y_price):
        self.image_path = f"./data/tavernes/parchment/{image_name}.png"
        self.x_text, self.y_text = x_text, y_text
        self.x_price, self.y_price = x_price, y_price
        self.font = None
        self.reset()

        self.mask = listMask

    def chooseMask(self):
        return choice(self.mask)
    
    def reset(self):
        self.image = Image.open(self.image_path)
        self.canvas = ImageDraw.Draw(self.image)
        self.line = 0
        self.bonus = 0

    def _split_lines(self, text, is_title, allow_upper):
        text = remove_accents(text)
        words = text.split()
        chunks, current = [], []

        for word in words:
            word = word if allow_upper else word.lower()
            if len(' '.join(current + [word])) > self.font.line_limit(is_title) + self.bonus:
                chunks.append(' '.join(current))
                current = [word]
            else:
                current.append(word)

        if current:
            chunks.append(' '.join(current))

        return chunks

    def _coord(self, is_title):
        offset = int(self.font.title_size / 2) if is_title else 0
        x = self.x_text + offset
        y = self.y_text + self.line * self.font.line_height
        self.line += 1
        return x, y

    def draw_text_in_mask_adaptive_font(self, text, title, font_path="arial.ttf", max_font_size=40, min_font_size=8, output_path="output.png") -> bool:
        text = remove_accents(text)
        self.choosenMask = self.chooseMask()
        if output_path.suffix != ".png":
            output_path = output_path.with_suffix(".png")
        print("[DEBUG]" + "-" * 50)
        print(f"[DEBUG] Texte : {text}")
        print(f"[DEBUG] Titre : {title}")
        print(f"[DEBUG] Image : {self.image_path}")
        print(f"[DEBUG] Masque : {self.choosenMask}")
        print(f"[DEBUG] Font : {font_path}")
        print(f"[DEBUG] Export : {output_path}")
        print("[DEBUG] " + "-" * 50)
        
        image = Image.open(self.image_path).convert("RGBA")
        mask = Image.open(self.choosenMask.path).convert("L")
        mask_array = np.array(mask)
        width, height = mask_array.shape[1], mask_array.shape[0]
        found_title_font = False
        title_font = ImageFont.truetype(font_path, max_font_size + 10)
        title_font_size = max_font_size + 10
        font = ImageFont.truetype(font_path, max_font_size)
        font_size_found = False
        for font_size in range(max_font_size, min_font_size - 1, -1):
            temp_image = image.copy()
            draw = ImageDraw.Draw(temp_image)
            if not found_title_font:
                title_font_size = font_size + 0
                title_font = ImageFont.truetype(font_path, font_size + 0)
            if not font_size_found:
                font = ImageFont.truetype(font_path, font_size)
            line_height = font.getbbox("A")[3] - font.getbbox("A")[1]
            line_height_title = title_font.getbbox("A")[3] - font.getbbox("A")[1]

            spacing = 2

            words = text.split()
            word_index = 0
            y = 0

            while y + line_height < height and word_index < len(words):
                row = mask_array[y:y+line_height, :]
                in_zone = False
                zone_start = 0

                for x in range(width):
                    col_slice = row[:, x]
                    is_black = np.all(col_slice < 50)
                    if is_black and not in_zone:
                        in_zone = True
                        zone_start = x
                    elif not is_black and in_zone:
                        in_zone = False
                        zone_end = x
                        max_width = zone_end - zone_start
                        line = ""
                        temp_index = word_index

                        while temp_index < len(words):
                            test_line = (line + " " if line else "") + words[temp_index]
                            bbox = draw.textbbox((0, 0), test_line, font=font)
                            w = bbox[2] - bbox[0]
                            if w <= max_width:
                                line = test_line
                                temp_index += 1
                            else:
                                break

                        if line:
                            draw.text((zone_start, y), line, font=font, fill=(0, 0, 0, 255))
                            #print(f"✅ Taille {font_size} : Ligne à ({zone_start}, {y}) : {line}")
                            word_index = temp_index
                        if word_index >= len(words):
                            break
                y += line_height + spacing

            title_index = 0
            title_list = title.split()
            used_height = 0
            y = 0
            temp_index = 0
            h = 0
            # TITRE
            if self.choosenMask.titre:
                while y + line_height_title < height and title_index < len(title_list):
                    row = mask_array[y:y+line_height_title, :]
                    in_zone = False
                    zone_start = 0

                    for x in range(width):
                        col_slice = row[:, x]
                        is_red = np.all(col_slice == 125)
                        if is_red and not in_zone:
                            in_zone = True
                            zone_start = x
                        elif not is_red and in_zone:
                            in_zone = False
                            line = ""

                            zone_end = x
                            max_width = zone_end - zone_start
                            max_height = get_max_red_height(mask_array, zone_start, zone_end, y)
                            #print(f"📏 Zone rouge détectée de largeur {max_width}px et hauteur {max_height}px à y={y}")

                            while temp_index < len(title_list):
                                test_line = (line + " " if line else "") + title_list[temp_index]
                                #print(f"Test de la ligne : {test_line}")
                                bbox = draw.textbbox((0, 0), test_line, font=title_font)
                                w = bbox[2] - bbox[0]
                                h = bbox[3] - bbox[1]

                                if w <= max_width:
                                    # Vérifie qu’on reste dans max_height
                                    if used_height + h > max_height:
                                        print("[ERROR] Hauteur max atteinte, on arrête ici.")
                                        found_title_font = False
                                        break
                                    line = test_line
                                    temp_index += 1
                                else:
                                    found_title_font = False
                                    break

                            if line:
                                draw.text((zone_start, y), line, font=title_font, fill=(0, 0, 0, 255))
                                #print(f"✅ Taille {title_font_size} : Ligne à ({zone_start}, {y}) : {line}")
                                title_index = temp_index
                                used_height += h
                            if title_index >= len(title_list):
                                found_title_font = False
                                break
                    y += line_height_title + spacing
            else:
                # Y'a pas de titre donc on skip
                print("[INFO] Pas de titre à écrire, on skip")
                found_title_font = True

            if title_index >= len(title_list):
                found_title_font = True
                #print(f"✅ Titre entièrement écrit avec taille {title_font_size}")

            if word_index >= len(words):
                font_size_found = True

            if font_size_found and found_title_font:
                if self.choosenMask.seal:
                    temp_image.save("./temp.png")
                    if self.apposer_sceau("./temp.png", self.choosenMask.path, self.chooseSeal(), output_path):
                        print("[INFO] Image avec sceau sauvegardée")
                else:
                    temp_image.save(output_path)
                print(f"[DEBUG] Texte entièrement écrit avec taille {font_size} — image sauvegardée : {output_path}")
                return True
        temp_image.save("./rejected.png")
        print("[ERROR] Impossible d’écrire tout le texte même avec la taille minimale.")
        return False


    def chooseSeal(self):
        dossier = "./data/tavernes/seals"
        if not os.path.isdir(dossier):
            raise ValueError(f"[ERROR] Dossier introuvable : {dossier}")

        fichiers_png = [f for f in os.listdir(dossier) if f.lower().endswith(".png")]
        if not fichiers_png:
            raise ValueError("[ERROR] Aucun fichier .png trouvé dans ce dossier.")

        fichier_choisi = choice(fichiers_png)
        chemin_complet = os.path.join(dossier, fichier_choisi)
        return chemin_complet

    def load_image(self, path: str) -> list:
        image = Image.open(path)
        pixels = image.load()
        width, height = image.size
        result = []
        for y in range(height):
            row = [pixels[x, y] for x in range(width)]
            result.append(row)
        return result

    def apposer_sceau(self, image_base_path, mask_path, sceau_path, output_path, couleur_zone=(198, 55, 124)):
        # Charger les images
        image = Image.open(image_base_path).convert("RGBA")
        mask = Image.open(mask_path).convert("RGB")
        sceau = Image.open(sceau_path).convert("RGBA")

        mask_array = np.array(mask)
        target_color = np.array(couleur_zone)

        # Détecter les pixels correspondants à la couleur
        tolerance = 30
        match_pixels = np.all(np.abs(mask_array - target_color) < tolerance, axis=-1)

        if not np.any(match_pixels):
            print("[ALERTE] Impossible d'apposer le sceau.")
            return False

        # Trouver les bords du rectangle englobant
        coords = np.argwhere(match_pixels)
        y0, x0 = coords.min(axis=0)
        y1, x1 = coords.max(axis=0)

        box_width = x1 - x0
        box_height = y1 - y0

        # Redimensionner le sceau à la taille de la zone
        sceau_resized = sceau.resize((box_width, box_height), resample=Image.Resampling.LANCZOS)

        # Coller le sceau
        image.paste(sceau_resized, (x0, y0), mask=sceau_resized)
        image.save(output_path)
        print(f"[INFO] Sceau apposé à ({x0}, {y0}), image sauvegardée : {output_path}")
        return False

    def write_text(self, text, is_title=False, override=False):
        for line in self._split_lines(text, is_title, self.font.allow_upper):
            if self.line < self.font.max_lines or override:
                self.canvas.text(self._coord(is_title), line, fill=(0, 0, 0), font=self.font.font(is_title))

    def write_price(self, price):
        if self.line >= self.font.max_lines:
            return
        coords = (self.x_price, self.y_price + self.font.line_height * (self.line - 1))
        self.canvas.text(coords, f"{price} pa", fill=(0, 0, 0), font=self.font.font(False))

    def select_font(self, font=None):
        self.font = font or choice(FontLibrary.available_fonts)

    def draw_tavern_menu(self, title, menu, output_path):
        self.reset()
        self.select_font()
        self.write_text(title, is_title=True)
        self.line += 2
        for dish, price in menu.items():
            self.write_text(dish)
            self.write_price(price)
        self._save(Path(output_path) / f"{title}.png")

    def draw_quest(self, title, description, reward, output_path):
        self.reset()
        self.bonus = 10
        self.select_font()
        self.write_text(description, override=True)
        self.line += 2
        if reward:
            self.write_text("Récompense :")
            self.write_text(reward, is_title=True)
        self._save(Path(output_path) / f"{title}.png")

    def _save(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.image.save(path)


class FontLibrary:
    available_fonts = [
        FontStyle("Ancient Medium", 30, 20, 30, 20, max_lines=18),
        FontStyle("Cardinal", 30, 25, 20, 25, True, 8, max_lines=13),
        FontStyle("halfelven", 30, 20, 20, 20, True, 0, max_lines=16),
        FontStyle("hobbiton", 30, 25, 20, 25, True, 0, max_lines=16),
        FontStyle("Magical Night", 30, 25, 20, 25, True, 0, max_lines=14),
        FontStyle("RunelikeFree-Regular", 30, 25, 24, 25, True, 0, max_lines=13)
    ]


class _ParchmentFactory:
    def __init__(self):
        mask1 = Mask("./data/tavernes/masks/mask1.png", seal=False)
        mask2 = Mask("./data/tavernes/masks/mask2.png")
        mask3 = Mask("./data/tavernes/masks/mask3.png")
        mask4 = Mask("./data/tavernes/masks/mask4.png")
        mask5 = Mask("./data/tavernes/masks/mask5.png")
        mask6 = Mask("./data/tavernes/masks/mask6.png")
        mask7 = Mask("./data/tavernes/masks/mask7.png", seal=False)
        mask8 = Mask("./data/tavernes/masks/mask8.png",seal=False)
        mask9 = Mask("./data/tavernes/masks/mask9.png")
        mask10 = Mask("./data/tavernes/masks/mask10.png", seal=False, titre=False)
        self.templates = [
            Parchment("Parchemin1", [mask1, mask2, mask3, mask7, mask9, mask10], 130, 310, 130, 90),
            Parchment("Parchemin2", [mask1, mask3, mask7, mask9, mask10], 70, 90, 300, 90),
            Parchment("Parchemin3", [mask1, mask2, mask3, mask4, mask5, mask6, mask8, mask9, mask10], 70, 90, 300, 90),
            Parchment("Parchemin4", [mask1, mask2, mask3, mask4, mask5, mask6, mask8, mask9, mask10], 90, 90, 320, 90),
            Parchment("Parchemin5", [mask1, mask2, mask3, mask6, mask7, mask9, mask10], 66, 60, 300, 90),
            Parchment("Parchemin6", [mask1, mask7, mask9, mask10], 100, 110, 300, 90)
        ]

    def draw_tavern(self, title, menu):
        parchment = choice(self.templates)
        parchment.draw_tavern_menu(title, menu, "./data/foundry/les-reliques-des-ainees/tavernes")

    def draw_quest(self, title, description, output_path):
        parchment = choice(self.templates)
        font = choice(FontLibrary.available_fonts).path
        parchment.draw_text_in_mask_adaptive_font(description, title, font_path=font, max_font_size=30, min_font_size=10, output_path=output_path)
        
    def draw_quest_(self, description, export_path):
        parchment = choice(self.templates)
        parchment.draw_quest("QUETE TEST", description, 0, export_path)


    def test_all(self, title, menu):
        for i, template in enumerate(self.templates, 1):
            for j, font in enumerate(FontLibrary.available_fonts, 1):
                template.select_font(font)
                name = f"parchment{i}_{title}_{j}"
                template.draw_tavern_menu(name, menu, "./data/tavernes/menus/tests")


ParchmentFactory = _ParchmentFactory()
