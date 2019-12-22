from RPi import GPIO
from time import sleep
from alsaaudio import Mixer
from alsaaudio import mixers


def setup(clk, dt):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


def increaseVolume(mixer):
    print("range is ", mixer.getrange())
    vol = mixer.getvolume()
    mixer.setvolume(vol + 5)
    print("volume set to ", vol + 5)


def decreaseVolume(mixer):
    print("range is ", mixer.getrange())
    vol = mixer.getvolume()
    mixer.setvolume(vol - 5)
    print("volume set to ", vol - 5)


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
    mixer = Mixer(mixers[0])
    setup(clk, dt)
    try:
        controlVolume(clk, dt, mixer)
    except KeyboardInterrupt:
        print("keyboard interrupt detected")
        endProgram()


if __name__ == '__main__':
    main()
