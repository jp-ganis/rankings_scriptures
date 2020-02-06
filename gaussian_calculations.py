import scipy.stats
import json
import csv
import re


def get_gaussian_scores_for_event(event):
	scores = []
	
	pts_scaler = 100
	
	c = 3.5
	increment = c / len(event["ladder"])
	
	multiplier = 1
	if event["rounds"] == 3: multiplier = 0.75
	
	for i in range(len(event["ladder"])):
		pts = scipy.stats.norm(0, 2).cdf((c/2) - (increment * (i + 1)))
		pts *= pts_scaler * multiplier
		
		scores.append(pts)
	
	return scores

def load_events_data():
	events = []

	with open('data_files/events.csv') as csvfile:
		readCSV = csv.reader(csvfile, delimiter=',')
		for row in readCSV:
			if row[0] == "NEW_EVENT_TAG":
				event_name = row[1]
				event_date = row[2]
				event_rounds = row[3]
				
				# if "2019" not in event_date and "2020" not in event_date: break
				
				events.append({})
				events[-1]["name"] = event_name
				events[-1]["date"] = event_date
				events[-1]["rounds"] = event_rounds
				events[-1]["ladder"] = []
				
			else:
				events[-1]["ladder"].append([row[0],row[1]])
				
	return events

def generate_data_files():
	events = load_events_data()
				
	rankings = {}
	event_idx = 0

	for event in events:
		event_idx += 1
		scores = get_gaussian_scores_for_event(event)
			
		for i in range(len(event["ladder"])):
			name = event["ladder"][i][0]
			pts = scores[i]
			
			if name not in rankings:
				rankings[name] = []
			
			event["ladder"][i].append(pts)
			rankings[name].append(pts)
		print(f'processing event {event_idx} out of {len(events)}', end='\r')
			
	for name in rankings:
		rankings[name] = sum(sorted(rankings[name], reverse=True)[:4])

	rankings = {k: v for k, v in sorted(rankings.items(), key=lambda item: item[1], reverse=True)}
	
	with open('data_files/gaussian_rankings.json', 'w') as json_file:
		json.dump(rankings, json_file)
		
if __name__ == '__main__':
	generate_data_files()
	