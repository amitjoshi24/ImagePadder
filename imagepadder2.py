# hi ur cute <3
from PIL import Image, ImageFile
import sys
from math import ceil
from pathlib import Path
import re

# Enable loading truncated images (sometimes necessary for HEIF/HEIC)
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Try to add HEIC/HEIF support
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
    HEIF_SUPPORT = True
    #print("HEIC/HEIF support enabled")
except ImportError:
    HEIF_SUPPORT = False
    #print("HEIC/HEIF support not available. Install with 'pip install pillow-heif'")

def check_heif_support(file_path):
    """Check if we're trying to open a HEIC/HEIF file without support."""
    suffix = file_path.suffix.lower()
    if suffix in ['.heic', '.heif'] and not HEIF_SUPPORT:
        print("ERROR: You're trying to open a HEIC/HEIF file but the pillow-heif library isn't installed.")
        print("Please install it with: pip install pillow-heif")
        return False
    return True

def hex_to_rgb(hex_color):
    """Convert hex color (#RRGGBB or #RGB) to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def get_background_color(hex_color, opacity=255):
    """Convert hex color and opacity to RGBA tuple."""
    rgb = hex_to_rgb(hex_color)
    alpha = opacity  # Now directly using 0-255 scale
    return rgb + (alpha,) if len(rgb) == 3 else rgb

def pad_image_aspect_ratio(file_path: Path, im: Image.Image, nw: int, nh: int, bg_color=(255,255,255), opacity=100):
    """Pad image to match a specific aspect ratio."""
    width, height = im.size

    padded_save_path = file_path.parent / (file_path.stem + f'-padded_{nw}x{nh}' + file_path.suffix)

    vertical_pad = nw/nh <= width/height

    new_width = width if vertical_pad else int(ceil(height * nw / nh))
    new_height = int(ceil(width * nh / nw)) if vertical_pad else height

    # Create new image with specified background color
    result = Image.new('RGBA', (new_width, new_height), bg_color)

    # Calculate padding offsets
    start_length = ((new_height - height) // 2) if vertical_pad else ((new_width - width) // 2)
    if vertical_pad:
        result.paste(im, (0, start_length))
    else:
        result.paste(im, (start_length, 0))

    print(f"Image saved to: {padded_save_path}")
    return result, padded_save_path

def pad_image_custom(file_path: Path, im: Image.Image, top: int, right: int, bottom: int, left: int, bg_color=(255,255,255), opacity=100):
    """Pad image with custom padding values for each side."""
    width, height = im.size
    
    # Calculate new dimensions
    new_width = width + left + right
    new_height = height + top + bottom
    
    # Create new image with specified background color
    result = Image.new('RGBA', (new_width, new_height), bg_color)
    
    # Paste the original image at the specified offset
    result.paste(im, (left, top))
    
    # Generate save path
    padded_save_path = file_path.parent / (file_path.stem + f'-padded_custom' + file_path.suffix)
    
    print(f"Image saved to: {padded_save_path}")
    return result, padded_save_path

def parse_color_input(color_input):
    """Parse color input from user and return RGBA tuple."""
    if color_input.startswith('#'):
        return hex_to_rgb(color_input)
    return (255, 255, 255)  # Default to white if invalid

if __name__ == "__main__":
    # Get file path
    raw_file_path = sys.argv[1] if len(sys.argv) > 1 else input("Image's filename to pad: ")
    file_path = Path(raw_file_path)

    # Check if we're trying to use a HEIC file without support
    has_heif_support = check_heif_support(file_path)

    try:
        # Try to open the image
        if not has_heif_support and file_path.suffix.lower() in ['.heic', '.heif']:
            raise ImportError("Cannot open HEIC/HEIF without pillow-heif")
        im = Image.open(raw_file_path)
        
        # Print image info
        print(f"Image loaded: {im.size[0]}x{im.size[1]} pixels")
    except:
        print('Image cannot be opened at this path: ' + raw_file_path)
        sys.exit(1)
    
    # Ask user which mode they want to use
    mode_options = ['aspect', 'custom']
    mode = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] in mode_options else input("Choose padding mode ('aspect' for aspect ratio or 'custom' for custom padding): ").strip().lower()
    
    # Get background color
    default_color = "#FFFFFF"
    color_input = sys.argv[-2] if len(sys.argv) > 3 and sys.argv[-2].startswith('#') else input(f"Background color (hex format, e.g. #FFFFFF for white) [default: {default_color}]: ").strip()
    if not color_input:
        color_input = default_color
    
    # Get opacity
    try:
        opacity = int(sys.argv[-1]) if len(sys.argv) > 4 and sys.argv[-1].isdigit() else int(input("Background opacity (0-255, default: 255): ").strip() or "255")
        opacity = max(0, min(255, opacity))  # Clamp between 0-255
    except ValueError:
        opacity = 255
    
    # Parse color and create RGBA
    bg_color = get_background_color(color_input, opacity)
    print(f"Using background color: {color_input} with {opacity}% opacity")
    
    result = None
    if mode == 'aspect':
        # Handle aspect ratio mode
        if len(sys.argv) > 3 and not sys.argv[3].startswith('#'):
            aspect_ratio = sys.argv[3]
        else:
            aspect_ratio = input("Enter aspect ratio you desire in the form of WIDTHxHEIGHT, e.g. \"16x9\": ")
        
        try:
            nw, nh = tuple(int(num) for num in aspect_ratio.split('x'))
            result, save_path = pad_image_aspect_ratio(file_path, im, nw, nh, bg_color, opacity)
        except Exception as e:
            print('Invalid aspect ratio. Must be in the format WIDTHxHEIGHT, e.g. \"16x9\".')
            print(f"Error: {e}")
            sys.exit(1)
    elif mode == 'custom':
        # Handle custom padding mode
        try:
            if len(sys.argv) > 6 and not sys.argv[3].startswith('#'):
                top = int(sys.argv[3])
                right = int(sys.argv[4])
                bottom = int(sys.argv[5])
                left = int(sys.argv[6])
            else:
                top = int(input("Enter top padding (pixels): "))
                right = int(input("Enter right padding (pixels): "))
                bottom = int(input("Enter bottom padding (pixels): "))
                left = int(input("Enter left padding (pixels): "))
            
            result, save_path = pad_image_custom(file_path, im, top, right, bottom, left, bg_color, opacity)
        except ValueError as e:
            print(f"Error with padding values: {e}")
            print("All padding values must be integers.")
            sys.exit(1)
    else:
        print("Invalid mode. Please choose 'aspect' or 'custom'.")
        sys.exit(1)
    
    # Save the resulting image
    if result:
        # Check if we're saving to a format that needs special handling
        output_format = save_path.suffix.lower()
        
        # Convert to RGB if the original image wasn't RGBA and opacity is full
        if im.mode != 'RGBA' and opacity == 255:
            result = result.convert('RGB')
            
        # Save with appropriate format
        if save_path.suffix.lower() in ['.jpg', '.jpeg']:
            # JPEG doesn't support transparency, convert to RGB
            result = result.convert('RGB')
            
        result.save(save_path, quality=95)
        
        # If the original is HEIC/HEIF but we're saving as another format, mention it
        if file_path.suffix.lower() in ['.heic', '.heif'] and save_path.suffix.lower() not in ['.heic', '.heif']:
            print(f"Note: Original HEIC/HEIF image converted to {save_path.suffix} format")
        print(f"Done! New image size: {result.size[0]}x{result.size[1]} pixels")
        print(f"Image saved with opacity level {opacity}/255 background")