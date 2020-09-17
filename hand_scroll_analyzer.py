import statistics
import json
import glob
import csv
import sys
import random

from collections import Counter
from matplotlib import pyplot as plt

import numpy as np 	
from xgboost import XGBClassifier, XGBRegressor
from xgboost import plot_importance

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error

def show_feature_importance(model):
	plot_importance(model)
	plt.show()

def per_unit_analysis(X, Y, lookup):
	pts = {}

	for i in range(len(X)):
		X_test = np.array([X[i]])
		y_test = np.array([Y[i]])
		
		X_train = np.array([X[j] for j in range(len(X)) if j != i])
		y_train = np.array([Y[j] for j in range(len(Y)) if j != i])
	
		model = XGBRegressor()
		model.fit(X_train, y_train)

		y_pred = model.predict(X_test)
		
		x = X_test[0]
		
		float_id = x[lookup["id_index"]]
		id = int(float_id)
		name = lookup[id]
			
		pts[name] = [int(y_pred[0]), y_test[0], int(y_pred[0])/y_test[0]]

	pts = {k:v for k,v in sorted(pts.items(), key = lambda i: i[1][2], reverse=True)}
	
	for p in sorted(list(pts.keys())):
		print(f'{p:45}\t{pts[p][0]:5}\t{pts[p][1]:5}\t{pts[p][2]:0.1f}')
		
	return pts
	
def excluded_faction_analysis(train_X, train_Y, test_X, test_Y, lookup):
	pts = {}
	internal_lookup = {}

	model = XGBRegressor()
	model.fit(train_X, train_Y)
	
	pred_Y = model.predict(test_X)
	
	for i in range(len(test_X)):	
		x = test_X[i]
	
		float_id = x[lookup["id_index"]]
		id = int(float_id)
		name = lookup[id]
			
		pts[name] = [int(pred_Y[i]), test_Y[i], int(pred_Y[i])/test_Y[i]]

	pts = {k:v for k,v in sorted(pts.items(), key = lambda i: i[1][2], reverse=True)}
	
	for p in sorted(list(pts.keys())):
		print(f'{p:45}\t{pts[p][0]:5}\t{pts[p][1]:5}\t{pts[p][2]:0.1f}')
		
	return pts

def baseline_test(X, Y, lookup, fnames):
	sum_mse = 0
	iters = 20

	for i in range(iters):
		seed = i
		test_size = 0.15
		X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=test_size, random_state=seed)

		model = XGBRegressor()
		model.fit(X_train, y_train)

		y_pred = model.predict(X_test)
		
		mse = mean_squared_error(y_test, y_pred)
		sum_mse += mse

		model.get_booster().feature_names = fnames
		
	print("MSE: %.2f" % (sum_mse/iters))
	show_feature_importance(model)

