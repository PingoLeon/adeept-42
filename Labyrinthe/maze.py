#!/usr/bin/python3
# File name   : findline.py
# Description : line tracking 
# Website     : www.adeept.com
# Author      : William
# Date        : 2019/11/21
import sys
import time
import cv2
import numpy as np

sys.path.insert(0,'/home/pi/adeept_picar-b/server/')
import RPi.GPIO as GPIO
import GUImove as move
import servo
import LED
import RGB
import ultra

sys.path.insert(0,'/home/pi/adeept-42/2-S2/')
import chiffre
import rectangle
import fleche

led = LED.LED()
angle_rate = 0.5

def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    RGB.setup()
    
def stop_robot():
    move.motorStop()       # Arrête les moteurs
    move.move(0, 'stop')  # Arrête le mouvement du robot
    servo.turnMiddle()     # Centre le servo (arrête le virage)

def checkdist_average():
    distance_list = []
    while len(distance_list) < 5:
        distance = ultra.checkdist() * 100
        distance_list.append(distance)
    
    average_distance = sum(distance_list) / len(distance_list)
    print("Average distance: %.2f cm" % average_distance)
    return average_distance
    
def checkcam():
    x, image = camera.read()
    cv2.imwrite("ARUCOTESTLABY.png",image)
    coinsMarqueurs, idsMarqueur, _ = cv2.aruco.detectMarkers(image, dictionnaire, parameters=parametres)
    if idsMarqueur is not None and len(coinsMarqueurs) == 4 and len(set(idsMarqueur.flatten())) == 1:
        stop_robot()
        print("✅ 4 Arucos avec le même identifiant trouvés !")
        #? Afficher les coins des arucos détectés
        ids = idsMarqueur.flatten()	
        image = cv2.imread('ARUCOTESTLABY.png')
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
        cv2.imwrite("ArucoOnImage.png", image)
        #cv2.waitKey(0)

        #! Déformer l’image pour ne travailler que dans la zone d’intérêt définie par ces 4 marqueurs
        print("🔍 On zoom sur l'image dans la zone des 4 marqueurs")
        image = cv2.imread('ARUCOTESTLABY.png')
        tous_coins = np.concatenate(tous_coins)
        # On calcule les coordonnées des coins de l'image zoomée
        top_left = np.min(tous_coins, axis=0)
        bottom_right = np.max(tous_coins, axis=0)
        top_right = np.array([bottom_right[0], top_left[1]])
        bottom_left = np.array([top_left[0], bottom_right[1]])

        # On spécifie les coordonnées des coins de l'image zoomée, +30 Pixels pour enlever les arucos de la zone et ainsi éviter les erreurs avec GoodFeaturesToTrack
        offset = 35
        
        if idsMarqueur[0] == 13:
            offset = 15
            
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
        
        value_return = None
        sens_fleche = None
        chiffre = None
        #! Recherche d'une flèche dans l'image zoomée et détermination de son sens
        if idsMarqueur[0] == 8: #? L'ID des rectangles de couleur est 8
            print("🤔 Il devrait y avoir un rectangle de couleur dans la zone zoomée")
            value_return = rectangle.detect_color() 
        elif idsMarqueur[0] == 13: #? L'ID de la flèche est 13
            print("🔍 On recherche une flèche dans l'image zoomée")
            sens_fleche = fleche.detect_fleche()
        elif idsMarqueur[0] == 9: #? L'ID des chiffres est 9
            print("🔢 On va essayer de voir si y'a un chiffre dans l'image")
            chiffre = chiffre.detect_chiffre() # 0 --> rien détecté / 1 --> Chiffre détecté et mis dans le terminal
        else:
            print("🚫 Rien de connu n'a été détecté...")
        if value_return is not None or sens_fleche is not None or chiffre is not None:
            print("on repart !")
        return sens_fleche
    
def maze():
    value_turn = 0
    while 1:
        #avancer lentement
        if value_turn == 0:
            move.move(40, 'forward')
            time.sleep(0.2)
        
        #prendre une image en même temps et l'analyser et dire si on doit tourner à droite ou à gauche
        dist = checkdist_average()
        if int(dist) <= 80:
            print("Distance > 50, prise d'image autorisée")
            if value_turn == 0:
                sens_fleche = checkcam()
            if sens_fleche is not None:
                if sens_fleche == 4 and value_turn ==0:
                    print("🔜 On tourne à droite")
                    servo.turnRight(angle_rate)
                    value_turn = 1
                if sens_fleche == 5 and value_turn ==0:
                    print("🔜 On tourne à gauche")
                    servo.turnLeft(angle_rate)
                    value_turn = 2
                    time.sleep
        else:
            print("Distance > 50")
            
        
        
    

if __name__ == '__main__':
    try:
        setup()
        move.setup()
        global dictionnaire, camera, parametres
        parametres = cv2.aruco.DetectorParameters_create()
        dictionnaire = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
        camera = cv2.VideoCapture(0)
        
        maze()
    except KeyboardInterrupt:
        RGB.both_off()
        led.colorWipe(0,0,0)
        camera.release()
        pass
    

        
        