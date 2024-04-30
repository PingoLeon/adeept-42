#!/usr/bin/python3
# File name   : findline.py
# Description : line tracking 
# Website     : www.adeept.com
# Author      : William
# Date        : 2019/11/21
import sys
sys.path.insert(0,'/home/pi/adeept_picar-b/server/')
import RPi.GPIO as GPIO
import time
import GUImove as move
import servo
import LED
import head
import RGB

import ultra



if __name__ == '__main__':
    try:
        while 1:
            previous_move, number_of_tiret = run(previous_move, number_of_tiret)
        pass
    except KeyboardInterrupt:
        head.reset_head()
        move.destroy()