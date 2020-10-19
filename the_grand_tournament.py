import random
import json
import csv

def d6(d=6):
	return random.randint(0,d)

def get_weapon_stats(unit):
	weapon_stats = [stat for stat in unit if stat[0] == 'w' and unit[stat] != 0]
	weapon_stats.remove("wounds")
	weapon_stats.append("save")
	
	return weapon_stats
		
def attack(unit_a, unit_b):
	wa = get_weapon_stats(unit_a)
	wb = get_weapon_stats(unit_b)
	
	da = 0
	db = 0
	
	unit_a[wa[-1]], unit_b[wa[-1]] = unit_b[wa[-1]] ,unit_a[wa[-1]]
	
	gotrek = False
	
	us = [unit_a, unit_b]
	ds = [0, 0]
	for n, w in enumerate([wa, wb]):
		u = us[n]
		gotrek = us[not n]["unit name"] == "gotrek"

		base_save = int(u[w[-1]])

		pts = int(u["points"])
		
		iters = 10
		
		attacks = 1
		to_hit = 4
		to_wound = 4
		to_save = 7

		for j in range(iters):
			for i in range(1):#int(2000/pts)):
				for s in w:
					if "attacks" in s: attacks = int(u[s])
					if "hit" in s: to_hit = int(u[s])
					if "wound" in s: to_wound = int(u[s])
					if "rend" in s: to_save = base_save + abs(int(u[s]))
					if "damage" in s:
						damage = int(u[s])
						if gotrek: damage = 0.3333333333
						
						for a in range(attacks):
							hit = d6()
							wound = d6()
							save = d6()
							
							if hit >= to_hit and wound >= to_wound and save < to_save:
								ds[n] += damage
		ds[n] /= iters
							
	# print(f'{unit_a["unit name"]:35} {int(ds[0]):10}\tvs\t{unit_b["unit name"]:35} {int(ds[1]):10}')	
	return ds[0] > ds[1], ds[0]
	
def all_v_all(data):
	wins = {d["unit name"]:0 for d in data if d["unit name"] != gotrek}
	matchups = set([])
		
	print(len(data))
		
	s=0
	for d in data:
		for e in data:
			if d == e: continue
			try:
				if (e["unit name"],d["unit name"]) in matchups: continue
				if d["unit name"] != "gatebreaker": continue
				s+=1
				
				win = attack(d, e)
				if not win: input()
				
				
				if win: wins[d["unit name"]] += 1
				else: wins[e["unit name"]] += 1
				
				matchups.add((d["unit name"],e["unit name"]))
				
				print(f'{s:10} {int(s/143915*100):10}%', end = '\t\t\t')
			except Exception as e:
				print("!",e)
			
	print(s)
	
	wins = {k:v for k,v in sorted(wins.items(), key=lambda i: i[1], reverse=True)}
	
	for w in wins:
		try:
			print(f'{w:45} {wins[w]}')
		except Exception as e:
			print("!!",e)
			
def bracket(data):
	wins = {d["unit name"]:0 for d in data}
	history = []
	
	random.shuffle(data)
	
	iters = 7
	max_rounds = 1
	
	for round in range(max_rounds):
		
		if round > 0:
			data = sorted(data, key=lambda d: wins[d["unit name"]])
	
		for i in range(0, len(data)-1, 2):
			print(round+1,i,end='\r')
			res = 0
			for j in range(iters):
				win = attack(data[i], data[i+1])
				if win: res += 1
			history.append((round+1,data[i]["unit name"], data[i+1]["unit name"], int(res/iters > 0.5)))
			if res/iters > 0.5: wins[data[i]["unit name"]] += 1
			else: wins[data[i+1]["unit name"]] += 1
		
		wins = {k:v for k,v in sorted(wins.items(), key=lambda i:i[1], reverse=True)}	
		
		# print()
		# print()
		# print(f'Round {round+1}')
		# for w in wins:
			# if wins[w] > round:
				# print(f'{w:45} {wins[w]}')
				
	
		
	wins = {k:v for k,v in sorted(wins.items(), key=lambda i:i[1], reverse=True)}	
	
	# print()
	# print()
	# print(f'Round {round+1}')
	# for w in wins:
		# print(f'{w:45} {wins[w]}-{(round+1)-wins[w]}')
		
	with open('bracket_results.csv', mode='w') as file:
		writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		for h in history:
			writer.writerow(h)
			
	return history
	
def round2(data):
	with open('metabreakers/data/scrollodrome.json') as json_file:
		b = json.load(json_file)
		
	ddict = {d["unit name"]: d for d in data}
	results = []
		
	for i in range(0, len(b)-1, 2):
		p1 = b[i]["winner"]
		p2 = b[i+1]["winner"]
		win=attack(ddict[p1], ddict[p2])
		winner = [p2,p1][win]
		results.append({"p1":p1, "p2":p2, "winner":winner})
		
	return results
	
if __name__ == '__main__':
	with open('hand_scrolls.json',encoding='utf-8') as json_file:
		data = json.load(json_file)
		data = [d for d in data if d["unit name"] != 0]

	ddict = {d["unit name"]: d for d in data}
	
	import re
	failures = []
	with open('scrollodrome.txt', encoding='utf-8') as file:	
		for l in file.readlines():
			try:
				m = re.findall(r'Player Name: (.*)<b', l)
				n = re.findall(r'Achievement ID: (.*)</div', l)
				o = re.findall(r'EVENT_NAME=<<(.*)>en>', l)
				date = re.findall(r'EVENT_DATE=<<(.*)>ey>', l)
				
				print(f'complete_achievement( a["{m[0]}"]["{n[0]}"], "{o[0]}", "{date[0]}" )')
			except Exception as e:
				print(len(failures))
				failures.append(f'{type(e)} {e} {l}')
				
		print()
		for f in failures:
			print(f)
			
		
		
