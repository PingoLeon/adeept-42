import RPi.GPIO as GPIO
import time
import GUImove as move
import servo
import LED

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

led = LED.LED()
turn_status = 0
speed = 75
noir = 1 # 0 --> white line / 1 --> black line
check_true_out = 0
backing = 0
last_turn = 0

def run():
    global turn_status, speed, angle_rate, noir, led, check_true_out, backing, last_turn
    droite = GPIO.input(line_pin_right)
    milieu = GPIO.input(line_pin_middle)
    gauche = GPIO.input(line_pin_left)
    #print('R%d   M%d   L%d'%(status_right,status_middle,status_left))

    if droite != noir and milieu != noir and gauche != noir: # 000
        #print("Il n'y a rien, il faut avancer et tourner progressivement à droite avec un angle qui augmente, afin de retrouver éventuellement la ligne")
        led.colorWipe(0, 0, 0)  # Éteindre la LED
        turn_status = 1
        servo.turnRight()
        move.move(speed, 'forward')
        check_true_out = 0
        backing = 0
        last_turn = -1

    elif droite != noir and milieu != noir and gauche == noir: # 001
        print("Il faut aller à droite")
        led.colorWipe(0, 0, 255)  # LED bleue
        turn_status = 1
        servo.turnRight()
        move.move(speed, 'forward')
        check_true_out = 0
        backing = 0
        last_turn = 1

    elif droite != noir and milieu == noir and gauche != noir: # 010
        print("Il faut aller tout droit pour garder la ligne au maximum")
        led.colorWipe(255, 255, 255)  # LED blanche
        turn_status = 0
        servo.turnMiddle()
        move.move(speed, 'forward')
        check_true_out = 0
        backing = 0
        last_turn = 0

    elif droite != noir and milieu == noir and gauche == noir: # 011
        print("On a encore de la marge, on va tout droit, il faudra bientôt tourner à droite")
        led.colorWipe(255, 255, 255)  # LED blanche
        turn_status = 0
        servo.turnMiddle()
        move.move(speed, 'forward')
        check_true_out = 0
        backing = 0
        last_turn = 0

    elif droite == noir and milieu != noir and gauche != noir: # 100
        print("On va à gauche")
        led.colorWipe(0, 255, 0)  # LED verte
        turn_status = -1
        servo.turnLeft()
        move.move(speed, 'forward')
        check_true_out = 0
        backing = 0
        last_turn = -1

    elif droite == noir and milieu != noir and gauche == noir: # 101
        print("Cas étrange, on est sur une bifurcation, on va choisir une direction aléatoire")
        led.colorWipe(255, 255, 0)  # LED jaune

        import random
        random_direction = random.choice([-1, 1])  # Choisir aléatoirement -1 (gauche) ou 1 (droite)

        if random_direction == -1:
            print("On va à gauche")
            turn_status = -1
            servo.turnLeft()
            move.move(speed, 'forward')
        else:
            print("On va à droite")
            turn_status = 1
            servo.turnRight()
            move.move(speed, 'forward')
        check_true_out = 0
        backing = 0

    elif droite == noir and milieu == noir and gauche != noir: # 110
        print("On a encore de la marge, on va bientôt tourner à gauche")
        led.colorWipe(255, 255, 255)  # LED blanche
        turn_status = 0
        servo.turnMiddle()
        move.move(speed, 'forward')
        check_true_out = 0
        backing = 0
        last_turn = -1

    elif droite == noir and milieu == noir and gauche == noir: # 111
        print("On est perpendiculaire par rapport à la ligne, il faut en sortir afin d'en faire une spirale avec l'étape suivante")
        led.colorWipe(0, 0, 0)  # Éteindre la LED
        turn_status = 1
        servo.turnRight()
        move.move(speed, 'forward')
        check_true_out = 0
        backing = 0
        last_turn = 1

    else: # Cas impossible (ne devrait jamais se produire)
        pass






#BOUCLE PRINCIPALE
if __name__ == '__main__':
    try:
        setup()
        move.setup()
        
        while 1:
            run()
            
        pass
    except KeyboardInterrupt:
        move.destroy()

