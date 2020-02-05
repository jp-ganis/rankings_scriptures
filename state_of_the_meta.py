import matplotlib.pyplot as plt 
import gaussian_calculations
import numpy as np
import statistics
import csv

def load_events():
	events = []
	with open('data_files/events.csv') as csvfile:
		readCSV = csv.reader(csvfile, delimiter=',')
		for row in readCSV:
			if row[0] == "NEW_EVENT_TAG":
				event_name = row[1]
				event_date = row[2]
				event_rounds = row[3]
				
				events.append({})
				events[-1]["name"] = event_name
				events[-1]["date"] = event_date
				events[-1]["rounds"] = event_rounds
				events[-1]["ladder"] = []
				
			else:
				events[-1]["ladder"].append([row[0],row[1]])
	return events


if __name__ == '__main__':
	events = load_events()

	months = {}
	for event in events:
		print(events.index(event), len(events), end='\r')
		month = event["date"].split(" ")
		month = month[1]+month[2]
		
		if month not in months:
			months[month] = {}
		
		scores = gaussian_calculations.get_gaussian_scores_for_event(event)
		for i in range(len(event["ladder"])):
			faction = event["ladder"][i][1]
			score = scores[i]
			
			if faction not in months[month]:
				months[month][faction] = []
				
			months[month][faction].append(score)
			
	print()
	print()
		
	with open('data_files/meta_history.csv', mode='w', newline='') as rankings_file:
		writer = csv.writer(rankings_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

		for m in months:
			for faction in months[m]:
				writer.writerow([m, faction, statistics.median(months[m][faction]), len(months[m][faction])])

			
			
			
			
