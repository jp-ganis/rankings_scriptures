from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import dateutil.parser as dp
import db_check_aliases
import trueskill as ts
import gaussian_fitter
import scipy.stats
import statistics
import datetime
import dataset
import json
import glob
import csv

def get_gaussian_scores_for_finish(position, num_players, rounds):
	scores = []
	
	pts_scaler = 100
	
	c = 3.5
	increment = c / num_players
	
	multiplier = 1
	# if int(rounds) < 5: multiplier = 0.6
	
	pts = scipy.stats.norm(0, 1).cdf((c/2) - (increment * (position + 1)))
	pts *= pts_scaler * multiplier
		
	return pts

def get_winrate_for_finish(position, num_players, rounds):
	wins = gaussian_fitter.get_win_distribution(num_players, rounds)
	
	return wins[position]/rounds
	
def populate_trueskill_table(db):
	statement = 'SELECT DISTINCT event_name FROM ladder_position ORDER BY date'
	events = list(db.query(statement))
	
	elos = defaultdict(ts.Rating)
	inserts = []
	
	for counter,e in enumerate(events):
		try:
			print(counter,len(events), end='\r')
			event_name = e['event_name']
			if '"' in event_name: continue
			
			statement = f'SELECT DISTINCT player, faction, position, num_players, event_name, date, rounds FROM ladder_position WHERE event_name="{event_name}" ORDER BY position'
			positions = list(db.query(statement))
			
			if len(positions) < 5: continue
			
			new_ratings = ts.rate([(elos[p['faction']],) for p in positions])
			
			for n,p in enumerate(positions):
				elos[p['faction']] = new_ratings[n][0]
				inserts.append(dict( faction=p['faction'], mu=elos[p['faction']].mu, sigma=elos[p['faction']].sigma, date=p['date'] ))
		except Exception as e:
			print(type(e), e)
			print(f'skipped {e["event_name"]}')

	if 'trueskill' in db.tables: db['trueskill'].drop()
	db['trueskill'].insert_many(inserts)
	
def populate_ladder_table(db):
	if 'ladder_position' in db.tables: db['ladder_position'].drop()
	
	with open('output_data_files/all_uk_events/datahub_event_data.json') as json_file:
		edata = json.load(json_file)
	edata.reverse()
	
	event_files = glob.glob("input_data_files/tablesoup_data/*.csv")
	
	inserts = []
	
	for counter,file in enumerate(event_files):
		print(counter,len(event_files), end='\r')
		
		with open(file,encoding='utf-8') as f:
			for num_players, l in enumerate(f):
				pass
				
		
		with open(file, newline='', encoding='utf-8') as csvfile:
			reader = csv.reader(csvfile)
			## skip first row with event metadata
			for row in reader:
				event_name = row[1]
				event_date = dp.parse(row[2])
				rounds = row[3]
				break
			
			windist = gaussian_fitter.get_win_distribution(num_players, int(rounds))
			
			for n,row in enumerate(reader):
				player = db_check_aliases.predefined_aliases(row[0])
				faction = db_check_aliases.predefined_faction_aliases(row[1])
				
				if faction == "-": continue
				if faction == "UNKNOWN_ARMY": continue
				
				inserts.append(dict( player=player, faction=faction, position=n, sim_wins=windist[n], num_players=num_players, event_name=event_name, date=event_date, rounds=rounds ))
				
	print()
	for counter,e in enumerate(edata):
		print(counter,len(edata), end='\r')
		windist = gaussian_fitter.get_win_distribution(len(e["ladder"]), int(e["rounds"]))
		
		for n,p in enumerate(e["ladder"]):
			player = db_check_aliases.predefined_aliases( p["player_name"] )
			faction = db_check_aliases.predefined_faction_aliases( p["faction"] )
			
			if faction == "-": continue
			if faction == "UNKNOWN_ARMY": continue
			
			inserts.append(dict( player=player, faction=faction, position=n, sim_wins=windist[n], num_players=len(e["ladder"]), event_name=e["name"], date=dp.parse(e["date"]), rounds=e["rounds"] ))
	
	print()
	db['ladder_position'].insert_many(inserts)

