from matplotlib import pyplot as plt
import networkx as nx
import json



def preprocess_list(l):
	seen = []
	new_l = []
	
	ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])
	
	for u in l:
		if u in seen:
			u = f'{ordinal(seen.count(u)+1)} {u}'
	
		seen.append(u)
		new_l.append(u)
		
	return new_l	

if __name__ == '__main__':
	with open('input_data_files/AoS_list_data.json',encoding='utf-8') as json_file:
		data = json.load(json_file)
	

	lists = []
	
	lists.append(["No Battalion", "Katakros", "Liege Kavalos", "20 x Mortek Guard", "20 x Mortek Guard", "5 x Deathriders", "Harvester", "Mortek Crawler", "Mortek Crawler"])
	lists.append(["Mortek Shield Corps", "Mortek Ballistari", "Liege Kavalos", "Soulmason", "Boneshaper", "20 x Mortek Guard", "10 x Mortek Guard", "10 x Mortek Guard", "10 x Mortek Guard", "Harvester", "Mortek Crawler", "Mortek Crawler", "Bone-tithe Shrieker", "Soulstealer Carrion"])
	lists.append(["Mortek Shield Corps", "Soulmason", "Boneshaper", "Boneshaper", "20 x Mortek Guard", "20 x Mortek Guard", "10 x Mortek Guard", "6 x Stalkers", "Mortek Crawler", "Mortek Crawler", "Bone-tithe Shrieker"])
	lists.append(["No Battalion", "Katakros", "Soulmason", "20 x Mortek Guard", "20 x Mortek Guard", "40 x Mortek Guard", "Mortek Crawler", "Mortek Crawler"])
	lists.append(["No Battalion", "Boneshaper", "Nagash", "40 x Mortek Guard", "10 x Mortek Guard", "10 x Mortek Guard", "Harvester", "Umbral Spellportal", "Suffocating Gravetide"])
	lists.append(["No Battalion", "Liege Kavalos", "Nagash", "Arkhan the Black" "20 x Mortek Guard", "10 x Mortek Guard", "10 x Mortek Guard", "Bone-tithe Shrieker"])
	lists.append(["Mortek Shield-corps", "Boneshaper", "Liege Kavalos", "Arkhan the Black", "40 x Mortek Guard", "10 x Mortek Guard", "10 x Mortek Guard", "Mortek Crawler", "Mortek Crawler", "Bone-tithe Shrieker", "Geminids"])
	lists.append(["Mortek Shield-corps", "Katakrosian Deathglaive", "Liege Kavalos", "Boneshaper", "Soulmason", "20 x Mortek Guard", "10 x Mortek Guard", "10 x Mortek Guard", "3 x Stalkers", "3 x Stalkers", "2 x Harbingers", "Harvester"])
	lists.append(["No Battalion", "Liege Kavalos", "Nagash", "15 x Deathriders", "5 x Deathriders", "5 x Deathriders", "Bone-tithe Shrieker", "Emerald Lifeswarm"])
	
	lists = []
	
	faction = "Fyreslayers"
	
	for p in data:
		if not "units" in data[p]["armyListData"]: continue
		if data[p]["armyListData"]["units"] is None: continue
		if data[p]["armyListData"]["allegiance"] != faction: continue
		
		units = [u["name"] for u in data[p]["armyListData"]["units"]]
		if len(units) == 0: continue
		
		lists.append(units)
	
	for i,l in enumerate(lists):
		lists[i] = preprocess_list(l)
	
	g = nx.Graph()
	
	for l in lists:
		for u in l:
			for v in l:
				if u != v:
					g.add_edge(u,v)
					
					
	pos = nx.spring_layout(g)
	betCent = nx.betweenness_centrality(g, normalized=True, endpoints=True)
	node_color = [20000.0 * g.degree(v) for v in g]
	node_size =  [v * 10000 for v in betCent.values()]
	plt.figure(figsize=(20,20))
	nx.draw_networkx(g, pos=pos, with_labels=True,
	node_color=node_color,
	node_size=node_size )
	
	# plt.show()
	
	nx.write_gexf(g, f'bcp_{faction}.gexf')