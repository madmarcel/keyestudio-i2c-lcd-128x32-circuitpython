"""
  Draw a cat bitmap on the LCD. The bitmap data is generated from the convert_to_bitmap.py tool, which converts an image file to a byte array that can be blitted to the LCD.
  The cat.png image is a 86x23 pixel black-and-white image. You can create your own bitmaps and convert them using the tool.
"""
import microcontroller
from lcd128_32_graphics import Lcd128_32_Graphics as lcdscreen
from cat_bitmap_data import BITMAP, WIDTH, HEIGHT

sda_pin = microcontroller.pin.GPIO17
scl_pin = microcontroller.pin.GPIO18

LCD_WIDTH = 128
LCD_HEIGHT = 32

lcd = lcdscreen(sda_pin, scl_pin)

lcd.clear()
lcd.blit(BITMAP, WIDTH, HEIGHT, (LCD_WIDTH - WIDTH) // 2, (LCD_HEIGHT - HEIGHT) // 2)
lcd.show()
