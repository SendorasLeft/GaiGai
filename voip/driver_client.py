import sys

from radio import Radio

INPUT_RATE = 16000
INPUT_ID = 2
OUTPUT_ID = 2


def main(radio_idx):
    radio = Radio(int(radio_idx),
                  input_rate=INPUT_RATE,
                  input_id=INPUT_ID,
                  output_id=OUTPUT_ID)

    radio.connect(channel=0)
    radio.start_speaker_stream()

    while True:
        radio.stream_mic_segment_to_server()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 driver_client.py <radio_idx>")
        sys.exit(0)
    main(sys.argv[1])