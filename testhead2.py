import time
import RPIservo

# Initialize the pan servo controller for left and right movement
P_sc = RPIservo.ServoCtrl()
P_sc.start()

if __name__ == '__main__':
    choice = -1
    try:
        for i in range(14):
                    P_sc.singleServo(1, -1, 2)
                    time.sleep(0.2)
        while True:
                for i in range(30):
                    P_sc.singleServo(1, 1, 2)
                    time.sleep(0.2)
                for i in range(30):
                    P_sc.singleServo(1, -1, 2)
                    time.sleep(0.2)

    except KeyboardInterrupt:
        pass