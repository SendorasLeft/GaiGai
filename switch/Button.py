from RPi import GPIO
from time import sleep

class Button:
    def __init__(self, pinNum):
        self.pinNum = pinNum
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pinNum, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        self.state = GPIO.input(pinNum)
    
    def stateChanged(self):
        if GPIO.input(self.pinNum) != self.state:
            return True
        else:
            return False

    def isPressed(self):
        newState = GPIO.input(self.pinNum)
        if newState != self.state:
            self.state = newState
            if newState == True:
                return 1
            else:
                return 0
        return -1

    def close(self):
        GPIO.cleanup()
    
    
