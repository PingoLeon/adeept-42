import time
import sys
sys.path.insert(0,'/home/pi/adeept_picar-b/server/')
import RPIservo
import Adafruit_PCA9685


# Initialize the pan servo controller for left and right movement
head = RPIservo.ServoCtrl()
head.start()

def reset():
    # Initialise the PCA9685 using the default address (0x40).
    pwm = Adafruit_PCA9685.PCA9685()
    pwm.set_pwm_freq(50)
    x = 0
    while x < 16:
        pwm.set_all_pwm(0, 300)
        x += 1

def tilt_head_right():
    head.moveAngle(1, -45)

def tilt_head_left():
    head.moveAngle(1, 45)

# Function to tilt the head based on the current position
def tilt_head(position):
    if position == "left":
        tilt_head_left()
    elif position == "right":
        tilt_head_right()

if __name__ == "__main__":
    reset()