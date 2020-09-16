import statistics
import json
import csv

if __name__ == '__main__':

	with open('output_data_files/all_events/datahub_faction_data.json') as json_file:
		fdata = json.load(json_file)
		
		
	
	hof_month = {}
	
	with open('output_data_files/meta_history.csv') as csvfile:
		readCSV = csv.reader(csvfile, delimiter=',')
		for row in readCSV:
			if int(row[3]) < 3: continue
			
			f = row[1]
			
			if f not in hof_month:
				hof_month[f] = {"month":None, "score":0}
			
			s = float(row[2])
			d = row[0]
			
			if s > hof_month[f]["score"]:
				hof_month[f]["month"] = d
				hof_month[f]["score"] = s
				
			
	hof_month = {k:v for k,v in sorted(hof_month.items(), key=lambda i:i[1]["score"], reverse=True)}
	
	for f in hof_month:
		print(f'{hof_month[f]["month"]},{f},{hof_month[f]["score"]}')
			
			 
		
		
		