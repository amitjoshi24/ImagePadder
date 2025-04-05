# hi ur cute <3
from PIL import Image
import sys
from math import ceil
from pathlib import Path

def pad_image_aspect_ratio(file_path: Path, im: Image.Image, nw: int, nh: int):
    """Pad image to match a specific aspect ratio."""
    width, height = im.size

    padded_save_path = file_path.parent / (file_path.stem + f'-padded_{nw}x{nh}' + file_path.suffix)

    vertical_pad = nw/nh <= width/height

    new_width = width if vertical_pad else int(ceil(height * nw / nh))
    new_height = int(ceil(width * nh / nw)) if vertical_pad else height

    # Create a new white image with the new dimensions
    result = Image.new(im.mode, (new_width, new_height), (255, 255, 255, 255) if im.mode == 'RGBA' else (255, 255, 255))

    # Calculate padding offsets
    start_length = ((new_height - height) // 2) if vertical_pad else ((new_width - width) // 2)
    if vertical_pad:
        result.paste(im, (0, start_length))
    else:
        result.paste(im, (start_length, 0))

    print(f"Image saved to: {padded_save_path}")
    return result, padded_save_path

def pad_image_custom(file_path: Path, im: Image.Image, top: int, right: int, bottom: int, left: int):
    """Pad image with custom padding values for each side."""
    width, height = im.size
    
    # Calculate new dimensions
    new_width = width + left + right
    new_height = height + top + bottom
    
    # Create a new white image with the new dimensions
    result = Image.new(im.mode, (new_width, new_height), (255, 255, 255, 255) if im.mode == 'RGBA' else (255, 255, 255))
    
    # Paste the original image at the specified offset
    result.paste(im, (left, top))
    
    # Generate save path
    padded_save_path = file_path.parent / (file_path.stem + f'-padded_custom' + file_path.suffix)
    
    print(f"Image saved to: {padded_save_path}")
    return result, padded_save_path

if __name__ == "__main__":
    # Handle command line arguments or prompt for input
    if len(sys.argv) > 1:
        raw_file_path = sys.argv[1]
    else:
        raw_file_path = input("image's filename to pad: ")

    file_path = Path(raw_file_path)
    try:
        im = Image.open(raw_file_path)
        print(f"Image loaded: {im.size[0]}x{im.size[1]} pixels")
    except:
        print('Image cannot be opened at this path: ' + raw_file_path)
        sys.exit(1)
    
    # Ask user which mode they want to use
    if len(sys.argv) > 2 and sys.argv[2] in ['aspect', 'custom']:
        mode = sys.argv[2]
    else:
        mode = input("Choose padding mode ('aspect' for aspect ratio or 'custom' for custom padding): ").strip().lower()
    
    result = None
    if mode == 'aspect':
        if len(sys.argv) > 3:
            aspect_ratio = sys.argv[3]
        else:
            aspect_ratio = input("Enter aspect ratio in the form of WIDTHxHEIGHT, e.g. \"16x9\": ")
        
        try:
            nw, nh = tuple(int(num) for num in aspect_ratio.split('x'))
            result, save_path = pad_image_aspect_ratio(file_path, im, nw, nh)
        except:
            print('Invalid aspect ratio. Must be in the format WIDTHxHEIGHT, e.g. \"16x9\".')
            sys.exit(1)
    elif mode == 'custom':
        if len(sys.argv) > 6:
            top, right, bottom, left = int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
        else:
            top = int(input("Enter top padding (pixels): "))
            right = int(input("Enter right padding (pixels): "))
            bottom = int(input("Enter bottom padding (pixels): "))
            left = int(input("Enter left padding (pixels): "))
        
        result, save_path = pad_image_custom(file_path, im, top, right, bottom, left)
    else:
        print("Invalid mode. Please choose 'aspect' or 'custom'.")
        sys.exit(1)
    
    # Save the resulting image
    if result:
        result.save(save_path)
        print(f"Done! New image size: {result.size[0]}x{result.size[1]} pixels")