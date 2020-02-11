from datetime import datetime
import scipy.stats
import shutil
import glob
import json
import sys
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
	
	with open(file, encoding='utf-8') as csvfile:
		readCSV = csv.reader(csvfile, delimiter=',')

		for row in readCSV:
			if event_date != None:
				if oldest_date_string != None and event_date_object < oldest_date: continue
				if newest_date_string != None and event_date_object > newest_date: continue
		
			if row[0] == "NEW_EVENT_TAG":
				event_name = row[1]
				event_date = row[2]
				event_rounds = row[3]
				
				event_date_object = None
				
				if '-' in event_date:
					event_date_object = datetime.strptime(event_date, '%d-%m-%Y')
				else:
					event_date_object = datetime.strptime(event_date, '%d %b %Y')
				
				if oldest_date_string != None and event_date_object < oldest_date: continue
				if newest_date_string != None and event_date_object > newest_date: continue
				
				events.append({})
				events[-1]["name"] = event_name
				events[-1]["date"] = event_date
				events[-1]["rounds"] = event_rounds
				events[-1]["ladder"] = []
				
			else:
				if len(row) > 3: continue
				
				## Known Aliases
				if row[0] == "James Ganis": row[0] = "Jp Ganis"
				elif row[0] == "Liam Watts": row[0] = "Liam Watt"
				elif row[0] == "Rich Hudspith": row[0] = "Richard Hudspith"
				
				row[1] = row[1].replace('Of', 'of')
				##
				
				events[-1]["ladder"].append({"player_name":row[0], "faction":row[1]})
	
	events = [e for e in events if len(e["ladder"]) > 6]
	
	return events

def load_raw_events_data(folder, oldest_date_string=None, newest_date_string=None):
	files = glob.glob(f'{folder}/*')
	events = []
	
	for f in files:
		events += load_events_csv_file(f, oldest_date_string, newest_date_string)
		
	print("Loaded {} events.\n".format(len(events)))
	return events

def get_gaussian_scores_for_event(event):
	scores = []
	
	pts_scaler = 100
	
	c = 3.5
	increment = c / len(event["ladder"])
	
	multiplier = 1
	if int(event["rounds"]) == 3: multiplier = 0.75
	
	for i in range(len(event["ladder"])):
		pts = scipy.stats.norm(0, 1).cdf((c/2) - (increment * (i + 1)))
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
			
	faction_data = {k: v for k, v in sorted(faction_data.items(), key=lambda item: item[1]["mean_gaussian_score"], reverse=True)}	
	
	rank = 0
	for f in faction_data:
		rank += 1
		faction_data[f]["gaussian_rank"] = rank
		
		faction_data[f]["faction_player_scores"] = {}
		
		for event in faction_data[f]["events"]:
			if event["player_name"] not in faction_data[f]["faction_player_scores"]:
				faction_data[f]["faction_player_scores"][event["player_name"]] = []
			
			faction_data[f]["faction_player_scores"][event["player_name"]].append(event["gaussian_score"])
			faction_data[f]["faction_player_scores"][event["player_name"]].sort(reverse=True)
			faction_data[f]["faction_player_scores"][event["player_name"]] = faction_data[f]["faction_player_scores"][event["player_name"]][:3]
			
		for player in faction_data[f]["faction_player_scores"]:
			faction_data[f]["faction_player_scores"][player] = sum(faction_data[f]["faction_player_scores"][player])
		
		faction_data[f]["faction_player_scores"] = {k: v for k, v in sorted(faction_data[f]["faction_player_scores"].items(), key=lambda item: item[1], reverse=True)}	
	
		
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
		
		entry["metabreakers_score"] = min(player_score / faction_average, 3.0) ## capped
		
	return event
		
