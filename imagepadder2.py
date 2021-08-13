# hi ur cute <3
from PIL import Image
import sys
from math import ceil

file = input("image's filename to pad:")

im = Image.open(file)

aspectRatio = input("enter aspect ratio you desire in the form of WIDTHxHEIGHT, i.e. \"4x3\":")

splitted = aspectRatio.split("x")
nw = int(splitted[0])
nh = int(splitted[1])
width, height = im.size

if nw/nh <= width/height:
	# vertical pad
	newwidth = width
	newheight = int(ceil(width * nh / nw))

	result = Image.new(im.mode, (newwidth, newheight), (255, 255, 255))
	startheight = (newheight - height)//2
	result.paste(im, (0, startheight))
	result.save("padded" + str(nw) + "x" + str(nh) + file)
else:
	# horizontal pad
	newheight = height
	newwidth = int(ceil(height * nw / nh))

	result = Image.new(im.mode, (newwidth, newheight), (255, 255, 255))
	startwidth = (newwidth - width)//2
	result.paste(im, (startwidth, 0))
	result.save("padded" + str(nw) + "x" + str(nh) + file)
