# Image Padder
A tool that pads images to any aspect ratio while preserving the original resolution. Add space around your images with custom padding or convert to specific aspect ratios like 16:9, 4:3, 1:1 square, and more.

## Features

- Preserve original image resolution and quality
- Choose any background color (with optional transparency)
- Create images with specific aspect ratios
- Process multiple images at once
- Works with all common image formats (JPG, PNG, HEIC etc.)

## Website  
[https://amitjoshi24.github.io/ImagePadder/](https://amitjoshi24.github.io/ImagePadder/)  

The web version is the easiest way to use Image Padder, with a user-friendly interface and additional options like custom padding.

**Note:** Browser-based tools have resolution limits (typically 16,384 × 16,384 pixels). For very high-resolution images, use the command-line version below.

## Installation
Python 3.4+ is required to run this.

No virtual environment is required for running this. However, if this makes you feel more comfortable, you can set one up by using the following code:

1. `python3 -m venv .venv`
2. `source .venv/bin/activate`

You'll also need to install the PIL/Pillow library:

```
pip install Pillow
```

## Usage
The image padder can be ran either by passing in command-line arguments or by using the interactive prompt.

**CLI arguments**:

For aspect ratio padding:
```
python3 imagepadder2.py '/Users/apple/Pictures/best_friends_photo.jpg' aspect 16x9 #FFFFFF 100
                          ^                                            ^      ^     ^       ^
                          |                                            |      |     |       |
                      image path                                   mode  ratio  color   opacity
```

For custom padding:
```
python3 imagepadder2.py '/Users/apple/Pictures/best_friends_photo.jpg' custom 20 30 20 30 #000000 50
                          ^                                            ^      ^  ^  ^  ^   ^       ^
                          |                                            |      |  |  |  |   |       |
                      image path                                   mode   top right bottom left color opacity
```

**Interactive prompt**:
```
python3 imagepadder2.py
```

Then follow the prompts:
```
> image's filename to pad: /Users/apple/Pictures/best_friends_photo.jpg
> Choose padding mode ('aspect' for aspect ratio or 'custom' for custom padding): aspect
> Enter aspect ratio you desire in the form of WIDTHxHEIGHT, e.g. "4x3": 16x9
> Background color (hex format, e.g. #FFFFFF for white) [default: #FFFFFF]: 
> Background opacity (0-100%, default: 100): 100
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
> Background opacity (0-100%, default: 100): 50
```

## Working with High-Resolution Images

While most image processing tools in browsers have canvas size limitations (typically around 16,384 × 16,384 pixels), the command-line version of Image Padder can handle much larger images by using Python's PIL/Pillow library directly. For gigapixel images or other extremely large files, the command-line version is the recommended approach, otherwise the website works fine.

## Credits

The program and the image padding algorithm were originally written by Amit Joshi ([@amitjoshi24](https://github.com/amitjoshi24)). Code improvements were made by Jeffrey Wang ([@jeffw16](https://github.com/jeffw16)).