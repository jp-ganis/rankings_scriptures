import slate3k as slate
import os.path
import random
import json
import glob
import csv
import re
import os
import ntpath
import subprocess

import cv2

from pdf2image import convert_from_path
from matplotlib import pyplot as plt

import numpy as np
from xgboost import XGBClassifier, XGBRegressor
from xgboost import plot_importance

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer


def convert_battletomes_to_txt():
	files = glob.glob('input_data_files/battletome_pdfs/*.pdf')
	

	for file in files:
		army = os.path.basename(file)[:-4]
		print(f'Processing {army} pdf...')
		
		try:
			if os.path.isfile(f'input_data_files/battletome_txts/{army}.txt'):
				continue
			
			with open(file, 'rb') as f:
				doc =  slate.PDF(f)
				
			with open(f'input_data_files/battletome_txts/{army}.txt', 'w') as f:
				for p in doc:
					f.write(p + "\n")
					f.write("PAGEBREAK\n")
		
			print("\n")
			
		except Exception as e:
			print(e)
			print()
			
def get_page_data():
	files = glob.glob('input_data_files/battletome_txts/*.txt')
	pages = {}
	
	for file in files:
		army = os.path.basename(file)[:-4]
		pages[army] = []
		print(f'Splitting {army} txt into pages...')
		
		with open(file, 'r', newline='') as text:
			page = []
		
			for line in text:
				line = line.strip()
				if len(line) == 0: continue
				
				if line != "PAGEBREAK":
					page.append(line)
				else:
					pages[army].append(page)
					page = []
			
	return pages
			
def strip_warscrolls_from_tomes(pages):
	print()
	print() 
	
	stat_dict = {}
	warscroll_regexes = ["[A|An]\s+(.*) is a single model", "A unit of (.*) has", "(.*) is a named"]
	scrolls = {}

	for army in pages:
		scrolls[army] = {}
		print(f'Stripping warscrolls from {army} pages...')
		
		for page in pages[army]:
			names = []
			
			for line in page:
				for pattern in warscroll_regexes:
					m = re.search(pattern, line)
					if m != None:
						names.append(m.group(1))
			
			scroll_count = len(names)
			
			if scroll_count == 1:
				scrolls[army][names[0]] = page
				
			elif scroll_count == 2:
				split_index = None
				
				for i,line in enumerate(page):
					if "KEYWORDS" in line:
						split_index = i + 2
						break
				
				page_a = page[:split_index]
				page_b = page[split_index:]
			
				scrolls[army][names[0]] = page_a
				scrolls[army][names[1]] = page_b
				
			elif scroll_count > 2:
				print("Too many scrolls found. F")
	
	print()
	print()
	
	return scrolls
	
def get_scroll_stats(scrolls):
	stat_dict = {}
		
	scroll_successes = 0
	scroll_attempts = 0
		
	for army in scrolls:
		for unit in scrolls[army]:
			scroll = scrolls[army][unit]
			scroll_attempts += 1
			
			weaponized = False
			for i in range(len(scroll)-4):
				if scroll[i] == "DESCRIPTION": weaponized = False
				elif "WEAPONS" in scroll[i]: weaponized = True
				elif weaponized: continue
			
				stats = scroll[i:i+4]
				
				if not stats[0][0].isdigit(): continue
				
				stats = [s.replace("''",'"') for s in stats]
				
				if not any(['"' in s for s in stats]): stats = scroll[i:i+3]
				
				if len([s for s in stats if '+' in s]) != 1: continue
				
				if all([s.isdigit() for s in stats[0]]) and int(stats[0]) > 40: continue
				
				if any([len(s) > 3 for s in stats]): continue
				
				bravery_count = 0
				for s in stats:
					if not all([c.isdigit() for c in s]): continue
					if int(s) < 2 or int(s) > 10: continue
					bravery_count += 1
				
				if bravery_count < 1: continue
				
				# print(unit,stats)
				sd = {}
				
				sd["move"] = "*"
				if (len(stats) > 3):
					sd["move"] = int([s[:s.index('"')] for s in stats if '"' in s][0])
				
				sd["save"] = int([s[:s.index('+')] for s in stats if '+' in s][0])
				
				stats = [s for s in stats if ('"' not in s and '+' not in s)]
				
				sd["wounds"] = int(stats[0])
				sd["bravery"] = int(stats[-1])
				sd["name"] = unit
				
				sd["wizard"] = int("WIZARD" in ''.join(scroll))
				sd["fly"] = int("FLY" in ''.join(scroll))
				sd["shoot"] = int("MISSILE WEAPONS" in ''.join(scroll))
				sd["length"] = len(''.join(scroll))
				sd["length2"] = len(scroll[0])
				sd["ignored"] = int("ignored" in ''.join(scroll).lower())
				sd["faction_id"] = len(army)
				sd["rend"] = int("-1" in ' '.join(scroll))
				sd["high_rend"] = int("-2" in ' '.join(scroll))
				sd["mega_rend"] = int("-3" in ' '.join(scroll))
				
				sd["faction"] = army
				
				scroll_successes += 1
				
				stat_dict[unit] = sd
				break
				
	print(scroll_successes, scroll_attempts)

	return stat_dict