def populate_tier_table(db):
	statement = f'SELECT DISTINCT player, faction, position, num_players, event_name, date, rounds FROM ladder_position ORDER BY date'
	all_positions = list(db.query(statement))
	
	scores = defaultdict(list)
	inserts = []
	
	for counter,lp in enumerate(all_positions):
		print(counter,len(all_positions), end='\r')
		rounds = int(lp['rounds'])
		if rounds < 5: continue
		
		s = get_gaussian_scores_for_finish(lp['position'], lp['num_players'], rounds)
		
		scores[lp['faction']].append(s)
		window_mean = statistics.mean( scores[lp['faction']][-10:] )
		
		inserts.append(dict( faction=lp['faction'], score=window_mean, count=len(scores[lp['faction']]), date=lp['date'] ))
		
	if 'tiers' in db.tables: db['tiers'].drop()
	db['tiers'].insert_many(inserts)
	
def plot_faction_performance(db, factions, earliest=None, resolution=30):
	fig, ax = plt.subplots()
	plt.setp(ax.xaxis.get_majorticklabels(), rotation=25)
	
	if earliest == None:
		earliest = dp.parse("1 Jan 2015")
	else:
		earliest = dp.parse(earliest)
		
	date = earliest
	dates = [date]
	
	while dates[-1] < datetime.datetime.now():
		date = dates[-1] + datetime.timedelta(days=resolution)
		dates.append(date)

	ys = [[] for _ in factions]
	
	for d in dates:
		for n,f in enumerate(factions):
			ys[n].append( get_score_for_date(db, f, d) )
			
	for n,y in enumerate(ys):
		plt.plot(dates, y, label=factions[n])

	plt.legend(loc="upper left")

	# every_nth = 12
	# for n, label in enumerate(ax.xaxis.get_ticklabels()):
		# if n % every_nth != 0:
			# label.set_visible(False)
			
	plt.show()
	
def get_tier_list_for_date(db, earliest=None, date=None):
	if date == None:
		date = datetime.datetime.now()
	else:
		date = dp.parse(date)
		
	if earliest == None:
		earliest = date - datetime.timedelta(days=30)
	else:
		earliest = dp.parse(earliest)
	
	statement = f'SELECT DISTINCT player, faction, position, num_players, event_name, date, rounds FROM ladder_position WHERE date > "{earliest}" AND date <= "{date}" ORDER BY date'
	rows = list(db.query(statement))
	
	scores = defaultdict(list)
	
	print()
	for counter,lp in enumerate(rows):
		print("\t", counter,len(rows), end='\r')
		
		s = get_gaussian_scores_for_finish(lp['position'], lp['num_players'], lp['rounds'])
		scores[lp['faction']].append(s)
		
	scores = {k:v for k,v in sorted(scores.items(), key=lambda i:statistics.mean(i[1]), reverse=True) if len(scores[k]) > 1}
		
	print(f'\t{len(rows)} ladder finishes processed between {earliest.strftime("%B %Y")} and {date.strftime("%B %Y")}.')
	print()
	for f in scores:
		print(f'\t\t{f:45} {int(statistics.mean(scores[f]))}')
	print()
			
def get_trueskill_tiers_for_date(db, earliest=None, date=None):
	if date == None:
		date = datetime.datetime.now()
	else:
		date = dp.parse(date)
		
	if earliest == None:
		earliest = date - datetime.timedelta(days=180)
	else:
		earliest = dp.parse(earliest)
	
	statement = f'SELECT DISTINCT faction,mu,sigma,date FROM trueskill WHERE date > "{earliest}" AND date <= "{date}" ORDER BY date'
	rows = list(db.query(statement))
	
	scores = defaultdict(list)
	
	print()
	for counter,lp in enumerate(rows):
		print("\t", counter,len(rows), end='\r')
		scores[lp['faction']].append(lp['mu']/lp['sigma'])
		
	scores = {k:v for k,v in sorted(scores.items(), key=lambda i:statistics.mean(i[1]), reverse=True) if len(scores[k]) > 1}
		
	print(f'\t{len(rows)} ladder finishes processed between {earliest.strftime("%B %Y")} and {date.strftime("%B %Y")}.')
	print()
	for f in scores:
		print(f'\t\t{f:45} {int(statistics.mean(scores[f]))}')
	print()
		
def get_score_for_date(db, faction, date):
	if type(date) == type("string"):
		date = dp.parse(date)

	statement = f'SELECT DISTINCT score,date FROM tiers WHERE faction="{faction}" ORDER BY date'
	rows = db.query(statement)
	
	s = 0
	for r in rows:
		s = r['score']
		if dp.parse(r['date']) > date:
			break
			
	return s
		
