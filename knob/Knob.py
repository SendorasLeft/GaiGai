from RPi import GPIO

class Knob:
    def __init__(self, clk, dt):
        self.clk = clk
        self.dt = dt
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        self.clkState = GPIO.input(clk)

    # returns 1 if is rotated clockwise, 0 if anticlockwise,
    # returns -1 if no state change
    def isRotatedCW(self):
        clkState = GPIO.input(self.clk)
        dtState = GPIO.input(self.dt)
        if clkState != self.clkState:
            self.clkState = clkState
            if dtState != clkState:
                return 1
            else:
                return 0
        return -1

    def close(self):
        GPIO.cleanup()
