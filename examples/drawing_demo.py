"""
Animated drawing demo for the 128x32 LCD.
Displays some animated bar graphs and text.
"""
import board
from lcd128_32_graphics import Lcd128_32_Graphics as lcdscreen
import microcontroller

# On some boards you can use board.SDA and board.SCL instead of pin numbers.
# My ESP32-S3 does not support that, so I manually specify the pin numbers below. Edit as needed.
# sda_pin = board.SDA
# scl_pin = board.SCL

# Note: The board module will not always list all the available pins,
# so you can use this line to find the correct pin objects.
# print(dir(microcontroller.pin))
sda_pin = microcontroller.pin.GPIO17
scl_pin = microcontroller.pin.GPIO18

def graphics_demo(sda_pin, scl_pin):
    lcd = lcdscreen(sda_pin, scl_pin)

    w = lcd.WIDTH
    h = lcd.HEIGHT    

    try:
        height = 3.0
        height_delta = 0.1
        temp = 0.0
        temp_delta = 0.1
        while True:
            lcd.clear()

            # border
            lcd.rect(0, 0, w, h)
            lcd.rect(2,2, w-4, h-4)

            # text
            lcd.text('Height', 5, 5)
            lcd.text('Temp', 5, 17)

            # horizontal bargraphs
            bar_width = int((height / 5.0) * (w - 60 - 10))
            lcd.rect(60, 5, bar_width, 8, fill=True)

            # this one has a line at the bottom
            lcd.line(60, 24, w - 10, 24)
            # and markers every 1.0 units
            for i in range(0, 6):
                x = 60 + int((i / 5.0) * (w - 60 - 10))
                lcd.line(x, 22, x, 26)
            bar_width = int((temp / 5.0) * (w - 60 - 10))
            lcd.rect(60, 17, bar_width, 8, fill=True)

            lcd.show()

            height += height_delta
            if height > 5.0:
                height_delta = -0.2
            elif height < 0.2:
                height_delta = 0.2

            temp += temp_delta
            if temp > 5.0:
                temp_delta = -0.1
            elif temp < 0.1:
                temp_delta = 0.1

            # time.sleep(0.01)
    except KeyboardInterrupt:
        lcd.clear()
        lcd.show()
        print('Demo stopped')

if __name__ == '__main__':
    graphics_demo(sda_pin, scl_pin)

