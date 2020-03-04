from matplotlib import pyplot as plt
import numpy as np
import statistics
import json

def go():
	with open('output_data_files/recent_events/datahub_player_data.json') as json_file:
		pdata = json.load(json_file)
		
	with open('output_data_files/recent_events/datahub_faction_data.json') as json_file:
		fdata = json.load(json_file)
	
	fs = statistics.stdev([fdata[f]["mean_gaussian_score"]**2 for f in fdata])
	
	print(fs)
	
	
if __name__ == '__main__':
	go()
	