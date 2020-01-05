from gpiozero import Button
from lcd_start_stop import display
from signal import pause

def switchedOn():
    print("on")
    display(1)

def switchedOff():
    print("off")
    display(0)

button = Button(26, pull_up=False) # 19

button.when_pressed = switchedOn
button.when_released = switchedOff

pause()
"""
button = Button(26, pull_up=False)
button.wait_for_press()
print("button pressed")
"""

