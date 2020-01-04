# Original code found at:
# https://github.com/modmypi/Rotary-Encoder/
# Install command for alsaaudio:
# sudo -H pip3 install pyalsaaudio


from RPi import GPIO
from time import sleep
import alsaaudio


def setup(clk, dt):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


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


def controlVolume(clkState, dtState, clkLastState, mixer):
    if clkState != clkLastState:
        if dtState != clkState:
            increaseVolume(mixer)
        else:
            decreaseVolume(mixer)
        sleep(0.1)


def loop(clk, dt, mixer):
    clkLastState = GPIO.input(clk)
    while True:
        clkState = GPIO.input(clk)
        dtState = GPIO.input(dt)
        controlVolume(clkState, dtState, clkLastState, mixer)
        clkLastState = clkState


def endProgram():
    GPIO.cleanup()


def volume_main():
    clk = 17 # 23 # 17
    dt =  18 # 24 # 18 
    mixer = alsaaudio.Mixer(alsaaudio.mixers()[0])
    setup(clk, dt)
    try:
        loop(clk, dt, mixer)
    except KeyboardInterrupt:
        print("keyboard interrupt detected")
        endProgram()


if __name__ == '__main__':
    main()
