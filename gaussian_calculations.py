import scipy.stats
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


if __name__ == '__main__':
	events = []

	with open('events.csv') as csvfile:
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
				
	rankings = {}
	event_idx = 0
	event_cap = 80

	for event in events:
		if event_idx > event_cap:
			break
		
		event_idx += 1
		scores = get_gaussian_scores_for_event(event)
			
		for i in range(len(event["ladder"])):
			name = event["ladder"][i][0]
			pts = scores[i]
			
			if name not in rankings:
				rankings[name] = []
			
			event["ladder"][i].append(pts)
			rankings[name].append(pts)
		print(f'processing event {event_idx} out of {event_cap}', end='\r')
			
	for name in rankings:
		rankings[name] = sum(sorted(rankings[name], reverse=True)[:4])

	rankings = {k: v for k, v in sorted(rankings.items(), key=lambda item: item[1], reverse=True)}

	with open('gaussian_rankings.csv', mode='w') as rankings_file:
		writer = csv.writer(rankings_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

		i = 0
		for f in rankings:
			i+=1
			rankings_file.write(f'{i},{f},{int(rankings[f])}\n')
			
	with open('gaussian_events.csv', mode='w') as events_file:
		writer = csv.writer(events_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

		for e in events[:event_cap]:
			for p in e["ladder"]:
				events_file.write(f'{p[0]},{p[1]},{e["date"]},{p[2]}\n')