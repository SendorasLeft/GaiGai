# check if a button is pressed
from gpiozero import Button

button = Button(2)

while True:
    if button.is_pressed:
        print("Button is pressed")
    else:
        print("Button is not pressed")

"""
# Wait for a button to be pressed before continuing:
from gpiozero import Button

button = Button(2)

button.wait_for_press()
print("Button was pressed")

# Run a function every time the button is pressed:
from gpiozero import Button
from signal import pause

def say_hello():
    print("Hello!")

button = Button(2)

button.when_pressed = say_hello

pause()
"""