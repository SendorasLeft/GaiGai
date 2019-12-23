import Button
from time import sleep

def loop(button):
    while True:
        isPressed = button.isPressed()
        if isPressed == 1:
            print("Button Pressed")
        elif isPressed == 0:
            print("Button not pressed")
        sleep(0.2)

def main():
    pinNum = 19
    button = Button.Button(pinNum)
    try:
        loop(button)
    except KeyboardInterrupt:
        print("keyboard interrupt detected, program closing...")
        button.close()

if __name__ == '__main__':
    main()

