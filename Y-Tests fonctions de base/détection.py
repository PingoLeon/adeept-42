"""
#! Algorithme par Léon Dalle - 06/03/2024
#? Utilisation de certaines portions de codes qui étaient fournies via BoostCamp (Auteur présumé : Romaric Sichler)

#*Nota Bene : Le code fonctionne bien pour la détection des flèches, quasi tout les essais sont concluants (Aruco 13)
#*            Mais la détection de l'Aruco 8 pour les rectangles de couleur est beaucoup plus aléatoire, surtout s'il faut repérer 3 arucos sur une même frame.
#*            Possibilité de changer l'aruco par un autre plus facilement détectable ?

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

def chiffre():
    image = cv2.imread("image_zoomee.png")
    
    #Dictionnaire de correspondance
    correspondances = {
        (1, 1, 1, 0, 1, 1, 1): 0,
        (0, 0, 1, 0, 0, 1, 0): 1,
        (1, 0, 1, 1, 1, 0, 1): 2,
        (1, 0, 1, 1, 0, 1, 1): 3,
        (0, 1, 1, 1, 0, 1, 0): 4,
        (1, 1, 0, 1, 0, 1, 1):5,
        (1, 1, 0, 1, 1, 1, 1):6,
        (1, 0, 1, 0, 0, 1, 0):7,
        (1, 1, 1, 1, 1, 1, 1):8,
        (1, 1, 1, 1, 0, 1, 1):9
    }

    (H, L) = image.shape[:2] #récupérer la hauteur et largeur de l'image

    # 7 zones d'intérêt à scanner
    segments = [
        ((int(L/4), 0), (int(L*3/4), int(H/6))),                # haut
        ((0, int(H/6)), (int(L/4), int(H/2))),                  # haut-gauche
        ((int(L*3/4), int(H/6)), (int(L), int(H/2))),           # haut-droite
        ((int(L/4), int(H*2/5)) , (int(L*3/4), int(H*3/5))),    # centre
        ((0, int(H/2)), (int(L/4), int(H*4/5))),                # bas-gauche
        ((int(L*3/4),int(H/2)),(int(L),int(H*5/6))),            # bas-droite
        ((int(L/4), int(H*5/6)), (int(L*3/4), int(H)))          # bas
    ]

    for rect in segments:
        color=tuple(np.random.random(size=3) * 256)
        image=cv2.rectangle(image, rect[0], rect[1],color, 3)

    #passer en niveau de gris
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #définir un seuil et binariser l'image
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    #nettoyer l'image avec un morphose (optionnel)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 5))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    #créer un tableau des états vus des segments (1 le segment est noir, 0 le segment est blanc)
    on = [0] * len(segments) 

    #voir l'état pour chaque segment :
    for (i, ((xA, yA), (xB, yB))) in enumerate(segments):
        # extraire une image binaire de la zone d'intérêt correspondant au segment
        segROI = thresh[yA:yB, xA:xB]
        #compter le nombre de pixel noir
        nbpixels = cv2.countNonZero(segROI)
        #calculer l'aire du segment
        area = (xB - xA) * (yB - yA)
        # modifier le tableau d'état vu si le nombre de pixels noir dépasse 30% (à affiner en fonction de vos caméras)
        if nbpixels / float(area) > 0.3:
            on[i]= 1

    #Afficher une croix au centre des segments identifiés
    for i in range(len(on)):
        if on[i]==1:
            milsegement=(int((segments[i][0][0]+segments[i][1][0])/2),int((segments[i][0][1]+segments[i][1][1])/2))
            cv2.putText(image, str("X"), milsegement, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    #finalement on va chercher dans le dictinnaire du début quel est le chiffre lu
    if tuple(on) not in correspondances:
        print("🚫 Aucun chiffre trouvé")
        print("On a tenté de rechercher le chiffre : ",on)
    else:
        nombrelu = correspondances[tuple(on)]
        print("✅ On a trouvé le chiffre : ", nombrelu)
    cv2.imshow('Zones trouvées', image)  
    cv2.waitKey(0)

try:
    #! Prendre une photo depuis la webcam
    camera = cv2.VideoCapture(0)
    x, image = camera.read()
    cv2.imwrite('opencv1.png', image)

    #?Test
    #image = cv2.imread('Cours1 S2-20240228\\flecheAR.jpg')
    
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
        

        # Arrêt au bout de 10 secondes sans détection (une boucle dure environ 0.03s, donc 333 boucles ~= 10s)
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

    # On spécifie les coordonnées des coins de l'image zoomée, +30 Pixels pour enlever les arucos de la zone et ainsi éviter les erreurs avec GoodFeaturesToTrack
    offset = 20
    points1 = np.float32([top_left + [offset, offset], top_right + [-offset, offset], bottom_right + [-offset, -offset], bottom_left + [offset, -offset]])
    points2 = np.float32([[0, 0], [200, 0], [200, 200], [0, 200]])

    # On calcule la matrice de transformation
    vecttrans = cv2.getPerspectiveTransform(points1, points2)

    #! On applique la transformation à l'image d'origine
    image_zoomee = cv2.warpPerspective(image, vecttrans, (200, 200))

    # On affiche l'image zoomée
    cv2.imshow("Zoom sur la zone", image_zoomee)
    cv2.imwrite('image_zoomee.png', image_zoomee)
    cv2.waitKey(0)

    #! Recherche d'une flèche dans l'image zoomée et détermination de son sens
    if idsMarqueur[0] == 13: #? L'ID de la flèche est 13
        print("🔍 On recherche une flèche dans l'image zoomée")
        trouver_fleche_et_son_sens()
    elif idsMarqueur[0] == 8: #? L'ID des rectangles de couleur est 8
        print("🤔 Il devrait y avoir un rectangle de couleur dans la zone zoomée")
    elif idsMarqueur[0] == 9:
        print("🔢 On va essayer de voir si y'a un chiffre dans l'image")
        chiffre()
    else:
        print("🚫 Rien de connu n'a été détecté...")
        
except Exception as e:
    print("🚫 Erreur :", e)