def convert_battletomes_to_images():
	import fitz

	files = glob.glob('input_data_files/battletome_pdfs/*.pdf')
	
	warscroll_pages = {}
	warscroll_pages["Beasts of Chaos"] = [86,104]
	warscroll_pages["Blades of Khorne"] = [102,128]
	warscroll_pages["Cities of Sigmar"] = [89,128]
	
	warscroll_pages["Daughters of Khaine"] = [76,88]
	warscroll_pages["Disciples of Tzeentch"] = [98,119]
	warscroll_pages["Flesh-eater Courts"] = [76,88]
	
	warscroll_pages["Fyreslayers"] = [76,88]
	warscroll_pages["Gloomspite Gitz"] = [84,88]
	warscroll_pages["Hedonites of Slaanesh"] = [80,88]
	
	warscroll_pages["Idoneth Deepkin"] = [126,88]
	warscroll_pages["Kharadron Overlords"] = [82,88]
	warscroll_pages["Legions of Nagash"] = [97,88]
	
	warscroll_pages["Maggotkin of Nurgle"] = [86,88]
	warscroll_pages["Nighthaunt"] = [72,88]
	warscroll_pages["Ogor Mawtribes"] = [102,88]
	
	warscroll_pages["Orruk Warclans"] = [92,88]
	warscroll_pages["Ossiarch Bonereapers"] = [96,88]
	warscroll_pages["Seraphon"] = [78,88]
	
	warscroll_pages["Skaven"] = [99,88]
	warscroll_pages["Slaves to Darkness"] = [88,88]
	warscroll_pages["Stormcast Eternals"] = [156,88]
	
	warscroll_pages["Sylvaneth"] = [90,88]
	
	
	for file in files:
		army = os.path.basename(file)[:-4]
		print(f'Processing {army} pdf...')

		doc = fitz.open(file)
		
		num_pages = doc.pageCount - warscroll_pages[army][0]
		c = 0
		
		for p in range(warscroll_pages[army][0], doc.pageCount):			
			c+= 1
			page = doc.loadPage(p) 
			pix = page.getPixmap()
			output = f'input_data_files/battletome_images/{army}_{p}.png'
			pix.writePNG(output)
			
			print(f'[{"."*c}{" "*(num_pages-c)}]',end='\r')
		print()
		
