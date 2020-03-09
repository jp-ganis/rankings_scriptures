from matplotlib import pyplot as plt
import numpy as np
import statistics
import datetime
import json
	

if __name__ == '__main__':
	with open('output_data_files/all_uk_events/datahub_event_data.json') as json_file:
		edata = json.load(json_file)
	with open('output_data_files/all_uk_events/datahub_faction_data.json') as json_file:
		fdata = json.load(json_file)
		
	x = []
	y = []
		
	for event in edata:
		factions = [e["faction"] for e in event["ladder"] if len(fdata[e["faction"]]["events"]) > 30]
		
		if len(factions) == 0: continue
		
		date = event["std_date"]
		date = date.split()
		date = date[1]+date[2][-2:]
		print(date)
		
		fscores = [fdata[f]["mean_gaussian_score"] for f in factions]
		fmean = statistics.mean(fscores)
		fmedian = statistics.median(fscores)
		
		# plt.scatter(date.timestamp(),fmean,c='r	')
		x.append(date)
		y.append(fmedian)

	x.reverse()
	y.reverse()
	
	N = 50
	cy = np.convolve(y, np.ones((N,))/N, mode='valid')
	plt.xticks(rotation=90)

	plt.plot([x[i] for i,_ in enumerate(cy)],cy)
	plt.show()
		
		