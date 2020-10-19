from bs4 import BeautifulSoup
import dateutil.parser as dp
from shutil import copyfile
import db_state_of_the_meta
import db_check_aliases
import Levenshtein
import requests
import dataset
import random
import json
import csv
import re

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
					
					if json_data['attendee_count'] < 6: continue
					
					event_urls.append(json_data['custom_url'])
	return event_urls
	
def get_event_data(event_link,output_folder,custom_file_name):
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
		player_line = player_line.strip()
		
		player_factions[player_line] = army_line
		ladder.append((player_line, army_line, winrate))
		
	file_name = output_folder+"/"+f'{custom_file_name}.csv'
	
	with open(file_name, mode='w', newline='',encoding='utf-8') as event_file:
		writer = csv.writer(event_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

		try:
			writer.writerow(["NEW_EVENT_TAG",event_name,date,rounds])
			for e in ladder:
				writer.writerow([e[0],e[1],e[2]])
		except Exception as e:
			print("row in",custom_file_name,"failed.", e)
			
	return file_name, player_factions, event_name, dp.parse(date), rounds
				
def get_smart_tto_data(db):
	base_url = "https://tabletop.to/"
	event_urls = get_aos_urls()
	
	# event_urls = ['onslaught-2020'] ## used for inputting a single event
	
	for event_url in event_urls:
		if "/" in event_url: continue
		
		print(event_urls.index(event_url), len(event_urls), end='\r')
		url = base_url+"/"+event_url
		
		page = requests.get(url)
		soup = BeautifulSoup(page.text, 'html.parser')
		
		event_file_name, player_faction_data, event_name, date, rounds = get_event_data(url, "input_data_files/tablesoup_data", event_url)
		
		event_id = db['event'].insert(dict( name=event_name, date=date, rounds=rounds ))
		
		defs = soup.find_all('a')
		for d in defs:
			if d.get('data-content'):
				string = d.get('data-content').replace("'", "")
				raw_mups = [x.group(1) for x in re.finditer(r'Round \d:(\s*((\w+\s*)+).*def\. ((\w+\s*)+))', string)]
				raw_kps = [int(x.group(1)[1:-1]) for x in re.finditer(r'((\(\d+\)))', string)]
				
				if len(raw_mups) == 0: continue
				
				m = str(raw_mups[0]).replace('\t', ' ')
				first_split = re.compile("\(\d+\)|(def\.)|:|(tied with)").split(m)
				names = [e.strip() for e in first_split if e != None and "Round" not in e and "def." not in e and "tied with" not in e and e.strip() != '']

				for n in range(0, len(names), 2):
					w_player = db_check_aliases.predefined_aliases(names[n])
					l_player = db_check_aliases.predefined_aliases(names[n+1])
					
					if w_player not in player_faction_data:
						w_player = min([(x, Levenshtein.distance(x, w_player)) for x in player_faction_data],key=lambda i:i[1])[0]
						
					if l_player not in player_faction_data:
						l_player = min([(x, Levenshtein.distance(x, l_player)) for x in player_faction_data],key=lambda i:i[1])[0]
					
					w_faction = db_check_aliases.predefined_faction_aliases( player_faction_data[w_player] )
					l_faction = db_check_aliases.predefined_aliases( player_faction_data[l_player] )

					w_kp = 0
					l_kp = 0
					
					try:
						w_kp = raw_kps[n]
						l_kp = raw_kps[n+1]
					except Exception as e:
						print(type(e), e, event_name, "Could not load killpoint data")
					
					db['game'].insert(dict( winner_name=w_player, winner_faction=w_faction, winner_kp=w_kp, loser_name=l_player, loser_faction=l_faction, loser_kp=l_kp, event_id=event_id))

if __name__ == '__main__':	
	db=dataset.connect("sqlite:///__tinydb.db")

	clear = input("clear previous database? y/n\t")
	
	if clear == "y" or clear == "Y":
		copyfile("__tinydb.db", f'db_backups/__tinydb_BAK_{random.randint(0,8931528518)}.db')

		for t in db.tables:
			db[t].drop()
		
		get_smart_tto_data(db)
		
		check_aliases.populate_player_table(db)
		check_aliases.populate_faction_table(db)
	
	
