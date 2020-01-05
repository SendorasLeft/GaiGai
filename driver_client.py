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

INPUT_RATE = 48000
INPUT_ID = None
OUTPUT_ID = None

MIC_THRESHOLD = 2000

# rotary encoder
VOL_PIN_A = 23
VOL_PIN_B = 24

CHNL_PIN_A = 17
CHNL_PIN_B = 18

lastUpdateTime = 0
screen = RPI_I2C_driver.lcd()

def volcw(asd, volControlA):         # turned cw
    if volControlA.is_pressed:
        # print("1")
        changeVol(1)

def volccw(asd, volControlB):        # turned ccw
    if volControlB.is_pressed:
        # print("-1")
        changeVol(0)

def chnlcw(asd, chnlControlA, radio, currChnl):  # turned cw
    # global lastUpdateTime
    global screen
    if chnlControlA.is_pressed:
        # print("1")        
        newChnl = changeChannel(1, currChnl) # return channel number
        # if (time() - lastUpdateTime >= 120): # update if 2s or longer has passed since the value stopped updating
        #     radio.change_channel(newChnl)
        # else:
        #     lastUpdateTime = time()
        screen.lcd_display_string(formatString("Channel " + str(newChnl)), 1)
        radio.change_channel(newChnl)

def chnlccw(asd, chnlControlB, radio, currChnl): # turned ccw
    # global lastUpdateTime
    global screen
    if chnlControlB.is_pressed:
        # print("-1")
        newChnl = changeChannel(0, currChnl) # return channel number
        screen.lcd_display_string(formatString("Channel " + str(newChnl)), 1)
        radio.change_channel(newChnl)

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
    volControlB.when_pressed = volcw(volControlB, volControlA)
    # ccw
    volControlA.when_pressed = volccw(volControlA, volControlB)

    # cw
    chnlControlB.when_pressed = chnlcw(chnlControlB, chnlControlA, radio, radio.get_current_channel())
    # ccw
    chnlControlA.when_pressed = chnlccw(chnlControlA, chnlControlB, radio, radio.get_current_channel())

    radio.connect(server=0)
    radio.start_speaker_stream()

    while True:
        radio.stream_mic_segment_to_server()
        


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 driver_client.py <radio_idx>")
        sys.exit(0)
    main(sys.argv[1])