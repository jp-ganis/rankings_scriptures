import matplotlib.pyplot as plt
import numpy as np
import statistics
import csv
import json
import datetime
import gaussian_fitter

if __name__ == '__main__':	

	with open('output_data_files/all_time_data/datahub_event_data.json', newline='') as json_file:
		events = json.load(json_file)

	months = {}
	delta_months = {}
	
	podiums = {}
	faction_cts = {}
	
	for event in events:
		print(events.index(event), len(events), end='\r')
		month = event["date"].split(" ")
		
		if len(month) == 1:
			month = datetime.datetime.strptime(month[0], '%d-%m-%Y').strftime('%b%Y')
			month=str(month)
		else:
			month = month[1]+month[2]
			
		if month not in months:
			months[month] = {}
			delta_months[month] = {}
		
		for i in range(len(event["ladder"])):
			faction = event["ladder"][i]["faction"]
			
			# if faction == "Flesh Eater Courts" and "Feb" in event["date"]:
				# print(event["name"],event["ladder"][i]["player_name"],event["date"])
				
			if faction not in podiums:
				podiums[faction] = []
				faction_cts[faction] = 0
				
			faction_cts[faction] += 1
				
				
			# if faction == "Flesh Eater Courts" and i <= 2 and "2019" in event["date"]:
				# print("FEC",event["name"],event["ladder"][i]["player_name"],event["date"])
				
			# if "Slaanesh" in faction and "2018" in event["date"] and "Feb" in event["date"]:
				# print("Slaanesh",event["name"],i,event["ladder"][i]["player_name"],event["date"])
			
			# score = gaussian_fitter.get_synthetic_wins(i, len(event["ladder"]), int(event["rounds"])) / 5 * 100
			score = event["ladder"][i]["gaussian_score"]
			# score = int(i < 3)
			delta = event["ladder"][i]["metabreakers_score"]
			
			if "2019" in event["date"] or "2020" in event["date"]:
				podiums[faction].append(score/float(event["rounds"]))
			
			if faction not in months[month]:
				months[month][faction] = []
				delta_months[month][faction] = []
				
			months[month][faction].append(score)
			delta_months[month][faction].append(delta)
	print()
	print()
	
	for p in podiums:
		if len(podiums[p]) > 3:
			podiums[p] = statistics.mean(podiums[p])
		else:
			podiums[p] = 0
		
	podiums = {k:v for k,v in sorted(podiums.items(), key=lambda x: x[1], reverse=True)}
	
	# for p in podiums:
		# print(p,int(podiums[p]*100))
		
	# print([e["name"] for e in events])
		
	with open('output_data_files/meta_history.csv', mode='w', newline='') as rankings_file:
		writer = csv.writer(rankings_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

		for m in months:
			for faction in months[m]:
				writer.writerow([m, faction, statistics.mean(months[m][faction]), len(months[m][faction]), statistics.median(delta_months[m][faction])])
				# writer.writerow([m, faction, sum(months[m][faction]), len(months[m][faction]), statistics.median(delta_months[m][faction])])
