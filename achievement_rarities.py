from collections import defaultdict
import json

def update_rarities_file():
	with open("metabreakers/data/achievement_data.json", newline='', encoding='utf-8') as json_file:
		adata = json.load(json_file)
		
	achievement_counts = {}
		
	for player in adata:
		for a in adata[player]:
			if a == "total_score": continue
			
			if a not in achievement_counts:
				achievement_counts[a] = 0
			
			if adata[player][a]["complete"]:
				achievement_counts[a] += 1
			
	achievement_counts = {k:v for k,v in sorted(achievement_counts.items(), key=lambda i: i[1], reverse=True)}
		
	with open(f'metabreakers/data/achievement_rarities.json', 'w') as json_file:
		json.dump(achievement_counts, json_file)
		
if __name__ == '__main__':
	with open("metabreakers/data/achievement_data.json", newline='', encoding='utf-8') as json_file:
		adata = json.load(json_file)
		
	achievement_counts = {}
		
	for player in adata:
		for a in adata[player]:
			if a == "total_score": continue
			
			if a not in achievement_counts:
				achievement_counts[a] = 0
			
			if adata[player][a]["complete"]:
				achievement_counts[a] += 1
			
	achievement_counts = {k:v for k,v in sorted(achievement_counts.items(), key=lambda i: i[1], reverse=True)}
		
	rarities = {}
		
	for a in achievement_counts:	
		pct = int(achievement_counts[a]/len(adata)*100)
		if pct < 1: pct = "<1"
		print(f'{a:55} {achievement_counts[a]:5}\t/{len(adata)} ({pct}%)')
		
	confirm = input("overwrite metabreakers data file? y/n ")
	if 'y' in confirm.lower():
		with open(f'metabreakers/data/achievement_rarities.json', 'w') as json_file:
			json.dump(achievement_counts, json_file)
	else:
		print("aborted")
		