import sys

from threading import Thread
from multiprocessing import Process

from radio import Radio
from knob.rotary_encoder import volume_main
from lcd.RPI_I2C_driver import RPI_I2C_driver
from lcd.channel_display import controlChannel

INPUT_RATE = 48000
INPUT_ID = None
OUTPUT_ID = None

MIC_THRESHOLD = 2000

def GPIOsetup(clk, dt):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def main(radio_idx):
    radio = Radio(int(radio_idx),
                  mic_threshold=MIC_THRESHOLD,
                  input_rate=INPUT_RATE,
                  input_id=INPUT_ID,
                  output_id=OUTPUT_ID)
    
    # GPIO setup for changing channel
    clk = 17
    dt = 18
    lcd = RPI_I2C_driver.lcd()
    GPIOsetup(clk, dt)
    channel = 0
    clkLastState = GPIO.input(clk)

    # initialize volume control
    volume_thread = Thread(target=volume_main)
    volume_thread.start()

    radio.connect(server=0)
    radio.start_speaker_stream()

    while True:
        radio.stream_mic_segment_to_server()
        # lcd channel stuff
        clkState = GPIO.input(clk)
        dtState = GPIO.input(dt)
        channel = controlChannel(clkState, dtState, clkLastState, channel, lcd)
        sleep(0.1)
        clkLastState = clkState


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 driver_client.py <radio_idx>")
        sys.exit(0)
    main(sys.argv[1])