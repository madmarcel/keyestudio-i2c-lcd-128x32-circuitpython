"""
  Very simple graphics demo for the 128x32 LCD, showing how to draw lines and rectangles
"""
import board
import microcontroller
from lcd128_32_graphics import Lcd128_32_Graphics as lcdscreen

# On some boards you can use board.SDA and board.SCL instead of pin numbers.
# My ESP32-S3 does not support that, so I manually specify the pin numbers below. Edit as needed.
# sda_pin = board.SDA
# scl_pin = board.SCL

# Note: The board module will not always list all the available pins,
# so you can use this line to find the correct pin objects.
# print(dir(microcontroller.pin))
sda_pin = microcontroller.pin.GPIO17
scl_pin = microcontroller.pin.GPIO18

lcd = lcdscreen(sda_pin, scl_pin)

lcd.clear()
lcd.rect(10, 5, 60, 20)
lcd.text('Hello', 20, 10)
lcd.line(0, 0, lcd.WIDTH - 1, lcd.HEIGHT - 1)
lcd.show()
