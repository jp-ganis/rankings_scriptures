from datetime import datetime
import statistics
import json
import csv


def gaussian_race():
	with open('output_data_files/all_uk_events/datahub_player_data.json') as json_file:
		pdata = json.load(json_file)
	
	with open('output_data_files/all_uk_events/datahub_faction_data.json') as json_file:
		fdata = json.load(json_file)
		
	with open('output_data_files/all_uk_events/datahub_event_data.json') as json_file:
		edata = json.load(json_file)
		
	for e in edata:
		date = e["date"]
		
		if '-' in date:
			date = datetime.strptime(date, '%d-%m-%Y')
		else:
			date = datetime.strptime(date, '%d %b %Y')
		
		e["date"] = date
		
		
	edata = sorted(edata, key=lambda i:i["date"])
	
	data_rows = {k:[0] for k in fdata}
	data_rows2 = {k:[0] for k in fdata}
	
	for i,e in enumerate(edata):
		fscores = {k:[0] for k in fdata}
		
		for p in e["ladder"]:
			fscores[p["faction"]].append(p["gaussian_score"])
	
		for f in fscores:
			fscores[f] = statistics.mean(fscores[f])
			
			if data_rows[f][-1] > 0 and fscores[f] == 0:
				fscores[f] = data_rows[f][-1]
			
			calc_list = [d for d in data_rows[f][-3:]+[fscores[f]] if d > 0]
			
			if len(calc_list) == 0: calc_list = [0]
			
			data_rows[f].append(statistics.mean(calc_list))
			data_rows2[f].append(fscores[f])
			
		# if i > 10: break
			
		
	with open('race.csv', 'w', newline='') as file:
		writer = csv.writer(file)
		
		for f in data_rows:
			writer.writerow([f]+data_rows[f])
	
		

def podium_race():
	with open('output_data_files/all_uk_events/datahub_player_data.json') as json_file:
		pdata = json.load(json_file)
	
	with open('output_data_files/all_uk_events/datahub_faction_data.json') as json_file:
		fdata = json.load(json_file)
		
	with open('output_data_files/all_uk_events/datahub_event_data.json') as json_file:
		edata = json.load(json_file)
		
	for e in edata:
		date = e["date"]
		
		if '-' in date:
			date = datetime.strptime(date, '%d-%m-%Y')
		else:
			date = datetime.strptime(date, '%d %b %Y')
		
		e["date"] = date
		
	edata = sorted(edata, key=lambda i:i["date"])
	
	data_rows = {k:[] for k in fdata}
	fscores = {k:0 for k in fdata}
	fcounts = {k:0 for k in fdata}
	
	for i,e in enumerate(edata):
		for placing,p in enumerate(e["ladder"]):
			thisf = p["faction"]
			if "Slaanesh" in thisf and fcounts["Hedonites of Slaanesh"] > 1: thisf = "Hedonites of Slaanesh"
			if "Skaven" in thisf and fcounts["Skaventide"] > 1: thisf = "Skaventide"
		
			fcounts[thisf] += 1
			if placing < 3:
				fscores[thisf] += 1
	
		for f in fscores:		
			fscores[f] *= 0.95
			fcounts[f] *= 0.95
			fscores[f] = max(0, fscores[f])
			data_rows[f].append(  fscores[f]  )
			
	
	with open('race.csv', 'w', newline='') as file:
		writer = csv.writer(file)
		writer.writerow(["faction"]+[e["date"].strftime('%b %Y') for e in edata])
		for f in data_rows:
			if f == "UNKNOWN_ARMY": continue
			if f == "Hosts of Slaanesh": continue
			writer.writerow([f]+data_rows[f])
	
		
	
	
if __name__ == '__main__':
	podium_race()
		
			
		
	
