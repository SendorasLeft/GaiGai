import pyaudio
import librosa
import math
import numpy as np

import constants
from pymumble_py3.callbacks import PYMUMBLE_CLBK_SOUNDRECEIVED
from pymumble_py3.mumble import Mumble


class Radio:
    """
    Class representing the client radio.
    """

    user_name = None
    mic = None
    player = None
    mic_rate = None
    mic_chunk = 1024
    mumble_client = None
    channel = -1
    speaker_stream_started = False
    mic_muted = False

    def __init__(self, radio_idx, input_rate=48000, input_id=None, output_id=None):
        assert (radio_idx in constants.RADIO_NAMES)
        self.user_name = constants.RADIO_NAMES[radio_idx]
        print("Radio Name:", self.user_name)
        self.mic_rate = input_rate
        if input_rate == constants.AUD_DEFAULT_RATE:
            self.mic_chunk = constants.CHUNK_SIZE
        else:
            self.mic_chunk = math.ceil(input_rate / constants.AUD_DEFAULT_RATE * constants.CHUNK_SIZE)
        self.p, self.mic, self.player = io_setup(aud_format=constants.AUD_FORMAT,
                                                 channels=constants.AUD_CHANNELS,
                                                 input_rate=input_rate,
                                                 input_id=input_id,
                                                 output_rate=constants.AUD_DEFAULT_RATE,
                                                 output_id=output_id,
                                                 input_frames_per_buffer=self.mic_chunk,
                                                 output_frames_per_buffer=constants.CHUNK_SIZE)

    def mute_mic(self):
        print("Microphone will now be muted. No sounds will be sent to the server.")
        self.mic_muted = True

    def unmute_mic(self):
        print("Microphone will now be un-muted.")
        self.mic_muted = False

    def get_current_channel(self):
        return self.channel

    def connect(self, channel):
        if not (channel in constants.CHANNELS):
            print("Invalid Channel Specified")
            return

        if self.mumble_client is not None:
            print("Disconnecting from channel", self.get_current_channel())
            self.disconnect()

        print("Now attempting to connect to channel", channel)
        server_details = constants.CHANNELS[channel]
        print(server_details)
        self.mumble_client = Mumble(host=server_details.address,
                                    user=self.user_name,
                                    port=server_details.port,
                                    password=server_details.password)
        self.mumble_client.start()
        self.mumble_client.is_ready()
        print("Connected to server.")

    def start_speaker_stream(self):
        if self.mumble_client is None or self.speaker_stream_started:
            return  # TODO: error code?

        self.mumble_client.callbacks.set_callback(PYMUMBLE_CLBK_SOUNDRECEIVED, self.play_sound)
        self.mumble_client.set_receive_sound(True)
        self.speaker_stream_started = True

    def disconnect(self):
        if self.mumble_client is not None:
            self.mumble_client.reset_callback(PYMUMBLE_CLBK_SOUNDRECEIVED)
            self.mumble_client.set_receive_sound(False)
            self.speaker_stream_started = False
            self.mumble_client.close()
            self.mumble_client = None
            prev_channel = self.get_current_channel()
            self.channel = -1
            return prev_channel
        else:
            return -2  # TODO: replace with proper error code or exception?

    def play_sound(self, sender, sound_segment):
        self.player.write(sound_segment.pcm)

    def stream_mic_segment_to_server(self):
        if not self.mic_muted:
            self.mumble_client.sound_output.add_sound(self.get_mic_segment())

    def get_mic_segment(self):
        data = self.mic.read(self.mic_chunk, exception_on_overflow=False)
        if self.mic_rate == constants.AUD_DEFAULT_RATE:
            return data
        else:
            decoded_data = np.fromstring(data, np.int16)
            #print(decoded_data)
            data_48k = librosa.resample(decoded_data,
                                        self.mic_rate,
                                        constants.AUD_DEFAULT_RATE)
            #data_48k_floor = np.floor(data_48k * 32768).astype(np.int16)
            #print(self.mic_chunk, self.mic_rate, constants.AUD_DEFAULT_RATE)
            #print(len(data_48k))
            return data_48k[0:1024].tostring()


def io_setup(aud_format,
             channels,
             input_rate,
             input_id,
             output_rate,
             output_id,
             input_frames_per_buffer,
             output_frames_per_buffer):

    p = pyaudio.PyAudio()

    if input_id is None:
        mic = p.open(format=aud_format,
                     channels=channels,
                     rate=input_rate,
                     input=True,
                     frames_per_buffer=input_frames_per_buffer-1)
    else:
        mic = p.open(format=aud_format,
                     channels=channels,
                     rate=input_rate,
                     input_device_index=input_id,
                     input=True,
                     frames_per_buffer=input_frames_per_buffer-1)

    if output_id is None:
        player = p.open(format=aud_format,
                        channels=channels,
                        rate=output_rate,
                        output=True,
                        frames_per_buffer=output_frames_per_buffer)
    else:
        player = p.open(format=aud_format,
                        channels=channels,
                        rate=output_rate,
                        output_device_index=output_id,
                        output=True,
                        frames_per_buffer=output_frames_per_buffer)
    return p, mic, player



