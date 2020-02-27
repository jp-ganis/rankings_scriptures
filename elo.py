import trueskill as ts
import statistics
import json
import glob
import csv


if __name__ == '__main__':
	data_folder = "input_data_files/tablesoup_data"

	files = glob.glob(f'{data_folder}/*')

	elos = {}

	with open("output_data_files/all_time_data/datahub_player_data.json", newline='', encoding='utf-8') as json_file:
		player_data = json.load(json_file)
		
	name_subs = {"James Ganis":"Jp Ganis", "Chris Caves Jnr":"Chris Caves Jr"}	
	
	for file in files:
		with open(file, newline='', encoding='utf-8') as csvfile:
			reader = csv.reader(csvfile)
			
			for row in reader:
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
						
				else:
					if row[0] == "NEW_EVENT_TAG": continue
					if row[1] == '-': continue
		
	for e in elos:
		elos[e] = elos[e].mu - elos[e].sigma**2
		elos[e] = int(elos[e]*100)
		
	elos = {k: v for k, v in sorted(elos.items(), key=lambda item: item[1], reverse=True)}	
	
	
	i = 0
	for e in elos:
		if e not in player_data: continue
		i+=1
		print(i,e,elos[e])
		# print("{:15} {:35}".format(i, e), elos[e])