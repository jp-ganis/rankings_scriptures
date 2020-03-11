from collections import defaultdict
import statistics
import json

def get_matchups(data):
	player_matchups = []
	
	for p in data:
		if "opponents" not in data[p]: continue
		
		for i,q in enumerate(data[p]["opponents"].values()):
			if q not in data: continue
			if i >= 5: continue
			
			player_matchups.append((p,q,data[p]["record"][i]))
			
	return player_matchups
	
def faction_matchups(data):
	player_matchups = get_matchups(data)
	
	faction_matchups = defaultdict(list)
	
	for m in player_matchups:
		f1 = data[m[0]]["armyListData"]["allegiance"]
		f2 = data[m[1]]["armyListData"]["allegiance"]
		
		if f1 is None or f2 is None: continue
		
		f1 = process_faction(f1)
		f2 = process_faction(f2)
			
		if (f2,f1) in faction_matchups:
			w = int(m[2] == "L")
			faction_matchups[(f2,f1)].append(w)
		else:
			w = int(m[2] == "W")
			faction_matchups[(f1,f2)].append(w)
		
	faction_matchups = {k:v for k,v in sorted(faction_matchups.items(), key=lambda i: statistics.mean(i[1]), reverse=True)}
		
	print()
	
	for f in faction_matchups:
		if len(faction_matchups[f]) < 10: continue
		print(f'\t{f[0]:25} {f[1]:25} ||| {statistics.mean(faction_matchups[f])*100:3.1f}%')
	print()
	print(len(faction_matchups))
	
def process_faction(f):
	f = f.replace('Allegiance: ','')
	f = f.strip()
	
	if '-' in f:
		f = f[:f.index('-')]
	
	return f
	
	
if __name__ == '__main__':
	with open('input_data_files/AoS_list_data.json',encoding='utf-8') as json_file:
		data = json.load(json_file)
		
	unit_winrates = defaultdict(list)
	
	faction = "Slaanesh"
		
	for p in data:
		if not "numWins" in data[p]: continue
		if not "units" in data[p]["armyListData"]: continue
		if data[p]["armyListData"]["units"] is None: continue
		if data[p]["armyListData"]["allegiance"] != faction: continue
		
		seen_count = defaultdict(int)
		for unit in data[p]["armyListData"]["units"]:
			seen_count[unit["name"]] += 1
			ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])
			ordinal = ordinal(seen_count[unit["name"]])
			
			u = ordinal+" "+unit["name"]
			unit_winrates[u].append(data[p]["numWins"]/len(data[p]["record"]))
			
			
	unit_winrates = {k:v for k,v in sorted(unit_winrates.items(),key=lambda i: statistics.mean(i[1])*len(i[1]),reverse=True)}
	
	for u in unit_winrates:
		print(f'{u:45} {statistics.mean(unit_winrates[u])*len(unit_winrates[u]):3.1f}')

	print()
	print()
	
	for p in data:
		if not "numWins" in data[p]: continue
		if not "units" in data[p]["armyListData"]: continue
		if data[p]["armyListData"]["units"] is None: continue
		if data[p]["armyListData"]["allegiance"] != faction: continue
		
		army = []
		
		seen_count = defaultdict(int)
		for unit in data[p]["armyListData"]["units"]:
			seen_count[unit["name"]] += 1
			
			ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])
			ordinal = ordinal(seen_count[unit["name"]])
			
			u = ordinal+" "+unit["name"]
			army.append(u)
			
		army = list(set(army))
		army = sorted(army, key=lambda i: int(statistics.mean(unit_winrates[i])*len(unit_winrates[i])), reverse=True)
		
		for u in army:
			print(u, int(statistics.mean(unit_winrates[u])*len(unit_winrates[u])))
			
		print()
		print()
			
		drop = []
		add = []
			
		max_sg = 3
		suggestions = 0
		for i,u in enumerate(unit_winrates):
			if suggestions >= max_sg: continue
			
			if u not in army:
				add.append(u)
				suggestions+=1
				drop.append(army[-i])
			
		
		for d in drop:
			print(f'Maybe consider dropping {d.replace("1st","")}')
			
		for a in add:
			print(f'Maybe consider adding {a.replace("1st","")}')
		
		break
	
		