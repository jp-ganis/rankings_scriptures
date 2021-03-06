from bs4 import BeautifulSoup
import dataset
import requests
import json
import csv
import re


def get_event_data(event_link,output_folder="",custom_file_name=None):
	page = requests.get(event_link)
	soup = BeautifulSoup(page.text, 'html.parser')
	
	event_name = soup.find('h1', {"id" : "event-title"}).getText().strip()
	date = soup.find('li', {"title" : "Event Date"}).getText().strip()

	player_links = soup.find_all('a', {"class": "btn btn-link removespacing"})
	
	army_links = soup.find_all('td', {"class": "text-center faction_column col-xs-4"})
	army_links += soup.find_all('td', {"class": "text-center faction_column col-xs-4 "})
	army_links += soup.find_all('td', {"class": "text-center col-xs-4 faction_column "})

	rounds = 0

	ladder = []
	player_factions = {}

	print(event_link, len(player_links))
	
	for i in range(len(player_links)):
		p = player_links[i]
		
		if len(army_links) > 0:
			a = army_links[i]
			army_line = str(a.getText())
			winrate = a.find_next('td').text.strip()
		else:
			print("No armies found for", event_link)
			a = "UNKNOWN_ARMY"
			army_line = "UNKNOWN_ARMY"
			winrate = "0/0/0"
			
		player_line = str(p.getText())
		
		if i == 0:
			rounds = sum([int(s) for s in winrate.split('/')])		
			if winrate == "0/0/0":
				rounds = 5
		
		if ": " in army_line:
			idx = army_line.index(" ")
			army_line = army_line[idx+1:]
		
		if player_line[-1] == "R": player_line = player_line[:-1]
		
		player_factions[player_line] = army_line
		ladder.append((player_line, army_line, winrate))
		
	file_name = output_folder+"/"+f'{event_name}.csv'
	if custom_file_name != None:
		file_name = output_folder+"/"+f'{custom_file_name}.csv'
	
	with open(file_name, mode='w', newline='',encoding='utf-8') as event_file:
		writer = csv.writer(event_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

		try:
			writer.writerow(["NEW_EVENT_TAG",event_name,date,rounds])
			for e in ladder:
				writer.writerow([e[0],e[1],e[2]])
		except Exception as e:
			print("row in",custom_file_name,"failed.", e)
			
	return file_name, player_factions, event_name, date, rounds
				
def get_aos_urls():
	events_page = "https://tabletop.to/events"
	page = requests.get(events_page)
	soup = BeautifulSoup(page.text, 'html.parser')
	
	scripts = soup.find_all("script")
	
	event_urls = []
	for s in scripts:
		if "dataset" in s.text:
			matches = re.findall(r'{[^}]*}', s.text)
			
			for m in matches:
				if "Age of Sigmar" in m:
					json_data = json.loads(m)
					
					if json_data['attendee_count'] < 16: continue
					
					event_urls.append(json_data['custom_url'])
	return event_urls

def get_all_ladders():
	base_url = "https://tabletop.to/"
	event_urls = get_aos_urls()
	
	event_urls = ['onslaught-2020'] ## used for inputting a single event
	
	for event_url in event_urls:
		if "/" in event_url: continue
		
		print(event_urls.index(event_url), len(event_urls), end='\r')
		url = base_url+"/"+event_url
		
		page = requests.get(url)
		soup = BeautifulSoup(page.text, 'html.parser')
		
		matchups = []
		
		defs = soup.find_all('a')
		for d in defs:
			if d.get('data-content'):
				string = d.get('data-content').replace("'", "")
				matchups += [x.group(1) for x in re.finditer(r'Round \d:(\s*((\w+\s*)+).*def\. ((\w+\s*)+))', string)]
				
		event_file_name,_,_,_,_ = get_event_data(url, "input_data_files/tablesoup_data", event_url)
		with open(event_file_name, mode='a', newline='',encoding='utf-8') as outfile:
			for m in matchups:
				m = m.replace('\t', ' ')
				first_split = re.compile("\(\d+\)|(def\.)|:|(tied with)").split(m)
				names = [e.strip() for e in first_split if e != None and "Round" not in e and "def." not in e and "tied with" not in e and e.strip() != '']
				outfile.write(','.join(names) + '\n')
			
		print(len(matchups))
		print()
			
		
	print()
	print()
		
def get_smart_tto_data():
	base_url = "https://tabletop.to/"
	event_urls = get_aos_urls()
	
	event_urls = ['onslaught-2020'] ## used for inputting a single event
	
	for event_url in event_urls:
		if "/" in event_url: continue
		
		print(event_urls.index(event_url), len(event_urls), end='\r')
		url = base_url+"/"+event_url
		
		page = requests.get(url)
		soup = BeautifulSoup(page.text, 'html.parser')
		
		smart_data = []
		
		event_file_name,player_faction_data,event_name,date,rounds = get_event_data(url, "input_data_files/tablesoup_data", event_url)
		
		defs = soup.find_all('a')
		for d in defs:
			if d.get('data-content'):
				string = d.get('data-content').replace("'", "")
				raw_mups = [x.group(1) for x in re.finditer(r'Round \d:(\s*((\w+\s*)+).*def\. ((\w+\s*)+))', string)]
				raw_kps = [int(x.group(1)[1:-1]) for x in re.finditer(r'((\(\d+\)))', string)]
				
				m = str(raw_mups[0]).replace('\t', ' ')
				first_split = re.compile("\(\d+\)|(def\.)|:|(tied with)").split(m)
				names = [e.strip() for e in first_split if e != None and "Round" not in e and "def." not in e and "tied with" not in e and e.strip() != '']
				
				for n in range(0, len(names), 2):
					w_player = names[n]
					l_player = names[n+1]
					
					w_faction = player_faction_data[w_player]
					l_faction = player_faction_data[l_player]
					
					w_kp = raw_kps[n]
					l_kp = raw_kps[n+1]
					
				
				
		# with open(event_file_name, mode='a', newline='',encoding='utf-8') as outfile:
			# outfile.write('__smart_data_tag\n')
			
			
		print(len(matchups))
		print()
			
		
	print()
	print()

			
if __name__ == '__main__':	
	db=dataset.connect("sqlite:///__tinydb.db")
	
	for t in db.tables:
		db[t].drop()
		
	get_smart_tto_data(db)
	
	


	
	
	
	
