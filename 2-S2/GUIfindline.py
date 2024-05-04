import sys
import os
from detection import detection
from labyrinthe import labyrinthe
import tools

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

led = LED.LED()
led_ctrl = LED.LED_ctrl()
turn_status = 0
#old speeds and angle (slow)
#speed = 55
#angle_rate = 0.2
#speed_turn = 55
speed = 70
angle_rate = 0.50
speed_turn = 70
color_select = 1 # 0 --> white line / 1 --> black line
check_true_out = 0
backing = 0
dist_to_check_max = 50
last_turn = 0

def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(line_pin_right,GPIO.IN)
    GPIO.setup(line_pin_middle,GPIO.IN)
    GPIO.setup(line_pin_left,GPIO.IN)
    RGB.setup()
    
def stop_program():
    move.motorStop()       # Arrête les moteurs
    move.move(0, 'stop')  # Arrête le mouvement du robot
    head.reset()
    servo.turnMiddle()     # Centre le servo (arrête le virage)
    RGB.both_off()
    led.colorWipe(0,0,0)
    led_ctrl.stop()
    

def stop_robot():
    move.motorStop()       # Arrête les moteurs
    move.move(0, 'stop')  # Arrête le mouvement du robot
    servo.turnMiddle()     # Centre le servo (arrête le virage)

def behavior(value_return):
    if value_return == 1:
        print("\n🔴 Un panneau rouge a été détecté ! 🔴\n")
        head.reset()
        RGB.both_off()
        RGB.red()
        led.colorWipe(255,0,0)
        time.sleep(10)
        print("\n🔃On repart !")

    elif value_return == 2:
        print("\n🟢 Un panneau vert a été détecté ! 🟢\n")
        head.reset()
        RGB.both_off()
        RGB.green()
        led.colorWipe(0,255,0)

    elif value_return == 3:
        print("\n🟡 Un panneau jaune a été détecté ! 🟡 \n")
        head.reset()
        RGB.both_off()
        RGB.yellow()
        led.colorWipe(0,255,255)
        
    elif value_return == 4 or value_return == 5:
        print("\n🤠 MODE LABYRINTHE 🤠\n")
        head.reset()
        labyrinthe()
        
    else:
        print("\n✅ On continue, aucun panneau de couleur n'a été repéré !\n")
        head.reset()


def checkcam():
    print('\n📸 CAMERA CHECK 📸\n')
    RGB.both_off()
    led.colorWipe(0,0,0)

    time.sleep(0.1)
    head.tilt_head('right')
    time.sleep(0.5)
    print("👁️ On regarde à droite")
    distance = tools.checkdist_average()
    if distance <= dist_to_check_max :
        value_return = detection() # 0 --> aucun panneau détecté / 1 --> panneau rouge / 2 --> panneau vert / 3 --> panneau jaune
    else:
        print("❗Trop loing")
        value_return = 0
    if value_return == 0:
        print("🛑 Aucun panneau détecté à droite")
        head.tilt_head('left')
        time.sleep(0.5)
        print("👁️ On regarde à gauche")
        distance = tools.checkdist_average()
        if distance <= dist_to_check_max :
            value_return = detection() # 0 --> aucun panneau détecté / 1 --> panneau rouge / 2 --> panneau vert / 3 --> panneau jaune
        else:
            print("❗Trop loing")
            value_return = 0
        if value_return == 0:
            print("🛑 Aucun panneau détecté à gauche")
            
            head.reset()
            time.sleep(0.5)
            print("👁️ On regarde tout droit")
            distance = tools.checkdist_average()
            if distance <= dist_to_check_max :
                value_return = detection() # 0 --> aucun panneau détecté / 1 --> panneau rouge / 2 --> panneau vert / 3 --> panneau jaune
            else:
                print("❗Trop loing")
                value_return = 0
            if value_return == 0:
                print("🛑 Aucun panneau détecté nulle part")
                return 0
            else:
                behavior(value_return)
                return 1
        else:
            behavior(value_return)
            return 1
    else:
        behavior(value_return)
        return 1

def run(previous_move):
    global turn_status, speed, angle_rate, color_select, led, check_true_out, backing, last_turn
    status_right = GPIO.input(line_pin_right)
    status_middle = GPIO.input(line_pin_middle)
    status_left = GPIO.input(line_pin_left)

    if status_right == 1 and status_middle == 1 and status_left == 1 and previous_move != "Camera":
        stop_robot()
        head.reset()
        checkcam()
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
    return previous_move

if __name__ == '__main__':
    try:
        setup()
        move.setup()
        
        stop_robot()
        head.reset()
        
        previous_move = ""
        time.sleep(0.2)

        while 1:
            previous_move = run(previous_move)
        pass
    except KeyboardInterrupt:
        head.reset()
        move.destroy()
        led.colorWipe(0,0,0)
        RGB.both_off()