from RPi import GPIO
from time import sleep
import RPI_I2C_driver


def setup(clk, dt):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def getNewChannel(channel, incr):
    if incr == 1:
        if channel < 5:
            return channel + 1
        else:
            return 0
    else:
        if channel > 0:
            return channel - 1
        else:
            return 5


def formatString(str):
    newStr = str
    while len(newStr) < 16:
        newStr += " "
    return newStr

def controlChannel(clkState, dtState, clkLastState, channel, mylcd):
    if clkState != clkLastState:
        newChannel = channel
        if dtState != clkState:
            newChannel = getNewChannel(channel, 1)
        else:
            newChannel = getNewChannel(channel, 0)
        print(newChannel)
        mylcd.lcd_display_string(formatString("Channel " + str(newChannel)), 1)
        return newChannel
    return channel


def loop(clk, dt, mylcd):
    clkLastState = GPIO.input(clk)
    channel = 0
    while True:
        clkState = GPIO.input(clk)
        dtState = GPIO.input(dt)
        channel = controlChannel(clkState, dtState, clkLastState, channel, mylcd)
        sleep(0.1)
        clkLastState = clkState


def endProgram():
    GPIO.cleanup()


def main():
    clk = 17
    dt = 18
    mylcd = RPI_I2C_driver.lcd()
    setup(clk, dt)
    try:
        loop(clk, dt, mylcd)
    except KeyboardInterrupt:
        print("keyboard interrupt detected")
        endProgram()


if __name__ == '__main__':
    main()
