#!/usr/bin/env python3
# tools/convert_to_bitmap.py
#
# Usage: 
#    python3 convert_to_bitmap.py cat.png ../examples/cat_bitmap_data.py --width 86 --height 23
#
# Input image should be black-and-white. White pixels will be treated as 'off' and black pixels as 'on' (you can invert this with --invert). 
# Don't use transparency or anti-aliasing, as the tool will threshold the image to pure black and white. 
# You can use an image editor to create simple monochrome bitmaps or convert existing images.
# The output is a Python file containing a byte array that can be blitted to the LCD using the blit() method. 
# The width and height should match the dimensions of the source image, or you can use the --fit option to control how the image is resized or cropped to fit the target dimensions.
#
# The images may look a little squashed horizontally on the LCD due to the non-square pixel aspect ratio, 
# so you may want to adjust the source image dimensions or use the --fit option to get the best results.
# I suggest doubling the width of the source image to compensate for the aspect ratio.
#
# This tool requires the Pillow library for image processing. You can install it with:
#    pip3 install Pillow
#
from pathlib import Path
from PIL import Image
import argparse

def pack_image(img, width, height, invert=False):
    # img: PIL image in mode '1' or 'L' (black=0)
    stride = (width + 7) // 8
    out = bytearray(stride * height)
    for y in range(height):
        for xb in range(stride):
            byte = 0
            for bit in range(8):
                x = xb * 8 + bit
                if x >= width:
                    b = 0
                else:
                    p = img.getpixel((x, y))
                    # coerce to int and handle different PIL modes robustly
                    try:
                        pv = int(p)
                    except Exception:
                        # in some modes getpixel may return a tuple
                        pv = int(p[0]) if isinstance(p, (list, tuple)) and len(p) > 0 else 255
                    # consider black/dark pixels as 'on'
                    on = (pv == 0) or (pv == 1) or (pv < 128)
                    if invert:
                        on = not on
                    b = 1 if on else 0                
                    byte |= (b << (7 - bit))  # MSB-first packing
                
            out[y * stride + xb] = byte
    return out

def main():
    p = argparse.ArgumentParser()
    p.add_argument('input', help='input image (PNG)')
    p.add_argument('output', help='output .py file to write')
    p.add_argument('--width', type=int, default=128)
    p.add_argument('--height', type=int, default=32)
    p.add_argument('--var', default='BITMAP')
    p.add_argument('--invert', action='store_true')
    p.add_argument('--fit', choices=['scale','crop','pad','original'], default='original')
    args = p.parse_args()

    src = Image.open(args.input).convert('L')

    if args.fit == 'scale':
        img = src.resize((args.width, args.height), Image.LANCZOS)
    elif args.fit == 'crop':
        img = src.crop((0,0,args.width,args.height)).resize((args.width,args.height), Image.LANCZOS)
    elif args.fit == 'pad':
        img = Image.new('L', (args.width, args.height), 255)
        src.thumbnail((args.width, args.height), Image.LANCZOS)
        ox = (args.width - src.width) // 2
        oy = (args.height - src.height) // 2
        img.paste(src, (ox, oy))
    else:
        # original: if source size doesn't match requested size, pad or crop
        if src.size != (args.width, args.height):
            # pad with white background
            img = Image.new('L', (args.width, args.height), 255)
            ox = max((args.width - src.width) // 2, 0)
            oy = max((args.height - src.height) // 2, 0)
            img.paste(src, (ox, oy))
        else:
            img = src

    # produce strict black/white (no dithering)
    bw = img.point(lambda p: 0 if p < 128 else 255).convert('1')

    packed = pack_image(bw.convert('L'), args.width, args.height, invert=args.invert)

    out_path = Path(args.output)
    with out_path.open('w', encoding='utf8') as f:
          f.write('# Auto-generated from {}\n'.format(args.input))
          f.write('WIDTH = {}\n'.format(args.width))
          f.write('HEIGHT = {}\n\n'.format(args.height))
          f.write('{} = bytes([\n'.format(args.var))
          # write bytes with spaces and line breaks for readability
          bytes_per_line = 12
          for i, b in enumerate(packed):
              f.write('0x{:02x}, '.format(b))
              if (i + 1) % bytes_per_line == 0:
                  f.write('\n')
          f.write('\n])\n')
    print('Wrote', out_path)

if __name__ == '__main__':
    main()
