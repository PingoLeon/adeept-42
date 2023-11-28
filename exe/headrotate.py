import time
import initservo as servo
import sys
sys.path.insert(0,'/home/pi/adeept_picar-b/server/')
import RPIservo


# Initialize the pan servo controller for left and right movement
P_sc = RPIservo.ServoCtrl()
P_sc.start()

# Function to tilt the head to the left with a wider angle
def tilt_head_left():
    print("Head Going Left\n")
    P_sc.singleServo(1, 1, 7)  # Adjust the third argument for the desired speed
    time.sleep(0.7)
    P_sc.stopWiggle()  # Stop the servo movement after 0.2 seconds


# Function to tilt the head to the right with a wider angle
def tilt_head_right():
    print("Head Going Left\n")
    P_sc.singleServo(1, -1, 5)  # Adjust the third argument for the desired speed
    time.sleep(0.5)
    P_sc.stopWiggle()  # Stop the servo movement after 0.2 seconds

def reset_head():
    
    servo.reset_servo()

# Function to tilt the head based on the current position
def tilt_head(position):
    if position == "left":
        tilt_head_left()
    elif position == "right":
        tilt_head_right()
