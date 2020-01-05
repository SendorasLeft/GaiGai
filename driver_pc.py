import sys

from radio import Radio

from threading import Thread

INPUT_RATE = 48000
INPUT_ID = None
OUTPUT_ID = None

MIC_THRESHOLD = 2000

radio = None


def speaker_loop():
    global radio
    while True:
        data = radio.handle_sound_queue()
        if data is not None:
            radio.play_sound(" ", data)
        time.sleep()


def main(radio_idx):
    global radio
    radio = Radio(int(radio_idx),
                  mic_threshold=MIC_THRESHOLD,
                  input_rate=INPUT_RATE,
                  input_id=INPUT_ID,
                  output_id=OUTPUT_ID)

    radio.connect(server=0)
    radio.start_speaker_stream()

    speaker_thread = Thread(target=speaker_loop)
    speaker_thread.start()

    while True:
        radio.stream_mic_segment_to_server()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 driver_client.py <radio_idx>")
        sys.exit(0)
    main(sys.argv[1])