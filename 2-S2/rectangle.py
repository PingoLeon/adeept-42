import cv2
import numpy as np

# Définir les plages de couleur comme des variables globales
limite1Rouge = [([179,100,100],[180,255,255])]
limite2Rouge = [([0,100,100],[9,255,255])]
limiteVert = [([40, 100, 100], [80, 255, 255])]
limiteJaune = [([20, 100, 100], [42, 255, 255])]

def detect_color():
    
    image = cv2.imread('image_zoomee.png')
    
    # Convertir l'image en HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Créer des masques pour chaque couleur
    mask_red1 = cv2.inRange(hsv, np.array(limite1Rouge[0][0]), np.array(limite1Rouge[0][1]))
    mask_red2 = cv2.inRange(hsv, np.array(limite2Rouge[0][0]), np.array(limite2Rouge[0][1]))
    mask_green = cv2.inRange(hsv, np.array(limiteVert[0][0]), np.array(limiteVert[0][1]))
    mask_yellow = cv2.inRange(hsv, np.array(limiteJaune[0][0]), np.array(limiteJaune[0][1]))

    # Compter le nombre de pixels de chaque couleur
    count_red = cv2.countNonZero(mask_red1) #+ cv2.countNonZero(mask_red2)
    count_green = cv2.countNonZero(mask_green)
    count_yellow = cv2.countNonZero(mask_yellow)

    # Créer un dictionnaire pour mapper les noms de couleur aux emojis
    color_emoji_map = {
        "red": "\U0001F534",  # Emoji de cercle rouge
        "green": "\U0001F7E2",  # Emoji de cercle vert
        "yellow": "\U0001F7E1"  # Emoji de cercle jaune
    }
    
    # Créer un dictionnaire pour mapper les noms de couleur aux valeurs de retour
    color_return_map = {
        "red": 1,
        "green": 2,
        "yellow": 3
    }
    
    # Trouver la couleur avec le plus grand nombre de pixels
    max_color = max([("red", count_red), ("green", count_green), ("yellow", count_yellow)], key=lambda x: x[1])
    
    # Afficher la couleur avec l'emoji approprié
    #print(color_emoji_map[max_color[0]], max_color[0])
    
    # Retourner la valeur correspondante
    return color_return_map[max_color[0]]

