from RPi import GPIO
from time import sleep
import alsaaudio


def setup(clk, dt):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


def increaseVolume(mixer):
    vol = mixer.getvolume()[0]
    if vol >= 95: # can't exceed 95 because it will be overly-loud
        return
    if vol + 5 > 95:
        mixer.setvolume(95)
        print("volume set to 95")
        return
    mixer.setvolume(vol + 5)
    print("volume set to", vol + 5)


def decreaseVolume(mixer):
    vol = mixer.getvolume()[0]
    if vol <= 0:
        return
    if vol - 5 < 0:
        mixer.setvolume(0)
        print("volume set to 0")
        return
    mixer.setvolume(vol - 5)
    print("volume set to", vol - 5)


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


def main():
    clk = 17
    dt = 18
    print(alsaaudio.mixers()[0])
    mixer = alsaaudio.Mixer(alsaaudio.mixers()[0])
    setup(clk, dt)
    try:
        loop(clk, dt, mixer)
    except KeyboardInterrupt:
        print("keyboard interrupt detected")
        endProgram()


if __name__ == '__main__':
    main()
