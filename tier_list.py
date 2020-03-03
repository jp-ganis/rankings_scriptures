import statistics
import json

def go():
	with open('output_data_files/uk_events/datahub_player_data.json') as json_file:
		pdata = json.load(json_file)
	
	with open('output_data_files/2020_events/datahub_faction_data.json') as json_file:
		fdata = json.load(json_file)
		
	# del fdata["Hosts of Slaanesh"]
	# del fdata["UNKNOWN_ARMY"]
		
	counts = {}
	for f in fdata:
		counts[f] = len(fdata[f]["events"])
	print()
	
	gaussian_scores = {k:fdata[k]["mean_gaussian_score"] for k in fdata}
	gaussian_scores = {k:v for k,v in sorted(gaussian_scores.items(), key=lambda i:i[1],reverse=True)}
	
	for g in gaussian_scores:
		if g == "-": continue
		if counts[g] < 5: continue
		print(f'{g:35} {gaussian_scores[g]:.0f}')
	
if __name__ == '__main__':
	go()
	