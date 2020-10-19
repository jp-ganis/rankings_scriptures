import statistics
import random
import json

import the_grand_tournament as tgt


def get_all_legal_lists(scrolls):
	iters = 10000
	
	lists = set({})
	
	for i in range(iters):
		print(i,end='\r')
		list = []
		
		while sum([l['points'] for l in list]) < 2000:
			list.append(random.choice(scrolls))
		
		lists.add("<div>".join([u['unit name'] for u in list[:-1]]))
		
	print()
	print(len(lists))
	
	return lists
	

if __name__ == '__main__':
	with open('hand_scrolls.json',encoding='utf-8') as json_file:
		data = json.load(json_file)
	data = {u["unit name"]: u for u in data}

	data["mancrusher"]["bodies"] = 10
	data["kraken-eater"]["bodies"] = 20
	data["warstomper"]["bodies"] = 20
	data["gatebreaker"]["bodies"] = 20
	
	scrolls = [data["mancrusher"], data["kraken-eater"], data["gatebreaker"], data["warstomper"]]
	
	lists = list(get_all_legal_lists(scrolls))
	newlists = []
	
	for l in lists:
		l = l.split('<div>')
		units = len(l)
		wounds = sum([data[u]['wounds'] for u in l])
		bodies = sum([data[u]['bodies'] for u in l])
		
		amalgam =0
		
		for d in l:
			d = data[d]
			_, amalgam = tgt.attack(d, data["mancrusher"])
			
		l += [units, wounds,bodies,amalgam]
		newlists.append(l)
		
	
	w = [1, 10, -1, 10]
	newlists = sorted(newlists, key=lambda l: l[-3]*w[0] + l[-2]*w[1] + l[-1]*w[0] + l[-4]*w[3], reverse=True)
	
	for l in newlists[:10]:
		print(l[-3]*w[0] + l[-2]*w[1] + l[-1]*w[0])
		for u in l:
			print('\t',u)
		print()
		print()