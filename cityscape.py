from collections import defaultdict
from datetime import datetime
import statistics
import json
import csv

import sys

if __name__ == '__main__':
	with open("output_data_files/all_global_events/datahub_event_data.json", newline='', encoding='utf-8') as json_file:
		edata = json.load(json_file)
	edata.reverse()
		
	with open("output_data_files/all_global_events/datahub_faction_data.json", newline='', encoding='utf-8') as json_file:
		fdata = json.load(json_file)
		
	fdata = {k:fdata[k] for k in fdata if len(fdata[k]["events"]) > 30}
	del fdata["-"]
	del fdata["UNKNOWN_ARMY"]
		
	book_releases = []
	with open('input_data_files/book_releases.csv') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		for row in csv_reader:
			book_releases.append( datetime.strptime(row[1].strip(), '%d %b %Y') )
			
	data = {d:{f:{"counts":0,"scores":[]} for f in fdata} for d in book_releases}
	
	today = 0
	
	for event in edata:
		date = datetime.strptime(event["std_date"], '%d %b %Y')
		
		if date > book_releases[today]:
			today = min(len(book_releases)-1, today+1)
	
		section = book_releases[today]
		for e in event["ladder"]:
			faction = e["faction"]
			if faction not in fdata: continue
			
			data[section][faction]["counts"] += 1
			data[section][faction]["scores"].append(e["gaussian_score"])
		
	with open('scape.csv', 'w', newline='') as file:
		writer = csv.writer(file)
		for d in data:
			for f in data[d]:
				if data[d][f]["counts"] < 1: continue
				writer.writerow([str(d),f,data[d][f]["counts"],statistics.mean(data[d][f]["scores"])])