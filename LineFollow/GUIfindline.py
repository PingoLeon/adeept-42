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
import head
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
    RGB.setup()

led = LED.LED()
turn_status = 0
#speed = 55
#angle_rate = 0.2
#speed_turn = 55
speed = 70
angle_rate = 0.50
speed_turn = 70
color_select = 1 # 0 --> white line / 1 --> black line
check_true_out = 0
backing = 0
last_turn = 0

def stop_robot():
    move.motorStop()       # Arrête les moteurs
    move.move(0, 'stop')  # Arrête le mouvement du robot
    servo.turnMiddle()     # Centre le servo (arrête le virage)

def run(previous_move, number_of_tiret):
    global turn_status, speed, angle_rate, color_select, led, check_true_out, backing, last_turn
    status_right = GPIO.input(line_pin_right)
    status_middle = GPIO.input(line_pin_middle)
    status_left = GPIO.input(line_pin_left)

    if status_right == 1 and status_middle == 1 and status_left == 1 and previous_move != "Camera" and number_of_tiret < number_of_tiret_max:
        number_of_tiret += 1
        print("On s'arrête ! On en est à ", number_of_tiret, " tirets")
        if number_of_tiret == number_of_tiret_max:
            stop_robot()
            print("Circuit terminé !")
            led.rainbow()
            exit()
        stop_robot()
        time.sleep(2)
        move.move(60, 'forward')
        time.sleep(0.5)
        previous_move = "Camera"
        
    elif status_right == color_select:
        if previous_move != "Left":
            print('à gauche')
        check_true_out = 0
        backing = 0
        led.colorWipe(0,255,0)
        turn_status = -1
        last_turn = -1
        servo.turnLeft(angle_rate)
        move.move(speed_turn, 'forward')
        previous_move = "Left"
    elif status_left == color_select:
        if previous_move != "Right":
            print('à droite')
        check_true_out = 0
        backing = 0
        turn_status = 1
        last_turn = 1
        led.colorWipe(0,0,255)
        servo.turnRight(angle_rate)
        move.move(speed_turn, 'forward')
        previous_move = "Right"

    elif status_middle == color_select:
        if previous_move != "Middle":
            print('En arrière')
        check_true_out = 0
        backing = 0
        led.colorWipe(255,255,255)
        turn_status = 0
        servo.turnMiddle()
        
        move.move(speed, 'forward')
        # time.sleep(0.2)
        previous_move = "Middle"
    
    else:
        if previous_move != "Back":
            print('Back')
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
        previous_move = "Back"
    return previous_move, number_of_tiret

if __name__ == '__main__':
    try:
        global number_of_tiret, number_of_tiret_max
        number_of_tiret = 0
        number_of_tiret_max = int(input("Combien de tirets le circuit comporte-t-il ? "))

        setup()
        move.setup()
        head.reset()
        previous_move = ""
        time.sleep(0.2)

        while 1:
            previous_move, number_of_tiret = run(previous_move, number_of_tiret)
        pass
    except KeyboardInterrupt:
        head.reset_head()
        move.destroy()
        led.colorWipe(0,0,0)
        RGB.both_off()
        