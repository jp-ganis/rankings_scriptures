from matplotlib import pyplot as plt
from collections import defaultdict
import matplotlib.dates as md
import numpy as np
import statistics
import datetime
import random
import json
import csv
	
def no_faction_resets():
	with open('output_data_files/all_uk_events/datahub_event_data.json') as json_file:
		edata = json.load(json_file)
	with open('output_data_files/all_uk_events/datahub_faction_data.json') as json_file:
		fdata = json.load(json_file)
		
	release_dict = {}
	with open('input_data_files/book_releases.csv', mode='r') as infile:
		reader = csv.reader(infile)
		for row in reader:
			release_dict[row[0].title()] = datetime.datetime.strptime(row[1].strip(), '%d %b %Y')
			
	x = []
	y = []
	
	faction_means = {f:[] for f in fdata}
	event_means = []
	tops = []
	bottoms = []
		
	for event in edata:
		date = event["std_date"]
		t = datetime.datetime.strptime(date, '%d %b %Y')
		date = date.split()
		date = date[0]+date[1]+date[2][-2:]
		
		factions = [e["faction"] for e in event["ladder"]]
		
		event_mean = []
		
		for p in event["ladder"]:
			faction_means[p["faction"]].append(p["gaussian_score"])
		
		for f in factions:
			event_mean.append(statistics.mean(faction_means[f]))
		
		event_means.append(statistics.mean(event_mean))
		
		fmedian = statistics.median(event_mean)
		# fmedian = statistics.stdev(fscores)
		
		x.append(t.timestamp())
		y.append(statistics.mean(event_mean))
		tops.append(np.percentile(event_mean, 15))
		bottoms.append(np.percentile(event_mean, 85))
		# x.append(date)

	x.reverse()
	y.reverse()
	tops.reverse()
	bottoms.reverse()
	
	for d in release_dict:
		plt.axvline(release_dict[d].timestamp(),c=list(np.random.choice([i/20 for i in range(20)], size=3)),label=d)
		plt.text(release_dict[d].timestamp() + 0.1, 0, d, rotation=90)
	
	with open('event_pc.csv', 'w', newline='') as file:
		writer = csv.writer(file)
		
		for i,e in enumerate(x):
			writer.writerow([datetime.datetime.strftime(datetime.datetime.fromtimestamp(e), '%d %b %Y'),y[i],tops[i],bottoms[i]])

	
def get_window_scores(edata):
	faction_scores = defaultdict(list)
	
	for event in edata:
		for e in event["ladder"]:
			faction_scores[e["faction"]].append(e["gaussian_score"])
			
	# faction_scores = {f:statistics.mean(faction_scores[f]) for f in faction_scores if len(faction_scores[f]) > 3}
	faction_scores = {k:v for k,v in sorted(faction_scores.items(), key=lambda i:statistics.mean(i[1]), reverse=True)}
	
	best = [f for f in faction_scores if len(faction_scores[f]) > 3][0]
	worst = [f for f in faction_scores if len(faction_scores[f]) > 3][-1]
	
	window_mean = statistics.mean(faction_scores[best])
	window_sd = statistics.mean(faction_scores[worst])
	
	
	return window_mean,window_sd
	

def get_player_scores(edata):
	player_scores = defaultdict(list)
	
	for event in edata:
		for e in event["ladder"]:
			player_scores[e["player_name"]].append(e["gaussian_score"])
			
	player_scores = {k:player_scores[k] for k in player_scores if len(player_scores[k]) > 1}
	player_scores = {k:statistics.stdev(v) for k,v in sorted(player_scores.items(), key=lambda i:statistics.mean(i[1]), reverse=True)}
	
	
	return statistics.mean(player_scores.values()), 0
		
def windows():
	with open('output_data_files/recent_events/datahub_event_data.json') as json_file:
		edata = json.load(json_file)
	with open('output_data_files/recent_events/datahub_faction_data.json') as json_file:
		fdata = json.load(json_file)
		
	release_dict = {}
	with open('input_data_files/book_releases.csv', mode='r') as infile:
		reader = csv.reader(infile)
		for row in reader:
			release_dict[row[0].title()] = datetime.datetime.strptime(row[1].strip(), '%d %b %Y')
			
	N = 500
	rolling_indices = [[i for i in range(j,j+N)] for j in range(len(edata)-N)]
	rolling_indices = []
	
	last_index = -1
	window = []
	
	for i,e in enumerate(edata[last_index + 1:]):
		window.append(i)
		last_index += 1
		
		d1 = datetime.datetime.strptime(edata[window[0]]["std_date"], "%d %b %Y")
		d2 = datetime.datetime.strptime(edata[window[-1]]["std_date"], "%d %b %Y")
		
		window_length = abs(d2-d1).days
		
		if window_length >= N or last_index >= len(edata)-1:
			rolling_indices.append(window)
			window = [last_index + 1]
		
	x = []
	y = []
	y2 = []
	
	window_scores = []
	for ris in rolling_indices:
		es = [edata[i] for i in ris]
		
		d1 = datetime.datetime.strptime(edata[ris[0]]["std_date"], "%d %b %Y")
		d2 = datetime.datetime.strptime(edata[ris[-1]]["std_date"], "%d %b %Y")
		
		m,s = get_window_scores(es)
		m,s = get_player_scores(es)
		window_scores.append(m)
		
		x.append(edata[ris[-1]]["std_date"])
		y.append(m)
		y2.append(s)
		
	x.reverse()
	y.reverse()
	y2.reverse()
	
	y_mu = statistics.mean(y)
	y_sd = statistics.stdev(y)

	# plt.axhline(y=y_mu+y_sd, color='r', linestyle='-')
	# plt.axhline(y=y_mu-y_sd, color='r', linestyle='-')

	plt.xticks(rotation=90)
	plt.plot(x,y)
	plt.plot(x,y2)
	plt.show()

def fotow():
	with open('output_data_files/all_uk_events/datahub_event_data.json') as json_file:
		edata = json.load(json_file)
		
	with open('output_data_files/all_uk_events/datahub_faction_data.json') as json_file:
		fdata = json.load(json_file)
		
	with open('output_data_files/all_uk_events/datahub_player_data.json') as json_file:
		pdata = json.load(json_file)
		
	# fdata = {k:fdata[k] for k in fdata if len(fdata[k]["events"]) > 10}
		
	# best = max(fdata, key=lambda f:fdata[f]["mean_gaussian_score"])
	# print(best, fdata[best]["mean_gaussian_score"])
	# input()
	edata.reverse()
		
	filth_ratings = defaultdict(float)
	for event in edata:
		if len(event["ladder"]) < 20: continue
		filth_ratings[event["name"]] = statistics.mean([fdata[f]["mean_gaussian_score"] for f in [e["faction"] for e in event["ladder"]]])
		
	player_ratings = defaultdict(float)
	for event in edata:
		player_ratings[event["name"]] = statistics.mean([pdata[p]["gaussian_score"] for p in [e["player_name"] for e in event["ladder"]]])
		
	y = [filth_ratings[f] for f in filth_ratings]
	
	fotows = [e["name"] for e in edata if "Old World" in e["name"]][1:]
	
	print(fotows)
	z = [filth_ratings[f] for f in fotows]
	print(z)
	
	ax = plt.gca()
	ax.set_facecolor('black')

	plt.scatter([0 for _ in y], y,c=y,cmap='inferno',s=5)
	plt.scatter([0 for _ in z], z, c='white', s=100)
	plt.show()

if __name__ == '__main__':
	fotow()