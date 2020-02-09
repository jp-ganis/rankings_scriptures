import numpy as np
import json
import glob
import csv
import sys



if __name__ == '__main__':
	data_folder = "input_data_files/tablesoup_data"
	output_file = "output_data_files/faction_data/faction_matchups.json"

	files = glob.glob(f'{data_folder}/*')

	faction_matchups = {}

	for file in files:
		with open(file, newline='', encoding='utf-8') as csvfile:
			reader = csv.reader(csvfile)
			player_factions = {}
			
			for row in reader:
				if len(row) > 5:
					for i in range(0, len(row), 2):
						if row[i] not in player_factions or row[i+1] not in player_factions: continue
					
						faction_a = player_factions[row[i]]
						faction_b = player_factions[row[i + 1]]
						
						if (faction_a,faction_b) not in faction_matchups:
							faction_matchups[(faction_a,faction_b)] = np.array([0,0])
							faction_matchups[(faction_b,faction_a)] = np.array([0,0])
						
						faction_matchups[(faction_a,faction_b)] += [1,0]
						faction_matchups[(faction_b,faction_a)] += [0,1]
						
						
				else:
					if row[0] == "NEW_EVENT_TAG": continue
					if row[1] == '-': continue
					
					name = row[0].replace('\t', ' ')
					player_factions[name] = row[1]
	
	l = {}
	
	for pair in faction_matchups:
		faction = pair[0]
		
		if faction in l: continue
		
		l[faction] = {"faction_name": faction}
		l[faction]["matchups"] = {}
		
		for pair in faction_matchups:
			if faction == pair[0]:
				l[faction]["matchups"][pair[1]] = {"Wins":int(faction_matchups[pair][0]), "Losses":int(faction_matchups[pair][1])}
	
	with open(output_file, 'w') as json_file:
		json.dump(l, json_file)
		
	for army in l["Flesh Eater Courts"]["matchups"]:
		print(army, l["Flesh Eater Courts"]["matchups"][army])
