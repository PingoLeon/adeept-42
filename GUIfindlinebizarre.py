import RPi.GPIO as GPIO
import time
import GUImove as move
import servo
import LED

line_pin_right = 19
line_pin_middle = 16
line_pin_left = 20
led = LED.LED()
turn_status = 0
speed = 75
angle_rate = 0.5
color_select = 1
check_true_out = 0
backing = 0
last_turn = 0
Tr = 11
Ec = 8


def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(line_pin_right, GPIO.IN)
    GPIO.setup(line_pin_middle, GPIO.IN)
    GPIO.setup(line_pin_left, GPIO.IN)
    GPIO.setup(Tr, GPIO.OUT,initial=GPIO.LOW)
    GPIO.setup(Ec, GPIO.IN)

def checkdist():       #Reading distance

    GPIO.output(Tr, GPIO.HIGH)
    time.sleep(0.000015)
    GPIO.output(Tr, GPIO.LOW)
    while not GPIO.input(Ec):
        pass
    t1 = time.time()
    while GPIO.input(Ec):
        pass
    t2 = time.time()
    return round((t2-t1)*340/2,2)



def run():
    global turn_status, speed, angle_rate, color_select, led, check_true_out, backing, last_turn

    status_right = GPIO.input(line_pin_right)
    status_middle = GPIO.input(line_pin_middle)
    status_left = GPIO.input(line_pin_left)
    
    dist = checkdist()*100
    print(dist)
    if 25 <= dist <= 30:
      move.motorStop()
      print('Tourner la tete a gauche')
      gauche = checkdist()*100
      time.sleep(3)  # Attendre pendant 1 seconde
      droite = checkdist()*100
      time.sleep(3)
      while status_right != color_select and status_left != color_select and status_middle != color_select :
        if gauche > droite:
            print('Turning left')
            servo.turnLeft(angle_rate)  
            move.move(speed, 'forward')
            time.sleep(2)
            servo.turnRight(angle_rate)  
            move.move(speed, 'backward')
            time.sleep(2)  
            servo.turnMiddle()
            move.move(speed, 'forward')
            time.sleep(0.5) 
        else:
            print('Turning right')
            servo.turnRight(angle_rate)
            move.move(speed, 'forward')
            time.sleep(2) 
            servo.turnLeft(angle_rate) 
            move.move(speed, 'backward')
            time.sleep(2)
            servo.turnMiddle() 
            move.move(speed, 'forward')
            time.sleep(0.5) 

    elif status_right == color_select:
        check_true_out = 0
        backing = 0
        print('left')
        turn_status = -1
        last_turn = -1
        servo.turnLeft(angle_rate)
        move.move(speed, 'forward')

    elif status_left == color_select:
        check_true_out = 0
        backing = 0
        print('right')
        turn_status = 1
        last_turn = 1
        servo.turnRight(angle_rate)
        move.move(speed, 'forward')

    elif status_middle == color_select:
        check_true_out = 0
        backing = 0
        print('middle')
        turn_status = 0
        servo.turnMiddle()
        move.move(speed, 'forward')

    else:
        print('none')
        led.colorWipe(255, 0, 0)
        if not backing:
            if check_true_out:
                check_true_out = 0
                if turn_status == 0:
                    if last_turn == 1:
                        servo.turnRight(angle_rate)
                    else:
                        servo.turnLeft(angle_rate)
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
                
if __name__ == '__main__':
    try:
        setup()
        move.setup()

        while 1:
            run()

        pass
    except KeyboardInterrupt:
        move.destroy()