from time import sleep

def loop(button):
    while True:
        if button.isPressed():
            print("Button Pressed")
        else:
            print("Button not pressed")

def main():
    pinNum = 19
    button = Button(pinNum)
    try:
        loop(button)
    except KeyboardInterrupt:
        print("keyboard interrupt detected, program closing...")
        button.close()

if __name__ == '__main__':
    main()