def get_tier_list_for_factions(db, factions=None, date=datetime.datetime.now()):
	s = {}
	
	if type(date) == type("string"):
		date = dp.parse(date)
	
	if factions == None:
		statement = f'SELECT DISTINCT faction FROM tiers WHERE count > 10 AND date > "{date - datetime.timedelta(days=90)}"'
		rows = db.query(statement)
		factions = [r['faction'] for r in rows]
	
	for f in factions:
		s[f] = get_score_for_date(db, f, date)
		
	s = {k:v for k,v in sorted(s.items(), key=lambda i:i[1], reverse=True)}
	
	return s

def get_named_tiers(db, date):
	tier_scores = get_tier_list_for_factions(db, date=date)

	mean = statistics.mean( list(tier_scores.values()) )
	std = statistics.stdev( list(tier_scores.values()) )
	smax = max(tier_scores.values())
	smin = min(tier_scores.values())
	
	tiers = {t:[] for t in ['s','a','b','c']}
	ftiers = {f:None for f in tier_scores}
	
	for f in tier_scores:
		s = tier_scores[f]
		
		if s >= smax - std:
			tiers['s'].append(f)
			ftiers[f] = 's'
		elif s >= mean:
			tiers['a'].append(f)
			ftiers[f] = 'a'
		elif s < smin + std:
			tiers['c'].append(f)
			ftiers[f] = 'c'
		elif s < mean:
			tiers['b'].append(f)
			ftiers[f] = 'b'
	
	
	print()
	for t in tiers:
		print(f'\t{t}')
		print('\t'+'-'*40)
		
		for f in tiers[t]:
			print(f'\t\t{f:25} {int(tier_scores[f])}')
	print()
			
	return ftiers
	
def simulate_filth_proportions(db, earliest, latest, num_players, rounds):
	earliest = dp.parse(earliest)
	latest = dp.parse(latest)
	
	statement = f'SELECT DISTINCT player, faction, position, num_players, sim_wins, event_name, date, rounds FROM ladder_position WHERE rounds>={rounds} AND date > "{earliest}" AND date < "{latest}"'
	rows = list(db.query(statement))
	
	appearances = {w: {i:[] for i in range(rounds)} for w in range(rounds+1)}
	
	wl_patterns = {3:[],4:[],5:[],6:[]}
	
	for i1 in [0,1]:
		for i2 in [0,1]:
			for i3 in [0,1]:
				wl_patterns[3].append([i1,i2,i3])
				for i4 in [0,1]:
					wl_patterns[4].append([i1,i2,i3,i4])
					for i5 in [0,1]:
						wl_patterns[5].append([i1,i2,i3,i4,i5])
						for i6 in [0,1]:
							wl_patterns[6].append([i1,i2,i3,i4,i5,i6])
						
	
	for pattern in wl_patterns[rounds]:
		player_wins = 0
		for g in range(rounds):
			player_losses = g - player_wins
			possible_opponents = [r for r in rows if r['sim_wins'] >= player_wins and r['sim_wins'] <= (rounds - player_losses)]
			
			appearances[sum(pattern)][g] += possible_opponents
			
			player_wins += pattern[g]
		
	print(len(rows))
	for w in appearances:
		for i in appearances[w]:
			print(f'Num Wins: {w}\tRound: {i+1}\tPossible Opponents: {len(appearances[w][i])}')
			
			counts = Counter([r['faction'] for r in appearances[w][i]])
			counts = {f:counts[f]/len(appearances[w][i]) for f in counts}
			counts = {k:v for k,v in sorted(counts.items(), key=lambda i:i[1], reverse=True)}
			
			for f in counts:
				print(f'\t{f:35} {counts[f]*100:.1f}%')
			
			input()
				
			
			
		print()
		
			
	
	

	
if __name__ == '__main__':	
	db = dataset.connect("sqlite:///__tinydb.db")
	ts.setup(backend='mpmath')
	
	# populate_ladder_table(db)
	# populate_tier_table(db)
	
	simulate_filth_proportions(db, "1 Jan 2020", "1 Nov 2020", 30, 5)
	
	
	
	# get_tier_list_for_date(db, "1 Jun 2020")