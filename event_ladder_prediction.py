import trueskill as ts
import statistics
import json
import glob
import csv
import random

from math import sqrt
from trueskill import BETA
from trueskill.backends import cdf

import gaussian_fitter

import numpy as np
from xgboost import XGBClassifier, XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error, mean_absolute_error

if __name__ == '__main__':
	data_folder = "input_data_files/tablesoup_data"

	files = glob.glob(f'{data_folder}/*')

	elos = {}

	with open("output_data_files/all_uk_events/datahub_player_data.json", newline='', encoding='utf-8') as json_file:
		player_data = json.load(json_file)
		
	with open("output_data_files/all_uk_events/datahub_faction_data.json", newline='', encoding='utf-8') as json_file:
		f_data = json.load(json_file)
		
	with open("output_data_files/faction_data/faction_matchups.json", newline='', encoding='utf-8') as json_file:
		m_data = json.load(json_file)
		
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
						
						
				else:
					if row[0] == "NEW_EVENT_TAG": continue
					if row[1] == '-': continue
		
	data_rows = []
			
	for player in player_data:
		if player not in elos: continue
		
		for event in player_data[player]["events"]:
			win_dist = gaussian_fitter.get_win_distribution(event["num_players"])
			wins = win_dist[event["placing"]-1]
			
			elo_m = elos[player].mu
			elo_s = elos[player].sigma
			f_score = f_data[event["faction"]]["mean_gaussian_score"]
			
			data_rows.append([player_data[player]["gaussian_score"], elo_m, elo_s, f_score, wins])
		
	print(len(data_rows))
	
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
	model = XGBRegressor()
	model.fit(X_train, y_train)
	
	# make predictions for test data
	y_pred = model.predict(X_test)
	predictions = [round(value) for value in y_pred]
	
	# evaluate predictions
	mse = mean_squared_error(y_test, predictions)
	print("Training RMSE: %.2f" % (mse**0.5))
			
	fotow = []
	with open('round.csv') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		for row in csv_reader:
			fotow += row
			
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
		
		if f1 in m_data and f2 in m_data[f1]["matchups"]:
			matchup_wl = m_data[f1]["matchups"][f2]
			w = matchup_wl["Wins"]
			l = matchup_wl["Losses"]
		
		r1 = 0.5
		r2 = 0.5
		
		if p1name in player_data:
			r1 = player_data[p1name]["gaussian_score"]
			
		if p2name in player_data:
			r2 = player_data[p2name]["gaussian_score"]
		
		new_data.append([r1, p1elo.mu, p1elo.sigma, p1f])
		new_data.append([r2, p2elo.mu, p2elo.sigma, p2f])
	
	
	y_pred = model.predict(new_data)
	predictions = [round(value) for value in y_pred]
	# yps = model.predict_proba(new_data)
	
	print()
	for i,x in enumerate(new_data):
		p1 = fotow[i*2]
		print(f'\t{p1.title():25} ||| {predictions[i]+1:25}')
	print()