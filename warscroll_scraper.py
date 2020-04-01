import slate3k as slate
import os.path
import random
import json
import glob
import csv
import re
import os

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
			
def strip_warscrolls_from_tomes():
	files = glob.glob('input_data_files/battletome_txts/*.txt')
	
	stat_dict = {}
	
	for file in files:
		army = os.path.basename(file)[:-4]
		print(f'Processing {army} txt...')
		
		with open(file, 'r', newline='') as text:
			page = []
		
			for line in text:
				line = line.strip()
				if len(line) == 0: continue
				
				if line == "PAGEBREAK":	
					if "WARSCROLL" in page:
						scrolls = []
						scroll_count = page.count("WARSCROLL")
						
						if scroll_count > 2:
							print("3 scroll page?!")
							print(page)
							
						elif scroll_count == 2 and page[0] != page[1]:
							split = page.index("KEYWORDS")+2
							scrolls = [page[:split], page[split:]]
							
						else:
							scrolls = [page]
						
						for scroll in scrolls:
							try:
								name = scroll[scroll.index("WARSCROLL")+1]
								name_b = scroll[scroll.index("WARSCROLL")-1]
							except Exception as e:
								print(e)
								print(scroll)
								print("Whatever")
							
							if name[0].isdigit():
								name = name_b
								
							if len(name_b) < len(name):
								name = name_b
							
							if name[0].isdigit():
								name = scroll[scroll.index("WARSCROLL")+1]
							
							name = name.title()
							
							if "Destruction" in name: continue
							
							# print('----------------------------------------')
							# print(f'{name} Warscroll')
							# print('----------------------------------------')
							
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
								
								
								# print(name,stats)
								sd = {}
								
								sd["move"] = "*"
								if (len(stats) > 3):
									sd["move"] = int([s[:s.index('"')] for s in stats if '"' in s][0])
								
								sd["save"] = int([s[:s.index('+')] for s in stats if '+' in s][0])
								
								stats = [s for s in stats if ('"' not in s and '+' not in s)]
								
								sd["wounds"] = int(stats[0])
								sd["bravery"] = int(stats[-1])
								sd["name"] = name
								
								sd["wizard"] = int("WIZARD" in ''.join(page))
								sd["hero"] = int("HERO" in ''.join(page))
								
								sd["faction"] = army
								
								stat_dict[name] = sd
								break
							
							# print(scroll)
							# print()
							# input()
				
					page = []
					
				else:
					page.append(line)
					
	return stat_dict
		
def get_stat_score(s):
	if s["move"] == '*': s["move"] = 12
	return s["wounds"] + (7-s["save"]) + s["bravery"] + s["move"] + s["wizard"]*3 + s["hero"]*2

if __name__ == '__main__':	
	sd = strip_warscrolls_from_tomes()
	
	# sd = {k:v for k,v in sorted(sd.items(),key=lambda i: get_stat_score(i[1]), reverse=True)}
	
	for s in sd:
		print(f'{s:50}\t {str(sd[s])}')
		
	print(len(sd))
	
	with open(f'output_data_files/warscrolls.json', 'w') as json_file:
		json.dump(sd, json_file)
	
		