import sys

import trueskill as ts
import statistics
import json
import glob
import csv
import random
import dateutil.parser as dp

from math import sqrt
from trueskill import BETA
from trueskill.backends import cdf

import numpy as np

def generate_matchup_file():
	data_folder = "input_data_files/tablesoup_data"

	files = glob.glob(f'{data_folder}/*')

	elos = {}

	with open("output_data_files/all_uk_events/datahub_player_data.json", newline='', encoding='utf-8') as json_file:
		player_data = json.load(json_file)
		
	with open("output_data_files/all_uk_events/datahub_faction_data.json", newline='', encoding='utf-8') as json_file:
		f_data = json.load(json_file)
		
	name_subs = {"James Ganis":"Jp Ganis", "Chris Caves Jnr":"Chris Caves Jr"}	
	data_rows = []
	
	player_ids = {p:i for i,p in enumerate(player_data)}
	id_lookup = {i:p for i,p in enumerate(player_data)}
	
	fids = {f:i for i,f in enumerate(f_data)}
	
	fid_lookup = {i:f for i,f in enumerate(f_data)}
	
	fids['-'] = -1
	fid_lookup[-1] = '-'
	
	max_pids = len(player_data)

	cutoff_dates = [dp.parse('08-Jul-2020'), dp.parse('31-Dec-2025')]
	if len(sys.argv) > 1: 
		cutoff_dates = [dp.parse(sys.argv[1]), dp.parse(sys.argv[2])]
 
	for file in files:
		with open(file, newline='', encoding='utf-8') as csvfile:
			reader = csv.reader(csvfile)
			for row in reader:
				date = dp.parse(row[2])
				break
			if not(date < cutoff_dates[1] and date > cutoff_dates[0]): continue	

		with open(file, newline='', encoding='utf-8') as csvfile:
			reader = csv.reader(csvfile)
			
			pfaction = {}
			
			new_rows = []
			for row in reader:
				new_rows.append(row)
				if len(row) == 3:
					row[1] = row[1].replace('Of','of')
					row[1] = row[1].replace('Ogor ','')
					
					if row[1] not in fids:
						row[1] = '-'
					
					pfaction[row[0]] = fids[row[1]]
				
			for row in new_rows:
				if len(row) > 5:
					if len(row) % 2 != 0: continue
				
					for i in range(0, len(row), 2):
						for v in row:
							v.replace(',','')
		
						player_a = row[i]
						player_b = row[i+1]
						
						if player_a in name_subs:
							player_a = name_subs[player_a]
							
						if player_b in name_subs:
							player_b = name_subs[player_b]
						
						if player_a not in elos:
							elos[player_a] = ts.Rating()
							
						if player_b not in elos:
							elos[player_b] = ts.Rating()
							
						elos[player_a],elos[player_b] = ts.rate_1vs1(elos[player_a], elos[player_b])

						if player_a not in player_ids:
							max_pids+=1
							player_ids[player_a] = max_pids
							id_lookup[max_pids] = player_a
							
						if player_b not in player_ids:
							max_pids+=1
							player_ids[player_b] = max_pids
							id_lookup[max_pids] = player_b
						
						try:
							if random.random() > 0.5:
								data_rows.append([player_ids[player_a], pfaction[row[i]], player_ids[player_b], pfaction[row[i+1]], 0])
							else:
								data_rows.append([player_ids[player_b], pfaction[row[i+1]], player_ids[player_a],pfaction[row[i]], 1])
						except:
							pass
						
				else:
					if row[0] == "NEW_EVENT_TAG": continue
					if row[1] == '-': continue
	
	print(len(data_rows))

	output_rows = []
	for i,d in enumerate(data_rows):
		p1id = d[0]
		p1f = d[1]
		p2id = d[2]
		p2f = d[3]
		winner_idx = d[-1]
		
		p1name = id_lookup[p1id]
		p2name = id_lookup[p2id]
		
		if p1name not in elos: elos[p1name] = ts.Rating()
		if p2name not in elos: elos[p2name] = ts.Rating()

		p1elo = elos[p1name]
		p2elo = elos[p2name]

		f1 = fid_lookup[p1f]
		f2 = fid_lookup[p2f]

		if "-" in f1 or "UNKN" in f1 or "-" in f2 or "UNKN" in f2:
			continue

		row = [p1name, f1, p2name, f2, winner_idx]
		output_rows.append(row)

	with open(f'output_data_files/tabletop_matchup_data.json', 'w') as json_file:
		json.dump(output_rows, json_file)
		

if __name__ == '__main__':
		generate_matchup_file()
