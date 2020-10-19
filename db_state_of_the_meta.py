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

def get_gaussian_score_for_finish(position, num_players, rounds):
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
	
	factions = {}
	inserts = []
	
	for counter,lp in enumerate(all_positions[-5000:]):
		print(counter,len(all_positions), end='\r')
		rounds = int(lp['rounds'])
		if rounds < 5: continue
		
		f = lp['faction']
		date = dp.parse(lp['date'])
		
		if date > datetime.datetime.now(): continue
		
		if f not in factions:
			factions[f] = dict(scores=[], tier='a', tier_score=0)
		
		factions[f]["scores"].append( dict(value=get_gaussian_score_for_finish(lp['position'], lp['num_players'], rounds), date=date ))
		factions[f]["tier_score"] = statistics.mean( [v['value'] for v in factions[f]["scores"][-10:]] )
		
		if len(factions[f]["scores"]) > 10:
			td = date - factions[f]["scores"][-10]['date']
			
			if td > datetime.timedelta(days=60):
				continue
		
		current_mean = statistics.mean( [factions[g]["tier_score"] for g in factions] )
		
		if len([factions[g]["tier_score"] for g in factions]) > 1:
			current_sd = statistics.stdev( [factions[g]["tier_score"] for g in factions] )
		else:
			current_sd = 10
		
		current_max = max( [factions[g]["tier_score"] for g in factions] )
		current_min = min( [factions[g]["tier_score"] for g in factions] )
		
		ts = factions[f]['tier_score']
		
		## top down
		if ts > current_max - current_sd*0.5:
			tier = 's'
		elif ts > current_mean + current_sd*0.5:
			tier = 'a'
		elif ts > current_mean:
			tier = 'b'
		## bottom up
		elif ts < current_min + current_sd*0.5:
			tier = 'e'
		elif ts < current_mean - current_sd*0.5:
			tier = 'd'
		elif ts < current_mean:
			tier = 'c'
		
		factions[f]['tier'] = tier
		
		inserts.append(dict( faction=f, tier=tier, score=ts, date=date+datetime.timedelta(days=3) ))
		
	for f in factions:
		print(f'{f:35} {factions[f]["tier"]}')
		
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

def get_named_tiers(db, date, factions=None):
	tier_scores = get_tier_list_for_factions(db, date=date)
	
	if factions != None:
		for faction in factions:
			tier_scores[faction] = get_score_for_date(db, faction, date)

	mean = statistics.mean( list(tier_scores.values()) )
	std = statistics.stdev( list(tier_scores.values()) )
	smax = max(tier_scores.values())
	smin = min(tier_scores.values())
	
	tiers = {t:[] for t in 'sabcde'}
	ftiers = {f:None for f in tier_scores}
	
	for f in tier_scores:
		s = tier_scores[f]
		
		## top
		if s >= smax - std*0.5:
			tiers['s'].append(f)
			ftiers[f] = 's'
		elif s >= mean + std*0.5:
			tiers['a'].append(f)
			ftiers[f] = 'a'
		elif s >= mean:
			tiers['b'].append(f)
			ftiers[f] = 'b'
		
		## bottom
		elif s < smin + std*0.5:
			tiers['e'].append(f)
			ftiers[f] = 'e'
		elif s < mean - std*0.5:
			tiers['d'].append(f)
			ftiers[f] = 'd'
		elif s < mean:
			tiers['c'].append(f)
			ftiers[f] = 'c'
	
	print()
	for t in tiers:
		print(f'\t{t}')
		print('\t'+'-'*40)
		
		for f in tiers[t]:
			print(f'\t\t{f:25} {int(tier_scores[f])}')
			
	# print()
	
	return ftiers, tiers
	
def simulate_filth_proportions(db, earliest, latest, num_players, rounds, wins=None):
	earliest = dp.parse(earliest)
	latest = dp.parse(latest)
	
	statement = f'SELECT DISTINCT player, faction, position, num_players, sim_wins, event_name, date, rounds FROM ladder_position WHERE rounds>={rounds} AND date > "{earliest}" AND date < "{latest}"'
	rows = list(db.query(statement))
	
	if wins != None:
		appearances = {w: {i:[] for i in range(rounds)} for w in [wins]}
	else:
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
						
	
	for pattern in [p for p in wl_patterns[rounds] if sum(p) in appearances]:
		player_wins = 0
		for g in range(rounds):
			player_losses = g - player_wins
			possible_opponents = [r for r in rows if r['sim_wins'] >= player_wins and r['sim_wins'] <= (rounds - player_losses)]
			
			appearances[sum(pattern)][g] += possible_opponents
			
			player_wins += pattern[g]
		
	print(len(rows))
	
	all_factions = []
	
	for w in appearances:
		for i in appearances[w]:
			all_factions += [r['faction'] for r in appearances[w][i]]
				
	
	all_factions = list(set(all_factions))
	_, tiers = get_named_tiers(db, latest)
	
	for w in appearances:
		for i in appearances[w]:
			print(f'Num Wins: {w}\tRound: {i+1}\tPossible Opponents: {len(appearances[w][i])}')
			
			counts = Counter([r['faction'] for r in appearances[w][i]])
			counts = {f:counts[f]/len(appearances[w][i]) for f in counts}
			counts = {k:v for k,v in sorted(counts.items(), key=lambda i:i[1], reverse=True)}
			
			for f in counts:
				print(f'\t{f:35} {counts[f]*100:.1f}%')

