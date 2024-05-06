import sys
import cv2
import numpy as np
import detection_class

sys.path.insert(0,'/home/pi/adeept_picar-b/server/')
import RPi.GPIO as GPIO
import GUImove as move
import servo
import LED
import RGB
import ultra
import RPIservo
import Adafruit_PCA9685

class Robot:
    def __init__(self, move, servo):
        self.head = RPIservo.ServoCtrl()
        self.head.start()
        self.move = move
        self.servo = servo
        self.led = LED.LED()
        self.led_ctrl = LED.LED_ctrl()
        self.RGB = RGB
    
    def setup(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(19, GPIO.IN)
        GPIO.setup(16, GPIO.IN)
        GPIO.setup(20, GPIO.IN)
        RGB.setup()

    def reset_head(self):
        pwm = Adafruit_PCA9685.PCA9685()
        pwm.set_pwm_freq(50)
        x = 0
        while x < 16:
            pwm.set_all_pwm(0, 300)
            x += 1

    def tilt_head_right(self):
        self.head.moveAngle(1, -45)

    def tilt_head_left(self):
        self.head.moveAngle(1, 45)

    def stop(self):
        self.move.move(0, 'stop')
        self.move.motorStop()
        self.servo.turnMiddle()
        self.reset_head()
    
    def destroy(self):
        self.stop()
        self.move.destroy()
        self.led_ctrl.destroy()
        RGB.both_off()
        self.led.colorWipe(0, 0, 0)
        self.led_ctrl.stop()
    
    def set_led_back(self, r, g, b):
        self.led.colorWipe(r, g, b)
    
    def set_led_front(self, color):
        if color == None:
            self.RGB.both_off()
        elif color == "red":
            self.RGB.red()
        elif color == "green":
            self.RGB.green()
        elif color == "yellow":
            self.RGB.yellow()
        
class Sensors:
    def __init__(self, robot):
        self.robot = robot
        self.parametres = cv2.aruco.DetectorParameters_create()
        self.dictionnaire = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)

    def check_distance_average(self):
        distance_list = []
        for _ in range(5):
            distance = ultra.checkdist() * 100  # Convertir en cm
            distance_list.append(distance)
        average_distance = sum(distance_list) / len(distance_list)
        return average_distance

    def take_image(self):
        camera = cv2.VideoCapture(0)
        x, image = camera.read()
        camera.release()
        cv2.imwrite("imageInitiale.png", image)
        sens_fleche = None
        coinsMarqueurs, idsMarqueur, _ = cv2.aruco.detectMarkers(image, self.dictionnaire, parameters=self.parametres)
        if idsMarqueur is not None and len(coinsMarqueurs) == 4 and len(set(idsMarqueur.flatten())) == 1:
            self.robot.stop()  # Utiliser l'instance de Robot stockée
            sens_fleche = self.zoomIn(image, coinsMarqueurs, idsMarqueur)
            return sens_fleche
        else:
            return None
    
    def zoomIn(self, image, coinsMarqueurs, idsMarqueur):
        print("✅ 4 Arucos avec le même identifiant trouvés !")
        ids = idsMarqueur.flatten()	
        tous_coins = []
        image_marquee = image
        for (coinMarqueur, idMarqueur) in zip(coinsMarqueurs, ids):
            coins = coinMarqueur.reshape((4, 2))
            tous_coins.append(coins)

        print("🔍 On zoom sur l'image dans la zone des 4 marqueurs")
        tous_coins = np.concatenate(tous_coins)
        top_left = np.min(tous_coins, axis=0)
        bottom_right = np.max(tous_coins, axis=0)
        top_right = np.array([bottom_right[0], top_left[1]])
        bottom_left = np.array([top_left[0], bottom_right[1]])

        offset = 35
        if idsMarqueur[0] == 13:
            offset = 15
            
        points1 = np.float32([top_left + [offset, offset], top_right + [-offset, offset], bottom_right + [-offset, -offset], bottom_left + [offset, -offset]])
        points2 = np.float32([[0, 0], [200, 0], [200, 200], [0, 200]])

        vecttrans = cv2.getPerspectiveTransform(points1, points2)
        image_zoomee = cv2.warpPerspective(image, vecttrans, (200, 200))
        cv2.imwrite('image_zoomee.png', image_zoomee)
        
        sens_fleche = None
        chiffre = None
        detection_instance = detection_class.Detection()  # Créez une instance de Detection
        if idsMarqueur[0] == 8: #? L'ID des rectangles de couleur est 8
            print("🤔 Il devrait y avoir un rectangle de couleur dans la zone zoomée")
            value_return = detection_instance.rectangle(image_zoomee) 
            return value_return #! 1 --> panneau rouge / 2 --> panneau vert / 3 --> panneau jaune
        
        elif idsMarqueur[0] == 13: #? L'ID de la flèche est 13
            print("🔍 On recherche une flèche dans l'image zoomée")
            value_return = detection_instance.fleche(image_zoomee)
            return value_return  #! 4 --> Droite / 5 --> Gauche
        
        elif idsMarqueur[0] == 9: #? L'ID des chiffres est 9
            print("🔢 On va essayer de voir si y'a un chiffre dans l'image")
            if image != None:
                print("L'image fonctionne !")
            value_return = detection_instance.chiffre(image_zoomee)  # Appelez la méthode chiffre() sur l'instance
            return 6 #! 6 --> Chiffre détecté
        
        else:
            print("🚫 Rien de connu n'a été détecté...")
            return 0