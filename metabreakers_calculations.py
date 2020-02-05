from datetime import datetime
import operator
import csv

## cutoff_date is furthest back in time we go, reverse_cutoff means its the further into the future we go
def load_scores(cutoff_date_string=None, reverse_cutoff=False):
	scores = {}

	with open('data_files/gaussian_events.csv', newline='') as csvfile:
		reader = csv.reader(csvfile, delimiter=',', quotechar='|')
		for row in reader:
			if len(row) > 0:
				if cutoff_date_string != None:
					date_string = row[2]
					date = datetime.strptime(date_string, '%d %b %Y')
					cutoff_date = datetime.strptime(cutoff_date_string, '%d %b %Y')

					if reverse_cutoff and date > cutoff_date: continue
					elif not reverse_cutoff and date < cutoff_date: continue
					
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
		if len(scores[player_id]) < 3: continue
		factions = [r[0] for r in scores[player_id]]
		faction_sum = 0
		
		for f in factions:
			f_mean = get_player_independent_faction_average(player_id, f, scores)
			if f_mean != None:
				faction_sum += f_mean
		
		faction_average = faction_sum / len(factions)
		
		player_average = sum([float(r[2]) for r in scores[player_id]])/len(scores[player_id])

		player_deltas[player_id] = player_average - faction_average
		
	
	ordered = {k: v for k, v in sorted(player_deltas.items(), key=lambda item: item[1], reverse=True)}	
	return ordered	
	
def get_player_most_played_faction(scores, player_id):
	faction_cts = {}

	for result in scores[player_id]:
		faction = result[0]
		
		if faction not in faction_cts:
			faction_cts[faction] = 0
			
		faction_cts[faction] += 1
		
	return  max(faction_cts.items(), key=operator.itemgetter(1))[0]
	
			
if __name__ == '__main__':
	scores = load_scores()
	
	o = average_faction_points(scores)
	for e in o:
		print("{:35} {}".format(e,o[e]))
	
	print()
	print()
	
	o, _= get_faction_deltas(scores)
	
	for e in o:
		print("{:35} {:.1f}".format(e,o[e]))
		
	#########################
	## output player data
	#########################
	player_deltas = get_player_deltas(scores)
	csv_file = open("data_files/metabreaker_rankings.csv", "w")
	rank = 0
	for f in player_deltas:
		rank += 1
		delta = "+"
		if player_deltas[f] < 0: delta = ""
		faction = get_player_most_played_faction(scores, f)
		
		csv_file.write('{},{},{},{}{:.1f}\n'.format(rank, f, faction, delta, player_deltas[f]))
	csv_file.close()
	
	#########################
	## output faction data
	#########################
	faction_points = average_faction_points(scores)
	faction_deltas, faction_cts = get_faction_deltas(scores)
	csv_file = open("data_files/faction_data.csv", "w")
	for f in faction_deltas:
		csv_file.write('{},{:.1f},{:.1f}\n'.format(f, faction_points[f], faction_deltas[f]))
	csv_file.close()