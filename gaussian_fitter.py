from scipy import stats
from scipy.stats import norm
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import numpy as np
import statistics
import json

def get_win_distribution(n,rounds=5):
	players = [(p, 0) for p in range(n)]

	for r in range(rounds):
		players = sorted(players, key=lambda p: p[1], reverse=True)
		
		for i in range(0, len(players), 2):
			players[i] = (players[i][0], players[i][1]+1)
			

	players = sorted(players, key=lambda p: p[1], reverse=True)

	results = [{r:len([p for p in players if p[1] == r])} for r in range(rounds+1)]
	wins = [p[1] for p in players]
	# wins = {i: wins.count(i) for i in range(rounds+1)}

	return wins
	
def get_synthetic_wins(placing, num_players, rounds=5):
	win_distribution = get_win_distribution(num_players, rounds)
	
	return win_distribution[placing]

if __name__ == '__main__':
	
	with open("output_data_files/all_time_data/datahub_faction_data.json", newline='', encoding='utf-8') as json_file:
		faction_data = json.load(json_file)
		
	with open("output_data_files/all_time_data/datahub_player_data.json", newline='', encoding='utf-8') as json_file:
		player_data = json.load(json_file)

	pds = []
	fds = []
	norms = []
	cs = []
	ss = []
	ds = []
	
	for player in player_data:
		last_scores = [e["gaussian_score"] for e in player_data[player]["events"]]
		avg_score = statistics.mean(last_scores)
	
		if len(player_data[player]["events"]) < 5: continue
	
		for event in player_data[player]["events"]:
			faction = event["faction"]
			
			player_score = event["gaussian_score"]
			faction_score = faction_data[faction]["mean_gaussian_score"]
			
			pdist = abs(player_score - avg_score)
			fdist = abs(player_score - faction_score)
			
			if pdist == 0 and fdist == 0: continue
			
			l = [pdist, fdist]
			norm = [float(i)/sum(l) for i in l]

			pds.append((player_score - avg_score))
			fds.append((player_score - faction_score))
			
			norms.append(norm[1])
			
			c = 'white'
			s = 2
			
			# if player == "Craig Graham":
				# c = 'red'
				# s = 120
			
			ss.append(s)
			cs.append(c)
			
	plt.rcParams['axes.facecolor'] = 'black'
	plt.axvline(0, color='purple')
	plt.axvline(1, color='yellow')
	plt.axvline(statistics.median(norms), color='r')

	# np.random.shuffle(norms)
			
	# plt.scatter([0 for i in range(len(norms))], [i for i in range(len(norms))], c='white')
	# plt.scatter([1 for i in range(len(norms))], [i for i in range(len(norms))], c='white')
	
	plt.scatter(norms, [i for i in range(len(norms))], s=ss, c=norms)
	
	
	# plt.scatter(pds,[i for i in range(len(pds))])
	# plt.scatter(fds,[i for i in range(len(fds))])
	plt.show()
			
			
			
			
		

