#!/usr/bin/python3
# File name   : findline.py
# Description : line tracking 
# Website     : www.adeept.com
# Author      : William
# Date        : 2019/11/21
import sys
sys.path.insert(0,'/home/pi/adeept_picar-b/server/')
import RPi.GPIO as GPIO
import time
import GUImove as move
import servo
import LED
import headrotate as head
import initservo as servostop
from video import camera
import RGB

line_pin_right = 19
line_pin_middle = 16
line_pin_left = 20

def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(line_pin_right,GPIO.IN)
    GPIO.setup(line_pin_middle,GPIO.IN)
    GPIO.setup(line_pin_left,GPIO.IN)
    #motor.setup()
    RGB.setup()

led = LED.LED()
turn_status = 0
speed = 55
angle_rate = 0.4
speed_turn = 55
color_select = 1 # 0 --> white line / 1 --> black line
check_true_out = 0
backing = 0
last_turn = 0

def stop_robot():
    move.motorStop()       # Arrête les moteurs
    move.move(0, 'stop')  # Arrête le mouvement du robot
    servo.turnMiddle()     # Centre le servo (arrête le virage)

def behavior(value_return):
    if value_return == 1:
        print("Un rectangle rouge a été détecté")
        print("On attend une minute avant de reprendre (raccourci à 10 secondes pour les tests)")
        head.reset_head()
        RGB.both_off()
        RGB.red()
        time.sleep(10)

    elif value_return == 2:
        print("Un rectangle vert a été détecté")
        print("On réinitialise la tête et on se remet en route")
        head.reset_head()
        RGB.both_off()
        RGB.green()

    elif value_return == 3:
        print("Un rectangle jaune a été détecté")
        print("On met les deux leds de devant en jaune et on réinitialise la tête et on reprend le suivi de ligne")
        head.reset_head()
        RGB.both_off()
        RGB.yellow()
        time.sleep(1)


def checkcam():
    print('Checking the camera for rectangles of color (red, green or yellow)')
    #RL.both_off()

    head.reset_head()
    time.sleep(1)
    head.tilt_head('right')
    value_return = camera()
    if value_return == 0:
        print("Aucun panneau détecté ici, on va à gauche")
        head.reset_head()
        time.sleep(3)
        head.tilt_head('left')
        time.sleep(1)
        value_return = camera()
        if value_return == 0:
            print("Aucun panneau détecté ici")
            return 0
        else:
            behavior(value_return)
            return 1
    else:
        behavior(value_return)
        return 1





def run(already_checked):
    global turn_status, speed, angle_rate, color_select, led, check_true_out, backing, last_turn
    status_right = GPIO.input(line_pin_right)
    status_middle = GPIO.input(line_pin_middle)
    status_left = GPIO.input(line_pin_left)
    #create a int value already_checked
    

    #print('R%d   M%d   L%d'%(status_right,status_middle,status_left))
    

    if status_right == 1 and status_middle == 1 and status_left == 1 and already_checked != 1:
        # All three sensors detect a black line
        stop_robot()
        checkcam()
        time.sleep(2)
        head.reset_head()
        move.move(60, 'forward')
        time.sleep(0.5)
        already_checked = 1
    elif status_right == color_select:
        check_true_out = 0
        backing = 0
        print('left')
        led.colorWipe(0,255,0)
        turn_status = -1
        last_turn = -1
        servo.turnLeft(angle_rate)
        move.move(speed_turn, 'forward')
        already_checked = 0
    elif status_left == color_select:
        check_true_out = 0
        backing = 0
        print('right')
        turn_status = 1
        last_turn = 1
        led.colorWipe(0,0,255)
        servo.turnRight(angle_rate)
        move.move(speed_turn, 'forward')
        already_checked = 0

    elif status_middle == color_select:
        check_true_out = 0
        backing = 0
        print('middle')
        led.colorWipe(255,255,255)
        turn_status = 0
        servo.turnMiddle()
        move.move(speed, 'forward')
        # time.sleep(0.2)
        already_checked = 0
    
    else:
        print('none')
        led.colorWipe(255,0,0)
        if not backing == 1:
            if check_true_out == 1:
                check_true_out = 0
                if turn_status == 0:
                    if last_turn == 1:
                        servo.turnRight(angle_rate)
                    else:
                        move.move(speed, 'backward')
                        time.sleep(0.3)
                elif turn_status == 1:
                    time.sleep(0.3)
                    servo.turnLeft(angle_rate)
                else:
                    time.sleep(0.3)
                    servo.turnRight(angle_rate)
                move.move(speed, 'backward')
                backing = 1
                #time.sleep(0.2)
            else:
                time.sleep(0.1)
                check_true_out = 1
        already_checked = 0
    return already_checked

if __name__ == '__main__':
    try:
        setup()
        move.setup()
        head.reset_head()
        already_checked = 0
        time.sleep(0.2)
        while 1:
            already_checked = run(already_checked)
            
        pass
    except KeyboardInterrupt:
        head.reset_head()
        move.destroy()