def quadrants(db, earliest, latest):
	earliest = dp.parse(earliest)
	latest = dp.parse(latest)
	
	statement = f'SELECT DISTINCT player, faction, position, num_players, sim_wins, event_name, date, rounds FROM ladder_position WHERE date > "{earliest}" AND date < "{latest}"'
	rows = list(db.query(statement))
	
	wins = defaultdict(list)
	counts = defaultdict(int)
	
	for r in rows:
		wins[r['faction']].append(r['sim_wins'])
		counts[r['faction']] += 1
		
	m_wins = statistics.mean([ statistics.mean(wins[f]) for f in wins ])
	m_count = statistics.mean([counts[f] for f in wins])
	
	qs = {}
	for f in wins:
		x = statistics.mean(wins[f]) - m_wins
		y = counts[f]-m_count 
		
		quadrant = 1
		
		if x > 0 and y > 0: quadrant = 1
		if x > 0 and y < 0: quadrant = 2
		if x < 0 and y < 0: quadrant = 3
		if x < 0 and y > 0: quadrant = 4
		
		qs[f] = quadrant
	
	qs = {k:v for k,v in sorted(qs.items(),key=lambda i:i[1])}
		
	for f in qs:
		q = qs[f]
		
		if q == 1:
			print(f'Powerful and Popular & {f}\\\\')
		if q == 2:
			print(f'Powerful and Unpopular & {f}\\\\')
		if q == 4:
			print(f'Weak and Popular & {f}\\\\')
		if q == 3:
			print(f'Weak and Unopular & {f}\\\\')
		
def populate_3month_tiers(db):
	date = dp.parse('1-Jan-2016')
	window = datetime.timedelta(days=93)
	
	inserts = []
	prevtier = defaultdict(str)
	
	min_games = 10
	
	statement = 'SELECT DISTINCT faction FROM ladder_position'
	all_factions = db.query(statement)
	all_factions = [f['faction'] for f in all_factions]
	
	while date < datetime.datetime.now():
		print(date)
		statement = f'SELECT DISTINCT player, faction, position, num_players, event_name, date, rounds FROM ladder_position WHERE date > "{date}" AND date < "{date+window}"'
		rows = db.query(statement)
		
		fscores = defaultdict(list)
		
		for r in rows:
			f = r['faction']
			fscores[f].append(get_gaussian_score_for_finish(r['position'], r['num_players'], r['rounds']))	
			
		if len(fscores) < 2: continue
		
		means = [statistics.mean( fscores[g] ) for g in fscores if len(fscores[g]) > min_games]
		
		if len(means) > 1:			
			current_mean = statistics.mean( means )
			current_sd = statistics.stdev( means )
			
			current_max = max( means )
			current_min = min( means )
			
		day_date = date
		while day_date < date + window:
			if day_date+window > datetime.datetime.now(): break
				
			for f in all_factions:
				if len(fscores[f]) < min_games or len(means) < 1:
					tier = prevtier[f]
				else:				
					ts = statistics.mean( fscores[f] )
					
					## top down
					if ts > current_max - current_sd*0.5:
						tier = 's'
					elif ts > current_mean + current_sd*0.5:
						tier = 'a'
					elif ts > current_mean:
						tier = 'b'
					## bottom up
					elif ts < current_min + current_sd*0.5:
						tier = 'e'
					elif ts < current_mean - current_sd*0.5:
						tier = 'd'
					elif ts < current_mean:
						tier = 'c'
				
					prevtier[f] = tier
				
				inserts.append(dict( faction=f, tier=tier, date=day_date, count=len(fscores[f])))
			day_date += datetime.timedelta(days=1)
	
		date += window
		
	if 'tiers' in db.tables: db['tiers'].drop()
	db['tiers'].insert_many(inserts)
		
def fec_matchups(db):
	statement = f'SELECT DISTINCT winner_faction, loser_faction, winner_name, loser_name FROM game join event ON game.event_id = event.id WHERE (loser_faction="Flesh Eater Courts" or winner_faction="Flesh Eater Courts") AND date > "2020-01-01"'
	rows = db.query(statement)
	
	matchups = defaultdict(list)
	
	for row in rows:
		if "Flesh" in row['winner_faction']: matchups[row['loser_faction']].append(1)
		else: matchups[row['winner_faction']].append(0)
		
	matchups = {k:v for k,v in sorted(matchups.items(), key=lambda i: sum(i[1])/len(i[1]), reverse=True) if "Flesh" not in k}
		
	print()
	for m in matchups:
		if len(matchups[m]) < 10: continue
		print(f'\t{m:35} {int(sum(matchups[m])/len(matchups[m])*100)}%\t\t{sum(matchups[m]):3}-{len(matchups[m]) - sum(matchups[m])}')
	print()
		
	
	
if __name__ == '__main__':	
	db = dataset.connect("sqlite:///__tinydb.db")
	ts.setup(backend='mpmath')
	
	# populate_ladder_table(db)
	# populate_tier_table(db)
	# populate_3month_tiers(db)
	
	# simulate_filth_proportions(db, "1 Jul 2020", "1 Nov 2020", 220, 5, 0)
	
	# quadrants(db, '1 Jan 2020', '1 Nov 2020')
	
	# loca_tier,_ = get_named_tiers(db, '1 Nov 2020', ["Nighthaunt"])
	# for f in loca_tier:
		# print(f, loca_tier[f])
	
	# get_tier_list_for_date(db, "1 Jun 2020")
	
	fec_matchups(db)
