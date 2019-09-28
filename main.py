#!/usr/bin/python3

import math
import struct
from collections import namedtuple
from PIL import Image as Img
import numpy as np


class Image:
    def __init__(self, bmp_header, dib_header, pixel_array):
        self.bmp_header = bmp_header
        self.dib_header = dib_header
        self.pixel_array = pixel_array

    def __str__(self):
        return 'BMP header: {}\nDIB header: {}'.format(self.bmp_header, self.dib_header)


DibHeaderTypes = {
    12: 'BITMAPCOREHEADER',
    64: 'OS22XBITMAPHEADER',
    16: 'OS22XBITMAPHEADER',
    40: 'BITMAPINFOHEADER',
    52: 'BITMAPV2INFOHEADER',
    56: 'BITMAPV3INFOHEADER',
    108: 'BITMAPV4HEADER',
    124: 'BITMAPV5HEADER'
}

DibHeader = namedtuple('DibHeader', [
    'size', 'width', 'height', 'colorplanes', 'bits_per_pixel', 'compression',
    'image_size', 'x_res', 'y_res'])


def parse_bmp_header(data):
    if data[:0x02] != b'BM':
        raise Exception('Format not supported')
    size = struct.unpack('I', data[0x02:0x06])[0]
    offset = struct.unpack('I', data[0x0a:0x0e])[0]

    return (size, offset)


def load_from_file(filename):
    with open(filename, 'rb') as f:
        data = f.read()

    # load header
    bmp_header = parse_bmp_header(data[:0x0e])

    dib_header_size = struct.unpack('<I', data[0x0e:0x12])[0]
    if dib_header_size != 108:
        # we use BITMAPV4HEADER
        raise Exception('Header not implemented')

    # unpack reference:
    # lowercase: signed, uppercase: unsigned
    # LONG - l
    # WORD - H
    # DWORD - L

    dib_header = DibHeader._make(struct.unpack(
        '<LllHHLLll', data[0x0e:0x0e+32]))

    if dib_header.compression != 0:
        raise Exception('compression not supported')

    # load data
    # pixel array is: rows from bottom to top, from left to right
    pixel_array = parse_pixelarray(dib_header, data[bmp_header[1]:])

    return Image(bmp_header, dib_header, pixel_array)


def parse_pixelarray(header, data):
    row_size = math.floor((header.bits_per_pixel * header.width) / 32) * 4
    rows = []
    for y in range(len(data) // row_size):
        row = []
        for i in range(y * row_size + 2, (y + 1) * row_size, 3):
            pixel = np.array([data[i], data[i-1], data[i-2]])
            row.append(pixel)
        rows.insert(0, row)
    return np.array(rows, dtype=np.uint8)


if __name__ == '__main__':
    image = load_from_file('marek.bmp')
    print(image)
