from RPi import GPIO
from time import sleep


def setup(button):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


def loop(button):
    lastState = False
    while True:
        buttonState = GPIO.input(button)
        if buttonState != lastState:
            if buttonState is True:
                print("Button Pressed...")
            else:
                print("Button not pressed...")
        lastState = buttonState
        sleep(0.5)


def endProgram():
    GPIO.cleanup()


def main():
    button = 26
    setup(button)
    try:
        loop(button)
    except KeyboardInterrupt:
        print("keyboard interrupt detected")
        endProgram()


if __name__ == '__main__':
    main()
