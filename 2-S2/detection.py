import numpy as np
import sys
import cv2
import time
import detection_class

count_recursivite = 0

def aruco_detect(input):
    
    image = input
        
    dictionnaire = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)

    # Récupérer la version d'OpenCV
    version_opencv = list(map(int, cv2.__version__.split('.')[:2]))
    # Créer les paramètres de détection en fonction de la version d'OpenCV
    if version_opencv[0] > 4 or (version_opencv[0] == 4 and version_opencv[1] >= 7):
        parametres = cv2.aruco.DetectorParameters()
        coinsMarqueurs, idsMarqueur, _ = cv2.aruco.ArucoDetector(dictionnaire, parametres).detectMarkers(image)
    else:
        parametres = cv2.aruco.DetectorParameters_create()
        coinsMarqueurs, idsMarqueur, _ = cv2.aruco.detectMarkers(image, dictionnaire, parameters=parametres)
        
    return coinsMarqueurs, idsMarqueur
    
def dist(point1, point2):
    return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5

def est_un_rectangle(topLeft, topRight, bottomRight, bottomLeft, tolerance=6):
    diag1 = dist(topLeft, bottomRight)
    diag2 = dist(topRight, bottomLeft)
    
    if abs(diag1 - diag2) <= tolerance:
        return True
    else:
        return False


