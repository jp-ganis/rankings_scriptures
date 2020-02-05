from bs4 import BeautifulSoup
import scipy.stats
import requests
import csv
import re

events_file = open('data_files/events.csv', 'w')

base_url = "http://www.rankings.baddice.co.uk"
page = requests.get(base_url+"/tournaments/region=3&game=6&season=1")
soup = BeautifulSoup(page.text, 'html.parser')

event_links = []

for a in soup.find_all('a', href=True):
	if "/tournament/" in a['href']:
		event_links.append(a['href'])
		
event_idx = -1

for link in event_links:
	event_idx += 1
	
	page = requests.get(base_url+link)
	event_soup = BeautifulSoup(page.text, 'html.parser')
	
	event_name = str(event_soup.find('h3').renderContents())
	event_name = re.search(r'Results - (([\w|-]+\s*)+)', str(event_name)).group(1)
	
	event_date = event_soup.find_all('div')
	rounds = 5
	
	for d in event_date:
		if 'rounds' in str(d.renderContents()):
			event_date = str(d.renderContents())
			rounds = re.search(r'(\d) rounds', event_date).group(1)
			event_date = re.search(r'on (\d+\s\w+\s\d+)', event_date).group(1)
			
	events_file.write(f'NEW_EVENT_TAG,{event_name},{event_date},{rounds}\n')
	
	name = None
	army = None
	
	hrefs = event_soup.find_all('a' , href=True)
	
	for a in hrefs:		
		if '/player/' in a['href']:
			name = str(a.renderContents())
			name = re.search(r'\s+(([\w|\']+\s*)+)', name).group(1)
			army = str(a.findNext('td').renderContents())
			army = re.search(r'army=((\w+\s*)+)', army)
			
			if army != None:
				army = army.group(1)
			else:
				army = "UNKNOWN_ARMY"
			
			events_file.write(f'{name},{army}\n')
	
	print(f'processing event {event_idx} out of {len(event_links)}', end='\r')
	
events_file.close()
	