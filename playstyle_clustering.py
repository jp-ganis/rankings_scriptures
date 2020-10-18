import json

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.datasets.samples_generator import make_blobs
from sklearn.cluster import KMeans

import statistics

if __name__ == '__main__':
	with open('output_data_files/all_uk_events/datahub_player_data.json') as json_file:
		pdata = json.load(json_file)
		
	with open('output_data_files/all_uk_events/datahub_faction_data.json') as json_file:
		fdata = json.load(json_file)
		
		
	## playstyles = [magic, combat, control, shooting, mobility]
	
	playstyles = {}
	playstyles["Hedonites of Slaanesh"] = [0, 2, 1, 0, 2]
	# playstyles["Hosts of Slaanesh"] = [0, 2, 1, 0, 2]
	playstyles["Ossiarch Bonereapers"] = [1, 2, 0, 0, 0]
	playstyles["Big Waaagh"] = [2, 2, 0, 0, 2]
	playstyles["Daughters of Khaine"] = [0, 2, 2, 0, 2]
	playstyles["Orruk Warclans"] = [1, 2, 0, 0, 2]
	playstyles["Skaventide"] = [1, 1, 1, 1, 1]
	playstyles["Idoneth Deepkin"] = [0, 2, 1, 0, 2]
	playstyles["Fyreslayers"] = [0, 2, 0, 0, 0]
	playstyles["Grand Host of Nagash"] = [2, 1, 2, 0, 1]
	# playstyles["Skaven"] = [1, 1, 1, 1, 1]
	playstyles["Legion of Grief"] = [1, 1, 2, 0, 1]
	playstyles["Disciples of Tzeentch"] = [2, 0, 2, 0, 1]
	playstyles["Bonesplitterz"] = [1, 1, 1, 1, 2]
	playstyles["Mawtribes"] = [0, 2, 0, 0, 2]
	playstyles["Legion of Blood"] = [1, 2, 1, 0, 0]
	playstyles["Blades of Khorne"] = [1, 2, 0, 0, 0]
	playstyles["Cities of Sigmar"] = [2, 0, 0, 2, 0]
	playstyles["Kharadron Overlords"] = [0, 0, 0, 2, 2]
	playstyles["Ironjawz"] = [1, 2, 0, 0, 2]
	playstyles["Sylvaneth"] = [1, 1, 1, 1, 1]
	playstyles["Maggotkin of Nurgle"] = [1, 1, 1, 0, 0]
	playstyles["Seraphon"] = [2, 0, 1, 2, 1]
	playstyles["Legion of Sacrement"] = [2, 1, 2, 0, 1]
	playstyles["Slaves to Darkness"] = [1, 2, 1, 0, 2]
	playstyles["Stormcast Eternals"] = [0, 1, 0, 2, 0]	
	playstyles["Beasts of Chaos"] = [1, 1, 1, 0, 1]
	playstyles["Gloomspite Gitz"] = [2, 0, 2, 0, 0]
	playstyles["Legions of Nagash"] = [2, 1, 2, 0, 1]
	playstyles["Nighthaunt"] = [0, 0, 1, 0, 1]
	playstyles["Lumineth Reamlords"] = [2, 1, 0, 2, 0]
	playstyles["Legions of Chaos Ascendant"] = [2, 1, 2, 0, 1]
	playstyles["Flesh Eater Courts"] = [1, 2, 0, 0, 2]

	#################
	# X = [playstyles[f] for f in playstyles]
	
	# kmeans = KMeans(n_clusters=5, init='k-means++', max_iter=300, n_init=10, random_state=0)
	# pred_y = kmeans.fit_predict(X)
	
	# clusters = {}
	# for n, f in enumerate(playstyles):
		# clusters[f] = pred_y[n]
		
	# clusters = {k:v for k,v in sorted(clusters.items(), key=lambda i: i[1])}
		
	# prev_c = 0
	# for f in clusters:
	
		# if clusters[f] != prev_c:
			# print()
			# print()
			
		# print(f'\t{f:35} {clusters[f]}')
		
		# prev_c = clusters[f]
	
	############################
	# x = []
	# y = []
	
	# pstyles = {}
	
	# for p in pdata:
		# cs = [clusters[e["faction"]]*1.0 for e in pdata[p]["events"] if e["faction"] in clusters]
		# if len(cs) == 0: continue
		
		# mc = statistics.mean(cs)
		# pstyles[p] = mc
		
	pfvectors = {p:{f:0 for f in fdata} for p in pdata}
		
	for p in pdata:
		pms = statistics.mean([e["gaussian_score"] for e in pdata[p]["events"]])
		for e in pdata[p]["events"]:
		
			if e["gaussian_score"] > pms: 
				pfvectors[p][e["faction"]] += 1
			elif e["gaussian_score"] < pms:
				pfvectors[p][e["faction"]] -= 1
	
	X = [[v for v in pfvectors[p].values()] for p in pfvectors]
	
	# wcss = []
	# max_c = 300
	# step = 10
	# for i in range(1, max_c, step):
		# print(i)
		# kmeans = KMeans(n_clusters=i, init='k-means++', max_iter=300, n_init=10, random_state=0)
		# kmeans.fit(X)
		# wcss.append(kmeans.inertia_)
	# plt.plot(range(1, max_c, step), wcss)
	# plt.title('Elbow Method')
	# plt.xlabel('Number of clusters')
	# plt.ylabel('WCSS')
	# plt.show()
		
	CLUSTERS=30
	kmeans = KMeans(n_clusters=CLUSTERS, init='k-means++', max_iter=300, n_init=10, random_state=0)
	pred_y = kmeans.fit_predict(X)
	
	clusters = {}
	for n, f in enumerate(pfvectors):
		clusters[f] = pred_y[n]
		
	clusters = {k:v for k,v in sorted(clusters.items(), key=lambda i: i[1])}
	
	# print()		
	# print()		
	# prev_c = 0
	# for f in clusters:
		# if clusters[f] != prev_c:
			# print()
			# print()
			
		# print(f'\t{f:35} {clusters[f]}')
		
		# prev_c = clusters[f]
	
	cluster_armies = {i:[] for i in range(CLUSTERS)}
	
	for p in clusters:
		c = clusters[p]
		print(p,c)
		cluster_armies[c] += [e["faction"] for e in pdata[p]["events"]]
		
	for i in cluster_armies:
		print()
		print(f'{i:5}')
		ccf=[(f, cluster_armies[i].count(f)) for f in sorted(cluster_armies[i],key=lambda f: cluster_armies[i].count(f),reverse=True)]
		for f in ccf:
			print(f)
	
	x=[]
	y=[]
	for p in pdata:
		for e in pdata[p]["events"]:
			c = clusters[p]
			cluster_count = cluster_armies[c].count(e["faction"])
			
			x.append(e["gaussian_score"])
			y.append(cluster_count)
			
	plt.scatter(x,y)
	plt.show()
	# x = []
	# y = []
	
	
	
	# for p in clusters:
		# for e in pdata[p]["events"]:
			
		# x.append(pdata[p]["gaussian_score"])
		# y.append(clusters[p])
		
	# plt.scatter(x, y)
	# plt.show()