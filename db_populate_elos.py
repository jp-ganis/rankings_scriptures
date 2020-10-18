from collections import defaultdict
import dateutil.parser as dp
import trueskill as ts
import check_aliases
import statistics
import dataset
import json

def populate_player_elos(db):
	if 'player_elo' in db.tables: db['player_elo'].drop()
	if 'faction_elo' in db.tables: db['faction_elo'].drop()
	
	player_elos = defaultdict(ts.Rating)
	faction_elos = defaultdict(ts.Rating)
	
	print("fetching unique games from db")
	gs = list(db['game'].distinct('winner_name','loser_name','winner_faction','loser_faction','event_id'))
	
	for g in gs:
		if gs.index(g) % 100 ==0: print(gs.index(g),end='\r')
		winner = g['winner_name']
		loser = g['loser_name']
		
		win_f = g['winner_faction']
		lose_f = g['loser_faction']
	
		player_elos[winner], player_elos[loser] = ts.rate_1vs1(player_elos[winner], player_elos[loser])
		faction_elos[win_f], faction_elos[lose_f] = ts.rate_1vs1(faction_elos[win_f], faction_elos[lose_f])
		
	player_elos = {k:v for k,v in sorted(player_elos.items(), key=lambda i: i[1].mu, reverse=True)}
	faction_elos = {k:v for k,v in sorted(faction_elos.items(), key=lambda i: i[1].mu, reverse=True)}
		
	p_updates = [dict(player=p, mu=player_elos[p].mu, sigma=player_elos[p].sigma) for p in player_elos]
	f_updates = [dict(faction=f, mu=faction_elos[f].mu, sigma=faction_elos[f].sigma) for f in faction_elos]
	
	db['player_elo'].insert_many(p_updates)
	db['faction_elo'].insert_many(f_updates)
	
def investigate_player_elos(db):
	elos = defaultdict(ts.Rating)
	for p in db['player_elo']:
		elos[p['player']] = ts.Rating(p['mu'], p['sigma'])
			
	with open('output_data_files/all_global_events/datahub_event_data.json') as json_file:
		edata = json.load(json_file)
		
	edata.reverse()
	
	for e in edata:
		try:
			print(edata.index(e),len(edata),end='\r')
			new_ratings = ts.rate([(elos[check_aliases.predefined_aliases(p["player_name"])],) for p in e["ladder"]])
			
			for n,e in enumerate(e["ladder"]):
				elos[check_aliases.predefined_aliases(e["player_name"])] = new_ratings[n][0]
		except:
			break
			
			
	rs = {}
	for p in elos:
		rs[p] = elos[p].mu/elos[p].sigma
	
	rs = {k:v for k,v in sorted(rs.items(), key=lambda i: i[1], reverse=True)}
	
	f = open("ALLELOS.txt", "w", encoding='utf-8')
	
	for n,r in enumerate(rs):
		s = f'{n:10} {r:35} {int(rs[r]*100)}\n'
		f.write(s)
		# print()
		
	f.close()
	
def investigate_faction_elos(db):
	elos = defaultdict(ts.Rating)
	for p in db['faction_elo']:
		elos[p['faction']] = ts.Rating(p['mu'], p['sigma'])
			
	with open('output_data_files/all_uk_events/datahub_event_data.json') as json_file:
		edata = json.load(json_file)
		
	edata.reverse()
	
	for e in edata:
		try:
			print(edata.index(e),len(edata),end='\r')
			if dp.parse(e["date"]) < dp.parse("Jan 2019"): continue
			new_ratings = ts.rate([(elos[check_aliases.predefined_faction_aliases(p["faction"])],) for p in e["ladder"]])
			
			for n,e in enumerate(e["ladder"]):
				elos[check_aliases.predefined_faction_aliases(e["faction"])] = new_ratings[n][0]
		except:
			break
			
	rs = {}
	for p in elos:
		if elos[p].sigma > 1: continue
		rs[p] = elos[p].mu/abs(elos[p].sigma)
	
	rs = {k:v for k,v in sorted(rs.items(), key=lambda i: i[1], reverse=True)}
	
	for n,r in enumerate(rs):
		s = f'{n:10} {r:35} {int(rs[r]*100)}'
		print(s)
		
	
if __name__ == '__main__':
	db = dataset.connect("sqlite:///__tinydb.db")
	ts.setup(backend='mpmath')
	
	investigate_faction_elos(db)
	# populate_player_elos(db)


		
	
		
	
		
