"""
#! Algorithme par Léon Dalle - 06/03/2024
#? Utilisation de certaines portions de codes qui étaient fournies via BoostCamp (Auteur présumé : Romaric Sichler)

Concevez un algorithme qui :
- prend une photo depuis la webcam de l’ordinateur
- trouve 4 ARuco avec le même identifiant dans l’image, sinon renvoie une erreur
- déforme l’image pour ne travailler que dans la zone d’intérêt définie par ces 4 marqueurs
- trouve le sens d’une contenue dans la zone définie et l’affiche en console
- vous pouvez utiliser des affichages graphiques pour que les éventuelles erreurs du programme soient transparentes
"""

import numpy as np
import sys
import cv2
import time

def trouver_fleche_et_son_sens():
    img = cv2.imread('image_zoomee.png')

    #réduisons le bruit en utilisant un flou gaussien
    img = cv2.GaussianBlur(img, (11,11), 0)
    #On travaille sur une image en niveau de gris
    img_gris = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    #on calcule les sommets avec une fonction bien pratique d'openCV, en prenant les 7 meilleurs sommets d'une éventuelle figure
    sommets = np.intp(cv2.goodFeaturesToTrack(img_gris,7,0.01,10))
    if sommets is None:
        print("🚫 Erreur : pas de sommets détectés !")
        exit()


    #rendu visuel pour débugger
    for i,vals in enumerate(sommets):
        x,y = vals.ravel()
        cv2.circle(img,(x,y),3,(255,255,0),-1)
        cv2.putText(img, str(i), (x,y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2, cv2.LINE_AA )

    #on prends les sommets les plus éloignés
    xmax, ymax = (np.max(sommets, axis = 0)).ravel()
    xmin, ymin = (np.min(sommets, axis = 0)).ravel() 

    #déterminons l'axe du milieu de notre flèche, puis traçons le visuellemet (cv2.line)
    xmil=int(xmin+((xmax-xmin)/2))
    cv2.line(img,(xmil,0),(xmil,img.shape[0]),(255,0,0),2)

    #au vu de la forme de notre flèche le nombre de sommmets le plus grand est dans la partie "pointe" notre flèche
    nbSommetsDroite=np.count_nonzero(sommets[:,0,0]>xmil)
    nbSommetsGauche=np.count_nonzero(sommets[:,0,0]<xmil)

    print("🎯 Flèche détectée ! Son sens est à ", end="")
    #on finit par afficher le sens de notre flèche
    if nbSommetsDroite>nbSommetsGauche:
        print('Droite')
    else:
        print('Gauche')


    #les prochaines lignes ne servent qu'à l'affichage graphique
    cv2.imshow('Flèche trouvée !',img)
    cv2.waitKey(0)

try:
    #! Prendre une photo depuis la webcam
    camera = cv2.VideoCapture(0)
    x, image = camera.read()
    cv2.imwrite('opencv1.png', image)

    #!trouve 4 ARuco avec le même identifiant dans l’image, sinon renvoie une erreur
    dictionnaire = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
    parametres =  cv2.aruco.DetectorParameters()
    coinsMarqueurs, idsMarqueur, PotentielsMarqueurs = cv2.aruco.ArucoDetector(dictionnaire, parametres).detectMarkers(cv2.imread('opencv1.png'))

    print("📡 Recherche des 4 ARuco avec le même identifiant ...")
    animation = "|||||/////-----\\\\\\"
    i = 0
    while True:
        if idsMarqueur is not None and len(coinsMarqueurs) == 4 and len(set(idsMarqueur.flatten())) == 1:
            cv2.imwrite('opencv1.png', image)
            break

        x, image = camera.read()
        coinsMarqueurs, idsMarqueur, PotentielsMarqueurs = cv2.aruco.ArucoDetector(dictionnaire, parametres).detectMarkers(image)
        

        # Arrêt au bout de 10 secondes sans détection
        if i == 333:
            print("🚫 Erreur : pas assez d'arucos détectés ou de même identifiant ! (Delay10sOutofBounds)")
            exit()

        # Print the animation
        print(animation[i % len(animation)], end="\r")
        i += 1
        sys.stdout.flush()
        time.sleep(0.01)
    print('\r' + ' ' * len(animation) + '\r', end='')
    print("✅ 4 Arucos avec le même identifiant trouvés !")



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
    cv2.imshow("Détection des arucos sur l'image", image)
    cv2.waitKey(0)

    #! Déformer l’image pour ne travailler que dans la zone d’intérêt définie par ces 4 marqueurs
    print("🔍 On zoom sur l'image dans la zone des 4 marqueurs")
    image = cv2.imread('opencv1.png')
    tous_coins = np.concatenate(tous_coins)
    # On calcule les coordonnées des coins de l'image zoomée
    top_left = np.min(tous_coins, axis=0)
    bottom_right = np.max(tous_coins, axis=0)
    top_right = np.array([bottom_right[0], top_left[1]])
    bottom_left = np.array([top_left[0], bottom_right[1]])

    # On spécifie les coordonnées des coins de l'image zoomée
    points1 = np.float32([top_left + [20, 20], top_right + [-20, 20], bottom_right + [-20, -20], bottom_left + [20, -20]])
    points2 = np.float32([[0, 0], [200, 0], [200, 200], [0, 200]])

    # On calcule la matrice de transformation
    vecttrans = cv2.getPerspectiveTransform(points1, points2)

    # On applique la transformation à l'image d'origine
    image_zoomee = cv2.warpPerspective(image, vecttrans, (200, 200))

    # On affiche l'image zoomée
    cv2.imshow("Zoom sur la zone", image_zoomee)
    cv2.imwrite('image_zoomee.png', image_zoomee)
    cv2.waitKey(0)

    #! Recherche d'une flèche dans l'image zoomée et détermination de son sens
    if idsMarqueur[0] == 13: #? L'ID de la flèche est 13
        print("🔍 On recherche une flèche dans l'image zoomée")
        trouver_fleche_et_son_sens()
    if idsMarqueur[0] == 8: #? L'ID des rectangles de couleur est 8
        print("🤔 Il devrait y avoir un rectangle de couleur dans la zone zoomée")
except Exception as e:
    print("🚫 Erreur :", e)