def create_data_rows(data, excluded_keywords=[]):
	data_rows = []
	excl_rows = []
	lookup = {}
	fnames = []
	
	keywords = [k["keywords"].split(',') for k in data]
	keywords = [k for kw in keywords for k in kw]
	kc = Counter(keywords)
	
	relevant_keywords = ["hero"] ## [k for k in kc if kc[k] > 5]
	
	fields_to_ignore = ["unit name", "keywords", "points", "wounds"]
	fields_to_ignore += [k for k in data[0].keys() if k[0] == "w"]
	
	fnames = [k for k in data[0].keys() if k not in fields_to_ignore]
	
	id = 0
	
	for d in data:
		if d["points"] <= 0: continue
		
		raw_points = d["points"]
		unit_size = d["models"]
		
		# if "wizard" in d["keywords"]: d["num boxes"] -= 2
		
		points = raw_points/unit_size
		
		row = [int(v) for k,v in d.items() if k not in fields_to_ignore]
		
		## keywords
		for k in relevant_keywords:
			row.append( int(k in d["keywords"].split(',')) )
			if k not in fnames: fnames.append(k)
			
		## effective_wounds
		raw_save = d["save"]
		dmg_reduction = (7 - raw_save) / 6
		if raw_save == 0: dmg_reduction = 0
		
		row.append(d["wounds"] + d["wounds"] * dmg_reduction)
		if "effective_wounds" not in fnames: fnames.append("effective_wounds")
		
		## damage
		avg_hit_roll = statistics.mean([d[v] for v in d if v[0] == "w" and "hit" in v and d[v] != 0])
		avg_wound_roll = statistics.mean([d[v] for v in d if v[0] == "w" and "wound" in v and d[v] != 0])
		avg_dmg = statistics.mean([d[v] for v in d if v[0] == "w" and "damage" in v and d[v] != 0])
		max_rend = max([d[v] for v in d if v[0] == "w" and "rend" in v])
		
		attacks = statistics.mean([d[v] for v in d if v[0] == "w" and "attacks" in v])
		
		row.append(-avg_hit_roll-avg_wound_roll+max_rend+avg_dmg+attacks)
		if "damage_amalgam" not in fnames: fnames.append("damage_amalgam")
			
		## shooting
		max_range = max([d[v] for v in d if v[0] == "w" and "range" in v])
		row.append(int(max_range > 3))
		if "can_shoot" not in fnames: fnames.append("can_shoot")
				
		## num weaps
		num_weaps = len([v for v in d if "wound" in v and d[v] != 0])
		row.append(num_weaps)
		if "num_weaps" not in fnames: fnames.append("num_weaps")

		## combo damage
		combo_damage = 0
		for w in range(1,num_weaps):	
			hit_roll = d[f'w{w}hit']
			wound_roll = d[f'w{w}wound']
			rend = d[f'w{w}rend']
			dmg = d[f'w{w}damage']
		
			hit_reduction = (7 - hit_roll) / 6
			wound_reduction = (7 - wound_roll) / 6
			rend_reduction = (7 - (4-rend)) / 6
			combo_damage += 100 * dmg * hit_reduction * wound_reduction * rend_reduction
		
		row.append(combo_damage)
		if "combo_damage" not in fnames: fnames.append("combo_damage")
		
		## wrap up
		if id in lookup:
			print("Collision")
		lookup["id_index"] = len(row)
		lookup[id] = d["unit name"]
		if "id" not in fnames: fnames.append("id")
		row.append(id)
		id += 1
		
		row.append(int(points))
		
		if any([k in d["keywords"] for k in excluded_keywords]):
			if "skaven" in d["keywords"]: continue
			row[4] = 0
			excl_rows.append(row)
		else:
			data_rows.append(row)
		
	print(fnames)
	print(f'{len(data_rows)} warscrolls loaded.')
	dataset = np.array(data_rows)
	
	excl_dataset = None
	excl_X = None
	excl_Y = None
	if len(excl_rows) > 0:
		print(f'{len(excl_rows)} warscrolls loaded for excluded keywords: {excluded_keywords}.')
		excl_dataset = np.array(excl_rows)
		excl_X = excl_dataset[:,:-1]
		excl_Y = excl_dataset[:,-1]
	
	X = dataset[:,:-1]
	Y = dataset[:,-1]

	return X, Y, lookup, fnames, excl_X, excl_Y

def create_meta_data_rows(data):
	data_rows = []
	lookup = {}
	fnames = []
	
	keywords = [k["keywords"].split(',') for k in data]
	keywords = [k for kw in keywords for k in kw]
	kc = Counter(keywords)
	
	relevant_keywords = [k for k in kc if kc[k] > 20]
	
	fields_to_ignore = ["unit name", "keywords", "meta", "wounds"]
	fields_to_ignore += [k for k in data[0].keys() if k[0] == "w"]
	
	fnames = [k for k in data[0].keys() if k not in fields_to_ignore]
	
	for d in data:
		if d["points"] <= 0: continue
		
		raw_points = d["points"]
		unit_size = d["models"]
		
		points = raw_points/unit_size
		
		row = [int(v) for k,v in d.items() if k not in fields_to_ignore]
		
		## keywords
		# for k in relevant_keywords:
			# row.append( int(k in d["keywords"].split(',')) )
			# if k not in fnames: fnames.append(k)
			
		## effective_wounds
		raw_save = d["save"]
		dmg_reduction = (7 - raw_save) / 6
		if raw_save == 0: dmg_reduction = 0
		
		row.append(d["wounds"] + d["wounds"] * dmg_reduction)
		if "effective_wounds" not in fnames: fnames.append("effective_wounds")
		
		## damage
		avg_hit_roll = statistics.mean([d[v] for v in d if v[0] == "w" and "hit" in v and d[v] != 0])
		avg_wound_roll = statistics.mean([d[v] for v in d if v[0] == "w" and "wound" in v and d[v] != 0])
		avg_dmg = statistics.mean([d[v] for v in d if v[0] == "w" and "damage" in v and d[v] != 0])
		max_rend = max([d[v] for v in d if v[0] == "w" and "rend" in v])
		
		row.append(-avg_hit_roll-avg_wound_roll+max_rend+avg_dmg)
		if "damage_amalgam" not in fnames: fnames.append("damage_amalgam")
				
		## num weaps
		num_weaps = len([v for v in d if "wound" in v and d[v] != 0])
		row.append(num_weaps)
		if "num_weaps" not in fnames: fnames.append("num_weaps")
				
		## wrap up
		row.append(int(d["meta"]))
		
		lookup[sum(row)] = d["unit name"]
		
		data_rows.append(row)
		
	print(fnames)
	print(f'{len(data_rows)} warscrolls loaded.')
	dataset = np.array(data_rows)
	
	X = dataset[:,:-1]
	Y = dataset[:,-1]

	return X, Y, lookup, fnames
	
