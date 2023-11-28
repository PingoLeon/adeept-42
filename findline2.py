import RPi.GPIO as GPIO
import time
line_pin_right = 20
line_pin_middle = 16
line_pin_left = 19


def setup():
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(line_pin_right,GPIO.IN)
        GPIO.setup(line_pin_middle,GPIO.IN)
        GPIO.setup(line_pin_left,GPIO.IN)

def run():
        status_right = GPIO.input(line_pin_right)
        status_middle = GPIO.input(line_pin_middle)
        status_left = GPIO.input(line_pin_left)
#  Detect whether the line searching module senses the lines

if status_middle == 1:
		print('forward')
elif status_left == 1:
		print('left')
elif status_right == 1:
		print('right')
else:
		print('stop')

if __name__ == '__main__':
	setup()
	while 1:
	run()
	pass
except	KeyboardInterrupt:

