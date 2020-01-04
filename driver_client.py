import sys

from threading import Thread
from multiprocessing import Process

from radio import Radio
from knob.rotary_encoder import volume_main

INPUT_RATE = 48000
INPUT_ID = None
OUTPUT_ID = None

MIC_THRESHOLD = 2000


def main(radio_idx):
    radio = Radio(int(radio_idx),
                  mic_threshold=MIC_THRESHOLD,
                  input_rate=INPUT_RATE,
                  input_id=INPUT_ID,
                  output_id=OUTPUT_ID)

    # initialize volume control
    volume_thread = Thread(target=volume_main)
    volume_thread.start()

    radio.connect(server=0)
    radio.start_speaker_stream()

    while True:
        radio.stream_mic_segment_to_server()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 driver_client.py <radio_idx>")
        sys.exit(0)
    main(sys.argv[1])