**Circuit Python Drivers for the Keyestudio 128x32 i2c LCD module**

The module uses an ST7565 controller, with an I2C adapter.
It should work with similar displays.

<img src="screenshots/module.jpg" alt="Keyestudio module" width="300"/>

***Files***

- `lcd_128_32.py` - character only library. 
- `lcd_128_32_graphics.py` - characters and graphics library using a framebuffer.

Both libraries require the `lcd128_32_font.py` file.

***Installation***

Copy all three files to your CIRCUITPY drive.

(`lcd_128_32.py`, `lcd_128_32_graphics.py` and `lcd128_32_font.py`)

You can omit `lcd_128_32_graphics.py` if you don't want to draw graphics.

***Prerequisites***

You will need to install the `Adafruit_CircuitPython_Bundle` onto your device.

***Examples***

- `examples/characters.py` - basic text demo
- `examples/graphics.py` - basic graphics demo
- `examples/drawing_demo.py` - animated graphics demo
- `examples/draw_cat_bitmap.py` - displays a cat bitmap image. Conversion tools are in `/tools`

***Screenshots***

<img src="screenshots/text.png" alt="Text demo" width="300"/>
<img src="screenshots/basic_graphics.png" alt="Basic graphics demo" width="300"/>
<img src="screenshots/graphics.png" alt="Animated graphics demo" width="300"/>
<img src="screenshots/cat_bitmap.png" alt="Display cat bitmap demo" width="300"/>


***Usage***

Below are quick-start examples and a short API summary for the two drivers in this repository.

**Character driver (`lcd128_32.py`)**

Basic usage (writes characters directly to the display):

```python
import board
from lcd128_32 import lcd128_32

# Use board.SDA / board.SCL where supported, or pass pin objects/numbers
lcd = lcd128_32(board.SDA, board.SCL)
lcd.Cursor(0, 0)        # page, column (0..3, 0..17)
lcd.Display('Hello')    # writes characters using the bundled font
```

API summary:
- `lcd = lcd128_32(sda_pin, scl_pin, addr=0x3F, doScan=False)` — constructor
- `lcd.Clear()` — clear the whole display
- `lcd.Cursor(y, x)` — set text cursor (page 0..3, column 0..17)
- `lcd.Display(str)` — write a text string at the current cursor

Notes: the character driver uses the bundled `lcd128_32_fonts` font. The font supports a limited set of glyphs matching the original module's ROM.

**Graphics framebuffer driver (`lcd128_32_graphics.py`)**

This driver provides a 128x32 framebuffer and drawing primitives. Changes are staged in RAM and flushed to the display with `show()`.

Example:

```python
import board
from lcd128_32_graphics import Lcd128_32_Graphics

lcd = Lcd128_32_Graphics(board.SDA, board.SCL)
lcd.clear()
lcd.text('Hello', 10, 4)        # text at x=10, y=4
lcd.rect(0, 0, 128, 32)         # border
lcd.line(10, 10, 100, 20)       # draw a line
lcd.show()                      # flush framebuffer to display
```

Key methods:
- `lcd.clear()` — clear framebuffer
- `lcd.show()` — push framebuffer to the display
- `lcd.set_pixel(x, y, color=1)` / `lcd.get_pixel(x,y)` — single-pixel access
- `lcd.hline(x, y, length, color=1)` / `lcd.vline(x, y, length, color=1)` — horizontal/vertical lines
- `lcd.line(x0,y0,x1,y1,color=1)` — generic Bresenham line
- `lcd.rect(x,y,w,h, color=1, fill=False)` — rectangle, optional filled
- `lcd.blit(bitmap, width, height, x, y)` — blit a packed bitmap into the framebuffer
- `lcd.text(string, x, y, spacing=1)` — draw text using built-in font

Bitmap format for `blit()`:
- The bitmap is a packed-bytes row-major format with stride = `(width + 7) // 8`.
- By default `blit()` expects MSB-first packing where the most-significant bit (bit7) of each byte corresponds to the leftmost pixel of that 8-pixel group.

If you need to convert images for `blit()`, see the `tools/convert_to_bitmap.py` helper below.

**Image converter (`tools/convert_to_bitmap.py`)**

Convert a PNG into a Python bytes array.

Example:

```bash
pip3 install pillow
python3 tools/convert_to_bitmap.py cat.png examples/cat_bitmap.py --width 86 --height 23 --var CAT_BITMAP
```

Options:
- `--width` / `--height` — output dimensions (default 128x32)
- `--var` — variable/base name used in the generated file
- `--invert` — invert black/white mapping
- `--fit` — how to fit source into target (`scale`, `crop`, `pad`, `original`)
