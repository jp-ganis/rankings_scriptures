import matplotlib.pyplot as plt
import dateutil.parser as dp
import scipy.stats
import statistics
import datetime
import dataset

import event_landscape

def get_gaussian_scores_for_finish(position, num_players, rounds):
	scores = []
	
	pts_scaler = 100
	
	c = 3.5
	increment = c / num_players
	
	multiplier = 1
	##if int(rounds) < 5: multiplier = 0.6
	
	pts = scipy.stats.norm(0, 1).cdf((c/2) - (increment * (position + 1)))
	pts *= pts_scaler * multiplier
		
	return pts
	
def get_normalized_history(games, mu=None):
	scores = []
	
	for row in games:
		scores.append(get_gaussian_scores_for_finish(row['position'], row['num_players'], row['rounds']))
		
	if len(scores) == 0: return [], 0
		
	if mu==None:
		mu = statistics.mean(scores)
	normed = [s-mu for s in scores]
	
	return normed, mu
		

def get_abuse(faction, date):
	## get all players who have done well with ko in 2020
	date = dp.parse(date)
	earliest = date - datetime.timedelta(days=365)
	statement = f'SELECT DISTINCT player FROM ladder_position WHERE faction = "{faction}" AND date > "{date}"'
	rows = db.query(statement)
	ko_abusers = [r['player'] for r in rows]
	
	delts = []
	
	for player in ko_abusers:
		if '"' in player: continue
		statement = f'SELECT DISTINCT position, num_players,rounds FROM ladder_position WHERE player = "{player}" AND date > "{earliest}" AND date < "{date}"'
		rows = db.query(statement)
		
		try:
			pre = statistics.mean([get_gaussian_scores_for_finish(row['position'], row['num_players'], row['rounds']) for row in rows])
		except statistics.StatisticsError:
			continue
		
		statement = f'SELECT DISTINCT position, num_players,rounds FROM ladder_position WHERE faction = "{faction}" AND player = "{player}" AND date > "{date}"'
		rows = db.query(statement)
		
		post = statistics.mean([get_gaussian_scores_for_finish(row['position'], row['num_players'], row['rounds']) for row in rows])
		
		try:
			delts.append(post-pre)
		except statistics.StatisticsError:
			continue
			
			
		
	print(len(ko_abusers))
	print(faction, statistics.mean(delts), statistics.stdev(delts))
	
	
def examine(faction):
	statement = f'SELECT DISTINCT player, position, num_players, rounds,date FROM ladder_position WHERE faction = "{faction}" ORDER BY date'
	rows = list(db.query(statement))
	
	scores = [get_gaussian_scores_for_finish(row['position'], row['num_players'], row['rounds']) for row in rows]
	
	w = 3
	smoothed = [statistics.mean(scores[i-w:i+w]) for i in range(w+1,len(scores))]
	
	plt.plot([dp.parse(rows[i]['date']) for i in range(len(smoothed))], smoothed)
	plt.show()
	

if __name__ == '__main__':
	db=dataset.connect("sqlite:///__tinydb.db")
	
	event_landscape.set_date_plot()
	
	examine("Kharadron Overlords")
	
	# get_abuse("Disciples Of Tzeentch", "1 Jan 2020")
	# get_abuse("Kharadron Overlords", "1 Jul 2020")
	# get_abuse("Hedonites Of Slaanesh", "1 Jun 2019")
