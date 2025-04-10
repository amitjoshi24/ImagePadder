# Image and Video Padder

<p align="center">
  <img src="https://github.com/amitjoshi24/ImagePadder/raw/main/favicon.jpg" width="150" alt="Image Padder Logo">
</p>

A tool that pads images or videos to any aspect ratio while preserving the original resolution. Add space around your images/videos with custom padding or convert to specific aspect ratios like 16:9, 4:3, 1:1 square, and more. Perfect for social media posts or vlogs, video thumbnails, and printing.

## Features

- Preserve original image/video resolution and quality
- Choose any background color, with optional transparency
- Pad images with specific aspect ratios or custom padding
- Process multiple images at once (website only, for now)
- Pad videos (command-line version only)
- Works with all common image formats (JPG, PNG, HEIC etc.)
- Works with all common video formats (mp4, mov, etc.)

## Website  
[https://amitjoshi24.github.io/ImagePadder/](https://amitjoshi24.github.io/ImagePadder/)  

The web version is the easiest way to use Image Padder, with a user-friendly interface and additional options like custom padding. The website does NOT support video padding, for that keep reading.

**Note:** Browser-based tools have resolution limits (typically 16,384 × 16,384 pixels). For very high-resolution images, HEIC/HEIF images, or video padding, use the command-line version or Python Graphical-User-Interface (GUI) below.

## Padding Images and Videos Locally ##

### Installation ###
Python 3.4+ is required to run this.

No virtual environment is required for running this. However, if this makes you feel more comfortable, you can set one up by using the following code:

1. `python3 -m venv .venv`
2. `source .venv/bin/activate`

### Dependencies

Install required dependencies using the requirements.txt file:

```
pip install -r requirements.txt
```

This will install:
- PIL (Pillow): Core image processing library
- pillow-heif: For HEIC/HEIF support (Apple's image format)
- moviepy: For video padding support
- tkinter: For GUI (included with standard Python)

Or install Python dependencies manually:

```
pip install Pillow
pip install moviepy
pip install pillow-heif
```

### External Dependencies

For video padding functionality, FFmpeg needs to be installed on your system:
- macOS: `brew install ffmpeg`
- Ubuntu/Linux: `sudo apt-get install ffmpeg`
- Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) or use `choco install ffmpeg` with Chocolatey

**Note:** The command-line tool will automatically detect if you're missing any required dependencies.

### Usage
Fortunately, I have just made a new GUI if you prefer

#### GUI Mode

![GUI Screenshot](https://github.com/amitjoshi24/ImagePadder/blob/main/guiss.jpg)

1. Run: `python imagepaddergui.py`
2. Select an image or video using the "Browse" button
3. Choose between "Aspect Ratio" or "Custom Padding" modes
4. Configure your padding settings
5. Select a background color (with optional transparency)
6. Click "Process" to create your padded image/video

#### Command Line Mode

The image padder can be ran either by passing in command-line arguments to `imagepadder2.py` or by using the interactive prompt also within `imagepadder2.py`. 

##### CLI arguments

###### Image Padding

For image aspect ratio padding:
```
python3 imagepadder2.py '/Users/apple/Pictures/best_friends_photo.jpg' aspect 16x9 #FFFFFF 255
```

| Parameter | Description |
|-----------|-------------|
| 1: Image/Video path | Path to the image/video file |
| 2: Mode | `aspect` for aspect ratio mode |
| 3: Ratio | Width and height in format `WxH` (e.g., `16x9`) |
| 4: Color | Background color in hex format (e.g., `#FFFFFF` for white) |
| 5: Opacity | Background opacity, 0-255 (e.g., `255` for fully opaque) |

For image custom padding:
```
python3 imagepadder2.py '/Users/apple/Pictures/best_friends_photo.jpg' custom 20 30 20 30 #000000 128
```

| Parameter | Description |
|-----------|-------------|
| 1: Image path | Path to the image file |
| 2: Mode | `custom` for custom padding mode |
| 3-6: Padding | Four values for padding in pixels: `top right bottom left` |
| 7: Color | Background color in hex format (e.g., `#000000` for black) |
| 8: Opacity | Background opacity, 0-255 (e.g., `128` for half-transparent) |

###### Video Padding (works the same way)

For video aspect ratio padding:
```
python3 imagepadder2.py '/Users/apple/Videos/vacation.mp4' aspect 16x9 #000000 255
```

For video custom padding:
```
python3 imagepadder2.py '/Users/apple/Videos/vacation.mp4' custom 50 50 50 50 #0000FF 255
```

##### Interactive Prompt (Works with both Images and Videos) #####


```
python3 imagepadder2.py
```

Then follow the prompts:
```
> image's filename to pad: /Users/apple/Pictures/best_friends_photo.jpg
> Choose padding mode ('aspect' for aspect ratio or 'custom' for custom padding): aspect
> Enter aspect ratio you desire in the form of WIDTHxHEIGHT, e.g. "4x3": 16x9
> Background color (hex format, e.g. #FFFFFF for white) [default: #FFFFFF]: 
> Background opacity (0-255, default: 255): 255
```
OR
```
> image's filename to pad: /Users/apple/Videos/vacation.mp4
> Choose padding mode ('aspect' for aspect ratio or 'custom' for custom padding): aspect
> Enter aspect ratio you desire in the form of WIDTHxHEIGHT, e.g. "4x3": 16x9
> Background color (hex format, e.g. #FFFFFF for white) [default: #FFFFFF]: #000000
> Background opacity (0-255, default: 255): 255
```
OR
```
> image's filename to pad: /Users/apple/Pictures/best_friends_photo.jpg
> Choose padding mode ('aspect' for aspect ratio or 'custom' for custom padding): custom
> Enter top padding (pixels): 20
> Enter right padding (pixels): 30
> Enter bottom padding (pixels): 20
> Enter left padding (pixels): 30
> Background color (hex format, e.g. #FFFFFF for white) [default: #FFFFFF]: #000000
> Background opacity (0-255, default: 255): 128
```

#### Examples

| **Command** | **Description** |
|-------------|-----------------|
| `python -m imagepadder2 image.jpg` | Interactive command-line mode |
| `python imagepaddergui.py` | Launch the graphical user interface |
| `python -m imagepadder2 image.jpg aspect 16x9` | Pad to 16:9 aspect ratio |
| `python -m imagepadder2 image.jpg custom 10 20 30 40` | Custom padding (top, right, bottom, left) |
| `python -m imagepadder2 image.jpg aspect 1x1 #FF0000 128` | Square with semi-transparent (128 out of 255) red (#FF0000) background |


### Notes ###

#### Working with High-Resolution Images ####

While most image processing tools in browsers have canvas size limitations (typically around 16,384 × 16,384 pixels), the command-line version of Image Padder can handle much larger images by using Python's PIL/Pillow library directly. For gigapixel images, or other extremely large files, the command-line version or GUI are needed, otherwise the website works fine.

#### Working with Videos ####
The command-line version and python GUI support padding videos to different aspect ratios or adding custom padding. Supported formats include MP4, AVI, MOV, MKV, WEBM, and WMV. The padding is applied to each frame while preserving the original audio track. Due to the processing required, video padding may take some time depending on the length and resolution of the video, but progress is shown in command line, and somewhat in the logs section of the GUI.

The parameters work the same way as for images, but the tool will automatically detect if the file is a video based on the extension (mp4, avi, mov, mkv, webm, wmv). Note that the script is still called "imagepadder2.py" even for videos. 

You can use the interactive prompt, CLI arguments, or GUI with both images and videos - the tool will automatically detect the file type and pad accordingly:

## Credits

The program and the image padding algorithm were originally written by Amit Joshi ([@amitjoshi24](https://github.com/amitjoshi24)). Code improvements were made by Jeffrey Wang ([@jeffw16](https://github.com/jeffw16)).

## Support the Project

If you find this tool useful, consider supporting its development through one of these options:

- [PayPal](https://paypal.me/amitjoshi168)
- [Venmo](https://venmo.com/Amit-Joshi-11) 
- [Ko-fi](https://ko-fi.com/amitjoshi24)

Thank you for your support!
