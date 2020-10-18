from gaussian_fitter import get_win_distribution

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

import dateutil.parser as dp

import listbot_data_dicts
import statistics

import csv


def set_date_plot():
	ax = plt.gca()
	
	fig=ax.figure
	fig.autofmt_xdate()

	formatter = mdates.DateFormatter("%m-%Y")
	ax.xaxis.set_major_formatter(formatter)
	locator = mdates.MonthLocator()
	ax.xaxis.set_major_locator(locator)
	
def plot_factions_over_time(edata, fdata, infactions=["Stormcast Eternals"]):
	faction_ratings = {f:[0] for f in fdata}
	
	x = []
	y = {f:[] for f in fdata}
	
	for e in edata:
		for p in e["ladder"]:
			faction_ratings[p["faction"]].append(p["gaussian_score"])

		x.append(dp.parse(e["date"]))
		
		for f in fdata:
			y[f].append(statistics.mean(faction_ratings[f][-75:]))

	for faction in infactions:
		date_plot(x,y[faction])

def populate_event_tier_lists(edata):
	faction_ratings = {}
	
	for e in edata:
		for p in e["ladder"]:
			if p["faction"] not in faction_ratings: faction_ratings[p["faction"]] = [0]
			faction_ratings[p["faction"]].append(p["gaussian_score"])
		
		e["tier_list"] = {}

		for f in faction_ratings:
			e["tier_list"][f] = statistics.mean(faction_ratings[f][-75:])
			
		
	return edata
			
def track_event_filth_over_time(edata):
	edata = populate_event_tier_lists(edata, fdata)

	filth_scores = []

	x = []
	y = []
	
	for e in edata:
		faction_scores = []
		
		for p in e["ladder"]:
			faction_scores.append(e["tier_list"][p["faction"]])
			
		x.append(dp.parse(e["date"]))
		filth_scores.append(statistics.mean(faction_scores))
		
		y.append(statistics.mean(filth_scores))
		
	set_date_plot()
	
	plt.scatter(x[20:], filth_scores[20:], s=2, c="grey")
	plt.plot(x[20:], y[20:])
	plt.show()
	
def track_power_gap_over_time(edata, fdata):
	edata = populate_event_tier_lists(edata, fdata)

	filth_scores = []

	x = []
	y = []
	
	for e in edata:
		x.append(dp.parse(e["date"]))
		
		## get interquartile distance
		tier_powers = list(e["tier_list"].values())
		median = statistics.median(tier_powers)
		upper_half = [t for t in tier_powers if t > median]
		lower_half = [t for t in tier_powers if t <= median]
		
		filth_scores.append(statistics.median(upper_half) - statistics.median(lower_half))
		
		y.append(statistics.mean(filth_scores))
		
	set_date_plot()
	
	plt.plot(x[20:], y[20:])
	plt.show()	

def get_average_filth_in_run(edata, fdata):
	edata = populate_event_tier_lists(edata, fdata)

	x=[]
	y={i:[] for i in range(6)}
	
	win_filth = {i:[50] for i in range(6)}

	last_e = edata[0]
	
	for e in edata:
		if e["rounds"] != '5': continue
		
		win_dist = get_win_distribution(len(e["ladder"]))
		
		for n, p in enumerate(e["ladder"]):
			wins = win_dist[n]
			win_filth[wins].append(last_e["tier_list"][p["faction"]])
			
		last_e = e
			
		x.append(dp.parse(e["date"]))
		
		for i in range(6):
			y[i].append(statistics.mean(win_filth[i]))
			
	set_date_plot()
	
	ax = plt.gca()
	ax.set_ylim(0,100)
		
	for i in range(6):
		plt.plot(x[20:],y[i][20:])
	plt.show()
	
def get_average_player_skill_in_run(edata, fdata, pdata):
	edata = populate_event_tier_lists(edata, fdata)

	x=[]
	y={i:[] for i in range(6)}
	
	win_filth = {i:[50] for i in range(6)}

	for e in edata:
		if e["rounds"] != '5': continue
		
		win_dist = get_win_distribution(len(e["ladder"]))
		
		for n, p in enumerate(e["ladder"]):
			wins = win_dist[n]
			win_filth[wins].append(pdata[p["player_name"]]["gaussian_score"])
			
		x.append(dp.parse(e["date"]))
		
		for i in range(6):
			y[i].append(statistics.mean(win_filth[i]))
			
	set_date_plot()
	
	for i in range(6):
		plt.plot(x[20:],y[i][20:])
	plt.show()

