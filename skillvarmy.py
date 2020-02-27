import matplotlib.pyplot as plt
from datetime import datetime
import statistics
import json
import gaussian_fitter as gf
import numpy as np
from scipy.stats import norm
from sklearn.metrics import mean_squared_error
	
def get_player_independent_faction_average(player_name, faction_data, default=None):
	faction_pts = []
	
	for event in faction_data["events"]:
		if event["player_name"] == player_name: continue
		faction_pts.append(event["gaussian_score"])
		
	if len(faction_pts) == 0: return default
	return sum(faction_pts) / len(faction_pts)
	
def get_event_independent_player_average(event, events):
	s = []
	
	for e in events:
		if e["event_name"] == event["event_name"] and e["date"] == event["date"]: continue
		s.append(e["gaussian_score"])
		
	return statistics.mean(s)


if __name__ == '__main__':
	with open('output_data_files/all_time_data/datahub_player_data.json') as json_file:
		pdata = json.load(json_file)
	
	with open('output_data_files/all_time_data/datahub_faction_data.json') as json_file:
		fdata = json.load(json_file)
	
	data_rows = []
	
	for player in pdata:
		if len(pdata[player]["events"]) < 3: continue
		
		average_score = statistics.mean([e["gaussian_score"] for e in pdata[player]["events"]])
		average_faction_score = statistics.mean([get_player_independent_faction_average(player, fdata[event["faction"]],average_score) for event in pdata[player]["events"]])
		
		for event in pdata[player]["events"]:
			escore = get_event_independent_player_average(event, pdata[player]["events"])
			indp_score = average_faction_score##get_player_independent_faction_average(player, fdata[event["faction"]])
			if indp_score is None: indp_score = average_score
			
			data_rows.append([average_score, indp_score, escore])
			
	d = np.array(data_rows)
	
	ax = plt.gca()
	ax.set_facecolor('black')
	
	plt.scatter(d[:,[1]],d[:,[2]],c=(92/255, 61/255, 4/255, 0.8),s=3)
	plt.scatter(d[:,[0]],d[:,[2]],c=(0.3, 0.1, 0.49, 0.8),s=3)
	
	plt.xlabel("player event score")
	plt.ylabel("aggregate faction score (yellow)\nplayer past performance (purple)")
	plt.show()
	
		
		