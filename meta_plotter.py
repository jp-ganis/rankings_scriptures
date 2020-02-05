import matplotlib.pyplot as plt 
import matplotlib
import numpy as np
import csv			
				
def plot_all_factions():
	months = {}
	faction_scores = {}
	faction_counts = {}
	
	tmp_scores = {}
	tmp_counts = {}
	
	factions = set([])
	
	with open('data_files/meta_history.csv') as csvfile:
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
				
				tmp_scores[faction] = []
				tmp_counts[faction] = []
				
			tmp_scores[faction].append(float(row[2]))
			tmp_counts[faction].append(float(row[3]))
				
				
			faction_scores[faction][month] = float(sum(tmp_scores[faction]) / len(tmp_scores[faction])) 
			faction_counts[faction][month] = float(sum(tmp_counts[faction]) / len(tmp_counts[faction]))
			
	
	font = {'size': 5}
	matplotlib.rc('font', **font)
	
	
	faction_plots = {}
	
	for f in factions:
		if len(faction_scores[f]) < 10: continue
		faction_plots[f] = [0]
	
	for month in months:
		for f in faction_plots:
			if f not in months[month]:
				if faction_plots[f][-1] > 0: 
					faction_plots[f].append(faction_plots[f][-1])
				else:
					faction_plots[f].append(np.nan)
			else:
				faction_plots[f].append(faction_scores[f][month])
				
				
	months = list(months.keys())
	months.reverse()
	
	relevant = ["Stormcast Eternals", "Sylvaneth"]
	
	for fp in faction_plots:
		if fp in relevant:
			ys = faction_plots[fp][1:]
			ys.reverse()
			plt.plot(months[-12:-1], ys[-12:-1], label=fp)
		
		
	plt.xlabel('date') 
	plt.ylabel('average event score') 
	plt.title(str(faction)) 
	
	plt.legend(loc="upper left")

	plt.show() 
		
	
	
if __name__ == '__main__':
	plot_all_factions()


	# font = {'size': 5}
	# matplotlib.rc('font', **font)
	
	# m2 = []
	# y2 = []
	# y3 = []
	
	# scores = []
	# counts = []
	
	# faction = "Ironjawz"
	# with open('data_files/meta_history.csv') as csvfile:
		# readCSV = csv.reader(csvfile, delimiter=',')
		# for row in readCSV:
			# if faction in row[1]:
				# m2.append(row[0].replace('20',''))
				
				# scores.append(float(row[2]))
				# counts.append(float(row[3])+30)
				
				# y2.append(float(sum(scores)/len(scores)))
				# y3.append(float(sum(counts)/len(counts)))
					
	# y3.reverse()
	
	# y2.reverse()
	# m2.reverse()
	
	# plt.plot(m2,y2)
	# plt.plot(m2,y3)
	
	# axes = plt.gca()
	# axes.set_ylim([0,100])

	# plt.xlabel('date') 
	# plt.ylabel('average event score') 
	# plt.title(str(faction)) 

	# plt.show() 
			