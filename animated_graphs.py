import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import csv
from datetime import datetime

def load_data(by_month=True):
	months = {}
	faction_scores = {}
	faction_counts = {}
	faction_deltas = {}
	
	tmp_scores = {}
	tmp_counts = {}
	tmp_deltas = {}
	
	with open('output_data_files/meta_history.csv') as csvfile:
		readCSV = csv.reader(csvfile, delimiter=',')
		for row in readCSV:
			faction = row[1]
			
			if faction == "UNKNOWN_ARMY": continue
			if "Tzeentch" in faction: faction = "Disciples of Tzeentch"
			if "Skaven" in faction: faction = "Skaven"
			
			month = "XX"
			if '2020' in row[0]:
				month = row[0].replace('2020','20')
			else:
				month = row[0].replace('20','')
				
			if month not in months:
				months[month] = []
				
				if by_month:
					tmp_scores[faction] = []
					tmp_counts[faction] = []
					tmp_deltas[faction] = []

			months[month].append(faction)
				
			if faction not in faction_scores:
				faction_scores[faction] = {}
				faction_counts[faction] = {}
				faction_deltas[faction] = {}
				
				tmp_scores[faction] = []
				tmp_counts[faction] = []
				tmp_deltas[faction] = []
				
			tmp_scores[faction].append(float(row[2]))
			tmp_counts[faction].append(float(row[3]))
			tmp_deltas[faction].append(float(row[4]))
				
			faction_deltas[faction][month] = float(sum(tmp_deltas[faction]) / len(tmp_deltas[faction])) 
			faction_scores[faction][month] = float(sum(tmp_scores[faction]) / len(tmp_scores[faction])) 
			faction_counts[faction][month] = float(sum(tmp_counts[faction]) / len(tmp_counts[faction]))
	
	return faction_scores, faction_counts

def augment(xold,yold,numsteps):
    xnew = []
    ynew = []
    for i in range(len(xold)-1):
        difX = xold[i+1]-xold[i]
        stepsX = difX/numsteps
        difY = yold[i+1]-yold[i]
        stepsY = difY/numsteps
        for s in range(numsteps):
            xnew = np.append(xnew,xold[i]+s*stepsX)
            ynew = np.append(ynew,yold[i]+s*stepsY)
    return xnew,ynew
	
def animate(i):
	faction_scores, faction_counts = load_data(False)

	all_keys = [k for k in [list(faction_scores[f].keys()) for f in faction_scores]]
	all_keys = list(set([e for sublist in all_keys for e in sublist]))
	all_keys = sorted(all_keys, key=lambda m: datetime.strptime(m, '%b%y'))
	
	factions = ["Flesh Eater Courts", "Idoneth Deepkin", "Daughters of Khaine", "Order"]
	colors = ['r','b','c','y','g']
	
	for faction in factions:
		rkeys = [all_keys.index(key) for key in all_keys if key in faction_counts[faction]][:i]
		rvalues = [faction_scores[faction][all_keys[rk]] for rk in rkeys]
		
		rkeys, rvalues = augment(rkeys, rvalues, 10)

		plt.plot(rkeys,rvalues,c=colors[factions.index(faction)])

if __name__ == '__main__':
	faction_scores, faction_counts = load_data(False)

	all_keys = [k for k in [list(faction_scores[f].keys()) for f in faction_scores]]
	all_keys = list(set([e for sublist in all_keys for e in sublist]))
	all_keys = sorted(all_keys, key=lambda m: datetime.strptime(m, '%b%y'))

	fig = plt.figure()
	ax = plt.axes(xlim=(0, 52), ylim=(0, 100))
	# plt.ylim(0,100)
	
	anim = animation.FuncAnimation(fig, animate, frames=200, repeat=True)
	anim.save('x.gif')
	
	
	