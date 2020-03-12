import statistics
import json
import glob
import csv

import xgboost as xgb
import numpy as np

from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

if __name__ == '__main__':
	
	with open("output_data_files/all_uk_events/datahub_player_data.json", newline='', encoding='utf-8') as json_file:
		pdata = json.load(json_file)
		
	with open("output_data_files/all_uk_events/datahub_faction_data.json", newline='', encoding='utf-8') as json_file:
		fdata = json.load(json_file)
		
	data_rows = []
	
	pids = {k:i for i,k in enumerate(pdata)}
	fids = {k:i for i,k in enumerate(fdata)}
	
	for player in pdata:
		last_event = None
	
		for event in pdata[player]["events"]:
			if last_event is None: 
				last_event = event
				last_event["faction_streak"] = 1
				continue
				
			row = [pids[player]]
			f = last_event["faction"]
			
			row += [last_event["gaussian_score"], fids[f], fdata[f]["mean_gaussian_score"], last_event["metabreakers_score"], last_event["faction_streak"]]
			
			changed_army = event["faction"] == last_event["faction"]
			last_fs = last_event["faction_streak"]
			last_event = event
			last_event["faction_streak"] = last_fs+1
			
			if changed_army:
				row.append(0)
			else:
				row.append(1)
				
		data_rows.append(row)
	
	for i in range(15):
		print(data_rows[i])
	
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
			
				
			
			