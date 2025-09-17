import cv2
import numpy as np
import matplotlib.pyplot as plt

def is_almost_axis_aligned(line, angle_threshold=10):
    x1, y1, x2, y2 = line
    angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
    return (angle < angle_threshold) or (np.abs(angle - 90) < angle_threshold)

def detect_long_axis_aligned_walls(image_path, display=True):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError("Image non trouvée : " + image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(gray, (9,9), 0)
    edges = cv2.Canny(blur, 40, 120, apertureSize=3)

    kernel = np.ones((7,7), np.uint8)
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=1)

    # HoughLinesP très permissif (bcp de lignes candidates)
    lines = cv2.HoughLinesP(
        closed,
        rho=1,
        theta=np.pi / 180,
        threshold=70,         # plus bas pour plus de détection
        minLineLength=110,    # à ajuster selon la taille de la map
        maxLineGap=15
    )

    img_lines = img.copy()
    count_kept = 0
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            # Garder les murs très droits (axiaux)
            if is_almost_axis_aligned((x1, y1, x2, y2), angle_threshold=12):
                cv2.line(img_lines, (x1, y1), (x2, y2), (0, 255, 0), 2)
                count_kept += 1

    if display:
        plt.figure(figsize=(18,6))
        plt.subplot(1,3,1)
        plt.title("Original")
        plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        plt.axis('off')
        plt.subplot(1,3,2)
        plt.title("Canny+fermeture")
        plt.imshow(closed, cmap='gray')
        plt.axis('off')
        plt.subplot(1,3,3)
        plt.title(f"Lignes axiales détectées ({count_kept})")
        plt.imshow(cv2.cvtColor(img_lines, cv2.COLOR_BGR2RGB))
        plt.axis('off')
        plt.show()

    return img_lines

# Utilisation


# Utilisation :
_, img_annotated = detect_long_axis_aligned_walls("img_test.jpg", display=False)
cv2.imwrite("walls_detected.png", img_annotated)
