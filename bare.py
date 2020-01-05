import sys

from threading import Thread
from multiprocessing import Process
from time import sleep, time
from RPi import GPIO

from radio import Radio
# from knob.rotary_encoder import volume_main
import RPI_I2C_driver
# from lcd.channel_display import controlChannel

from gpiozero import Button
from knob.vol_control import changeVol
from knob.channel_control import changeChannel
from lcd.formatString import formatString
from switch.lcd_start_stop import display

INPUT_RATE = 48000
INPUT_ID = None
OUTPUT_ID = None

MIC_THRESHOLD = 1000

# rotary encoder
VOL_PIN_A = 23
VOL_PIN_B = 24

CHNL_PIN_A = 17
CHNL_PIN_B = 18

POWER_PIN = 26
MUTE_PIN = 19

lastUpdateTime = 0
screen = RPI_I2C_driver.lcd()
currChnl = 0

volControlA = Button(VOL_PIN_A, pull_up=True)
volControlB = Button(VOL_PIN_B, pull_up=True)
chnlControlA = Button(CHNL_PIN_A, pull_up=True)
chnlControlB = Button(CHNL_PIN_B, pull_up=True)

def volcw():         # turned cw
    if volControlA.is_pressed:
        # print("1")
        changeVol(1)

def volccw():        # turned ccw
    if volControlB.is_pressed:
        # print("-1")
        changeVol(0)

def chnlcw():  # turned cw
    # global lastUpdateTime
    if chnlControlA.is_pressed:
        print("1")
        newChnl = changeChannel(1, currChnl) # return channel number
        # if (time() - lastUpdateTime >= 120): # update if 2s or longer has passed since the value stopped updating
        #     radio.change_channel(newChnl)
        # else:
        #     lastUpdateTime = time()
        screen.lcd_display_string(formatString("Channel " + str(newChnl)), 1)
        currChnl = newChnl

def chnlccw(): # turned ccw
    # global lastUpdateTime
    if chnlControlB.is_pressed:
        print("-1")
        newChnl = changeChannel(0, currChnl) # return channel number
        screen.lcd_display_string(formatString("Channel " + str(newChnl)), 1)
        currChnl = newChnl

# power on off
def switchedOn():
    print("on")
    display(1)

def switchedOff():
    print("off")
    display(0)
    
def muteMic():
    i = 1
    
def unmuteMic():
    i = 1

# def GPIOsetup(clk, dt):
#     GPIO.setmode(GPIO.BCM)
#     GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#     GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def main(radio_idx):
    # initialize volume control
    # volume_thread = Thread(target=volume_main)
    # volume_thread.start()
    #
    # channel_selection_thread = Thread(target=channel_selection)
    # channel_selection_thread.start()

    # power button
    powerButton = Button(POWER_PIN, pull_up=False)
    # mute button
    muteButton = Button(MUTE_PIN, pull_up=False)

    powerButton.when_pressed = switchedOn
    powerButton.when_released = switchedOff
    muteButton.when_pressed = unmuteMic
    muteButton.when_released = muteMic
    
    # assign functions for change volume
    volControlB.when_pressed = volcw
    volControlA.when_pressed = volccw

    # assign functions for change channel
    chnlControlB.when_pressed = chnlcw
    chnlControlA.when_pressed = chnlccw

    while True:
        i = 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 driver_client.py <radio_idx>")
        sys.exit(0)
    main(sys.argv[1])