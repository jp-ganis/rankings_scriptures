from datetime import datetime
import scipy.stats
import json
import csv

def load_events_csv_file(file, oldest_date_string=None, newest_date_string=None):
	events = []

	event_date = None
	oldest_date = None
	newest_date = None

	if oldest_date_string != None:
		oldest_date = datetime.strptime(oldest_date_string, '%d %b %Y')
		
	if newest_date_string != None:
		newest_date = datetime.strptime(newest_date_string, '%d %b %Y')
	
	with open(file) as csvfile:
		readCSV = csv.reader(csvfile, delimiter=',')
		for row in readCSV:

			if event_date != None:
				if oldest_date_string != None and event_date_object < oldest_date: continue
				if newest_date_string != None and event_date_object > newest_date: continue
		
			if row[0] == "NEW_EVENT_TAG":
				event_name = row[1]
				event_date = row[2]
				event_rounds = row[3]
				
				event_date_object = datetime.strptime(event_date, '%d %b %Y')
				
				if oldest_date_string != None and event_date_object < oldest_date: continue
				if newest_date_string != None and event_date_object > newest_date: continue
				
				events.append({})
				events[-1]["name"] = event_name
				events[-1]["date"] = event_date
				events[-1]["rounds"] = event_rounds
				events[-1]["ladder"] = []
				
			else:
				events[-1]["ladder"].append({"player_name":row[0], "faction":row[1]})
				
	print("Loaded {} events.\n".format(len(events)))
	return events

def load_raw_events_data(folder, oldest_date_string=None, newest_date_string=None):
	events = load_events_csv_file('raw_event_data/events.csv', oldest_date_string, newest_date_string)
	return events

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

def populate_gaussian_scores(event):
	gaussian_scores = get_gaussian_scores_for_event(event)

	for i in range(len(event["ladder"])):
		event["ladder"][i]["placing"] = i+1
		event["ladder"][i]["gaussian_score"] = gaussian_scores[i]
		
	return event
	
def generate_faction_data(events):
	faction_data = {}

	for event in events:
		for entry in event["ladder"]:
			faction = entry["faction"]
			
			if faction not in faction_data:
				faction_data[faction] = {"faction_name":faction, "events":[]}
				
			faction_data[faction]["events"].append({"event_name":event["name"], "player_name":entry["player_name"], "gaussian_score":entry["gaussian_score"]})
			
	for f in faction_data:
		scores = [s["gaussian_score"] for s in faction_data[f]["events"]]
		faction_data[f]["mean_gaussian_score"] = sum(scores)/len(scores)
			
	return faction_data
	
def get_player_independent_faction_average(player_name, faction_data):
	faction_pts = []
	
	for event in faction_data["events"]:
		if event["player_name"] == player_name: continue
		
		faction_pts.append(event["gaussian_score"])
		
	if len(faction_pts) == 0: return None
	return sum(faction_pts) / len(faction_pts)
	
def populate_metabreakers_scores(event, faction_data):
	for entry in event["ladder"]:
		faction = entry["faction"]
		player = entry["player_name"]
		player_score = entry["gaussian_score"]
		
		faction_average = get_player_independent_faction_average(player, faction_data[faction])
		
		if faction_average == None:
			faction_average = player_score
		
		entry["metabreakers_score"] = player_score / faction_average
		
	return event
		
def generate_player_data(events):
	player_data = {}
	
	for event in events:
		for entry in event["ladder"]:
			player_name = entry["player_name"]
		
			if player_name not in player_data:
				player_data[player_name] = {"player_name":player_name, "events":[]}
				
			player_data[player_name]["events"].append({"event_name":event["name"], "faction":entry["faction"], "gaussian_score":entry["gaussian_score"], "metabreakers_score":entry["metabreakers_score"]})
	
	''' scores '''
	for player_name in player_data:
		player_data[player_name]["gaussian_score"] = sum(sorted([e["gaussian_score"] for e in player_data[player_name]["events"]], reverse=True)[:4])
		player_data[player_name]["metabreakers_score"] = sum(sorted([e["metabreakers_score"] for e in player_data[player_name]["events"]], reverse=True)[:3]) / 3


	''' get most played faction '''
	for player_name in player_data:
		data = player_data[player_name]
		played_factions = [e["faction"] for e in data["events"]]
		most_played_faction = max(set(played_factions), key=played_factions.count)
		
		player_data[player_name]["most_played_faction"] = most_played_faction
		
	'''get best scoring factions'''
	for player_name in player_data:
		data = player_data[player_name]
		
		gauss_events = sorted([e for e in player_data[player_name]["events"]], key=lambda e: e["gaussian_score"], reverse=True)[:4]
		metabreakers_events = sorted([e for e in player_data[player_name]["events"]], key=lambda e:e["metabreakers_score"], reverse=True)
		
		scoring_gauss_factions = [e["faction"] for e in gauss_events]
		scoring_mbrs_factions = [e["faction"] for e in metabreakers_events]
		
		most_played_gauss_faction = max(set(scoring_gauss_factions), key=scoring_gauss_factions.count)
		most_played_mbrs_faction = max(set(scoring_mbrs_factions), key=scoring_mbrs_factions.count)
		
		player_data[player_name]["best_scoring_faction"] = most_played_gauss_faction
		player_data[player_name]["best_metabreakers_faction"] = most_played_mbrs_faction
		

	## gaussian rank
	## mars score
	## mars rank
	## mbrs rank
	## best_scoring_faction
	## best_metabreakers_faction
	

		
		
	return player_data

	
if __name__ == '__main__':
	print("Loading events data...")
	events = load_raw_events_data(4, "1 Jan 2019")
	
	print("Calculating gauss scores...")
	events = [populate_gaussian_scores(e) for e in events]
	
	print("Generating faction data...")
	faction_data = generate_faction_data(events)
	
	print("Calculating metabreakers scores...")
	events = [populate_metabreakers_scores(e, faction_data) for e in events]
		
	print("Generating player data...")
	player_data = generate_player_data(events)
	
	player_data = {k: v for k, v in sorted(player_data.items(), key=lambda item: item[1]["gaussian_score"], reverse=True)}	
	
	''' Output json files'''
	with open('data_files/datahub_player_data.json', 'w') as json_file:
		json.dump(player_data, json_file)
		
	with open('data_files/datahub_faction_data.json', 'w') as json_file:
		json.dump(faction_data, json_file)
		
	with open('data_files/datahub_event_data.json', 'w') as json_file:
		json.dump(events, json_file)