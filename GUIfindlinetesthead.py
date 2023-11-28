import time
import RPIservo

# Initialize the pan servo controller for left and right movement
P_sc = RPIservo.ServoCtrl()
P_sc.start()

# Function to tilt the head to the left with a wider angle
def tilt_head_left():
    P_sc.singleServo(1, 1, 7)  # Increase the second argument for a wider angle

# Function to tilt the head to the right with a wider angle
def tilt_head_right():
    P_sc.singleServo(1, -1, 7)  # Decrease the second argument for a wider angle

# Function to bring the head back to the middle
def tilt_head_middle():
    P_sc.singleServo(1, 1, 10)  # Adjust the angle as needed


if __name__ == '__main__':
    choice = -1
    try:
        while True:
            
            if choice == 1:
                for i in range(5):
                    tilt_head_right()
                    time.sleep(0.2)
                print("Going Right\n")
                time.sleep(3)  # Adjust the duration as needed
                choice = -1
            else:
                # Tilt the head to the right with a wider angle
                for i in range(15):
                    tilt_head_left()
                    time.sleep(0.2)
                    tilt_head_left()
                    tilt_head_left()
                print("Going Left ! \n")
                time.sleep(3)  # Adjust the duration as needed
                choice = 1
    except KeyboardInterrupt:
        pass