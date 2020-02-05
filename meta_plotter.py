import matplotlib.pyplot as plt 
import matplotlib
import numpy as np
import csv			
				
				
if __name__ == '__main__':
	font = {'family' : 'normal','size': 5}
	matplotlib.rc('font', **font)
	
	m2 = []
	y2 = []
	y3 = []
	
	scores = []
	counts = []
	
	faction = "Ironjawz"
	with open('data_files/meta_history.csv') as csvfile:
		readCSV = csv.reader(csvfile, delimiter=',')
		for row in readCSV:
			if faction in row[1]:
				m2.append(row[0].replace('20',''))
				
				scores.append(float(row[2]))
				counts.append(float(row[3])+30)
				
				y2.append(float(sum(scores)/len(scores)))
				y3.append(float(sum(counts)/len(counts)))
					
	y3.reverse()
	
	y2.reverse()
	m2.reverse()
	
	plt.plot(m2,y2)
	plt.plot(m2,y3)
	
	axes = plt.gca()
	# axes.set_ylim([0,100])

	plt.xlabel('date') 
	plt.ylabel('average event score') 
	plt.title(str(faction)) 

	plt.show() 
			