from matplotlib import pyplot as plt
import numpy as np
import statistics
import json

def go():
	with open('output_data_files/recent_events/datahub_player_data.json') as json_file:
		pdata = json.load(json_file)
		
	with open('output_data_files/recent_events/datahub_faction_data.json') as json_file:
		fdata = json.load(json_file)
	
	fs = {f:fdata[f]["mean_gaussian_score"] for f in fdata if len(fdata[f]["events"]) > 3}
	
	for f in fs:
		print(f)
	for f in fs:
		print(fs[f])
		# print(f,fs[f])
	
	
if __name__ == '__main__':
	go()
	