def split_warscrolls():
	files = glob.glob('input_data_files/battletome_images/*.png')
	s_template = cv2.imread('input_data_files/warscroll_template.png', 0)
	
	w, h = 106,106
	ow,oh = -32, -24

	methods = [cv2.TM_CCOEFF, cv2.TM_CCOEFF_NORMED, cv2.TM_CCORR,cv2.TM_CCORR_NORMED, cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]
	
	c = 0
	
	base_output = "output_data_files/warscroll_images/"
	
	armies = ["Daughters of Khaine", "Legions of Nagash", "Idoneth Deepkin", "Maggotkin of Nurgle", "Orruk Warclans", "Seraphon", "Sylvaneth"]
	
	for file in files:
		
		fname = ntpath.basename(file)
	
		if not any([a in file for a in armies]):
			img = cv2.imread(file, 0)

			# Detect blobs.
			params = cv2.SimpleBlobDetector_Params()
			params.filterByArea = True
			params.minArea = 2500

			detector = cv2.SimpleBlobDetector_create(params)
			
			keypoints = detector.detect(img)
			
			imkp = cv2.drawKeypoints(img, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

			font = cv2.FONT_HERSHEY_SIMPLEX
			cv2.putText(imkp,f'KP_COUNT: {len(keypoints)}',(64,64), font, 1,(255,0,0),2)
			
			if len(keypoints) == 2:
				h,w = img.shape
				
				img_top = img[0:int(h/2), 0:w]
				img_bottom = img[int(h/2):h, 0:w]
				
				cv2.imwrite(f'{base_output}{fname.replace(".png","__split_top.png")}', img_top)
				cv2.imwrite(f'{base_output}{fname.replace(".png","__split_bottom.png")}', img_bottom)
			else:
				cv2.imwrite(f'{base_output}{fname.replace(".png","__split_full.png")}', img)
			
		else:
			img = cv2.imread(file, 0)
			edges = cv2.Canny(img,50,150,apertureSize = 3) 
			
			# This returns an array of r and theta values 
			lines = cv2.HoughLines(edges, 1, np.pi/180, 400) 
			  
			# The below for loop runs till r and theta values  
			# are in the range of the 2d array 
			for line in lines:
				for r,theta in line: 
					  
					# Stores the value of cos(theta) in a 
					a = np.cos(theta) 

					# Stores the value of sin(theta) in b 
					b = np.sin(theta) 
					  
					# x0 stores the value rcos(theta) 
					x0 = a*r 
					  
					# y0 stores the value rsin(theta) 
					y0 = b*r 
					  
					# x1 stores the rounded off value of (rcos(theta)-1000sin(theta)) 
					x1 = int(x0 + 1000*(-b)) 
					  
					# y1 stores the rounded off value of (rsin(theta)+1000cos(theta)) 
					y1 = int(y0 + 1000*(a)) 

					# x2 stores the rounded off value of (rcos(theta)+1000sin(theta)) 
					x2 = int(x0 - 1000*(-b)) 
					  
					# y2 stores the rounded off value of (rsin(theta)-1000cos(theta)) 
					y2 = int(y0 - 1000*(a)) 
					  
					# cv2.line draws a line in img from the point(x1,y1) to (x2,y2). 
					# (0,0,255) denotes the colour of the line to be  
					#drawn. In this case, it is red.  
					cv2.line(edges, (x1,y1), (x2,y2), (0,0,255), 2) 
					
			if len(lines) >= 6:
				h,w = img.shape
				
				img_top = img[0:int(h/2), 0:w]
				img_bottom = img[int(h/2):h, 0:w]
				
				cv2.imwrite(f'{base_output}{fname.replace(".png","__split_top.png")}', img_top)
				cv2.imwrite(f'{base_output}{fname.replace(".png","__split_bottom.png")}', img_bottom)
			else:
				cv2.imwrite(f'{base_output}{fname.replace(".png","__split_full.png")}', img)
				
def get_unit_names():
	pass
	
def get_statwheel_stats():
	files = glob.glob('output_data_files/warscroll_images//*.png')
	s_template = cv2.imread('input_data_files/warscroll_template.png', 0)
	o_template = cv2.imread('input_data_files/old_template.png', 0)
	
	w, h = 106,106
	ow,oh = -32, -24

	methods = [cv2.TM_CCOEFF, cv2.TM_CCOEFF_NORMED, cv2.TM_CCORR,cv2.TM_CCORR_NORMED, cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]
	
	c = 0
	
	base_output = "output_data_files/warscroll_images/"
	wheel_output = "output_data_files/statwheel_images/"
	
	armies = ["Daughters of Khaine", "Legions of Nagash", "Idoneth Deepkin", "Maggotkin of Nurgle", "Orruk Warclans", "Seraphon", "Sylvaneth"]
	
	for file in files:
		fname = ntpath.basename(file)
		
		if any([a in fname for a in armies]):
			template = o_template
			box_mult = 0.75
		else:
			template = s_template
			box_mult = 1.0
				
		img = cv2.imread(file, 0)
		
		res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)

		min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
		
		top_left = max_loc[0] + ow, max_loc[1] + oh
			
		bottom_right = (top_left[0] + int(w*box_mult), top_left[1] + int(h*box_mult))

		font = cv2.FONT_HERSHEY_SIMPLEX
		# cv2.putText(imkp,f'KP_COUNT: {len(keypoints)}',(64,64), font, 1,(255,0,0),2)
		
		cv2.rectangle(img, top_left, bottom_right, (0,255,0), 2)
		cv2.imshow("X",img)
		cv2.waitKey(0)
		

if __name__ == '__main__':	
	# convert_battletomes_to_images()
	# split_warscrolls()
	# get_statwheel_stats()
	
	pages = get_page_data()
	scrolls = strip_warscrolls_from_tomes(pages)
	stats = get_scroll_stats(scrolls)
	
	with open('output_data_files/new_features.json', 'w') as json_file:
		json.dump(stats, json_file)
		
	# print(stats)
		