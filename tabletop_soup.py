from bs4 import BeautifulSoup
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
	army_links = soup.find_all('td', {"class":"text-center faction_column col-xs-4"})

	rounds = 0

	ladder = []

	print(event_link, len(player_links))
	
	for i in range(len(player_links)):
		p = player_links[i]
		a = army_links[i]
		player_line = str(p.getText())
		army_line = str(a.getText())
		winrate = a.find_next('td').text.strip()
		
		if i == 0:
			rounds = sum([int(s) for s in winrate.split('/')])
		
		if ": " in army_line:
			idx = army_line.index(" ")
			army_line = army_line[idx+1:]
		
		if player_line[-1] == "R": player_line = player_line[:-1]
		
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
			
	return file_name
			
			
			
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
				
		try:
			event_file_name = get_event_data(url, "tablesoup_data", event_url)
			with open(event_file_name, mode='a', newline='',encoding='utf-8') as outfile:
				for m in matchups:
					m = m.replace('\t', ' ')
					first_split = re.compile("\(\d+\)|(def\.)|:|(tied with)").split(m)
					names = [e.strip() for e in first_split if e != None and "Round" not in e and "def." not in e and "tied with" not in e and e.strip() != '']
					outfile.write(','.join(names) + '\n')
			
			
			
		except Exception as e:
			print(event_url, e)
			
		print(len(matchups))
		print()
			
		
	print()
	print()
	
			
if __name__ == '__main__':	
	get_all_ladders()
	
	
	