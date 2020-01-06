import pyaudio
import wave
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

CHANNELS = [1, 5, 3, 4, 6]

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

CHUNK = 1024

CH_POWERON = "./voice/chinese/poweron.wav"
CH_POWEROFF = "./voice/chinese/poweroff.wav"
CH_CHNL0 = "./voice/chinese/chnl0.wav"
CH_CHNL1 = "./voice/chinese/chnl1.wav"
CH_CHNL2 = "./voice/chinese/chnl2.wav"
CH_CHNL3 = "./voice/chinese/chnl3.wav"
CH_CHNL4 = "./voice/chinese/chnl4.wav"
CH_MUTE = "./voice/chinese/muted.wav"
CH_UNMUTE = "./voice/chinese/unmuted.wav"

EN_POWERON = "./voice/english/poweron.wav"
EN_POWEROFF = "./voice/english/poweroff.wav"
EN_CHNL0 = "./voice/english/chnl0.wav"
EN_CHNL1 = "./voice/english/chnl1.wav"
EN_CHNL2 = "./voice/english/chnl2.wav"
EN_CHNL3 = "./voice/english/chnl3.wav"
EN_CHNL4 = "./voice/english/chnl4.wav"
EN_MUTE = "./voice/english/muted.wav"
EN_UNMUTE = wave.open("./voice/english/unmuted.wav")

CHNL0 = [EN_CHNL0, CH_CHNL0]
CHNL1 = [EN_CHNL1, CH_CHNL1]
CHNL2 = [EN_CHNL2, CH_CHNL2]
CHNL3 = [EN_CHNL3, CH_CHNL3]
CHNL4 = [EN_CHNL4, CH_CHNL4]

# BILINGUAL NOTIFICATION
POWERON = [EN_POWERON, CH_POWERON]
POWEROFF = [EN_POWEROFF, EN_POWEROFF]
CHNLS = [CHNL0, CHNL1, CHNL2, CHNL3, CHNL4]
MUTE = [EN_MUTE, CH_MUTE]
UNMUTE = [EN_UNMUTE, CH_UNMUTE]
