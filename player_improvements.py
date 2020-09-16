import matplotlib.pyplot as plt 
import numpy as np
from statistics import mean, median
import json

def best_fit_slope_and_intercept(xs,ys):
	xs = np.array(xs)
	ys = np.array(ys)

	m = (((mean(xs)*mean(ys)) - mean(xs*ys)) / ((mean(xs)*mean(xs)) - mean(xs*xs)))

	b = mean(ys) - m*mean(xs)

	return m, b
			

if __name__ == '__main__':
	with open('output_data_files/all_time_data/datahub_player_data.json', newline='') as json_file:
		data = json.load(json_file)
		
		scores = []
		games = []
		ms = {}
		
		for player in data:
			for faction in [e["faction"] for e in data[player]["events"]]:
				events = list(reversed(data[player]["events"]))
				event_scores = [e["gaussian_score"] for e in events if e["faction"] == faction]
				average_event_score = median(event_scores)

				games_played = len(event_scores)
				
				if games_played < 5: continue
				
				print(player,faction,games_played)
				
				scores.append(average_event_score)
				games.append(games_played)
				
		m, b = best_fit_slope_and_intercept(scores, games)
		plt.plot(scores, [m*i+b for i in scores])
		
		plt.scatter(scores, games)
		plt.show()
				
				# m, b = best_fit_slope_and_intercept([i for i in range(len(event_scores))], event_scores)

				# ms[player] = m
			
		# plt.hist(scores, density=True, bins=15)

		# ms = {k: v for k, v in sorted(ms.items(), key=lambda item: item[1], reverse=True)}	

		# for player in ["Liam Watt"]:
			# events = list(reversed(data[player]["events"]))
			# event_scores = [e["gaussian_score"] for e in events]
			# average_event_score = median(event_scores)

			# games_played = len(events)
			
			# if games_played < 5: continue
			
			# scores.append(average_event_score)
			# games.append(games_played)
			
			# m, b = best_fit_slope_and_intercept([i for i in range(len(event_scores))], event_scores)
			
			# plt.scatter([i for i in range(len(event_scores))], event_scores)
			# plt.title(player)
			# plt.plot([i for i in range(len(event_scores))], [m*i+b for i in range(len(event_scores))])
			# plt.show()
