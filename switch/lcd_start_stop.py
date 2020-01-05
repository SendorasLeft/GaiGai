import RPI_I2C_driver
from time import sleep

# ni hao
LCD_NIHAO = [
        # [ 0x2, 0x4, 0xd, 0x14, 0x5, 0x4, 0x4, 0x4 ],
        [ 0x1, 0x2, 0x6, 0xa, 0x2, 0x2, 0x2, 0x2 ],
        # [ 0x8, 0xe, 0xa, 0x8, 0xa, 0x8, 0x18, 0x8 ]
        [ 0x4, 0xf, 0x11, 0x4, 0x15, 0x4, 0xc, 0x4 ],
        [ 0x4, 0x8, 0x11, 0x1f, 0x12, 0xc, 0xc, 0x12 ],
        [ 0xe, 0x2, 0x4, 0x1f, 0x4, 0x4, 0xc, 0x4 ],
]

def powerOn(screen):
    str = "Hello!"
    screen.lcd_clear()
    screen.backlight(1)
    print(str)
    screen.lcd_display_string(str, 1)
    screen.lcd_load_custom_chars(LCD_NIHAO)
    screen.lcd_display_string_pos(chr(0), 1, 6)
    screen.lcd_display_string_pos(chr(1), 1, 7)
    screen.lcd_display_string_pos(chr(2), 1, 8)
    screen.lcd_display_string_pos(chr(3), 1, 9)

def powerOff(screen):
    str = "Goodbye!"
    screen.lcd_clear()
    print(str)
    screen.lcd_display_string(str, 1)
    sleep(1)
    screen.lcd_clear()
    screen.backlight(0)


# val = 1 to say hi, val = 0 to say bye
def display(val):
    screen = RPI_I2C_driver.lcd()
    if val == 1:
        powerOn(screen)
    elif val == 0:
        powerOff(screen)
    else:
        print("error")
        
