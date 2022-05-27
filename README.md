keeping full resolution, pads image to be whatever aspect ratio you want, names it "padded" + the original file name

## Installation
Python 3.4+ is required to run this.

No virtual environment is required for running this. However, if this makes you feel more comfortable, you can set one up by using the following code:

1. ```bash
python3 -m venv .venv
```
2. ```bash
source .venv/bin/activate
```

## Usage
The image padder can be ran either by passing in command-line arguments or by using the interactive prompt.

'''CLI arguments''':
```bash
python3 imagepadder2.py '/Users/apple/Pictures/best_friends_photo.jpg' 16x9
```

'''Interactive prompt''':
```bash
python3 imagepadder2.py
```
```
> image's filename to pad: /Users/apple/Pictures/best_friends_photo.jpg
> enter aspect ratio you desire in the form of WIDTHxHEIGHT, e.g. "4x3": 16x9
```