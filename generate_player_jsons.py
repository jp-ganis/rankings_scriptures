import gaussian_calculations
import metabreakers_calculations as mbc
import operator
import csv
import re


def get_gaussian_rankings_score_for_player(player_name):
	with open('gaussian_rankings.csv', newline='') as csvfile:
		reader = csv.reader(csvfile, delimiter=',', quotechar='|')
		for row in reader:
			if row[1] == player_name:
				return row[2], row[0]
	
def get_metabreakers_score_for_player(player_name):
	with open('metabreaker_rankings.csv', newline='') as csvfile:
		reader = csv.reader(csvfile, delimiter=',', quotechar='|')
		for row in reader:
			if row[1] == player_name:
				return row[3], row[0]
	return 0, 0
	
def get_best_metabreakers_faction_for_player(player_data, player_name, mbc_scores):
	data = player_data[player_name]
	
	faction_scores = {}
	faction_rankings = {}
	
	for event in data['events']:
		faction = event[1]
		pts = event[2]
		
		faction_average = mbc.get_player_independent_faction_average(player_name, faction, mbc_scores)
		
		if faction_average == None:
			faction_average = pts
		
		if faction not in faction_scores:
			faction_scores[faction] = []
			faction_rankings[faction] = 0
			
		faction_scores[faction].append(pts - faction_average)
	
	for faction in faction_scores:
		faction_rankings[faction] = sum(sorted(faction_scores[faction],reverse=True)[:3])
		
	return max(faction_rankings.items(), key=operator.itemgetter(1))[0]
	

def get_best_scoring_faction_for_player(player_data, player_name):
	data = player_data[player_name]
	
	faction_scores = {}
	faction_rankings = {}
	
	for event in data['events']:
		faction = event[1]
		pts = event[2]
		
		if faction not in faction_scores:
			faction_scores[faction] = []
			faction_rankings[faction] = 0
			
		faction_scores[faction].append(pts)
	
	for faction in faction_scores:
		faction_rankings[faction] = sum(sorted(faction_scores[faction],reverse=True)[:3])
		
	return max(faction_rankings.items(), key=operator.itemgetter(1))[0]
			
		

'''
Player data is a json table with one entry per player, containing:

player_name, rankings_score, rankings_rank, most_played_faction, badges,
meta_adjusted_rankings_score, mars_rank, best_scoring_faction, best_metabreakers_faction,
metabreakers_rankings_score, metabreakers_rankings_rank, {{all_event_games}}

'''
if __name__ == '__main__':
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
				
			player_data[name]["events"].append([event["name"], faction, pts, i+1, len(event["ladder"])])
	print()
	print()
	
	
	faction_data = {}
	with open('faction_data.csv', newline='') as csvfile:
		reader = csv.reader(csvfile, delimiter=',', quotechar='|')
		for row in reader:
			faction_data[row[0]] = [row[1], row[2]]
	
	mbc_scores = mbc.load_scores()
	for player in player_data:
		player_data[player]["most_played_faction"] = mbc.get_player_most_played_faction(mbc_scores, player)
		player_data[player]["player_name"] = player
		player_data[player]["rankings_score"], player_data[player]["rankings_rank"] = get_gaussian_rankings_score_for_player(player)
		player_data[player]["badges"] = []
		player_data[player]["meta_adjusted_rankings_score"], player_data[player]["meta_adjusted_rankings_rank"] = 0, 0
		player_data[player]["metabreakers_rankings_score"], player_data[player]["metabreakers_rankings_rank"] = get_metabreakers_score_for_player(player)
		player_data[player]["best_scoring_faction"] = get_best_scoring_faction_for_player(player_data, player)
		player_data[player]["best_metabreakers_faction"] = get_best_metabreakers_faction_for_player(player_data, player, mbc_scores)

	
	
	print(player_data["James Ganis"])