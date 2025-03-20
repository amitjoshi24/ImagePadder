Amit Joshi's Image Padder pads images to be whatever aspect ratio you want while keeping preserving the original resolution. A suffix `-padded_WxH` is added to the resulting file.

The program and the image padding algorithm were originally written by Amit Joshi ([@amitjoshi24](https://github.com/amitjoshi24)). Code improvements were made by Jeffrey Wang ([@jeffw16](https://github.com/jeffw16)).

## Website
[@https://amitjoshi24.github.io/ImagePadder/]([https://github.com/amitjoshi24](https://amitjoshi24.github.io/ImagePadder/))

## Installation
Python 3.4+ is required to run this.

No virtual environment is required for running this. However, if this makes you feel more comfortable, you can set one up by using the following code:

1. `python3 -m venv .venv`
2. `source .venv/bin/activate`

## Usage
The image padder can be ran either by passing in command-line arguments or by using the interactive prompt.

**CLI arguments**:
`python3 imagepadder2.py '/Users/apple/Pictures/best_friends_photo.jpg' 16x9`

**Interactive prompt**:
`python3 imagepadder2.py`

```
> image's filename to pad: /Users/apple/Pictures/best_friends_photo.jpg
> enter aspect ratio you desire in the form of WIDTHxHEIGHT, e.g. "4x3": 16x9
```
