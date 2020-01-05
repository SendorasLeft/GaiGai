from gpiozero import Button
from lcd_start_stop import display

button = Button(26) # 19

def switchedOn():
    display(1)

def switchedOff():
    display(0)

button.when_pressed = switchedOn
button.when_released = switchedOff