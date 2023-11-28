# initservo.py
import time
import Adafruit_PCA9685

def reset_servo():
    # Initialise the PCA9685 using the default address (0x40).
    pwm = Adafruit_PCA9685.PCA9685()
    pwm.set_pwm_freq(50)
    x = 0
    while x < 16:
        pwm.set_all_pwm(0, 300)
        x += 1

if __name__ == "__main__":
    # If this script is executed directly, call the function
    reset_servo()

	

	


