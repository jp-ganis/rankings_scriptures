from bs4 import BeautifulSoup
import requests
import csv
import re

base_url = "http://www.rankings.baddice.co.uk"
page = requests.get(base_url+"/ranking/region=3&game=6&season=0")
soup = BeautifulSoup(page.text, 'html.parser')

player_links = []
for a in soup.find_all('a', href=True):
	if "/player/" in a['href']:
		player_links.append(a['href'])
		
		
entries = {}
player_idx = -1
		
for link in player_links:
	player_idx += 1
	
	if player_idx > 500:
		break
	
	page = requests.get(base_url+link)
	player_soup = BeautifulSoup(page.text, 'html.parser')
	
	name = player_soup.find('h3').renderContents()
	name = re.search(r'Rankings? - ((\w+\s*)+)', str(name)).group(1)
	
	if name == "JP Gains": name = "James Ganis"
	
	entries[name] = []
	
	trs = player_soup.find_all('tr')
	
	for tr in trs:
		tds = tr.find_all('td')
		
		idx = 0
		
		army = None
		date = None
		points = None
		
		for td in tds:
			string = str(td.renderContents())
			
			if idx == 1:
				## date
				r = re.search(r'(\d+ \w\w\w \d+)', string)
				if r:
					date = r.group(1)
				
			elif idx == 3:
				## army
				r = re.search(r'army=((\w+\s*)+)', string)
				if r:
					army = r.group(1)
					
			elif idx == 5:
				## points
				r = re.search(r'(\d+.\d+)', string)
				if r:
					points = r.group(1)
				
			idx += 1
			
		if army != None and date != None and points != None:
			entries[name].append((army,date,points))
		
	print(player_idx, end='\r')
print()
		
with open('filth3.csv', mode='w') as filth_file:
	writer = csv.writer(filth_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

	for e in entries:
		for event in entries[e]:
			writer.writerow([e, event[0], event[1], event[2]])