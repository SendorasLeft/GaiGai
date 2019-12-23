# Original code found at:
# https://github.com/modmypi/Rotary-Encoder/
# Install command for alsaaudio:
# sudo -H pip3 install pyalsaaudio


from RPi import GPIO
from time import sleep
import alsaaudio
import RPI_I2C_driver


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


def controlVolume(clkState, dtState, clkLastState, mixer, mylcd):
    if clkState != clkLastState:
        if dtState != clkState:
            increaseVolume(mixer)
        else:
            decreaseVolume(mixer)
        vol = mixer.getvolume()[0]
        mylcd.lcd_display_string("Vol: " + str(vol), 1)
        sleep(0.1)


def loop(clk, dt, mixer, mylcd):
    clkLastState = GPIO.input(clk)
    while True:
        clkState = GPIO.input(clk)
        dtState = GPIO.input(dt)
        controlVolume(clkState, dtState, clkLastState, mixer, mylcd)
        clkLastState = clkState


def endProgram():
    GPIO.cleanup()


def main():
    clk = 17
    dt = 18
    mixer = alsaaudio.Mixer(alsaaudio.mixers()[0])
    mylcd = RPI_I2C_driver.lcd()
    setup(clk, dt)
    try:
        loop(clk, dt, mixer, mylcd)
    except KeyboardInterrupt:
        print("keyboard interrupt detected")
        endProgram()


if __name__ == '__main__':
    main()
