"""
Circuit Python (ESP32-S3) driver for 128x32 I2C LCD displays based on the ST7565 controller.
Designed for use with Keyestudio 128x32 I2C LCD module (KS-12832A), but should work with similar displays.
Requires the lcd128_32_fonts module for character bitmaps.
Only 94 limited characters in fonts can be displayed due to the original font design.
"""

import busio
import time
import lcd128_32_fonts
from adafruit_bus_device.i2c_device import I2CDevice

cursor = [0, 0]

class lcd128_32:

    def __init__(self, sda_pin, scl_pin, addr=0x3F, doScan=False):
        self.addr = addr
        if sda_pin is None or scl_pin is None:
            raise ValueError('Could not resolve sda/scl pins to board pins')
        comm_port = busio.I2C(scl=scl_pin, sda=sda_pin, frequency=400000)
        self._i2c_bus = comm_port
        self.i2c = I2CDevice(comm_port, addr, probe=True)

        if doScan:
            # Diagnostic: scan bus and print found addresses (helps debug OSError 5)
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

        self.Init()
        
    def WriteByte_command(self, cmd):
        self.reg_write(0x00, cmd)
    
    def WriteByte_dat(self, dat):
        self.reg_write(0x40, dat)

    def reg_write(self, reg, data):
        # Create buffers for the register and data
        register_buffer = bytearray([reg])
        data_buffer = bytearray([data])
        buf = register_buffer + data_buffer 
        # Use I2CDevice as a context manager to handle locking
        try:
            with self.i2c:
                self.i2c.write(buf) 
        except OSError as e:
            print(f"I2C write to {hex(self.addr)} at register {reg} failed: {e}")
            print('Hints: check SDA/SCL wiring, pull-ups, correct voltage (3.3V), and device address.')
            raise
    
    def Init(self):
        # self.i2c.start()
        time.sleep(0.01)
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
        self.Clear()
        self.WriteByte_command(0xff)
        self.WriteByte_command(0x72)
        self.WriteByte_command(0xfe)
        self.WriteByte_command(0xd6)
        self.WriteByte_command(0x90)
        self.WriteByte_command(0x9d)
        self.WriteByte_command(0xaf)
        self.WriteByte_command(0x40)
    
    def Clear(self):
        for i in range(4):
            self.WriteByte_command(0xb0 + i)
            self.WriteByte_command(0x10)
            self.WriteByte_command(0x00)
            for j in range(128):
                self.WriteByte_dat(0x00)
    
    def Cursor(self, y, x):
        if x > 17:
            x = 17
        if y > 3:
            y = 3
        cursor[0] = y
        cursor[1] = x
        
    def WriteFont(self, num):
        for item in lcd128_32_fonts.textFont[num]:
            self.WriteByte_dat(item)
    
    def Display(self, str):
        self.WriteByte_command(0xb0 + cursor[0])
        self.WriteByte_command(0x10 + cursor[1] * 7 // 16)
        self.WriteByte_command(0x00 + cursor[1] * 7 % 16)

        # character map in the same order as the original font indices
        # Construct mapping manually to match indices 62..94
        tail = [
            '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '/',
            ':', ';', '<', '=', '>', '?', '@', '{', '|', '}', '~', ' ', '.', '^', '_', '`', '[', '\\', ']'
        ]
        chars = '0123456789' + 'abcdefghijklmnopqrstuvwxyz' + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' + ''.join(tail)
        cmap = {c: i for i, c in enumerate(chars)}

        for ch in str:
            idx = cmap.get(ch)
            if idx is None:
                # unknown char -> space
                idx = cmap.get(' ', 87)
            self.WriteFont(idx)
