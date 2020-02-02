import numpy as np
import glob
import csv


data_folder = "tablesoup_data"


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
this_faction = 'Flesh Eater Courts'
for f in faction_matchups:
	if this_faction in f[0]:
		l[f[1]] = faction_matchups[f]
		

l = {k: v for k, v in sorted(l.items(), key=lambda item: (item[1][0]/(item[1][0]+item[1][1]), item[1][0]), reverse=True)}

print(this_faction)
for e in l:
	print('\t',end='')
	win = l[e][0]
	loss = l[e][1]
	
	winrate = int((win/(win+loss))*100)
	
	print('{:35} {:3}W {:3}L\t{}%'.format(e, win, loss, winrate))
	
