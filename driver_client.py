import sys

from threading import Thread
from multiprocessing import Process
from time import sleep
from RPi import GPIO

from radio import Radio
# from knob.rotary_encoder import volume_main
import RPI_I2C_driver
# from lcd.channel_display import controlChannel

from gpiozero import Button
from knob.vol_control import changeVol
from knob.channel_control import changeChannel

INPUT_RATE = 48000
INPUT_ID = None
OUTPUT_ID = None

MIC_THRESHOLD = 2000

# rotary encoder
VOL_PIN_A = 17
VOL_PIN_B = 18

CHNL_PIN_A = 23
CHNL_PIN_B = 24

def volcw(volControlA):         # turned cw
    if volControlA.is_pressed:  # pin B rising while A is active
        # print("1")
        return changeVol(1)

def volccw(volControlB):        # turned ccw
    if volControlB.is_pressed:  # pin A rising while B is active
        # print("-1")
        return changeVol(0)

def chnlcw(volControlA, radio):  # turned cw
    if chnlControlA.is_pressed:  # pin B rising while A is active
        # print("1")        
        return changeChannel(1, radio)

def chnlccw(volControlB, radio): # turned ccw
    if chnlControlB.is_pressed:  # pin A rising while B is active
        # print("-1")       
        return changeChannel(0, radio)

# global channel
# channel = 0

# def GPIOsetup(clk, dt):
#     GPIO.setmode(GPIO.BCM)
#     GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#     GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def main(radio_idx):
    # global channel
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

    # change channel stuff
    volControlA = Button(VOL_PIN_A, pull_up=True)
    volControlB = Button(VOL_PIN_B, pull_up=True)
    chnlControlA = Button(CHNL_PIN_A, pull_up=True)
    chnlControlB = Button(CHNL_PIN_B, pull_up=True)
    
    # cw
    volControlB.when_pressed = volcw(volControlA)
    # ccw
    volControlA.when_pressed = volccw(volControlB)

    # cw
    chnlControlB.when_pressed = chnlcw(chnlControlA, radio)
    # ccw
    chnlControlA.when_pressed = chnlccw(chnlControlB, radio)

    radio.connect(server=0)
    radio.start_speaker_stream()

    while True:
        radio.stream_mic_segment_to_server()
        


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 driver_client.py <radio_idx>")
        sys.exit(0)
    main(sys.argv[1])