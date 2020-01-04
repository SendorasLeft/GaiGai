# Original code found at:
# https://www.raspberrypi.org/forums/viewtopic.php?t=198815
# Written by PiLauwers

from gpiozero import Button
from vol_control import changeVol 

pinA = Button(17, pull_up=True) # 23 / 17
pinB = Button(18, pull_up=True) # 24 / 18

def ccw():                # turned ccw
    if pinB.is_pressed: 
        # print("-1")       # pin A rising while B is active
        changeVol(0)

def cw():                 # turned cw
    if pinA.is_pressed:
        # print("1")        # pin B rising while A is active
        changeVol(1)

pinA.when_pressed = ccw   # register the event handler for pin A
pinB.when_pressed = cw    # register the event handler for pin B

