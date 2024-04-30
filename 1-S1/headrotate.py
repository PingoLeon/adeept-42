import time
import initservo as servo
import sys
sys.path.insert(0,'/home/pi/adeept_picar-b/server/')
import RPIservo


# Initialize the pan servo controller for left and right movement
head = RPIservo.ServoCtrl()
head.start()

def reset():
    servo.reset()

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
    time.sleep(1)
    tilt_head_left()
    time.sleep(1)
    tilt_head_right()
    time.sleep(1)
    reset()