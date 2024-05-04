import numpy as np
import sys
import cv2
import time
import chiffre
import fleche
import rectangle

def aruco_detect(input):
    
    if isinstance(input, str):
        image = cv2.imread(input)
    else:
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


def detection(): 
    try:
        #! Prendre une photo depuis la webcam
        camera = cv2.VideoCapture(0)
        x, image = camera.read()
        cv2.imwrite('opencv1.png', image)

        #?Test
        #image = cv2.imread('Cours1 S2-20240228\\flecheAR.jpg')
        
        #!trouve 4 ARuco avec le même identifiant dans l’image, sinon renvoie une erreur
        # Initialisation de la détection des Arucos
        coinsMarqueurs, idsMarqueur = aruco_detect("opencv1.png")
        
        print("📡 Recherche des 4 ARuco avec le même identifiant ...")
        animation = "|||||/////-----\\\\\\"
        i = 0
        while True:
            if idsMarqueur is not None and len(coinsMarqueurs) == 4 and len(set(idsMarqueur.flatten())) == 1:
                cv2.imwrite('opencv1.png', image)
                break

            x, image = camera.read()
            
            coinsMarqueurs, idsMarqueur = aruco_detect(image)
            

            # Arrêt au bout de 10 secondes sans détection (une boucle dure environ 0.03s, donc 333 boucles ~= 10s)
            if i == 333:
                print("🚫 Erreur : pas assez d'arucos détectés ou de même identifiant ! (Delay10sOutofBounds)")
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
        image = cv2.imread('opencv1.png')
        tous_coins = []
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
            cv2.line(image, topLeft, topRight, (0, 255, 0), 2)
            cv2.line(image, topRight, bottomRight, (0, 255, 0), 2)
            cv2.line(image, bottomRight, bottomLeft, (0, 255, 0), 2)
            cv2.line(image, bottomLeft, topLeft, (0, 255, 0), 2)
            # calculer puis afficher un point rouge au centre
            cX = int((topLeft[0] + bottomRight[0]) / 2.0)
            cY = int((topLeft[1] + bottomRight[1]) / 2.0)
            cv2.circle(image, (cX, cY), 4, (0, 0, 255), -1)
            # affiher l'identifiant
            cv2.putText(image, str(idMarqueur),
                (topLeft[0], topLeft[1] - 15), cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (0, 255, 0), 2)
            
            tous_coins.append(coins)
            
        # afficher l'image
        #cv2.imshow("Détection des arucos sur l'image", image)
        #cv2.waitKey(0)

        #! Déformer l’image pour ne travailler que dans la zone d’intérêt définie par ces 4 marqueurs
        print("🔍 On zoom sur l'image dans la zone des 4 marqueurs")
        image = cv2.imread('opencv1.png')
        tous_coins = np.concatenate(tous_coins)
        # On calcule les coordonnées des coins de l'image zoomée
        top_left = np.min(tous_coins, axis=0)
        bottom_right = np.max(tous_coins, axis=0)
        top_right = np.array([bottom_right[0], top_left[1]])
        bottom_left = np.array([top_left[0], bottom_right[1]])

        # On spécifie les coordonnées des coins de l'image zoomée, +30 Pixels pour enlever les arucos de la zone et ainsi éviter les erreurs avec GoodFeaturesToTrack
        offset = 35
        
        if idsMarqueur[0] == 13:
            offset = 25
            
        points1 = np.float32([top_left + [offset, offset], top_right + [-offset, offset], bottom_right + [-offset, -offset], bottom_left + [offset, -offset]])
        points2 = np.float32([[0, 0], [200, 0], [200, 200], [0, 200]])

        # On calcule la matrice de transformation
        vecttrans = cv2.getPerspectiveTransform(points1, points2)

        #! On applique la transformation à l'image d'origine
        image_zoomee = cv2.warpPerspective(image, vecttrans, (200, 200))

        # On affiche l'image zoomée
        #cv2.imshow("Zoom sur la zone", image_zoomee)
        cv2.imwrite('image_zoomee.png', image_zoomee)
        #cv2.waitKey(0)

        #! Recherche d'une flèche dans l'image zoomée et détermination de son sens
        if idsMarqueur[0] == 8: #? L'ID des rectangles de couleur est 8
            print("🤔 Il devrait y avoir un rectangle de couleur dans la zone zoomée")
            value_return = rectangle.detect_color() 
            return value_return # 0 --> rien détecté / 1 --> panneau rouge / 2 --> panneau vert / 3 --> panneau jaune
        elif idsMarqueur[0] == 13: #? L'ID de la flèche est 13
            print("🔍 On recherche une flèche dans l'image zoomée")
            sens_fleche = fleche.detect_fleche()
            return sens_fleche  # 0 --> rien détecté / 4 --> Droite / 5 --> Gauche
        elif idsMarqueur[0] == 9: #? L'ID des chiffres est 9
            print("🔢 On va essayer de voir si y'a un chiffre dans l'image")
            chiffre_return = chiffre.detect_chiffre() # 0 --> rien détecté / 1 --> Chiffre détecté et mis dans le terminal
            if chiffre_return == 0:
                print("♻️ On relance un cycle !")
                detection()
        else:
            print("🚫 Rien de connu n'a été détecté...")
            
    except Exception as e:
        print("🚫 Erreur :", e)
        

if __name__ == "__main__":
    detection()