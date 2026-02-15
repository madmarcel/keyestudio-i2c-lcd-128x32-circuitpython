"""
 Basic character display demo for the 128x32 LCD.
 Shows all the characters in the built-in font set, which includes ASCII and some extended characters.
"""

import board
import microcontroller
import lcd128_32

# On some boards you can use board.SDA and board.SCL instead of pin numbers.
# My ESP32-S3 does not support that, so I manually specify the pin numbers below. Edit as needed.
# sda_pin = board.SDA
# scl_pin = board.SCL

# Note: The board module will not always list all the available pins,
# so you can use this line to find the correct pin objects.
# print(dir(microcontroller.pin))
sda_pin = microcontroller.pin.GPIO17
scl_pin = microcontroller.pin.GPIO18

lcd = lcd128_32.lcd128_32(sda_pin, scl_pin)

lcd.Clear()
lcd.Cursor(0, 4)
lcd.Display("KEYESTUDIO")
lcd.Cursor(1, 0)
lcd.Display("ABCDEFGHIJKLMNOPQR")
lcd.Cursor(2, 0)
lcd.Display("123456789+-*/<>=$@")
lcd.Cursor(3, 0)
lcd.Display("%^&(){}:;'|?,.~\\[]")