def generate_player_data(events):
	player_data = {}
	
	for event in events:
		rank = 0
		for entry in event["ladder"]:
			rank += 1
			player_name = entry["player_name"]
		
			if player_name not in player_data:
				player_data[player_name] = {"player_name":player_name, "events":[]}
				
			player_data[player_name]["events"].append({"event_name":event["name"], "faction":entry["faction"], "gaussian_score":entry["gaussian_score"], \
			"metabreakers_score":entry["metabreakers_score"], "placing": rank, "num_players":len(event["ladder"])})
	
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
		metabreakers_events = sorted([e for e in player_data[player_name]["events"]], key=lambda e:e["metabreakers_score"], reverse=True)[:3]
		
		scoring_gauss_factions = [e["faction"] for e in gauss_events]
		scoring_mbrs_factions = [e["faction"] for e in metabreakers_events]
		
		most_played_gauss_faction = max(set(scoring_gauss_factions), key=scoring_gauss_factions.count)
		most_played_mbrs_faction = metabreakers_events[0]["faction"]
		
		player_data[player_name]["best_scoring_faction"] = most_played_gauss_faction
		player_data[player_name]["best_metabreakers_faction"] = most_played_mbrs_faction
		
	gauss_ordered = {k: v for k, v in sorted(player_data.items(), key=lambda item: item[1]["gaussian_score"], reverse=True)}	
	mbrs_ordered = {k: v for k, v in sorted(player_data.items(), key=lambda item: item[1]["metabreakers_score"], reverse=True)}	

	idx = 0
	for player in gauss_ordered:
		idx += 1
		player_data[player]["gaussian_rank"] = idx
		
	idx = 0
	for player in mbrs_ordered:
		idx += 1
		player_data[player]["metabreakers_rank"] = idx
		
	return player_data

	
if __name__ == '__main__':
	update_specs = {}
	update_specs["northern_rankings"] = {"input_folder": "input_data_files/northern_events", "output_folder": "output_data_files/northern_events", "cutoff_date": "1 Jan 2020" }
	update_specs["uk_rankings"] = {"input_folder": "input_data_files/uk_events", "output_folder": "output_data_files/uk_events", "cutoff_date": "1 Jan 2019" }
	
	update_specs["northern_rankings"]["metabreakers_folder"] = "metabreakers/data/northern_events"
	update_specs["uk_rankings"]["metabreakers_folder"] = "metabreakers/data/uk_events"
	
	for rankings in update_specs:
		input_folder = update_specs[rankings]["input_folder"]
		output_folder = update_specs[rankings]["output_folder"]
		cutoff_date =  update_specs[rankings]["cutoff_date"]
		
		print(f'\nProcessing {rankings}...')
		
		print("\nLoading events data...")
		events = load_raw_events_data(input_folder, cutoff_date)
		
		print("\nCalculating gauss scores...")
		events = [populate_gaussian_scores(e) for e in events]
		
		print("\nGenerating faction data...")
		faction_data = generate_faction_data(events)
		
		print("\nCalculating metabreakers scores...")
		events = [populate_metabreakers_scores(e, faction_data) for e in events]
			
		print("\nGenerating player data...")
		player_data = generate_player_data(events)
		
		player_data = {k: v for k, v in sorted(player_data.items(), key=lambda item: item[1]["gaussian_score"], reverse=True)}	
		
		''' Output json files'''
		with open(f'{output_folder}/datahub_player_data.json', 'w') as json_file:
			json.dump(player_data, json_file)
			
		with open(f'{output_folder}/datahub_faction_data.json', 'w') as json_file:
			json.dump(faction_data, json_file)
			
		with open(f'{output_folder}/datahub_event_data.json', 'w') as json_file:
			json.dump(events, json_file)
			
		with open(f'{output_folder}/datahub_metabreakers_data.json', 'w') as json_file:
			mbrs_sorted = {k: v for k, v in sorted(player_data.items(), key=lambda item: item[1]["metabreakers_score"], reverse=True)}	
			json.dump(mbrs_sorted, json_file)
			
		print("\nUploading to metabreakers folder...")
		files_to_move = glob.glob(f'{output_folder}/*')
	
		file_locations = {}
		
		for nf in files_to_move:
			file_locations[nf] = update_specs[rankings]["metabreakers_folder"]
			
		for file in file_locations:
			shutil.copy(file, file_locations[file])