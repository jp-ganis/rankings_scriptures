from db_state_of_the_meta import get_score_for_date
from scipy import stats

import json
import statistics


if __name__ == '__main__':
	with open("output_data_files/listbot_unit_points.json", newline='', encoding='utf-8') as json_file:
		data = json.load(json_file)
		
		
	factions = ["gloomspite", "bonereapers", "khaine", "sylvaneth", "beasts of chaos", "mawtribes", "kharadron", "cities of sigmar", "nighthaunt", "fyreslayers", "slaanesh", "tzeentch"]
	factions += ["flesh", "slaves", "deepkin", "legions of nagash", "ironjawz", "seraphon", "sylvaneth", "nurgle"]
		
	funits = {f:[] for f in factions}
		
	for f in factions:		
		for d in data:
			if f in data[d][-1]:
				funits[f].append(data[d])
				
				
	scrolls = {f:0 for f in factions}
	
	for f in funits:
		scrolls[f] = int(statistics.mean([-(int(u[-2]) - u[0]) for u in funits[f]]))
		
	scrolls = {k:v for k,v in sorted(scrolls.items(), key=lambda i:i[1], reverse=True)}
	
		
	meta_scores = {}
	meta_scores["kharadron"] = 65
	meta_scores["ironjawz"] = 62
	meta_scores["khaine"] = 62
	meta_scores["seraphon"] = 62
	meta_scores["tzeentch"] = 60
	meta_scores["deepkin"] = 56
	meta_scores["slaves"] = 54
	meta_scores["nurgle"] = 53
	meta_scores["cities of sigmar"] = 53
	meta_scores["slaanesh"] = 51
	meta_scores["fyreslayers"] = 48
	meta_scores["gloomspite"] = 45
	meta_scores["beasts of chaos"] = 38
	meta_scores["nighthaunt"] = 31
	meta_scores["sylvaneth"] = 28
	
	meta_scores["bonereapers"] = 50
	meta_scores["mawtribes"] = 44
	meta_scores["flesh"] = 41
	meta_scores["legions of nagash"] = 38
	
	
	
	z_scores = stats.zscore([meta_scores[f] for f in meta_scores])
	
	for n,f in enumerate(meta_scores):
		meta_scores[f] = int(z_scores[n]*100)
		
		
	z_scores = stats.zscore([scrolls[f] for f in scrolls])
	
	for n,f in enumerate(scrolls):
		scrolls[f] = int(z_scores[n]*100)
	
	scrolls["deepkin"] = 1
		
	for f in scrolls:
		meta_scores[f] = meta_scores[f] - scrolls[f]
	
	quadrants = {}
	
	for f in scrolls:
		x = meta_scores[f]
		y = scrolls[f]
		
		if x > 0 and y > 0:
			quadrant = "A - Strong Abilities, Strong Scrolls"
			
		elif x > 0 and y < 0: 
			quadrant = "B - Strong Abilities, Weak Scrolls"
			
		elif x < 0 and y > 0: 
			quadrant = "C - Weak Abilities, Strong Scrolls"
			
		elif x < 0 and y < 0: 
			quadrant = "D - Generally Garbage"
			
		quadrants[f] = quadrant
		
	quadrants = {k:v for k,v in sorted(quadrants.items(), key=lambda i:i[1])}
	
	print()
	for f in quadrants:
		print(f'\t{f:35} {quadrants[f]}')
	print()
	
		