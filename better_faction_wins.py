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
from better_player_wins import get_player_elos

def get_faction_elos():
	data_folder = "input_data_files/tablesoup_data"
	ss = 0

	files = glob.glob(f'{data_folder}/*')

	elos = {}
		
	with open("output_data_files/all_uk_events/datahub_faction_data.json", newline='', encoding='utf-8') as json_file:
		f_data = json.load(json_file)
	
	fids = {f:i for i,f in enumerate(f_data)}
	
	fid_lookup = {i:f for i,f in enumerate(f_data)}
	
	fids['-'] = -1
	fid_lookup[-1] = '-'

	fids['UNKNOWN_ARMY'] = -1

	fc={}
	fw={}

	date_brackets = [[dp.parse('08-Jul-2019'), dp.parse('31-Dec-2019')],[dp.parse('01-Jan-2020'), dp.parse('08-Jul-2020')]]
	date_brackets = [date_brackets[1]]

	pelos = get_player_elos()
	pelos = {k:v for k,v in sorted(pelos.items(), key=lambda i: i[1].mu, reverse=True)}
	pelos = list(pelos.keys())[:20]

	for cutoff_dates in date_brackets:
		print(cutoff_dates)
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

							try:
								if any(["Tinsdale" in e for e in row]): continue
								player_a = pfaction[row[i]]
								player_b = pfaction[row[i+1]]
							except:
								continue
							
							if player_a == -1 or player_b == -1:
								continue

							if player_a not in fc:
								fc[player_a] = 0
								fw[player_a] = 0
							if player_b not in fc:
								fc[player_b] = 0
								fw[player_b] = 0

							fc[player_a]+=1
							fc[player_b]+=1

							fw[player_a]+=1

							if player_a not in elos:
								elos[player_a] = ts.Rating()
								
							if player_b not in elos:
								elos[player_b] = ts.Rating()
								
							elos[player_a],elos[player_b] = ts.rate_1vs1(elos[player_a], elos[player_b])
							ss+=1
							
					else:
						if row[0] == "NEW_EVENT_TAG": continue
						if row[1] == '-': continue
			
		elos = {k:v for k,v in sorted(elos.items(),key=lambda i: i[1].mu, reverse=True)}
		for f in elos:
			#if fc[f] < 40: continue
			print(f'{fid_lookup[f]:35} {int(elos[f].mu**2*10/2)}\t{int(elos[f].sigma**2*10/2)}\t{int(fw[f]/fc[f]*100)}%')

		print(ss)
		elos = {fid_lookup[k]:v for k,v in elos.items()}
		return elos
		#fw = {k:v for k,v in sorted(fw.items(),key=lambda i: i[1]/fc[i[0]], reverse=True)}
		#for f in fw:
		#	print(f'{fid_lookup[f]:35} {int(fw[f]/fc[f]*100)}%')

if __name__ == '__main__':
	get_faction_elos()
