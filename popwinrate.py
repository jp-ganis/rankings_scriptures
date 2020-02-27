import json
import matplotlib.pyplot as plt 
import matplotlib
import numpy as np
import random
import csv			
from datetime import datetime
import statistics
import scipy.stats
import itertools
from surprise import SVD
from surprise.model_selection import cross_validate

def plot_winrate_vs_popularity():
	with open('output_data_files/all_time_data/datahub_faction_data.json') as json_file:
		data = json.load(json_file)
		
		
	faction_cts = {k:len(data[k]["events"]) for k in data if k not in ["Stormcast Eternals","Blades of Khorne", "Order", "Chaos"] and len(data[k]["events"]) > 30}
	faction_cts = {k:v for k,v in sorted(faction_cts.items(), key=lambda i:i[1],reverse=True)}
	
	for f in faction_cts:
		plt.scatter(data[f]["mean_gaussian_score"],faction_cts[f],label=f,s=8)
		# plt.scatter(data[f]["mean_gaussian_score"], scipy.stats.norm.pdf(data[f]["mean_gaussian_score"], 45, 10)*10000, c='black', s=1)
		
	plt.xlabel("mean event score")
	plt.ylabel("army popularity")
	# plt.legend(loc="upper left")
	plt.show()
	
def most_common_army_pairs():
	with open('output_data_files/all_time_data/datahub_player_data.json') as json_file:
		pdata = json.load(json_file)
	
	with open('output_data_files/all_time_data/datahub_faction_data.json') as json_file:
		fdata = json.load(json_file)
	
	del fdata['-']
	for k in ["Death","Order","Chaos","Destruction","UNKNOWN_ARMY"]:
		del fdata[k]
			
	faction_cts = {k:len(fdata[k]["events"]) for k in fdata}
	total = sum([faction_cts[k] for k in faction_cts])
	
	factions = list(fdata.keys())
	fpairs = {}
	for f in factions:
		for g in factions:
			if f==g: continue
			fpairs[(f,g)] = 0
			fpairs[(g,f)] = 0
			
	for p in pdata:
		pfactions = [e["faction"] for e in pdata[p]["events"]]
		combos = list(itertools.combinations(pfactions, 2))
		
		for c in combos:
			if c in fpairs:
				fpairs[c] += 1
				
	fpairs = {k:v for k,v in fpairs.items() if fpairs[k] > 10}
	fpairs = {k:v for k,v in sorted(fpairs.items(), key=lambda x: x[1], reverse=True)}
	
	scores = {}
	
	for i,f in enumerate(fpairs):
		p1 = faction_cts[f[0]]/total
		p2 = faction_cts[f[1]]/total
		
		p_combo = p1 * p2
		
		scores[f] = (1 - p_combo) * fpairs[f]
		
	scores = {k:v for k,v in sorted(scores.items(), key=lambda x: x[1], reverse=True)}
	
	# for i,f in enumerate(scores):
		# p1 = (faction_cts[f[0]]/total)
		# p2 = (faction_cts[f[1]]/total)
		# print(f'{i:4} {f[0]:25} {f[1]:25} {int(scores[f]*100):5} {p1*p2:5.5}')
	
	f = "Idoneth Deepkin"
	for s in scores:
		if f in s[0]:
			print(f'{s[0]:25} {s[1]:25} {int(scores[s])}')
	
def get_top_n(predictions, n=10):
	from collections import defaultdict
	'''Return the top-N recommendation for each user from a set of predictions.

	Args:
	predictions(list of Prediction objects): The list of predictions, as
	returned by the test method of an algorithm.
	n(int): The number of recommendation to output for each user. Default
	is 10.

	Returns:
	A dict where keys are user (raw) ids and values are lists of tuples:
	[(raw item id, rating estimation), ...] of size n.
	'''

	# First map the predictions to each user.
	top_n = defaultdict(list)
	for uid, iid, true_r, est, _ in predictions:
		top_n[uid].append((iid, est))

	# Then sort the predictions for each user and retrieve the k highest ones.
	for uid, user_ratings in top_n.items():
		user_ratings.sort(key=lambda x: x[1], reverse=True)
		top_n[uid] = user_ratings[:n]

	return top_n
	
def svd():
	from surprise import BaselineOnly
	from surprise import Dataset
	from surprise import Reader
	from surprise.model_selection import cross_validate

	with open('output_data_files/all_time_data/datahub_player_data.json') as json_file:
		pdata = json.load(json_file)
	
	with open('output_data_files/all_time_data/datahub_faction_data.json') as json_file:
		fdata = json.load(json_file)

	ffs =["Death","Order","Chaos","Destruction","UNKNOWN_ARMY","-"]
		
	for k in ffs:
		del fdata[k]
		
	factions = list(fdata.keys())
		
	faction_vectors = []
	
	playerids = []
	
	with open('ratings.csv','w') as rfile:
		for i,p in enumerate(pdata):
			pfactions = [e["faction"] for e in pdata[p]["events"] if e["faction"] not in ffs]	
			playerids.append(p)
			
			faction_ratings = {}
			
			for f in pfactions:
				faction_ratings[factions.index(f)] = 1/pfactions.count(f)
			
			faction_vectors.append(faction_ratings)
			
			for f in faction_ratings:
				s=f'{i},{f},{faction_ratings[f]}\n'
				rfile.write(s)
		
		
	reader = Reader(line_format='user item rating', sep=',')
	data = Dataset.load_from_file('ratings.csv', reader=reader)
	trainset = data.build_full_trainset()

	algo = SVD()
	algo.fit(trainset)
	cross_validate(algo, data, measures=['RMSE', 'MAE'], cv=5, verbose=True)

	testset = trainset.build_anti_testset()
	
	predictions = algo.test(testset)

	top_n = get_top_n(predictions, n=3)
	
	with open('recommendations.csv','w') as rfile:
		for uid, user_ratings in top_n.items():
			s = playerids[int(uid)] + " " + str([factions[int(iid)] for (iid, _) in user_ratings]) + "\n"
			rfile.write(s)
	
if __name__ == '__main__':
	# most_common_army_pairs()
	svd()
	
	
