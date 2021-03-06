import trueskill as ts
import statistics
import json
import glob
import csv
import random

from math import sqrt
from trueskill import BETA
from trueskill.backends import cdf

import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def win_probability(player_rating, opponent_rating):
    delta_mu = player_rating.mu - opponent_rating.mu
    denom = sqrt(2 * (BETA * BETA) + pow(player_rating.sigma, 2) + pow(opponent_rating.sigma, 2))
    return cdf(delta_mu / denom)
	
if __name__ == '__main__':
	data_folder = "input_data_files/tablesoup_data"

	files = glob.glob(f'{data_folder}/*')

	elos = {}

	with open("output_data_files/all_uk_events/datahub_player_data.json", newline='', encoding='utf-8') as json_file:
		player_data = json.load(json_file)
		
	with open("output_data_files/all_uk_events/datahub_faction_data.json", newline='', encoding='utf-8') as json_file:
		f_data = json.load(json_file)
		
	name_subs = {"James Ganis":"Jp Ganis", "Chris Caves Jnr":"Chris Caves Jr"}	
	data_rows = []
	
	player_ids = {p:i for i,p in enumerate(player_data)}
	id_lookup = {i:p for i,p in enumerate(player_data)}
	
	fids = {f:i for i,f in enumerate(f_data)}
	
	fid_lookup = {i:f for i,f in enumerate(f_data)}
	
	fids['-'] = -1
	fid_lookup[-1] = '-'
	
	max_pids = len(player_data)
	
	for file in files:
		with open(file, newline='', encoding='utf-8') as csvfile:
			reader = csv.reader(csvfile)
			
			pfaction = {}
			
			new_rows = []
			for row in reader:
				new_rows.append(row)
				if len(row) == 3:
					row[1] = row[1].replace('Of','of')
					row[1] = row[1].replace('Ogor ','')
					
					if row[1] not in fids:
						row[1] = '-'
					
					pfaction[row[0]] = fids[row[1]]
				
			for row in new_rows:
				if len(row) > 5:
					if len(row) % 2 != 0: continue
				
					for i in range(0, len(row), 2):
						for v in row:
							v.replace(',','')
		
						player_a = row[i]
						player_b = row[i+1]
						
						if player_a in name_subs:
							player_a = name_subs[player_a]
							
						if player_b in name_subs:
							player_b = name_subs[player_b]
						
						if player_a not in elos:
							elos[player_a] = ts.Rating()
							
						if player_b not in elos:
							elos[player_b] = ts.Rating()
							
						elos[player_a],elos[player_b] = ts.rate_1vs1(elos[player_a], elos[player_b])
						
						if player_a not in player_ids:
							max_pids+=1
							player_ids[player_a] = max_pids
							id_lookup[max_pids] = player_a
							
						if player_b not in player_ids:
							max_pids+=1
							player_ids[player_b] = max_pids
							id_lookup[max_pids] = player_b
						
						try:
							if random.random() > 0.5:
								data_rows.append([player_ids[player_a], pfaction[row[i]], player_ids[player_b], pfaction[row[i+1]], 0])
							else:
								data_rows.append([player_ids[player_b], pfaction[row[i+1]], player_ids[player_a],pfaction[row[i]], 1])
						except:
							pass
						
				else:
					if row[0] == "NEW_EVENT_TAG": continue
					if row[1] == '-': continue
		
	print(len(data_rows))

	elos = {k:v for k,v in sorted(elos.items(), key=lambda i:i[1].mu, reverse=True)}

	n = 0
	for e in elos:
		if e not in player_data: continue
		if len(player_data[e]["events"]) < 3: continue
		n+=1
		print(f'{n:20}\t{e:35}\t{int(elos[e].mu*100)}')

	import sys
	sys.exit()
	#for e in elos:
		#print(f'{e:35} {elos[e]:25}')

	for i,d in enumerate(data_rows):
		p1id = d[0]
		p1f = d[1]
		p2id = d[2]
		p2f = d[3]
		p1win = d[-1]
		
		p1name = id_lookup[p1id]
		p2name = id_lookup[p2id]
		
		if p1name not in elos: elos[p1name] = ts.Rating()
		if p2name not in elos: elos[p2name] = ts.Rating()
		
		p1elo = elos[p1name]
		p2elo = elos[p2name]
		
		# d = [p1id, p1elo.mu, p1elo.sigma, p1f, p2id, p2elo.mu, p2elo.sigma, p2f, p1win]
		
		f1 = fid_lookup[p1f]
		f2 = fid_lookup[p2f]
		
		w = 1
		l = 1
		
		data_rows[i] = [p1id,p1elo.mu,p1elo.sigma,p1f, p2id,p2elo.mu,p2elo.sigma,p2f, w/(w+l), win_probability(p1elo,p2elo), p1win]
		
		
	# load data
	dataset = np.array(data_rows)
	
	# split data into X and y
	X = dataset[:,:-1]
	Y = dataset[:,-1]
	
	# split data into train and test sets
	seed = 7
	test_size = 0.1
	X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=test_size, random_state=seed)
	
	# fit model no training data
	model = XGBClassifier()
	model.fit(X_train, y_train)
	
	# make predictions for test data
	y_pred = model.predict(X_test)
	predictions = [round(value) for value in y_pred]
	
	# evaluate predictions
	accuracy = accuracy_score(y_test, predictions)
	print("Training Accuracy: %.2f%%" % (accuracy * 100.0))
			
	fotow = []
	with open('round.csv') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		for row in csv_reader:
			fotow += row

	for i,f in enumerate(fotow):
		if i % 2 == 1: continue
		fotow[i] = f.title()
	print(fotow)
			
	players = {fotow[i]:fotow[i+1] for i in range(0,len(fotow),2)}
	
	new_data = []
	for p in players:
		for q in players:
			p1name = p
			f1 = players[p]
			
			p2name = q
			f2 = players[q]
			
			if p1name not in player_ids:
				max_pids+=1
				player_ids[p1name] = max_pids
				id_lookup[max_pids] = p1name
				
			if p2name not in player_ids:
				max_pids+=1
				player_ids[p2name] = max_pids
				id_lookup[max_pids] = p2name
			
			p1id = player_ids[p1name]
			p1f = fids[f1]
			
			p2id = player_ids[p2name]
			p2f = fids[f2]

			if p1name not in elos: elos[p1name] = ts.Rating()
			if p2name not in elos: elos[p2name] = ts.Rating()
			
			p1elo = elos[p1name]
			p2elo = elos[p2name]
			
			f1 = fid_lookup[p1f]
			f2 = fid_lookup[p2f]
			
			w = 1
			l = 1
			
			new_data.append([p1id,p1elo.mu,p1elo.sigma,p1f, p2id,p2elo.mu,p2elo.sigma,p2f, w/(w+l), win_probability(p1elo,p2elo)])
	
	new_data = np.array(new_data)
	y_pred = model.predict(new_data)
	predictions = [round(value) for value in y_pred]
	yps = model.predict_proba(new_data)
	
	for i,x in enumerate(new_data):
		p1 = id_lookup[x[0]]
		p2 = id_lookup[x[4]]
		# print(f'\t{p1:25} vs {p2:25} {yps[i][int(predictions[i])]*100:5.1f}%')
		
	output = {p:{q:0 for q in players} for p in players}
	for i,x in enumerate(new_data):
		p1 = id_lookup[x[0]]
		p2 = id_lookup[x[4]]
		
		if p1 == p2: continue
		
		s = yps[i][int(predictions[i])]*100
		if predictions[i] == 0: s = 100-s
		
		output[p1][p2] = s
		# print(f'{p1},{p2},{yps[i][int(predictions[i])]*100:.1f}%')
		
	#import pandas
	#df = pandas.DataFrame(output, players.keys(), players.keys())
	#df.to_excel("output2.xlsx")
		
		
	import sys
	#sys.exit()
	
	
	############# do fotow predictions
	wins = {p:0 for p in fotow if fotow.index(p) % 2 == 0}
	
	for i in range(5):
		new_data = []
		for i in range(0,len(fotow),4):
			p1name = fotow[i].title()
			f1 = fotow[i + 1]
			
			p2name = fotow[i + 2].title()
			f2 = fotow[i + 3]
			
			if p1name not in player_ids:
				max_pids+=1
				player_ids[p1name] = max_pids
				id_lookup[max_pids] = p1name
				
			if p2name not in player_ids:
				max_pids+=1
				player_ids[p2name] = max_pids
				id_lookup[max_pids] = p2name
			
			p1id = player_ids[p1name]
			p1f = fids[f1]
			
			p2id = player_ids[p2name]
			p2f = fids[f2]

			if p1name not in elos: elos[p1name] = ts.Rating()
			if p2name not in elos: elos[p2name] = ts.Rating()
			
			p1elo = elos[p1name]
			p2elo = elos[p2name]
			
			f1 = fid_lookup[p1f]
			f2 = fid_lookup[p2f]
			
			w = 1
			l = 1
			
			new_data.append([p1id,p1elo.mu,p1elo.sigma,p1f, p2id,p2elo.mu,p2elo.sigma,p2f, w/(w+l), win_probability(p1elo,p2elo)])
		
		
		new_data = np.array(new_data)
		y_pred = model.predict(new_data)
		predictions = [round(value) for value in y_pred]
		yps = model.predict_proba(new_data)
		
		print()
		for i,x in enumerate(new_data):
			p1 = id_lookup[x[0]]
			p2 = id_lookup[x[4]]
			print(f'\t{p1:25} vs {p2:25} ||| {[p1,p2][int(predictions[i])]:25} ({yps[i][int(predictions[i])]*100:5.1f}% )')
			winner = [p1,p2][int(predictions[i])]
			
			wins[winner] += 1
		
		wins = {k:v for k,v in sorted(wins.items(),key=lambda i: i[1], reverse=True)}
		
		fotow2 = []
		
		for w in wins:
			fotow2 += [w, fotow[fotow.index(w)+1]]
		
		fotow = fotow2
		
		for w in wins:
			print(w)
		for w in wins:
			print(wins[w])
		
		print()