def detection(count_recursivite = 0): 
    #! Prendre une photo depuis la webcam
    camera = cv2.VideoCapture(0)
    x, image = camera.read()
    cv2.imwrite('imageInitiale.png', image)
    
    #!trouve 4 ARuco avec le même identifiant dans l’image, sinon renvoie une erreur
    coinsMarqueurs, idsMarqueur = aruco_detect(image)
    
    print("📡 Recherche des 4 ARuco avec le même identifiant ...")
    animation = "|||||/////-----\\\\\\"
    i = 0
    while True:
        if idsMarqueur is not None and len(coinsMarqueurs) == 4 and len(set(idsMarqueur.flatten())) == 1:
            cv2.imwrite('imageInitiale.png', image)
            break

        x, image = camera.read()
        
        coinsMarqueurs, idsMarqueur = aruco_detect(image)
        

        # Arrêt au bout de 10 secondes sans détection (une boucle dure environ 0.03s, donc 333 boucles ~= 10s)
        if i == 50:
            print("🚫 Erreur : pas assez d'arucos détectés ou de même identifiant ! (Delay3sOutofBounds)")
            return 0

        # Print the animation
        print(animation[i % len(animation)], end="\r")
        i += 1
        sys.stdout.flush()
        time.sleep(0.01)
    print('\r' + ' ' * len(animation) + '\r', end='')
    print("✅ 4 Arucos avec le même identifiant trouvés !")
    
    #Fermer la caméra :
    camera.release()

    #? Afficher les coins des arucos détectés
    ids = idsMarqueur.flatten()	
    tous_coins = []
    image_marquee = image
    for (coinMarqueur, idMarqueur) in zip(coinsMarqueurs, ids):
        # extraire les angles des aruco (toujours dans l'ordre haut-gauche, haut-droite, bas-gauche, bas-droit)
        coins = coinMarqueur.reshape((4, 2))
        (topLeft, topRight, bottomRight, bottomLeft) = coins
        # convertir en entier (pour l'affichage)
        topRight = (int(topRight[0]), int(topRight[1]))
        bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
        bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
        topLeft = (int(topLeft[0]), int(topLeft[1]))
        
        # dessiner un quadrilatère autour de chaque aruco
        cv2.line(image_marquee, topLeft, topRight, (0, 255, 0), 2)
        cv2.line(image_marquee, topRight, bottomRight, (0, 255, 0), 2)
        cv2.line(image_marquee, bottomRight, bottomLeft, (0, 255, 0), 2)
        cv2.line(image_marquee, bottomLeft, topLeft, (0, 255, 0), 2)
        
        # calculer puis afficher un point rouge au centre
        cX = int((topLeft[0] + bottomRight[0]) / 2.0)
        cY = int((topLeft[1] + bottomRight[1]) / 2.0)
        cv2.circle(image_marquee, (cX, cY), 4, (0, 0, 255), -1)
        # affiher l'identifiant
        cv2.putText(image_marquee, str(idMarqueur),(topLeft[0], topLeft[1] - 15), cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 255, 0), 2)
        tous_coins.append(coins)
    
    cv2.imwrite('ArucosDétectés.png', image_marquee)
    # calculer les centres de chaque ArUco marker
    centres = []
    for coinMarqueur in coinsMarqueurs:
        coins = coinMarqueur.reshape((4, 2))
        cX = int((coins[0, 0] + coins[2, 0]) / 2.0)
        cY = int((coins[0, 1] + coins[2, 1]) / 2.0)
        centres.append((cX, cY))

    # trier les centres par ordre croissant de x, puis de y
    centres = sorted(centres, key=lambda c: (c[0], c[1]))

    # vérifier si les centres forment un rectangle
    (topLeft, topRight, bottomLeft, bottomRight) = centres

    if est_un_rectangle(topLeft, topRight, bottomRight, bottomLeft):
        print("👍 Les Aruco markers forment un rectangle")
    else:
        print("🛑 Les ArUco markers ne forment pas un rectangle")
        detection()

    #! Déformer l’image pour ne travailler que dans la zone d’intérêt définie par ces 4 marqueurs
    print("🔍 On zoom sur l'image dans la zone des 4 marqueurs")
    tous_coins = np.concatenate(tous_coins)
    # On calcule les coordonnées des coins de l'image zoomée
    top_left = np.min(tous_coins, axis=0)
    bottom_right = np.max(tous_coins, axis=0)
    top_right = np.array([bottom_right[0], top_left[1]])
    bottom_left = np.array([top_left[0], bottom_right[1]])

    # On spécifie les coordonnées des coins de l'image zoomée, +30 Pixels pour enlever les arucos de la zone et ainsi éviter les erreurs avec GoodFeaturesToTrack
    offset = 35
    
    if idsMarqueur[0] == 13:
        offset = 30
        
    points1 = np.float32([top_left + [offset, offset], top_right + [-offset, offset], bottom_right + [-offset, -offset], bottom_left + [offset, -offset]])
    points2 = np.float32([[0, 0], [200, 0], [200, 200], [0, 200]])

    # On calcule la matrice de transformation
    vecttrans = cv2.getPerspectiveTransform(points1, points2)

    #! On applique la transformation à l'image d'origine
    image_zoomee = cv2.warpPerspective(image, vecttrans, (200, 200))
    cv2.imwrite('image_zoomee.png', image_zoomee)
    
    detection_instance = detection_class.Detection()  # Créez une instance de Detection
    #! Recherche d'une flèche dans l'image zoomée et détermination de son sens
    if idsMarqueur[0] == 8: #? L'ID des rectangles de couleur est 8
        print("🤔 Il devrait y avoir un rectangle de couleur dans la zone zoomée")
        value_return = detection_instance.rectangle(image_zoomee) 
        return value_return #! 1 --> panneau rouge / 2 --> panneau vert / 3 --> panneau jaune
    
    elif idsMarqueur[0] == 13: #? L'ID de la flèche est 13
        print("🔍 On recherche une flèche dans l'image zoomée")
        sens_fleche = detection_instance.fleche(image_zoomee)
        return sens_fleche  #! 4 --> Droite / 5 --> Gauche
    
    elif idsMarqueur[0] == 9: #? L'ID des chiffres est 9
        print("🔢 On va essayer de voir si y'a un chiffre dans l'image")
        chiffre_return = detection_instance.chiffre(image_zoomee) # 0 --> rien détecté / 1 --> Chiffre détecté et mis dans le terminal
        
        if chiffre_return == 0:
            print("♻️ On relance un cycle ! -> ",count_recursivite)
            if count_recursivite >= 15:
                print("🛑 Trop de cycles, on arrête")
                return 0
            count_recursivite += 1
            detection(count_recursivite)
        return 6 #! 6 --> Chiffre détecté
    else:
        print("🚫 Rien de connu n'a été détecté...")
        return 0
        

if __name__ == "__main__":
    detection()