def get_most_common_recent_factions(edata, fdata):
	earliest = dp.parse("01-Jan-2020")
	latest = dp.parse("01-Jun-2020")
	
	earliest = dp.parse("01-Jan-2019")
	latest = dp.parse("01-Jul-2019")
	
	earliest = dp.parse("01-Jun-2018")
	latest = dp.parse("01-Dec-2018")
	
	faction_counts = {i:{f:0 for f in fdata} for i in range(5)}
	
	event_count = 0
	
	for e in edata:
		if e["rounds"] != '5': continue
		if dp.parse(e["date"]) < earliest or dp.parse(e["date"]) > latest: continue
		
		event_count += 1
		
		win_dist = get_win_distribution(len(e["ladder"]))
		
		for n, p in enumerate(e["ladder"]):
			if p["faction"] in ["-", "UNKNOWN_ARMY"]: continue
			wins = win_dist[n]
			
			for i in range(0, wins):
				faction_counts[i][p["faction"]] += 1

	print(f'{event_count} events parsed.')
	
	for i in faction_counts:
		faction_counts[i]["Skaventide"] = faction_counts[i]["Skaven"] + faction_counts[i]["Skaventide"] + 1
		faction_counts[i]["Skaven"] = 0
		
		faction_counts[i] = {k:v for k,v in sorted(faction_counts[i].items(), key=lambda i: i[1], reverse=True)}
		
		print(f'Game {i+1}')
		
		for f in [f for f in faction_counts[i]][:5]:
			print(f'\t{f:35} {int(faction_counts[i][f]/sum([faction_counts[i][x] for x in faction_counts[i]])*100):4}%')
			
		print()
	
def tier_list_over_time(edata, fdata):
	edata = populate_event_tier_lists(edata, fdata)
	
	data_rows = {}
	
	for e in edata:
		tl = {k:v for k,v in sorted(e["tier_list"].items(), key=lambda i: i[1], reverse=True)}

		data_rows[dp.parse(e["date"])] = tl		
		
		
	new_rows = {}
	top_row = ["Faction", "GA", "Image URL"]
	
	for d in data_rows:
		top_row.append(d)
		
		for f in data_rows[d]:
			if len(fdata[f]["events"]) < 30: continue
			if f in ["-", "UNKNOWN_ARMY"]: continue
			
			if f not in new_rows: new_rows[f] = [f, "Order", 	"imgurl"]
			
			new_rows[f].append(data_rows[d][f])
		
	with open('animated_tier_list.csv', mode='w') as file:
		writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		
		writer.writerow(top_row)
		
		for faction in new_rows:
			writer.writerow(new_rows[faction])

	print(new_rows["Ossiarch Bonereapers"])

def territory_over_time(edata, fdata):
	edata = populate_event_tier_lists(edata)
	
	over_time = {}
	territories = {}
	
	for e in edata:
		for f in [p["faction"] for p in e["ladder"]]:
			if f not in territories: territories[f] = 0	
			territories[f] += e["tier_list"][f]
		
		territories = {k:v for k,v in sorted(territories.items(), key=lambda i: i[1], reverse=True) if k not in ["-","UNKNOWN_ARMY"]}
		
		
		over_time[dp.parse(e["date"])] = territories
		
	for t in territories:
		print(f'{t:35} {int(territories[t])}')
		
	return over_time
	
if __name__ == '__main__':
	data_dicts = listbot_data_dicts.get_data_dicts("all_global_events")
	
	pdata = data_dicts["player_data"]
	fdata = data_dicts["faction_data"]
	edata = data_dicts["event_data"]
	
	faction_replacements = ["Khorne", "Tzeentch", "Slaanesh", "Nurgle", "Skaven", "Mawtribes"]
	legions_of_nagash = ["Legion of Grief", "Legion of Blood", "Legion of Night", "Legions of Nagash", "Grand Host of Nagash", "Legion of Sacrement"]
	
	for e in edata:
		for p in e["ladder"]:
			f = p["faction"]
			
			if f in legions_of_nagash:
				p["faction"] = "Legions of Nagash"
				
			for fr in faction_replacements:
				if fr in f:
					p["faction"] = fr
				
	edata = sorted(edata, key=lambda e: dp.parse(e["date"]))
	
	
	territory_over_time(edata, fdata)
