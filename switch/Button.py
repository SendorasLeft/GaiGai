from RPi import GPIO
from time import sleep

class Button:
    def __init__(self, pinNum):
        self.pinNum = pinNum
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pinNum, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        self.state = GPIO.input(pinNum)
    
    def isPressed(self):
        newState = GPIO.input(pinNum)
        if newState != self.state:
            self.state = newState
            if newState = True:
                return True
            else:
                return False

    def close():
        GPIO.cleanup()
    
    