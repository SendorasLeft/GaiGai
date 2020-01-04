import pyaudio
from collections import namedtuple

# radio_idx to username mappings
RADIO_NAMES = {
    1: "RadioOne",
    2: "RadioTwo",
    3: "RadioThree",
    4: "RadioFour",
    5: "RadioFive",
    6: "RadioSix",
    7: "RadioSeven"
}

CHANNELS = [1, 5, 3, 4]

# pyaudio
AUD_FORMAT = pyaudio.paInt16
AUD_CHANNELS = 1
AUD_DEFAULT_RATE = 48000

# packet chunk
CHUNK_SIZE = 1024

# server details TODO: define new channels
ServerDetails = namedtuple("ServerDetails",
                           "password address port")
SERVERS = {
    0: ServerDetails(password="password",
                     address="192.168.43.130",
                     port=64738),
    1: ServerDetails(password="password",
                     address="192.168.43.130",
                     port=64738),
    2: ServerDetails(password="password",
                     address="192.168.43.130",
                     port=64738)
}
