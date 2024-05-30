import sys
import os
import detection
import labyrinthe
import tools

sys.path.insert(0,'/home/pi/adeept_picar-b/server/')
import RPi.GPIO as GPIO
import time
import GUImove as move
import servo

speed = 70
angle_rate = 0.50
speed_turn = 70
color_select = 1 # 0 --> white line / 1 --> black line
check_true_out = 0
backing = 0
dist_to_check_max = 50
last_turn = 0
turn_status = 0

def behavior(value_return):
    #! Fonction behavior pour faire différentes actions en fonction de ce qui a été observé, return 1 toujours
    if value_return == 1:
        print("\n🔴 Un panneau rouge a été détecté ! 🔴\n")
        robot.set_led_front(None)
        robot.set_led_front("red")
        robot.set_led_back(255,0,0)
        print("On s'arrête 10 secondes...\n")
        time.sleep(10)
        print("\n🔃 On repart !")
        
    elif value_return == 2:
        print("\n🟡 Un panneau jaune a été détecté ! 🟡 \n")
        robot.set_led_front(None)
        robot.set_led_front("yellow")
        robot.set_led_back(0,255,255)
        time.sleep(1)
        print("\n🔃 On repart !")
        
    elif value_return == 3:
        print("\n🟢 Un panneau vert a été détecté ! 🟢\n")
        robot.set_led_front(None)
        robot.set_led_front("green")
        robot.set_led_back(0,255,0)
        time.sleep(1)
        print("\n🔃 On repart !")
        
    elif value_return == 4 or value_return == 5:
        robot.reset_head()
        time.sleep(1)
    
    robot.reset_head()


def checkcam():
    print('\n📸 CAMERA CHECK 📸\n')
    
    robot.set_led_front(None)
    robot.set_led_back(0,0,0)
    
    value_return = 0
    
    robot.tilt_head_right()
    print("👁️ On regarde à droite")
    time.sleep(0.5)
    if sensors.check_distance_average() <= dist_to_check_max :
        value_return = detection.detection() # 0 --> aucun panneau détecté / 1 --> panneau rouge / 2 --> panneau vert / 3 --> panneau jaune    else:
        print("❗ Trop loing : ", round(sensors.check_distance_average(),2))
    
    if value_return == 0:
        print("🛑 Aucun panneau détecté à droite")
        robot.tilt_head_left()
        print("👁️ On regarde à gauche")
        time.sleep(0.5)
        if sensors.check_distance_average() <= dist_to_check_max :
            value_return = detection.detection() # 0 --> aucun panneau détecté / 1 --> panneau rouge / 2 --> panneau vert / 3 --> panneau jaune
        else:
            print("❗ Trop loing : ", round(sensors.check_distance_average(),2))
    
                
    if value_return == 0:
        print("🛑 Aucun panneau détecté à gauche")
        robot.reset_head()
        print("👁️ On regarde tout droit")
        time.sleep(0.5)
        if sensors.check_distance_average() <= dist_to_check_max :
            value_return = detection.detection()
        else:
            print("❗ Trop loing : ", round(sensors.check_distance_average(),2))
    
    if value_return == 0:
        print("🛑 Aucun panneau détecté nulle part")
    else:
        behavior(value_return)

def run(previous_move):
    global turn_status, speed, angle_rate, color_select, led, check_true_out, backing, last_turn
    status_right = GPIO.input(19)
    status_middle = GPIO.input(16)
    status_left = GPIO.input(20)

    if status_right == 1 and status_middle == 1 and status_left == 1 and previous_move != "Camera":
        robot.stop()
        checkcam()
        move.move(60, 'forward')
        time.sleep(0.5)
        previous_move = "Camera"
        
    elif status_right == color_select:
        if previous_move != "Left":
            print('à gauche')
        check_true_out = 0
        backing = 0
        robot.set_led_back(0,255,0)
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
        robot.set_led_back(0,0,255)
        servo.turnRight(angle_rate)
        move.move(speed_turn, 'forward')
        previous_move = "Right"

    elif status_middle == color_select:
        if previous_move != "Middle":
            print('En arrière')
        check_true_out = 0
        backing = 0
        robot.set_led_back(255,255,255)
        turn_status = 0
        servo.turnMiddle() 
        move.move(speed, 'forward')
        previous_move = "Middle"
    
    else:
        if previous_move != "Back":
            print('Retour à la ligne')
        robot.set_led_back(255,0,0)
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
            else:
                time.sleep(0.1)
                check_true_out = 1
        previous_move = "Back"
    return previous_move

if __name__ == '__main__':
    try:
        
        #! Setup
        move.setup()
        robot = tools.Robot(move, servo)
        sensors = tools.Sensors(robot)
        robot.setup()
        
        
        #! Réinitialisation des servos et moteurs
        robot.stop()
        robot.reset_head()
        
        previous_move = ""
        while 1:
                previous_move = run(previous_move)
        pass
    except KeyboardInterrupt:
        robot.stop()
        robot.destroy()