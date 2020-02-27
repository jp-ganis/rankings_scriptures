import matplotlib.pyplot as plt 
import matplotlib
import numpy as np
import random
import csv			
from datetime import datetime
				
def plot_all_factions():
	months = {}
	faction_scores = {}
	faction_counts = {}
	
	tmp_scores = {}
	tmp_counts = {}
	tmp_deltas = {}
	
	faction_deltas = {}
	
	factions = set([])
	
	with open('output_data_files/meta_history.csv') as csvfile:
		readCSV = csv.reader(csvfile, delimiter=',')
		for row in readCSV:
			faction = row[1]
			
			if faction == "UNKNOWN_ARMY": continue
			if "Tzeentch" in faction: faction = "Disciples of Tzeentch"
			if "Skaven" in faction: faction = "Skaven"
			
			factions.add(faction)
			
			month = "XX"
			if '2020' in row[0]:
				month = row[0].replace('2020','20')
			else:
				month = row[0].replace('20','')
				
			if month not in months:
				months[month] = []
				
				tmp_scores[faction] = []
				tmp_counts[faction] = []
				tmp_deltas[faction] = []
				
			
			key = month
			if "17" in key or "16" in key or "15" in key: continue
			if key in ["Jan18","Feb18","Mar18","Apr18"]: continue
				
			months[month].append(faction)
				
			if faction not in faction_scores:
				faction_scores[faction] = {}
				faction_counts[faction] = {}
				faction_deltas[faction] = {}
				
				tmp_scores[faction] = []
				tmp_counts[faction] = []
				tmp_deltas[faction] = []
				
			tmp_scores[faction].append(float(row[2]))
			tmp_counts[faction].append(float(row[3]))
			tmp_deltas[faction].append(float(row[4]))
				
			faction_deltas[faction][month] = float(sum(tmp_deltas[faction]) / len(tmp_deltas[faction])) 
			faction_scores[faction][month] = float(sum(tmp_scores[faction]) / len(tmp_scores[faction])) 
			faction_counts[faction][month] = float(sum(tmp_counts[faction]) / len(tmp_counts[faction]))
			
	
	font = {'size': 5}
	matplotlib.rc('font', **font)


	# relevant = ["Daughters of Khaine","Idoneth Deepkin","Flesh Eater Courts", "Skaventide"]
	# relevant = ["Idoneth Deepkin", "Skaventide", "Flesh Eater Courts", "Hedonites of Slaanesh"]
	
	# rkeys = [k for k in [list(faction_scores[f].keys()) for f in faction_scores]]
	# rkeys = list(set([e for sublist in rkeys for e in sublist]))
	
	# rkeys = [rk for rk in rkeys if all([rk in faction_scores[r] for r in relevant])]
	# rkeys = sorted(rkeys, key=lambda m: datetime.strptime(m, '%b%y'))
	
	
	# for faction in relevant:
		# f = faction_scores[faction]
		# fd = faction_deltas[faction]
		# fc = faction_counts[faction]
		
		# f = {k:v for k,v in sorted(f.items(), key=lambda m: datetime.strptime(m[0], '%b%y'))}
		# fd = {k:v for k,v in sorted(fd.items(), key=lambda m: datetime.strptime(m[0], '%b%y'))}
		# fc = {k:v for k,v in sorted(fc.items(), key=lambda m: datetime.strptime(m[0], '%b%y'))}
	
		# plt.plot(rkeys, [f[rk] for rk in rkeys],label=faction)
		# # plt.plot(list(fc.keys()), list(fc.values()))
		# # plt.plot(list(fd.keys()), list(fd.values()))
		# plt.xlabel("Date")
		# plt.ylabel("Average Event Score")
		# plt.ylim(0,100)
		
	# plt.legend(loc="upper left")
	# plt.show()
	
	all_keys = [k for k in [list(faction_scores[f].keys()) for f in faction_scores]]
	all_keys = list(set([e for sublist in all_keys for e in sublist]))
	all_keys = sorted(all_keys, key=lambda m: datetime.strptime(m, '%b%y'))
	
	month_tops = {k:None for k in all_keys}
	
	print()
	print(f'{"Date":20} {"Top Faction (monthly average)":25}\t{"Second":25}\t{"Third":25}')
	print('-'*120)
	for key in all_keys:
		if "17" in key or "16" in key or "15" in key: continue
		if key in ["Jan18","Feb18","Mar18","Apr18"]: continue
		rfactions = [f for f in faction_scores if key in faction_scores[f] and faction_counts[f][key] > 5]
		rfactions = sorted(rfactions, key=lambda f: faction_scores[f][key], reverse=True)
		
		for r in rfactions:
			if "Deepkin" in r:
				r = bcolors.WARNING + r + bcolors.ENDC

		
		mx = max(rfactions,key=lambda f: faction_scores[f][key])
		
		marker = ""
		if "Deepkin" in mx or "Deepkin" in rfactions[1]: marker = ""
		
		# print(f'{(key+marker):20} {mx:25}{faction_scores[mx][key]}\t\t{rfactions[1]:25}\t\t{rfactions[2]:25}')
		print(f'{(key+marker):20} {mx:25}({int(faction_scores[mx][key])})\t{rfactions[1]:25}({int(faction_scores[rfactions[1]][key])})\t{rfactions[2]:25}({int(faction_scores[rfactions[2]][key])})')
	print()
	
	
	
if __name__ == '__main__':
	plot_all_factions()