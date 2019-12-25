# Original code found at:
# https://github.com/modmypi/Rotary-Encoder/
# Install command for alsaaudio:
# sudo -H pip3 install pyalsaaudio

from Knob import Knob
from time import sleep
import alsaaudio

def getVolumeChange(vol):
    if vol >= 94:
        return 1
    elif vol >= 90:
        return 2
    elif vol >= 80:
        return 3
    elif vol >= 70:
        return 4
    elif vol >= 55:
        return 5
    else:
        return 7

def increaseVolume(mixer):
    vol = mixer.getvolume()[0]
    if vol >= 97: # can't exceed 96 because it will be overly-loud
        return
    if vol + getVolumeChange(vol) > 97:
        mixer.setvolume(97)
        print("volume set to 97")
        return
    mixer.setvolume(vol + getVolumeChange(vol))
    print("volume set to", mixer.getvolume()[0])

def decreaseVolume(mixer):
    vol = mixer.getvolume()[0]
    if vol <= 25: # can't exceed 25 because it will be too soft
        return
    if vol - getVolumeChange(vol) < 25:
        mixer.setvolume(25)
        print("volume set to 25")
        return
    mixer.setvolume(vol - getVolumeChange(vol))
    print("volume set to", mixer.getvolume()[0])

def loop(knob, mixer):
    while True:
        isRotatedCW = knob.isRotatedCW()
        if isRotatedCW == 1:
            increaseVolume(mixer)
        elif isRotatedCW == 0:
            decreaseVolume(mixer)
        sleep(0.01)

def main():
    clk = 17
    dt = 18
    knob = Knob(clk, dt)
    mixer = alsaaudio.Mixer(alsaaudio.mixers()[0])
    try:
        loop(knob, mixer)
    except KeyboardInterrupt:
        print("keyboard interrupt detected, program closing...")
        knob.close()

if __name__ == '__main__':
    main()
