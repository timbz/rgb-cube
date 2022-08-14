from serial import Serial
from time import sleep
from cobs import cobs
from binascii import hexlify

class RgbCube:

    data = bytearray(8*8*3)

    baudrate = 115200

    red_idx = [[
        [108, 111, 114, 117],
        [132, 135, 138, 141],
        [156, 159, 162, 165],
        [180, 183, 186, 189],
    ], [
        [105, 102, 99, 96],
        [129, 126, 123, 120],
        [153, 150, 147, 144],
        [177, 174, 171, 168],
    ], [
        [84, 87, 90, 93],
        [60, 63, 66, 69],
        [36, 39, 42, 45],
        [12, 15, 18, 21],
    ], [
        [81, 78, 75, 72],
        [57, 54, 51, 48],
        [33, 30, 27, 24],
        [9, 6, 3, 0],
    ]]

    green_idx = [[
        [106, 103, 100, 97],
        [130, 127, 124, 121],
        [154, 151, 148, 145],
        [178, 175, 172, 169],
    ], [
        [109, 112, 115, 118],
        [133, 136, 139, 142],
        [157, 160, 163, 166],
        [181, 184, 187, 190],
    ], [
        [82, 79, 76, 73],
        [58, 55, 52, 49],
        [34, 31, 28, 25],
        [10, 7, 4, 1],
    ], [
        [85, 88, 91, 94],
        [61, 64, 67, 70],
        [37, 40, 43, 46],
        [13, 16, 19, 22],
    ]]

    blue_idx = [[
        [110, 113, 116, 119],
        [134, 137, 140, 143],
        [158, 161, 164, 167],
        [182, 185, 188, 191],
    ], [
        [107, 104, 101, 98],
        [131, 128, 125, 122],
        [155, 152, 149, 146],
        [179, 176, 173, 170],
    ], [
        [86, 89, 92, 95],
        [62, 65, 68, 71],
        [38, 41, 44, 47],
        [14, 17, 20, 23],
    ], [
        [83, 80, 77, 74],
        [59, 56, 53, 50],
        [35, 32, 29, 26],
        [11, 8, 5, 2],
    ]]


    def __init__(self, serial_name):
        self.serial = Serial(serial_name, self.baudrate)
        sleep(0.3) # wait for the arduino to reboot
        sleep(self.update()) # turn off all leds
        self.red_idx_flat = []
        self.green_idx_flat = []
        self.blue_idx_flat = []
        for z in range(4):
            for y in range(4):
                for x in range(4):
                    self.red_idx_flat.append(self.red_idx[z][y][x])
                    self.green_idx_flat.append(self.green_idx[z][y][x])
                    self.blue_idx_flat.append(self.blue_idx[z][y][x])


    def __del__(self):
        self.serial.close()

    def debug_print(self):
        print(hexlify(self.data))

    def fill(self, r, g, b):
        for i in range(len(self.data)):
            if i % 3 == 0:
                self.data[i] = r
            elif i % 3 == 1:
                self.data[i] = g
            elif i % 3 == 2:
                self.data[i] = b


    def set(self, x, y, z, r, g, b):
        idx = z*16 + y*4 + x
        self.data[self.red_idx_flat[idx]] = r
        self.data[self.green_idx_flat[idx]] = g
        self.data[self.blue_idx_flat[idx]] = b
        #self.data[self.red_idx[z][y][x]] = r
        #self.data[self.green_idx[z][y][x]] = g
        #self.data[self.blue_idx[z][y][x]] = b


    def update(self):
        """Sends the cube data and returns the estimated transfer time"""
        encoded = cobs.encode(self.data)
        self.serial.write(encoded + b'\x00')
        return len(encoded) * 8.0 / self.baudrate + 0.001 # 1ms extra
