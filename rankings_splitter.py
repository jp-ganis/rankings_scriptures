import csv

prefixes = ["gaussian_rankings", "metabreaker_rankings", "northern_rankings"]
rank_one_titles = {prefixes[0]: "Rank 1", prefixes[1]: "Underdog Alpha", prefixes[2]: "Rank 1"}
suffixes = ["_top1", "_top15", "_16plus"]

pigmar_data_path = "metabreakers/data"

for p in prefixes:
	with open(f'{p}.csv') as csvfile:
		readCSV = csv.reader(csvfile, delimiter=',')
		row_index = 1
		
		## clear previous file contents
		for s in suffixes:
			open(f'{pigmar_data_path}/{p}{s}.csv', 'w').close()
		
		for row in readCSV:
			if row_index == 1:
				with open(f'{pigmar_data_path}/{p}{suffixes[0]}.csv', mode='a', newline='') as split_file:
					writer = csv.writer(split_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
					writer.writerow([rank_one_titles[p]]+row[1:])
		
			elif row_index <= 16:
				with open(f'{pigmar_data_path}/{p}{suffixes[1]}.csv', mode='a', newline='') as split_file:
					writer = csv.writer(split_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
					writer.writerow([row_index]+row[1:])
			
			else:
				with open(f'{pigmar_data_path}/{p}{suffixes[2]}.csv', mode='a', newline='') as split_file:
					writer = csv.writer(split_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
					writer.writerow([row_index]+row[1:])
				
		
			row_index += 1
			