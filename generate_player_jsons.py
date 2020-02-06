import gaussian_calculations
import metabreakers_calculations as mbc
import operator
import json
import csv
import re


def get_gaussian_rankings_score_for_player(player_name):
	with open('data_files/gaussian_rankings.json', newline='') as json_file:
		data = json.load(json_file)
		
		ranked_names = {k: v for k, v in sorted(data.items(), key=lambda item: item[1], reverse=True)}
		
		ranked_names = list(ranked_names.keys())
		
		if player_name in data:
			return data[player_name], ranked_names.index(player_name) + 1
	
def get_metabreakers_score_for_player(player_name):
	with open('data_files/metabreaker_rankings.json', newline='') as json_file:
		data = json.load(json_file)
		
		ranked_names = {k: v for k, v in sorted(data.items(), key=lambda item: item[1], reverse=True)}
		
		ranked_names = list(ranked_names.keys())
		
		if player_name in data:
			return data[player_name], ranked_names.index(player_name) + 1
	return 0, 0
	
def get_best_metabreakers_faction_for_player(player_data, player_name, mbc_scores):
	data = player_data[player_name]
	
	faction_scores = {}
	faction_rankings = {}
	metabreakers_scores = {}
	
	for event in data['events']:
		faction = event["faction"]
		pts = event["points"]
		
		faction_average = mbc.get_player_independent_faction_average(player_name, faction, mbc_scores)
		
		if faction_average == None:
			faction_average = pts
		
		if faction not in faction_scores:
			faction_scores[faction] = []
			faction_rankings[faction] = 0
			
		faction_scores[faction].append(pts - faction_average)
		metabreakers_scores[event["event_name"]] = pts - faction_average
	
	for faction in faction_scores:
		faction_rankings[faction] = sum(sorted(faction_scores[faction],reverse=True)[:3])
		
	return max(faction_rankings.items(), key=operator.itemgetter(1))[0], metabreakers_scores
	

def get_best_scoring_faction_for_player(player_data, player_name):
	data = player_data[player_name]
	
	faction_scores = {}
	faction_rankings = {}
	
	for event in data['events']:
		faction = event["faction"]
		pts = event["points"]
		
		if faction not in faction_scores:
			faction_scores[faction] = []
			faction_rankings[faction] = 0
			
		faction_scores[faction].append(pts)
	
	for faction in faction_scores:
		faction_rankings[faction] = sum(sorted(faction_scores[faction],reverse=True)[:3])
		
	return max(faction_rankings.items(), key=operator.itemgetter(1))[0]
		

def get_meta_adjusted_ranking_for_player(player_data, player_name, faction_deltas):
	data = player_data[player_name]
	
	top_x = sorted(data["events"], key=lambda e: e["points"], reverse=True)[:4]
	
	adjusted_score = sum([e["points"] for e in top_x])
	original_score = adjusted_score
	
	for event in top_x:
		faction = event["faction"]
		if faction in faction_deltas:
			faction_delta = faction_deltas[faction]
			adjusted_score += faction_delta
		
	return adjusted_score

def recalculate_gaussian_data():
	gaussian_calculations.generate_data_files()
	
def recalculate_metabreakers_data():
	mbc.generate_data_files()
		
'''
Player data is a json table with one entry per player, containing:

player_name, rankings_score, rankings_rank, most_played_faction, badges,
meta_adjusted_rankings_score, mars_rank, best_scoring_faction, best_metabreakers_faction,
metabreakers_rankings_score, metabreakers_rankings_rank, {{all_event_games}}

'''
if __name__ == '__main__':
	recalculate_gaussian_data()
	recalculate_metabreakers_data()

	events = gaussian_calculations.load_events_data()
	player_data = {}
	
	for event in events:
		print(f'processing event {events.index(event) + 1} out of {len(events)}', end='\r')
		
		scores = gaussian_calculations.get_gaussian_scores_for_event(event)
			
		for i in range(len(event["ladder"])):
			name = event["ladder"][i][0]
			faction = event["ladder"][i][1]
			pts = scores[i]
			
			if name not in player_data:
				player_data[name] = {}
				player_data[name]["events"] = []
				
				
			event_json = {"event_name": event["name"], "faction": faction, "points": pts, "placing":i+1, "num_players":len(event["ladder"])}
			player_data[name]["events"].append(event_json)

	mbc_scores = mbc.load_scores()
	faction_deltas, _ = mbc.get_faction_deltas(mbc_scores)
	
	print()
	print()
	
	meta_adjusted = {}
	for player in player_data:
		meta_adjusted[player] = get_meta_adjusted_ranking_for_player(player_data, player, faction_deltas)
		
	meta_adjusted_ordered = {k: v for k, v in sorted(meta_adjusted.items(), key=lambda item: item[1], reverse=True)}	
	
	idx = 0
	for player in meta_adjusted_ordered:
		idx += 1
	
		player_data[player]["most_played_faction"] = mbc.get_player_most_played_faction(mbc_scores, player)
		player_data[player]["player_name"] = player
		player_data[player]["rankings_score"], player_data[player]["rankings_rank"] = get_gaussian_rankings_score_for_player(player)
		player_data[player]["badges"] = []
		player_data[player]["meta_adjusted_rankings_score"], player_data[player]["meta_adjusted_rankings_rank"] = meta_adjusted_ordered[player], idx
		player_data[player]["metabreakers_rankings_score"], player_data[player]["metabreakers_rankings_rank"] = get_metabreakers_score_for_player(player)
		player_data[player]["best_scoring_faction"] = get_best_scoring_faction_for_player(player_data, player)
		player_data[player]["best_metabreakers_faction"], mbrs_event_scores = get_best_metabreakers_faction_for_player(player_data, player, mbc_scores)
		
		player_data[player]["metabreakers_rankings_score"] *= 100
		
		for e in player_data[player]["events"]:
			e["metabreaker_score"] = mbrs_event_scores[e["event_name"]]


	for d in player_data["James Ganis"]:
		print(d, player_data["James Ganis"][d])
	
	with open('data_files/player_data.json', 'w') as json_file:
		json.dump(player_data, json_file)
		
	with open('metabreakers/data/player_data.json', 'w') as json_file:
		json.dump(player_data, json_file)