def all_factions(pts, data_dict):
	errors = {}
	for p in pts:
		og_data = data_dict[p]
		error = abs(pts[p][0]-pts[p][1])/pts[p][1]
		errors[p] = error
		
	errors = {k:v for k,v in sorted(errors.items(), key=lambda i: i[1], reverse=True)}
	
	factions = ["gloomspite", "bonereapers", "khaine", "sylvaneth", "beasts of chaos", "mawtribes", "kharadron", "cities of sigmar", "nighthaunt", "fyreslayers", "slaanesh", "tzeentch"]
	factions += ["flesh", "slaves", "deepkin"]
	
	f_scores = {f:[] for f in factions}
	
	for p in pts:
		og_data = data_dict[p]
		faction = ""
		
		for f in factions:
			if f in og_data["keywords"]:
				faction = f
				break
		
		if faction == "":
			print(p, og_data["keywords"])
			continue
		
		f_scores[faction].append(pts[p][2])
	
	print()
	f_scores = {k:v for k,v in sorted(f_scores.items(), key=lambda i: statistics.mean(i[1]), reverse=True)}
	for f in f_scores:
		print(f'{f:45}\t{statistics.mean(f_scores[f]):.3f}')
	print()
	
def specific_faction(X, Y, lookup, data_dict, faction, excl_X=None, excl_Y=None):
	pts = {}
	
	if excl_X is None:
		pts = per_unit_analysis(X, Y, lookup)
	else:
		pts = excluded_faction_analysis(X, Y, excl_X, excl_Y, lookup)
	
	pts = {k:v for k,v in sorted(pts.items(),key=lambda i: i[1][2],reverse=True)}
		
	print()
	print(faction)
	print()
	
	for p in pts:
		og_data = data_dict[p]
		if faction in og_data["keywords"]:
			print(f'{p:40}\t{pts[p][0] * og_data["models"]:5}\t{pts[p][1] * og_data["models"]:5}\t{pts[p][2]:0.2f}')
			
	print()
	print()
	
def get_faction_feature_means(X, Y, lookup, fnames, data_dict, faction):
	fmeans = {}

	for x in X:
		float_id = x[lookup["id_index"]]
		id = int(float_id)
		name = lookup[id]
		
		if faction not in data_dict[name]["keywords"]:
			continue
			
		for i,f in enumerate(x):
			if fnames[i] not in fmeans: fmeans[fnames[i]] = []
			fmeans[fnames[i]].append(f)
	
	return fmeans
	
		
		
	
if __name__ == '__main__':
	with open('hand_scrolls.json',encoding='utf-8') as json_file:
		data = json.load(json_file)
		data = [d for d in data if d["unit name"] != 0]
		
	data_dict = {d["unit name"]:d for d in data}
	
	factions = ["beasts", "cities", "daughters", "flesh-eater", "fyreslayer", "gitz", "deepkin", "kharadron", "khorne", "legions", "lumineth", "nighthaunt", "nurgle", "mawtribes", "orruk", "ossiarch", "seraphon", "skaven", "slaanesh", "slaves to darkness", "stormcast", "sylvaneth"]
		
	xfaction = []
	if "x" in sys.argv:
		xfaction = [sys.argv[1]]
		
	X, Y, lookup, fnames, excl_X, excl_Y = create_data_rows(data, xfaction)
	
	if "fc" in sys.argv:
		
		damages = {}
		
		for f in factions:
			fmeans = get_faction_feature_means(X, Y, lookup, fnames, data_dict, f)
			
			if len(sys.argv) < 2:
				print(fnames)
				sys.exit()
				
			relevant_feature = sys.argv[1]
			damages[f] = int(statistics.mean(fmeans[relevant_feature])*100)
				
		damages = {k:v for k,v in sorted(damages.items(), key=lambda i: i[1], reverse=True)}
		
		for d in damages:
			print(f'{d:35}\t\t{damages[d]}')
			
		sys.exit()
	
	if len(sys.argv) > 1:
		faction = sys.argv[1]
		specific_faction(X, Y, lookup, data_dict, faction, excl_X, excl_Y)
	else:
		baseline_test(X,Y,lookup,fnames)