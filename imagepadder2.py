# hi ur cute <3
from PIL import Image
import sys
from math import ceil
from pathlib import Path

def pad_image(file_path: Path, nw: int, nh: int):
    width, height = im.size

    padded_save_path = file_path.parent / (file_path.stem + '-padded_' + str(nw) + 'x' + str(nh) + file_path.suffix)

    vertical_pad = nw/nh <= width/height

    new_width = width if vertical_pad else int(ceil(height * nw / nh))
    new_height = int(ceil(width * nh / nw)) if vertical_pad else height

    result = Image.new(im.mode, (new_width, new_height), (255, 255, 255))

    start_length = ((new_height - height) // 2) if vertical_pad else ((new_width - width) // 2)
    if vertical_pad:
        result.paste(im, (0, start_length))
    else:
        result.paste(im, (start_length, 0))

    result.save(padded_save_path)

if __name__ == "__main__":
    if len(sys.argv) > 2:
        raw_file_path = sys.argv[1]
        aspect_ratio = sys.argv[2]
    else:
        raw_file_path = input("image's filename to pad: ")
        aspect_ratio = input("enter aspect ratio you desire in the form of WIDTHxHEIGHT, e.g. \"4x3\": ")

    file_path = Path(raw_file_path)
    try:
        im = Image.open(raw_file_path)
    except:
        print('Image cannot be opened at this path: ' + raw_file_path)
    
    try:
        nw, nh = tuple(int(num) for num in aspect_ratio.split('x'))
    except:
        print('Invalid aspect ratio. Must be in the format WIDTHxHEIGHT, e.g. \"4x3\".')

    pad_image(file_path, nw, nh)