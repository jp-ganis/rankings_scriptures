import statistics
import json
import csv
import dateutil.parser as dp

import better_faction_wins as bfw
import better_player_wins as bpw

def easy_mean(l):
	if len(l) == 0: return -0.01
	else: return statistics.mean(l)

def x_outta_y(l):
	return f'{l.count(1):4} /{len(l):4}'

def get_underdog_factions(matchup_data):
	pelos = bpw.get_player_elos()
	felos = bfw.get_faction_elos()
	
	print()
	print()
	print('-'*100)
	print()


	fuf = {}

	for m in matchup_data:
		p1,f1,p2,f2,windex = m

		wp = [(p1,f1),(p2,f2)][windex]
		lp = [(p1,f1),(p2,f2)][not windex]

		wf = wp[1]
		lf = lp[1]
		wp = wp[0]
		lp = lp[0]

		for f in [wf,lf]:
			if f not in fuf:
				fuf[f] = {"favoured":[],"unfavoured":[],"neutral":[]}

		diff = pelos[wp].mu - pelos[lp].mu

		if abs(diff) < 1:
			fuf[wf]["neutral"].append(1)
			fuf[lf]["neutral"].append(0)

		elif diff > 0:
			fuf[wf]["favoured"].append(1)
			fuf[lf]["unfavoured"].append(0)

		elif diff < 0:
			fuf[wf]["unfavoured"].append(1)
			fuf[lf]["favoured"].append(0)

	fuf = {k:v for k,v in sorted(fuf.items(), key=lambda i: easy_mean(i[1]["unfavoured"]), reverse=True)}

	for f in fuf:
		if sum([len(fuf[f][e]) for e in fuf[f]]) < 40: continue
		
		fv = x_outta_y(fuf[f]["favoured"])
		u = x_outta_y(fuf[f]["unfavoured"])
		n = x_outta_y(fuf[f]["neutral"])

		print(f'{f:35}\t{fv:15}\t{n:15}\t{u:15}')

def faction_determined_wins(matchup_data):
	pelos = bpw.get_player_elos()
	felos = bfw.get_faction_elos()
	
	print()
	print()
	print('-'*100)
	print()


	fuf = {}

	s = 0
	sx =0
	seen = set({})
	for m in matchup_data:

		p1,f1,p2,f2,windex = m
		if f1 not in felos or f2 not in felos: continue 

		if str(m) in seen: continue
		seen.add(str(m))

		wp = [(p1,f1),(p2,f2)][windex]
		lp = [(p1,f1),(p2,f2)][not windex]

		wf = wp[1]
		lf = lp[1]
		wp = wp[0]
		lp = lp[0]


		pdiff = pelos[wp].mu - pelos[lp].mu
		fdiff = felos[wf].mu - felos[lf].mu

		if abs(pdiff) < 0.05 * pelos[lp].mu:
			if fdiff > 0: s+=1
			sx += 1
	print(s,sx,s/sx)
	print(len(seen))


if __name__ == '__main__':
	with open("output_data_files/tabletop_matchup_data.json", newline='', encoding='utf-8') as json_file:
		matchup_data = json.load(json_file)

	get_underdog_factions(matchup_data)
	faction_determined_wins(matchup_data)
