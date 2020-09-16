from scipy import stats
from scipy.stats import norm
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import numpy as np
import statistics
import json
import scipy.optimize
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns


def get_win_distribution(n,rounds=5):
	players = [(p, 0) for p in range(n)]

	for r in range(rounds):
		players = sorted(players, key=lambda p: p[1], reverse=True)
		
		for i in range(0, len(players), 2):
			players[i] = (players[i][0], players[i][1]+1)
			

	players = sorted(players, key=lambda p: p[1], reverse=True)

	results = [{r:len([p for p in players if p[1] == r])} for r in range(rounds+1)]
	wins = [p[1] for p in players]

	return wins

if __name__ == '__main__':
	
	with open("output_data_files/all_events/datahub_faction_data.json", newline='', encoding='utf-8') as json_file:
		fdata = json.load(json_file)
		
	with open("output_data_files/all_events/datahub_player_data.json", newline='', encoding='utf-8') as json_file:
		pdata = json.load(json_file)
		
	with open("output_data_files/all_events/datahub_event_data.json", newline='', encoding='utf-8') as json_file:
		edata = json.load(json_file)


		
		
	# wins = get_win_distribution(32)
	# wins = [5,5,4,4,4,4,4,4,4,4,4,4,4,4,4,4,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,2,0,0,0,0,0]
	# sns.distplot(wins, hist=True, kde=True, bins=6, color = 'darkblue', hist_kws={'edgecolor':'black'},kde_kws={'linewidth': 4})
	
	# plt.xlabel("Number of Wins")
	# plt.ylabel("Probability Density Function")
	# plt.show()
