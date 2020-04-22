import json
from datahub import get_player_independent_faction_average as pifa

if __name__ == '__main__':
	with open("output_data_files/recent_events/datahub_faction_data.json", newline='', encoding='utf-8') as json_file:
		fdata = json.load(json_file)
		
		
	for f in fdata:
		md = fdata[f]["mean_delta"]
		mgs = fdata[f]["mean_gaussian_score"]
		pop = len(fdata[f]["events"])
		r = mgs/pop
		fdata[f]["r"] = r
	
	fdata = {k:v for k,v in sorted(fdata.items(), key=lambda i: i[1]["r"], reverse=True)}
	
	for f in fdata:
		if len(fdata[f]["events"]) < 25: continue
		md = fdata[f]["mean_delta"]
		mgs = fdata[f]["mean_gaussian_score"]
		pop = len(fdata[f]["events"])
		r = mgs/pop
		print(f'{f:35} {md:5.1f}\t{mgs:5.1f}\t{r:5.3f}')
		
		