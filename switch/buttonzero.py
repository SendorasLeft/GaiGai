from gpiozero import Button

button = Button(26) # 19

def switchedOn:
    print("button pressed")

def switchedOff:
    print("button released")

button.when_pressed = switchedOn
button.when_released = switchedOff