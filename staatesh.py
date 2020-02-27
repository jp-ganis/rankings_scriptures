import matplotlib.pyplot as plt
from datetime import datetime
import statistics
import json
import gaussian_fitter as gf
import numpy as np
from scipy.stats import norm
from sklearn.metrics import mean_squared_error


if __name__ == '__main__':
	with open('output_data_files/all_time_data/datahub_player_data.json') as json_file:
		pdata = json.load(json_file)
	
	with open('output_data_files/all_time_data/datahub_faction_data.json') as json_file:
		fdata = json.load(json_file)
	
	rfaction = "Hedonites of Slaanesh"
	
	hos_players = list(set([event["player_name"] for event in fdata[rfaction]["events"]]))
	if "Player" in hos_players: hos_players.remove("Player")
		
	data = {k:{"sl":[], "nsl":[]} for k in hos_players}
	
	metric = "gaussian_score"
	
	for player in hos_players:
		for event in pdata[player]["events"]:
			if event["faction"] != rfaction:
				data[player]["nsl"].append(event[metric])
				# data[player]["nsl"].append(gf.get_synthetic_wins(event["placing"]-1, event["num_players"]))
			else:
				data[player]["sl"].append(event[metric])
				# data[player]["sl"].append(gf.get_synthetic_wins(event["placing"]-1, event["num_players"]))
				
	data = {k:v for k,v in sorted(data.items(), key = lambda i: i[1]["sl"], reverse=True)}
			
	x = []
	y = []
		
	for i,p in enumerate(data):
		if len(data[p]["nsl"]) < 1 or len(data[p]["sl"]) < 1: continue
		if len(pdata[p]["events"]) < 5: continue
		
		sl_mean = statistics.mean(data[p]["sl"])
		nsl_mean = statistics.mean(data[p]["nsl"])
		
		x.append(sl_mean)
		y.append(nsl_mean)
		
		print(f'{p:25} {sl_mean:5.0f} {nsl_mean:5.0f} {sl_mean - nsl_mean:5.0f}')
	
	x=np.array(x)
	y=np.array(y)
	z = x-y
	
	msl,ssl = statistics.mean(x),statistics.stdev(x)
	mnsl,snsl = statistics.mean(y),statistics.stdev(y)
	
	gauss_x = np.arange(-50, 200, 0.1)
	gauss_y = norm.pdf(gauss_x,msl,ssl)
	gauss_y2 = norm.pdf(gauss_x,mnsl,snsl)
	
	# plt.plot(gauss_x,gauss_y,label="Playing Slaanesh",c="magenta")
	# plt.plot(gauss_x,gauss_y2,label="Not Playing Slaanesh",c="black")

	print(statistics.mean(z))
	
	plt.axvline(x=fdata[rfaction]["mean_gaussian_score"],c="magenta",label=f'Faction Average')
	# plt.axvline(x=mnsl,c=(0.1,0.1,0.1,0.1))
	
	print(msl, mnsl)

	y_pred1 = x
	y_pred2 = y
	print(x)
	print(y)
	y_true = [fdata[rfaction]["mean_gaussian_score"] for _ in x]
	print(f'faction mse: {mean_squared_error(y_true, y_pred1)**0.5}')
	print(f'player mse: {mean_squared_error(y_true, y_pred2)**0.5}')
	
	
	plt.scatter(x,y)
	plt.plot([i for i in range(100)],[i for i in range(100)],label="Player Average")
	# plt.plot(np.unique(x), np.poly1d(np.polyfit(x, y, 1))(np.unique(x)))
	plt.xlabel(f'score playing {rfaction}')
	plt.ylabel("score playing other armies")
	plt.legend(loc="upper right")
	plt.show()
			

