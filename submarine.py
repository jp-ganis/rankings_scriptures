from collections import defaultdict
import statistics
import glob
import json
import csv
import random
import numpy as np
from matplotlib import pyplot as plt
	
if __name__ == '__main__':
	data_folder = "input_data_files/tablesoup_data"

	files = glob.glob(f'{data_folder}/*')

	elos = {}

	with open("output_data_files/all_uk_events/datahub_player_data.json", newline='', encoding='utf-8') as json_file:
		pdata = json.load(json_file)
		
	with open("output_data_files/all_uk_events/datahub_faction_data.json", newline='', encoding='utf-8') as json_file:
		fdata = json.load(json_file)
		
	with open("output_data_files/faction_data/faction_matchups.json", newline='', encoding='utf-8') as json_file:
		matchup_data = json.load(json_file)
		
	with open('input_data_files/AoS_list_data.json',encoding='utf-8') as json_file:
		bcp_data = json.load(json_file)
		
	name_subs = {"James Ganis":"Jp Ganis", "Chris Caves Jnr":"Chris Caves Jr"}	
	data_rows = []

	records = defaultdict(list)
	schedules = defaultdict(list)

	for file in files:
		with open(file, newline='', encoding='utf-8') as csvfile:
			reader = csv.reader(csvfile)
			
			pfaction = {}
			
			erecords = defaultdict(list)
			eopps = defaultdict(list)
			
			new_rows = []
			for row in reader:
				new_rows.append(row)
				if len(row) == 3:
					row[1] = row[1].replace('Of','of')
					row[1] = row[1].replace('Ogor ','')
					
					pfaction[row[0]] = row[1]
				
				
			for row in new_rows:
				if len(row) > 5:
					if len(row) % 2 != 0: continue
		
					player = [p for p in row if row.count(p) > 1][0]
					record = []
						
					eopps[player] = [p for p in row if p != player]
						
					for i in range(0, len(row), 2):
						for v in row:
							v.replace(',','')
						
						if row[i] == player:
							record.append("W")
						else:
							record.append("L")	
				
					if len(record) == 5:
						records[player].append(record)
						erecords[player] = record
						
				else:
					if row[0] == "NEW_EVENT_TAG": continue
					if row[1] == '-': continue
			
			if len(erecords) > 1:
				for e in erecords:	
					sos = sum([pdata[q]["gaussian_score"] for q in eopps[e] if q in pdata])
					schedules[e].append(sos)

	normal = []
	sub = []
	
	winrate = {i:[] for i in range(5)}
	
	for p in records:
		if len(schedules[p]) < 1: continue
		
		numWins = records[p][0].count('W')
		
		if numWins != 3: continue
		
		for i,g in enumerate(records[p][0]):
			winrate[i].append(int(g == "W"))
		
		
	for g in winrate:
		print(g,statistics.mean(winrate[g]))
		
	# for player in bcp_data:
		# d = bcp_data[player]
		
		# if "record" not in d: continue
		# if len(d["record"]) != 5: continue
		
		# record = d["record"]
		# records[player].append(record)