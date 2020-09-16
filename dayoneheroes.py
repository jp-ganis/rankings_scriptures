import statistics
import json
import glob
import csv


if __name__ == '__main__':
	data_folder = "input_data_files/tablesoup_data"

	files = glob.glob(f'{data_folder}/*')
	
	wls = {}
	
	for file in files:
		try:
			with open(file, newline='', encoding='utf-8') as csvfile:
				reader = csv.reader(csvfile)
				
				factions = {}
				
				for row in reader:
					if len(row) == 3:
						for j,v in enumerate(row):
							row[j]=row[j].replace(',','')
							row[j]=row[j].replace("’",'')
							row[j]=row[j].replace("'",'')
							row[j]=row[j].replace("OSiorain",'O')
							if "Regan" in row[j]: row[j] = "Regan Hnnnnng"
							if "Phipps" in row[j]: row[j] = "DP King"
			
						factions[row[0]] = row[1]
						
					elif len(row) > 5:
						if len(row) % 2 != 0: continue
					
						for i in range(0, len(row), 2):
							for j,v in enumerate(row):
								row[j]=row[j].replace(',','')
								row[j]=row[j].replace("’",'')
								row[j]=row[j].replace("'",'')
								row[j]=row[j].replace("OSiorain",'O')
								if "Regan" in row[j]: row[j] = "Regan Hnnnnng"
								if "Phipps" in row[j]: row[j] = "DP King"
			
							player_a = row[i]
							player_b = row[i+1]
							
							mvp = player_a
							if row.count(player_b) > 2:
								mvp = player_b
							
							if factions[player_a] not in wls:
								wls[factions[player_a]] = []
							
							if mvp == player_a:
								wls[factions[mvp]].append(1)
							else:
								wls[factions[mvp]].append(0)
						
						wls[factions[mvp]].append("X")
			
					else:
						if row[0] == "NEW_EVENT_TAG": continue
						if row[1] == '-': continue
		except:
			pass
		
	new_wls = {f:[] for f in wls}
	for f in wls:
		dd = []
		for g in wls[f]:
			if g == "X":
				new_wls[f].append(dd)
				dd = []
			else:
				dd.append(g)
			
	days = {}
	todo_days = {i:[0] for i in range(5)}
	
	for f in new_wls:
		wins = {i:[0] for i in range(5)}
		
		for e in new_wls[f]:
			if len(e) < 5: continue
			
			for i in range(5):
				wins[i].append(e[i])
				todo_days[i].append(e[i])
				
		if f == "-": continue
		days[f] = [int(statistics.mean(wins[i])*100) for i in range(5)]
		
	days = {k:v for k,v in sorted(days.items(), key=lambda u:sum(u[1]), reverse=True)}
	
	todo_days = [int(statistics.mean(todo_days[i])*100) for i in range(5)]
		
	print(todo_days)
		
	for f in days:
		print(f'{f:35}',end=' ')
		for i,g in enumerate(days[f]):
			print(f'{g:3}',end=' ')
		print()
		
	
	for f in days:
		print(f'{f},',end=' ')
		for i,g in enumerate(days[f]):
			print(f'{g},',end=' ')
		print()
			
			
		
