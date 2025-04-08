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

# Add these imports near the top of the file
try:
    import moviepy.editor as mp
    from moviepy.video.fx.all import resize
    VIDEO_SUPPORT = True
    #print("Video support enabled")
except ImportError:
    VIDEO_SUPPORT = False
    #print("Video support not available. Install with 'pip install moviepy'")

def check_heif_support(file_path):
    """Check if we're trying to open a HEIC/HEIF file without support."""
    suffix = file_path.suffix.lower()
    if suffix in ['.heic', '.heif'] and not HEIF_SUPPORT:
        print("ERROR: You're trying to open a HEIC/HEIF file but the pillow-heif library isn't installed.")
        print("Please install it with: pip install pillow-heif")
        return False
    return True

def check_video_support(file_path):
    """Check if we're trying to open a video file without support."""
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.wmv']
    suffix = file_path.suffix.lower()
    if suffix in video_extensions and not VIDEO_SUPPORT:
        print("ERROR: You're trying to open a video file but the moviepy library isn't installed.")
        print("Please install it with: pip install moviepy")
        return False
    return True

def hex_to_rgb(hex_color):
    """Convert hex color (#RRGGBB or #RGB) to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def get_background_color(hex_color, opacity=255):
    """Convert hex color and opacity to RGBA tuple (values 0-255)."""
    rgb = hex_to_rgb(hex_color)
    # Ensure we're working with 0-255 scale
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

def pad_video_aspect_ratio(file_path: Path, nw: int, nh: int, bg_color=(255,255,255), opacity=255):
    """Pad video to match a specific aspect ratio."""
    if not VIDEO_SUPPORT:
        print("Video support not available. Install with 'pip install moviepy'")
        return None
    
    # Load the video
    video = mp.VideoFileClip(str(file_path))
    width, height = video.size
    
    # Generate the output path
    padded_save_path = file_path.parent / (file_path.stem + f'-padded_{nw}x{nh}' + file_path.suffix)
    
    # Make sure we have just RGB (no alpha) for video processing
    if len(bg_color) == 4:  # RGBA format
        bg_color = bg_color[:3]  # Take just RGB values
    
    # Verify color values are in correct range (0-255)
    print(f"Using background color for video: RGB {bg_color} (should be values 0-255)")
    
    # Calculate the target aspect ratio
    target_ratio = nw / nh
    original_ratio = width / height
    
    # Determine if we need vertical or horizontal padding
    vertical_pad = target_ratio <= original_ratio
    
    if vertical_pad:
        # Need vertical padding (top/bottom)
        new_height = int(width / target_ratio)
        padding = new_height - height
        top_pad = padding // 2
        
        # Create a function to pad each frame
        def pad_frame(get_frame, t):
            import numpy as np
            frame = get_frame(t)
            # Note: frame is 0-1 float values, bg_color is 0-255 integers
            h, w = frame.shape[:2]
            color = np.array(bg_color, dtype=np.float32)  # moviepy uses 0-1 scale for colors
            padded = np.zeros((new_height, w, 3))
            
            #print(f"Using color values (0-1 scale): {color}")
            # Fill with background color
            for i in range(3):  # RGB channels
                padded[:, :, i] = color[i]
            
            # Insert original frame in the middle
            padded[top_pad:top_pad+h, :] = frame
            return padded
        
        # Apply padding to the video
        padded_video = video.fl(pad_frame)
    else:
        # Need horizontal padding (left/right)
        new_width = int(height * target_ratio)
        padding = new_width - width
        left_pad = padding // 2
        
        # Create a function to pad each frame
        def pad_frame(get_frame, t):
            import numpy as np
            frame = get_frame(t)
            # Note: frame is 0-1 float values, bg_color is 0-255 integers
            h, w = frame.shape[:2]
            color = np.array(bg_color, dtype=np.float32)  # moviepy uses 0-1 scale for colors
            padded = np.zeros((h, new_width, 3))
            
            #print(f"Using color values (0-1 scale): {color}")
            # Fill with background color
            for i in range(3):  # RGB channels
                padded[:, :, i] = color[i]
            
            # Insert original frame in the middle
            padded[:, left_pad:left_pad+w] = frame
            return padded
        
        # Apply padding to the video
        padded_video = video.fl(pad_frame)
    
    # Save the padded video
    print(f"Processing video. This may take some time depending on the video length...")
    
    padded_video.write_videofile(str(padded_save_path), 
                                 codec='libx264', 
                                 audio_codec='aac',
                                 preset='fast',  # Use faster preset for better speed
                                 threads=4)
    
    # Close the video objects to free resources
    video.close()
    padded_video.close()
    
    return padded_save_path

def pad_video_custom(file_path: Path, top: int, right: int, bottom: int, left: int, bg_color=(255,255,255), opacity=255):
    """Pad video with custom padding values for each side."""
    if not VIDEO_SUPPORT:
        print("Video support not available. Install with 'pip install moviepy'")
        return None
    
    # Load the video
    video = mp.VideoFileClip(str(file_path))
    width, height = video.size
    
    # Generate the output path
    padded_save_path = file_path.parent / (file_path.stem + f'-padded_custom' + file_path.suffix)
    
    # Make sure we have just RGB (no alpha) for video processing
    if len(bg_color) == 4:  # RGBA format
        bg_color = bg_color[:3]  # Take just RGB values
    
    # Verify color values are in correct range (0-255)
    print(f"Using background color for video: RGB {bg_color} (should be values 0-255)")
    # Calculate new dimensions
    new_width = width + left + right
    new_height = height + top + bottom
    
    # Create a function to pad each frame
    def pad_frame(get_frame, t):
        import numpy as np
        frame = get_frame(t)
        h, w = frame.shape[:2]
        color = np.array(bg_color, dtype=np.float32)  # moviepy uses 0-1 scale for colors
        padded = np.zeros((new_height, new_width, 3))
        
        #print(f"Using color values (0-1 scale): {color}")
        # Fill with background color
        for i in range(3):  # RGB channels
            padded[:, :, i] = color[i]
        
        # Insert original frame at the specified offset
        padded[top:top+h, left:left+w] = frame
        return padded
    
    # Apply padding to the video
    padded_video = video.fl(pad_frame)
    
    # Save the padded video
    print(f"Processing video. This may take some time depending on the video length...")
    padded_video.write_videofile(str(padded_save_path), 
                                 codec='libx264', 
                                 audio_codec='aac',
                                 preset='fast',  # Use faster preset for better speed
                                 threads=4)
    
    # Close the video objects to free resources
    video.close()
    padded_video.close()
    
    return padded_save_path

def get_padding_mode(sys_args):
    """Get the padding mode (aspect or custom) from arguments or user input."""
    mode_options = ['aspect', 'custom']
    mode = sys_args[2] if len(sys_args) > 2 and sys_args[2] in mode_options else input(
        "Choose padding mode ('aspect' for aspect ratio or 'custom' for custom padding): "
    ).strip().lower()
    
    if mode not in mode_options:
        print("Invalid mode. Please choose 'aspect' or 'custom'.")
        sys.exit(1)
        
    return mode

def get_background_settings(sys_args):
    """Get background color and opacity from arguments or user input."""
    # Get background color
    default_color = "#FFFFFF"
    color_input = sys_args[-2] if len(sys_args) > 3 and sys_args[-2].startswith('#') else input(
        f"Background color (hex format, e.g. #FFFFFF for white) [default: {default_color}]: "
    ).strip()
    
    if not color_input:
        color_input = default_color
    
    # Get opacity
    try:
        opacity = int(sys_args[-1]) if len(sys_args) > 4 and sys_args[-1].isdigit() else int(
            input("Background opacity (0-255, default: 255): ").strip() or "255"
        )
        opacity = max(0, min(255, opacity))  # Clamp between 0-255
    except ValueError:
        opacity = 255
    
    # Parse color and create RGBA
    bg_color = get_background_color(color_input, opacity)
    print(f"Using background color: {color_input} with opacity level {opacity}/255")
    
    return bg_color, opacity, color_input

def get_aspect_ratio(sys_args):
    """Get aspect ratio from arguments or user input."""
    if len(sys_args) > 3 and not sys_args[3].startswith('#'):
        aspect_ratio = sys_args[3]
    else:
        aspect_ratio = input("Enter aspect ratio you desire in the form of WIDTHxHEIGHT, e.g. \"16x9\": ")
    
    try:
        nw, nh = tuple(int(num) for num in aspect_ratio.split('x'))
        return nw, nh
    except Exception as e:
        print('Invalid aspect ratio. Must be in the format WIDTHxHEIGHT, e.g. \"16x9\".')
        print(f"Error: {e}")
        sys.exit(1)

def get_custom_padding(sys_args):
    """Get custom padding values from arguments or user input."""
    try:
        if len(sys_args) > 6 and not sys_args[3].startswith('#'):
            return (int(sys_args[3]), int(sys_args[4]), int(sys_args[5]), int(sys_args[6]))
        else:
            return (
                int(input("Enter top padding (pixels): ")),
                int(input("Enter right padding (pixels): ")),
                int(input("Enter bottom padding (pixels): ")),
                int(input("Enter left padding (pixels): "))
            )
    except ValueError as e:
        print(f"Error with padding values: {e}")
        print("All padding values must be integers.")
        sys.exit(1)

if __name__ == "__main__":
    # Get file path
    raw_file_path = sys.argv[1] if len(sys.argv) > 1 else input("Image's filename to pad: ")
    file_path = Path(raw_file_path)

    # Check if we're trying to use a HEIC file without support
    has_heif_support = check_heif_support(file_path)

    # After getting the file path, check if it's a video
    is_video = file_path.suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.wmv']
    
    if is_video:
        # Check if we have video support
        has_video_support = check_video_support(file_path)
        if not has_video_support:
            sys.exit(1)
        
        # Get common parameters
        mode = get_padding_mode(sys.argv)
        bg_color, opacity, color_input = get_background_settings(sys.argv)
        
        if mode == 'aspect':
            nw, nh = get_aspect_ratio(sys.argv)
            save_path = pad_video_aspect_ratio(file_path, nw, nh, bg_color, opacity)
        elif mode == 'custom':
            top, right, bottom, left = get_custom_padding(sys.argv)
            save_path = pad_video_custom(file_path, top, right, bottom, left, bg_color, opacity)
        
        # Display success message
        print(f"Video processing complete with {opacity}/255 opacity background")
        print(f"Video saved to: {save_path}")
    else:
        # Existing code for processing images
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
        
        # Get common parameters
        mode = get_padding_mode(sys.argv)
        bg_color, opacity, color_input = get_background_settings(sys.argv)
        
        result = None
        if mode == 'aspect':
            nw, nh = get_aspect_ratio(sys.argv)
            result, save_path = pad_image_aspect_ratio(file_path, im, nw, nh, bg_color, opacity)
        else:
            top, right, bottom, left = get_custom_padding(sys.argv)
            result, save_path = pad_image_custom(file_path, im, top, right, bottom, left, bg_color, opacity)
        
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
            
            result.save(save_path, quality=100)
            
            # If the original is HEIC/HEIF but we're saving as another format, mention it
            if file_path.suffix.lower() in ['.heic', '.heif'] and save_path.suffix.lower() not in ['.heic', '.heif']:
                print(f"Note: Original HEIC/HEIF image converted to {save_path.suffix} format")
            print(f"Done! New image size: {result.size[0]}x{result.size[1]} pixels")
            # print(f"Image saved with opacity level {opacity}/255 background")