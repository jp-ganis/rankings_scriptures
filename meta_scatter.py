import matplotlib.pyplot as plt 
import matplotlib
import numpy as np
import random
import csv			
from datetime import datetime
				
def plot_all_factions():
	months = {}
	faction_scores = {}
	faction_counts = {}
	
	tmp_scores = {}
	tmp_counts = {}
	tmp_deltas = {}
	
	faction_deltas = {}
	
	factions = set([])
	
	relevant = ["Idoneth Deepkin"]
	
	with open('output_data_files/meta_history.csv') as csvfile:
		readCSV = csv.reader(csvfile, delimiter=',')
		for row in readCSV:
			faction = row[1]
			factions.add(faction)
			
			month = "XX"
			if '2020' in row[0]:
				month = row[0].replace('2020','20')
			else:
				month = row[0].replace('20','')
				
			if month not in months:
				months[month] = []
				
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
			
			if faction in relevant:
				cc = (relevant.index(faction)/len(relevant))
				plt.scatter(month, float(row[2]), color=(cc,0,0,1), label=faction)
				
			
	
	font = {'size': 5}
	matplotlib.rc('font', **font)
	# plt.legend(loc="upper left")
	plt.show()

	
	
if __name__ == '__main__':
	plot_all_factions()