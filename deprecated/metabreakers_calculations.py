import scipy.stats
import operator
import json

def load_scores():
	scores = {}

	with open('data_files/gaussian_events.csv', newline='') as csvfile:
		data = json.load(csvfile, delimiter=',', quotechar='|')
		for row in spamreader:
			if len(row) > 0:
				name = row[0]
				
				if name not in scores:
					scores[name] = []
					
				scores[name].append(row[1:])
	return scores

def average_faction_points(scores):
	faction_pts = {}
	faction_cts = {}

	for s in scores:
		for e in scores[s]:
			if e[1] not in faction_pts:
				faction_pts[e[0]] = 0
				faction_cts[e[0]] = 0
				
			faction_pts[e[0]] += float(e[2])
			faction_cts[e[0]] += 1
		
	for f in faction_pts:
		faction_pts[f] /= faction_cts[f]
	
	ordered = {k: v for k, v in sorted(faction_pts.items(), key=lambda item: item[1], reverse=True)}	
	return ordered
		
				
def get_player_independent_faction_average(player_id, faction, scores):
	faction_pts = 0
	faction_cts = 0
	
	player_pts = 0
	player_cts = 0

	for p_id in scores:
		if p_id == player_id: continue
		
		for result in scores[p_id]:
			if result[0] == faction:
				faction_pts += float(result[2])
				faction_cts += 1
		
	if faction_cts == 0: return None
	return faction_pts/faction_cts

def get_faction_deltas(scores):
	faction_deltas = {}
	faction_cts = {}
		
	for player_id in scores:
		player_average = sum([float(r[2]) for r in scores[player_id]])/len(scores[player_id])
	
		for s in scores[player_id]:
			faction = s[0]
			
			faction_average = get_player_independent_faction_average(player_id, faction, scores)
			
			if faction_average == None: continue
			
			delta = faction_average - player_average
			
			if faction not in faction_deltas:
				faction_deltas[faction] = 0
				faction_cts[faction] = 0
				
			faction_deltas[faction] += delta
			faction_cts[faction] += 1
		
	for f in faction_deltas:
		faction_deltas[f] /= faction_cts[f]
		
	ordered = {k: v for k, v in sorted(faction_deltas.items(), key=lambda item: item[1], reverse=True)}	
	return ordered, faction_cts
	
def get_player_deltas(scores):
	player_deltas = {}
	
	for player_id in scores:
		player_deltas[player_id]  = get_player_metabreaker_score(player_id, scores)
		
	ordered = {k: v for k, v in sorted(player_deltas.items(), key=lambda item: item[1], reverse=True)}	
	
	return ordered	
	
def get_player_metabreaker_score(player_id, scores):
	metabreakers_scores = []
	
	for event in scores[player_id]:
		faction = event[0]
		pts = float(event[2])
		
		faction_average = get_player_independent_faction_average(player_id, faction, scores)
		
		if faction_average == None:
			faction_average = pts
			
		metabreakers_scores.append(pts / faction_average)
		
	top_x_events = 5	
	return sum(sorted(metabreakers_scores,reverse=True)[:top_x_events]) / top_x_events
	
def get_player_most_played_faction(scores, player_id):
	faction_cts = {}

	for result in scores[player_id]:
		faction = result[0]
		
		if faction not in faction_cts:
			faction_cts[faction] = 0
			
		faction_cts[faction] += 1
		
	return  max(faction_cts.items(), key=operator.itemgetter(1))[0]
	
			
def generate_data_files():
	scores = load_scores()

	#########################
	## output player data
	#########################
	player_deltas = get_player_deltas(scores)
	
	with open('data_files/metabreaker_rankings.json', 'w') as json_file:
		json.dump(player_deltas, json_file)

	#########################
	## output faction data
	#########################
	faction_points = average_faction_points(scores)
	faction_deltas,faction_counts = get_faction_deltas(scores)
	
	faction_json = {}
	
	for f in faction_deltas:
		faction_json[f] = {"deltas":faction_deltas[f], "scores":faction_points[f], "counts":faction_counts[f]}
	
	with open('data_files/metabreakers_faction_data.json', 'w') as json_file:
		json.dump(faction_json, json_file)
		
		
if __name__ == '__main__':
	generate_data_files()