"""
Framebuffer graphics driver for 128x32 ST7565 I2C LCDs (CircuitPython).
Provides pixel-level drawing, lines, rectangles, blitting and text rendering
using the existing `lcd128_32_fonts` glyphs.

Usage:
  from lcd128_32_graphics import Lcd128_32_Graphics as lcdscreen
  lcd = lcdscreen(sda_pin, scl_pin)
  lcd.text('Hello', 0, 0)
  lcd.show()

This driver maintains a 128x32 framebuffer (4 pages of 128 bytes) and
flushes it to the display with `show()`.
"""

import time
import lcd128_32_fonts
import busio
from adafruit_bus_device.i2c_device import I2CDevice


class Lcd128_32_Graphics:
    WIDTH = 128
    HEIGHT = 32
    PAGES = 4

    def __init__(self, sda_pin, scl_pin, addr=0x3F, doScan=False):
        if sda_pin is None or scl_pin is None:
            raise ValueError('Could not resolve sda/scl pins to board pins')
        comm_port = busio.I2C(scl=scl_pin, sda=sda_pin, frequency=400000)
        self._i2c_bus = comm_port
        self.i2c = I2CDevice(comm_port, addr, probe=True)
        self.addr = addr
        if doScan:
            try:
                while not comm_port.try_lock():
                    pass
                try:
                    scanned = comm_port.scan()
                    print('I2C scan at init:', [hex(a) for a in scanned])
                finally:
                    comm_port.unlock()
            except Exception as e:
                print('I2C scan failed during init:', e)

        # framebuffer: pages*width bytes
        self.buffer = bytearray(self.PAGES * self.WIDTH)
        self.Init()

    def reg_write(self, reg, data):
        buf = bytearray([reg, data])
        try:
            with self.i2c:
                self.i2c.write(buf)
        except OSError as e:
            print('I2C write failed:', e)
            raise

    def WriteByte_command(self, cmd):
        self.reg_write(0x00, cmd)

    def WriteByte_dat(self, dat):
        self.reg_write(0x40, dat)

    def Init(self):
        time.sleep(0.01)
        # same init sequence as the original driver
        self.WriteByte_command(0xe2)
        time.sleep(0.01)
        self.WriteByte_command(0xa3)
        self.WriteByte_command(0xa0)
        self.WriteByte_command(0xc8)
        self.WriteByte_command(0x22)
        self.WriteByte_command(0x81)
        self.WriteByte_command(0x30)
        self.WriteByte_command(0x2c)
        self.WriteByte_command(0x2e)
        self.WriteByte_command(0x2f)
        self.clear()
        self.WriteByte_command(0xff)
        self.WriteByte_command(0x72)
        self.WriteByte_command(0xfe)
        self.WriteByte_command(0xd6)
        self.WriteByte_command(0x90)
        self.WriteByte_command(0x9d)
        self.WriteByte_command(0xaf)
        self.WriteByte_command(0x40)

    def clear(self):
        for i in range(len(self.buffer)):
            self.buffer[i] = 0x00

    def show(self):
        # write framebuffer by pages
        for page in range(self.PAGES):
            self.WriteByte_command(0xB0 + page)
            # set column to 0
            self.WriteByte_command(0x10)
            self.WriteByte_command(0x00)
            start = page * self.WIDTH
            end = start + self.WIDTH
            for b in self.buffer[start:end]:
                self.WriteByte_dat(b)

    def set_pixel(self, x, y, color=1):
        if x < 0 or x >= self.WIDTH or y < 0 or y >= self.HEIGHT:
            return
        page = y >> 3
        bit = y & 0x07
        idx = page * self.WIDTH + x
        if color:
            self.buffer[idx] |= (1 << bit)
        else:
            self.buffer[idx] &= ~(1 << bit)

    def get_pixel(self, x, y):
        if x < 0 or x >= self.WIDTH or y < 0 or y >= self.HEIGHT:
            return 0
        page = y >> 3
        bit = y & 0x07
        idx = page * self.WIDTH + x
        return (self.buffer[idx] >> bit) & 1

    def hline(self, x, y, length, color=1):
        for i in range(length):
            self.set_pixel(x + i, y, color)

    def vline(self, x, y, length, color=1):
        for i in range(length):
            self.set_pixel(x, y + i, color)

    def line(self, x0, y0, x1, y1, color=1):
        """Draw a generic line using Bresenham's algorithm."""
        dx = abs(x1 - x0)
        sx = 1 if x0 < x1 else -1
        dy = -abs(y1 - y0)
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set_pixel(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def rect(self, x, y, w, h, color=1, fill=False):
        if fill:
            for yy in range(h):
                self.hline(x, y + yy, w, color)
        else:
            self.hline(x, y, w, color)
            self.hline(x, y + h - 1, w, color)
            self.vline(x, y, h, color)
            self.vline(x + w - 1, y, h, color)

    def blit(self, bitmap, width, height, x, y):
        # bitmap: bytes or bytearray, packed rows, stride = (width+7)//8
        stride = (width + 7) // 8
        for row in range(height):
            for col in range(width):
                byte = bitmap[row * stride + (col >> 3)]
                bit = (byte >> (7 - (col & 7))) & 1
                self.set_pixel(x + col, y + row, bit)

    def _char_index_map(self):
        # replicate mapping used in original driver
        tail = [
            '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '/',
            ':', ';', '<', '=', '>', '?', '@', '{', '|', '}', '~', ' ', '.', '^', '_', '`', '[', '\\', ']'
        ]
        chars = '0123456789' + 'abcdefghijklmnopqrstuvwxyz' + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' + ''.join(tail)
        cmap = {c: i for i, c in enumerate(chars)}
        return cmap

    def draw_char(self, x, y, ch):
        cmap = self._char_index_map()
        idx = cmap.get(ch, None)
        if idx is None:
            idx = cmap.get(' ', 87)
        glyph = lcd128_32_fonts.textFont[idx]
        shift = y & 7
        page = y >> 3
        for col in range(7):
            gx = glyph[col]
            # low part goes to current page
            low = (gx << shift) & 0xFF
            if 0 <= page < self.PAGES:
                # OR into buffer to preserve background pixels
                self.buffer[page * self.WIDTH + x + col] |= low
            # high part spilled to next page
            if shift != 0 and (page + 1) < self.PAGES:
                high = (gx >> (8 - shift)) & 0xFF
                self.buffer[(page + 1) * self.WIDTH + x + col] |= high

    def text(self, string, x, y, spacing=1):
        for ch in string:
            if x + 7 > self.WIDTH:
                break
            self.draw_char(x, y, ch)
            x += 7 + spacing
