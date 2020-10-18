import Levenshtein
import dataset


def get_player_aliases(db):
	wnames = db['game'].distinct('winner_name')
	wnames = [list(n.values())[0] for n in wnames]
	
	lnames = db['game'].distinct('loser_name')
	lnames = [list(n.values())[0] for n in lnames]
	
	names = wnames+lnames
	
	ls = {}
	aliases = {}
	
	for n in names:
		for m in names:
			if n != m:
				ls[(n,m)] = Levenshtein.distance(n,m)
			
	ls = {k:v for k,v in sorted(ls.items(), key=lambda i: i[1])}
	
	for l in ls:
		if ls[l] < 3 and len(l[0]) > 7:
			if "jnr" in l[0].lower() and "snr" in l[1].lower(): continue
			if "jnr" in l[1].lower() and "snr" in l[0].lower(): continue
			
			if "jr" in l[0].lower() and "sr" in l[1].lower(): continue
			if "jr" in l[1].lower() and "sr" in l[0].lower(): continue
			
			if "ian" in l[0].lower() and "dan" in l[1].lower(): continue
			if "ian" in l[1].lower() and "dan" in l[0].lower(): continue
			
			if "rawson" in l[0].lower() and "janson" in l[1].lower(): continue
			if "rawson" in l[1].lower() and "janson" in l[0].lower(): continue
		
			if l[0] not in aliases: aliases[l[0]] = [l[0]]
			if l[1] not in aliases: aliases[l[1]] = [l[1]]
		
			aliases[l[0]].append(l[1])
			aliases[l[1]].append(l[0])
			
	for name in aliases:
		aliases[name] = sorted(aliases[name])
		
	return aliases

def predefined_faction_aliases(name):
	name = name.lower().strip().replace('\t',' ')
	
	if "tzeentch" in name:
		name = "disciples of tzeentch"
		
	elif "khorne" in name:
		name = "blades of khorne"
		
	elif "nurgle" in name:
		name = "maggotkin of nurgle"
		
	elif "slaanesh" in name:
		name = "hedonites of slaanesh"
		
	elif "daughters" in name or "khaine" in name:
		name = "daughters of khaine"
		
	elif "cities" in name or "sigmar" in name or "hallowheart" in name or "greywater" in name or "tempest" in name:
		name = "cities of sigmar"
		
	elif "flesh" in name:
		name = "flesh eater courts"
	
	elif "skaven" in name:
		name = "skaven"
	
	elif "unknown" in name:
		name = "-"

	return name.title()

def predefined_aliases(name):
	name = name.lower().strip().replace('\t',' ')
	
	if "ganis" in name:
		name = "Jp Ganis"
		
	elif "laurie" in name and "h" in name and "w" in name:
		name = "Laurie Huggett-Wilde"
	
	elif "stu" in name and "west" in name:
		name = "stu west"
		
	elif "phil" in name and "mcguinness" in name:
		name = "Phil McGuinness"
		
	elif name == "john bayliss":
		name = "John B"
		
	return name.title()
	
def populate_player_table(db):
	print("populating players...")
	if 'player' in db.tables: db['player'].drop()
	
	players_to_insert=[]
	
	for idx,g in enumerate(db['game']):
		print(f'{idx}',end='\r')
		names = [g['winner_name'], g['loser_name']]
		
		for n in names:
			new_name = predefined_aliases(n)
			
			if new_name != n:
				data = dict(id=g['id'], winner_name=predefined_aliases(g['winner_name']), loser_name=predefined_aliases(g['loser_name']))
				db['game'].update(data, ['id'])
			
			n = new_name
			
			if n not in players_to_insert:
				players_to_insert.append(n)
				
	db['player'].insert_many([dict(name=p) for p in players_to_insert])
	print()
	

def populate_faction_table(db):
	if 'faction' in db.tables: db['faction'].drop()
	print("populating factions...")
	
	factions_to_insert=[]
	
	for idx,g in enumerate(db['game']):
		print(f'{idx}',end='\r')
		names = [g['winner_faction'], g['loser_faction']]
		
		for n in names:
			new_name = predefined_faction_aliases(n)
			
			if new_name != n:
				data = dict(id=g['id'], winner_faction=predefined_faction_aliases(g['winner_faction']), loser_faction=predefined_faction_aliases(g['loser_faction']))
				db['game'].update(data, ['id'])
			
			n = new_name
			
			if n not in factions_to_insert:
				factions_to_insert.append(n)
				
	db['faction'].insert_many([dict(name=f) for f in factions_to_insert])
	print()
		