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
	
	faction_means = {f:[] for f in fdata}
		
	for event in edata:
		date = event["std_date"]
		date = date.split()
		date = date[0]+date[1]+date[2][-2:]
		
		factions = [e["faction"] for e in event["ladder"]]
		
		event_mean = []
		
		for p in event["ladder"]:
			faction_means[p["faction"]].append(p["gaussian_score"])
		
		for f in factions:
			event_mean.append(statistics.mean(faction_means[f]))
		
		fmedian = statistics.median(event_mean)
		# fmedian = statistics.stdev(fscores)
		
		x.append(date)
		y.append(statistics.mean([statistics.mean(faction_means[f]) for f in faction_means if len(faction_means[f]) > 1]))

	x.reverse()
	y.reverse()
	
	## change window to include faction recently rather than faction over all time
	## add vertical lines for book releases
	
	N = 10
	cy = np.convolve(y, np.ones((N,))/N, mode='valid')
	plt.xticks(rotation=90)
	
	
	ticks = [i for i in range(0,len(x)+100,3)]
	plt.xticks(ticks)

	plt.plot([x[i] for i,_ in enumerate(cy)],cy)
	plt.show()