

import sys
import os
import time
import cv2
import numpy as np
import tools

sys.path.insert(0,'/home/pi/adeept_picar-b/server/')
import RPi.GPIO as GPIO
import time
import GUImove as move
import servo
import LED
import head
import RGB
import ultra
import functions

led = LED.LED()

fuc = functions.Functions()
fuc.start() 
    
def scan():
    radar_send = fuc.radarScan()
    distances_left = []
    distances_right = []

    # Calculer l'angle médian
    min_angle = radar_send[0][1]
    max_angle = radar_send[-1][1]
    median_angle = (min_angle + max_angle) / 2

    for i in range(len(radar_send)):
        distance, angle = radar_send[i]
        distance = round(distance * 100, 2)
        if angle < median_angle:
            distances_left.append(distance)
        else:
            distances_right.append(distance)

    mean_distance_left = sum(distances_left) / len(distances_left) if distances_left else 0
    mean_distance_right = sum(distances_right) / len(distances_right) if distances_right else 0

    #print("moyenne distance gauche : ", mean_distance_left)
    #print("moyenne distance droite : ", mean_distance_right)
    if mean_distance_left > mean_distance_right:
        print("🔜 La moyenne des distances est supérieure à gauche")
        print("On va à gauche ! ⬅️")
        return 2
    else:
        print("🔜 La moyenne des distances est supérieure à droite")
        print("On va à droite ! ➡️")
        return 1
    
#Avancer tant qu'aucun obstacle à 30cm
def scenario_lab_scan(value_turn):
    angle_rate = 0.45
    sens_fleche = None
    
    while 1:
        if value_turn is None:
            #On avance tout droit tant que rien à -20cm
            while tools.checkdist_average() > 30:
                sens_fleche = tools.checkcamlaby()
                move.move(40, 'forward')
                time.sleep(0.1)
                if sens_fleche is not None:
                    break
            if sens_fleche is None:
                tools.stop_robot()
                value_turn = scan()
            else:
                value_turn = sens_fleche
        print("Manoeuvre !")
        move.move(65, 'backward')
        time.sleep(0.3)
        if value_turn == 1 or value_turn == 4:
            servo.turnRight(angle_rate)
        elif value_turn == 2 or value_turn == 5:
            servo.turnLeft(angle_rate)
        sens_fleche = None
        value_turn = None
        move.move(65, 'forward')
        time.sleep(1.2)
        servo.turnMiddle()


            
def labyrinthe(value_turn):
    servo.turnMiddle()
    
    time.sleep(0.2)
    scenario_lab_scan(value_turn)
    print("Fin du prog !")
    os._exit(0)
    
    

if __name__ == '__main__':
    try:
        labyrinthe()
    except KeyboardInterrupt:
        head.reset_head()
        move.destroy()
        led.colorWipe(0,0,0)
        RGB.both_off()
    
    
    

        
        
