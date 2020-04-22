import statistics
import json
import glob
import csv
import random

from matplotlib import pyplot as plt

import numpy as np
from xgboost import XGBClassifier, XGBRegressor
from xgboost import plot_importance

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error

def show_feature_importance(model):
	plot_importance(model)
	plt.show()
	plt.bar(range(len(model.feature_importances_)), model.feature_importances_)
	plt.show()

def per_unit_analysis(X, Y, lookup):
	pts = {}

	for i in range(len(X)):
		X_test = [X[i]]
		y_test = [Y[i]]
		
		X_train = [X[j] for j in range(len(X)) if j != i]
		y_train = [Y[j] for j in range(len(Y)) if j != i]
	
		model = XGBRegressor()
		model.fit(X_train, y_train)

		y_pred = model.predict(X_test)
		
		x = X_test[0]
		name = lookup[sum(x)+y_test[0]]
			
		pts[name] = [int(y_pred[0]), y_test[0]]
		
		# accuracy = mean_squared_error(y_test, y_pred)
		# print("MSE: %.2f" % (accuracy))

	for i,x in enumerate([k for k in data["Archaon"].keys() if k not in ["name","faction"]]):
		print(f'{i:5} {x:25}')
		
	pts = {k:v for k,v in sorted(pts.items(), key = lambda i: i[1][0] - i[1][1], reverse=True)}
	
	for p in sorted(list(pts.keys())):
		print(f'{p:45}\t{pts[p][0]:5}\t{pts[p][1]:5}')
		
	return pts

def baseline_test(X, Y, lookup):
	seed = 3#random.randint(1,100)
	test_size = 0.15
	X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=test_size, random_state=seed)

	model = XGBRegressor()
	model.fit(X_train, y_train)

	y_pred = model.predict(X_test)

	for i,x in enumerate(X_test):
		print(f'{lookup[sum(x)+y_test[i]]:35} {int(y_pred[i]):5} {y_test[i]:}')

	accuracy = mean_squared_error(y_test, y_pred)
	print("MSE: %.2f" % (accuracy))

	for i,x in enumerate([k for k in data["Archaon"].keys() if k not in ["name","faction"]]):
		print(f'{i:5} {x:25}')
		
	# show_feature_importance(model)

def create_data_rows(data):
	data_rows = []
	lookup = {}
	
	with open('output_data_files/new_features.json',encoding='utf-8') as json_file:
		ndata = json.load(json_file)
	
	for d in data:
		if int(data[d]["points"]) < 0: continue
		if data[d]["move"] == '*': data[d]["move"] = 9
		
		pts = data[d]["points"]
		data[d]["points"] = 0
		
		data[d]["rend"] = 0
		data[d]["high_rend"] = 0
		data[d]["mega_rend"] = 0
		
		data[d]["unit_size"] = 3
		
		if d in ndata:
			for k in ndata[d]:
				if "rend" in k:
					data[d][k] = ndata[d][k]
		
		row = [int(v) for k,v in data[d].items() if k not in ["name", "faction"]]
		row.append(int(pts))
		
		lookup[sum(row)] = d
		
		data_rows.append(row)
		
	print(f'{len(data_rows)} warscrolls loaded.')
	dataset = np.array(data_rows)
	
	X = dataset[:,:-1]
	Y = dataset[:,-1]

	return X, Y, lookup


if __name__ == '__main__':
	with open('output_data_files/unit_sizes.json',encoding='utf-8') as json_file:
		data = json.load(json_file)
		
	X, Y, lookup = create_data_rows(data)

	# baseline_test(X,Y,lookup)
	per_unit_analysis(X, Y, lookup)
	