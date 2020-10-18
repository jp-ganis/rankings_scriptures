from PIL import Image
import os, sys

path = "./"
dirs = os.listdir( path )

def resize():
	for item in dirs:
		if ".py" in item: continue
		
		im = Image.open(path+item)
		f, e = os.path.splitext(path+item)
		imResize = im.resize((40,40), Image.ANTIALIAS)
		imResize.save(f + '.png')

resize()