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

# switch
POWER_PIN = 26
MUTE_PIN = 19

radio = None
lastUpdateTime = 0
channel = 0
screen = RPI_I2C_driver.lcd()
screen.backlight(0)
power = False # True

volControlA = Button(VOL_PIN_A, pull_up=True)
volControlB = Button(VOL_PIN_B, pull_up=True)
chnlControlA = Button(CHNL_PIN_A, pull_up=True)
chnlControlB = Button(CHNL_PIN_B, pull_up=True)

def volcw():
    if power == True and volControlA.is_pressed:
        # print("1")
        changeVol(1)

def volccw():
    if power == True and volControlB.is_pressed:
        # print("-1")
        changeVol(0)

def chnlcw():
    global lastUpdateTime, channel
    if power == True and chnlControlA.is_pressed:
        print("1")
        currChnl = radio.get_current_channel()
        newChnl = changeChannel(1, currChnl) # return channel number
        lastUpdateTime = time()
        channel = newChnl
        screen.lcd_display_string(formatString("Channel " + str(newChnl)), 1)
        # radio.change_channel(newChnl)
        

def chnlccw():
    # global lastUpdateTime
    if power == True and chnlControlB.is_pressed:
        print("-1")
        currChnl = radio.get_current_channel()
        newChnl = changeChannel(0, currChnl) # return channel number
        lastUpdateTime = time()
        channel = newChnl
        screen.lcd_display_string(formatString("Channel " + str(newChnl)), 1)
        # radio.change_channel(newChnl)

# power on off
def switchedOn():
    global power
    print("on")
    display(1)
    power = True

def switchedOff():
    global power
    print("off")
    display(0)
    power = False
    
def muteMic():
    if power == True:
        radio.mute_mic()
    
def unmuteMic():
    if power == True:
        radio.unmute_mic()

# def GPIOsetup(clk, dt):
#     GPIO.setmode(GPIO.BCM)
#     GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#     GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def main(radio_idx):
    global radio
    radio = Radio(int(radio_idx),
                  mic_threshold=MIC_THRESHOLD,
                  input_rate=INPUT_RATE,
                  input_id=INPUT_ID,
                  output_id=OUTPUT_ID)

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

    radio.connect(server=0)
    radio.start_speaker_stream()

    while True:
        radio.stream_mic_segment_to_server()
        if radio.get_current_channel() != channel and time() - lastUpdateTime >= 120:
            print("changing channel...")
            radio.change_channel(channel)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 driver_client.py <radio_idx>")
        sys.exit(0)
    main(sys.argv[1])