from PIL import Image, ImageDraw, ImageFont
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

def draw_text_in_mask_adaptive_font(base_image_path, mask_path, text, title, font_path="arial.ttf", max_font_size=40, min_font_size=8, output_path="output.png"):
    image = Image.open(base_image_path).convert("RGBA")
    mask = Image.open(mask_path).convert("L")
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
                    print(f"📏 Zone rouge détectée de largeur {max_width}px et hauteur {max_height}px à y={y}")

                    while temp_index < len(title_list):
                        test_line = (line + " " if line else "") + title_list[temp_index]
                        print(f"Test de la ligne : {test_line}")
                        bbox = draw.textbbox((0, 0), test_line, font=title_font)
                        w = bbox[2] - bbox[0]
                        h = bbox[3] - bbox[1]

                        if w <= max_width:
                            # Vérifie qu’on reste dans max_height
                            if used_height + h > max_height:
                                print("⛔ Hauteur max atteinte, on arrête ici.")
                                found_title_font = False
                                break
                            line = test_line
                            temp_index += 1
                        else:
                            found_title_font = False
                            break

                    if line:
                        draw.text((zone_start, y), line, font=title_font, fill=(0, 0, 0, 255))
                        print(f"✅ Taille {title_font_size} : Ligne à ({zone_start}, {y}) : {line}")
                        title_index = temp_index
                        used_height += h
                    if title_index >= len(title_list):
                        found_title_font = False
                        break
            y += line_height_title + spacing

        if title_index >= len(title_list):
            found_title_font = True
            print(f"✅ Titre entièrement écrit avec taille {title_font_size}")

        if word_index >= len(words):
            font_size_found = True

        if font_size_found and found_title_font:
            temp_image.save(output_path)
            print(f"🎉 Texte entièrement écrit avec taille {font_size} — image sauvegardée : {output_path}")
            return

    print("❌ Impossible d’écrire tout le texte même avec la taille minimale.")
