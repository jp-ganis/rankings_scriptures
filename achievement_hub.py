from collections import defaultdict
import dateutil.parser as dp
import listbot_data_dicts
import event_landscape
import gaussian_fitter
import json

def initialize_achievement_data(matchup_data, pdata):
	a = {}
		
	for m in matchup_data:
		event, date, pwin, fwin, plose, flose = m
		a[pwin] = {}
		a[plose] = {}
		
	for p in pdata:
		a[p] = {}
		
	for p in a:
		## matchups
		factions = {}
		factions["Lumineth Realmlords"] = "actually_i_kinda_like_the_teclis_model"
		factions["Legion of Blood"] = "bite_me"
		factions["Nighthaunt"] = "black_coach_down"
		factions["Khorne"] = "blood_of_the_blood_god"
		factions["Daughters of Khaine"] = "bringing_the_pain_train_to_the_khaine_dame"
		factions["Courts"] = "chew_on_this"
		factions["Mawtribes"] = "count_as_zero_models_when_their_dead_though"
		factions["Deepkin"] = "eels_whyd_it_have_to_be_eels"
		factions["Beasts"] = "goat"
		factions["Kharadron"] = "im_gonna_pay_you_100_aethergold"
		factions["Behemat"] = "jack"
		factions["Ironjawz"] = "jawbreakers"
		factions["Tzeentch"] = "just_as_planned"
		factions["Seraphon"] = "life_uh_finds_a_way"
		factions["Slaves"] = "light_be_with_you"
		factions["Stormcast"] = "lightning_doesnt_even_strike_once"
		factions["Grief"] = "literally_griefing"
		factions["Gitz"] = "lots_o_grots"
		factions["Sacrament"] = "more_like_arkhant"
		factions["Sacrement"] = "more_like_arkhant"
		factions["Fyreslayers"] = "nobody_tosses_a_wait"
		factions["Skaven"] = "ratcatchin"
		factions["Nurgle"] = "that_was_sick"
		factions["Legion of Night"] = "the_real_fake_mortarch"
		factions["Grand Host"] = "this_is_my_boomstick"
		factions["Bonereapers"] = "tithe_evasion"
		factions["Slaanesh"] = "wait_were_you_enjoying_that"
		factions["Cities"] = "we_did_it_rage_kage"
		factions["Bonesplitter"] = "winners_dont_split_and_splitters_dont_win"
		factions["Sylvaneth"] = "wyld_wyld_west"
		
		for f in factions:
			a[p][factions[f]] = {"id":factions[f], "category":"matchups", "points":10}

		## faction_tiers
		a[p]["at_all_costs"] = {"id":"at_all_costs", "category": "faction_tiers", "points":10}
		a[p]["challenge_mode"] = {"id":"challenge_mode", "category": "faction_tiers", "points":10}
		
		## general
		a[p]["on_the_board"] = {"id":"on_the_board", "category": "general", "points":10}
		a[p]["double_up"] = {"id":"double_up", "category": "general", "points":10}
		a[p]["triple_threat"] = {"id":"triple_threat", "category": "general", "points":10}
		a[p]["quadratic_equations"] = {"id":"double_up", "category": "general", "points":10}
		a[p]["iambic_pentameter"] = {"id":"iambic_pentameter", "category": "general", "points":10}
		
		a[p]["just_play"] = {"id":"just_play", "category": "general", "points":10}
		a[p]["just_play_2"] = {"id":"just_play_2", "category": "general", "points":10}
		a[p]["just_play_3"] = {"id":"just_play_3", "category": "general", "points":10}
		a[p]["just_play_4"] = {"id":"just_play_4", "category": "general", "points":10}
		a[p]["just_play_5"] = {"id":"just_play_5", "category": "general", "points":30}
		
		a[p]["ok_but_sometimes_you_just_gotta_let_em_know"] = {"id":"ok_but_sometimes_you_just_gotta_let_em_know", "category": "general", "points":30}
		a[p]["i_coulda_been_somebody"] = {"id":"i_coulda_been_somebody", "category": "general", "points":10}
		a[p]["its_5_and_0_somewhere"] = {"id":"its_5_and_0_somewhere", "category": "general", "points":10}
		
		a[p]["grudge_bearer"] = {"id":"grudge_bearer", "category": "general", "points":10}
		a[p]["grudge_bearer_2"] = {"id":"grudge_bearer_2", "category": "general", "points":20}
		a[p]["grudge_bearer_3"] = {"id":"grudge_bearer_3", "category": "general", "points":50}
		
		a[p]["this_game_is_entirely_luck"]= {"id":"this_game_is_entirely_luck", "category": "general", "points":10}
		a[p]["this_game_is_entirely_skill"]= {"id":"this_game_is_entirely_skill", "category": "general", "points":10}
		
		## matchups
		a[p]["i_am_sigmars_sixes_to_hit"] = {"id":"i_am_sigmars_sixes_to_hit", "category": "general", "points":10}
		a[p]["i_declare_im_jinking"] = {"id":"i_declare_im_jinking", "category": "general", "points":10}
		a[p]["trust_aethermatics_not_superstition"] = {"id":"trust_aethermatics_not_superstition", "category": "general", "points":10}
		a[p]["the_activation_wars"] = {"id":"the_activation_wars", "category": "general", "points":10}
		
		a[p]["rage_against_the_machine"] = {"id":"rage_against_the_machine", "category": "general", "points":10}
		a[p]["lovable"] = {"id":"lovable", "category": "general", "points":10}
		a[p]["two_thin_coats"] = {"id":"two_thin_coats", "category": "general", "points":10}
		
		## scotland
		a[p]["bench_em"] = {"id":"bench_em", "category": "scotland", "points":10}
		a[p]["bench_all_of_em"] = {"id":"bench_all_of_em", "category": "scotland", "points":30}
		a[p]["squad_goals"] = {"id":"squad_goals", "category": "scotland", "points":30}
		a[p]["two_heads_are_better_than_one"] = {"id":"two_heads_are_better_than_one", "category": "scotland", "points":30}
		a[p]["theyll_never_take_our_freedom"] = {"id":"theyll_never_take_our_freedom", "category": "scotland", "points":10}
		a[p]["never_meet_your_heroes"] = {"id":"never_meet_your_heroes", "category": "scotland", "points":10}
		
		## kill_points
		a[p]["objectives"] = {"id":"objectives", "category": "kill_points", "points":10}
		a[p]["objectives_2"] = {"id":"objectives_2", "category": "kill_points", "points":20}
		a[p]["objectives_3"] = {"id":"objectives_3", "category": "kill_points", "points":50}
		a[p]["objectives_4"] = {"id":"objectives_4", "category": "kill_points", "points":100}
		
		
	return a, factions
		
def populate_achievement_data(achievements, matchup_data, fdata, pdata, edata, defeat_achis):
	## matchup
	scotland_6n_players = ["Leigh Martin", "Andy Currie", "David Jack", "Nathan Watson", "Jp Ganis", "Paul DiDuca", "Mike Callaghan", "John Bayliss"]
	benchem_data = {}
	win_counts = defaultdict(int)
	grudges = defaultdict(list)
	melee_armies = ["Lumineth Realmlords", "Legion of Blood", "Nighthaunt", "Khorne", "Daughters" "Courts", "Mawtribes", "Deepkin", "Beasts", "Sons of Behemat", "Ironjawz", "Skaven", "Grief", "Fyreslayers", "Nurgle","Slaanesh","Bonereapers","Bonesplitter","Sylvaneth"]
	shooting_armies = ["Lumineth Realmlords", "Kharadron", "Tzeentch", "Seraphon", "Skaven","Cities","Bonesplitter","Sylvaneth"]
	magic_armies = ["Lumineth Realmlords", "Tzeentch", "Seraphon", "Sacrement", "Sacrament", "Skaven", "Gitz","Cities","Sylvaneth"]
	asf_armies = ["Slaanesh", "Idoneth Deepkin", "Fyreslayers", "Courts"]
	event_counts = defaultdict(int)

	
	for m in matchup_data:
		event, date, pwin, fwin, plose, flose = m
		
		date = dp.parse(date)
		a_date = f'{event} - {date.strftime("%B %Y")}'
		
		win_counts[pwin] += 1
		
		if win_counts[pwin] >= 5:
			achievements[pwin]["its_5_and_0_somewhere"]["event_and_date"] = a_date
			
		grudges[plose].append((pwin, a_date))
		
		if pwin == "John Harper" or plose == "John Harper":
			achievements[pwin]["never_meet_your_heroes"]["event_and_date"] = a_date
			achievements[plose]["never_meet_your_heroes"]["event_and_date"] = a_date
			
			
		achievements[pwin]["this_game_is_entirely_skill"]["event_and_date"] = a_date
		achievements[plose]["this_game_is_entirely_luck"]["event_and_date"] = a_date
			
		
		for f in defeat_achis:
			if f in flose:
				achievements[pwin][defeat_achis[f]]["event_and_date"] = a_date
		
		for f in melee_armies:
			if f in flose:
				achievements[pwin]["i_am_sigmars_sixes_to_hit"]["event_and_date"] = a_date
		for f in shooting_armies:
			if f in flose:
				achievements[pwin]["i_declare_im_jinking"]["event_and_date"] = a_date
		for f in magic_armies:
			if f in flose:
				achievements[pwin]["trust_aethermatics_not_superstition"]["event_and_date"] = a_date
		for f in asf_armies:
			if f in flose:
				achievements[pwin]["the_activation_wars"]["event_and_date"] = a_date
				
			
		if plose in scotland_6n_players:
			if pwin not in benchem_data: benchem_data[pwin] = []
			benchem_data[pwin].append((plose, a_date))
			
	## faction tiers
	for e in edata:
		date = dp.parse(e["std_date"])
		event = e["name"]
		a_date = f'{event} - {date.strftime("%B %Y")}'
		
		tl = e["tier_list"]
		wins = gaussian_fitter.get_win_distribution(len(e["ladder"]), rounds=int(e["rounds"]))
		
		for n,p in enumerate(e["ladder"]):
			pwins = wins[n]
			
			event_counts[p["player_name"]] += 1
			if event_counts[p["player_name"]] >= 1:	
				achievements[p["player_name"]]["just_play"]["event_and_date"] = a_date
			if event_counts[p["player_name"]] >= 3:	
				achievements[p["player_name"]]["just_play_2"]["event_and_date"] = a_date
			if event_counts[p["player_name"]] >= 5:	
				achievements[p["player_name"]]["just_play_3"]["event_and_date"] = a_date
			if event_counts[p["player_name"]] >= 10:	
				achievements[p["player_name"]]["just_play_4"]["event_and_date"] = a_date
			if event_counts[p["player_name"]] >= 50:	
				achievements[p["player_name"]]["just_play_5"]["event_and_date"] = a_date
				
			##wins
			if pwins >= 1:
				achievements[p["player_name"]]["on_the_board"]["event_and_date"] = a_date
			if pwins >= 2:
				achievements[p["player_name"]]["double_up"]["event_and_date"] = a_date
			if pwins >= 3:
				achievements[p["player_name"]]["triple_threat"]["event_and_date"] = a_date
			if pwins >= 4:			
				achievements[p["player_name"]]["quadratic_equations"]["event_and_date"] = a_date
			if pwins >= 5:
				achievements[p["player_name"]]["iambic_pentameter"]["event_and_date"] = a_date
		
			if n == 0:
				achievements[p["player_name"]]["ok_but_sometimes_you_just_gotta_let_em_know"]["event_and_date"] = a_date
			elif n == 1 or n == 2:
				achievements[p["player_name"]]["i_coulda_been_somebody"]["event_and_date"] = a_date
				
		
			##faction_tiers
			if p["faction"] in tl:	
				for n,t in enumerate(tl):
					if t in ["-", "UNKNOWN_ARMY"]: continue
					if t == p["faction"] and n < 3:
						achievements[p["player_name"]]["at_all_costs"]["event_and_date"] = a_date
						
					if t == p["faction"] and n > len(tl) - 3:
						achievements[p["player_name"]]["challenge_mode"]["event_and_date"] = a_date
		
	## grudges
	for p in grudges:
		gs = [g[0] for g in grudges[p]]
		for g in gs:
			if g in grudges:
				gc = [r[0] for r in grudges[g]].count(p)
			
				a_date = [i[1] for i in grudges[p] if i[0] == g][0]
			
				if gc >= 1:
					achievements[p]["grudge_bearer"]["event_and_date"] = a_date
				if gc >= 3:
					achievements[p]["grudge_bearer_2"]["event_and_date"] = a_date
				if gc >= 5:
					achievements[p]["grudge_bearer_3"]["event_and_date"] = a_date
		
	## misc
	for p in benchem_data:
		achievements[p]["bench_em"]["event_and_date"] = benchem_data[p][0][1]
		bd = list(set([b[0] for b in benchem_data[p]]))
		
		if len(bd) >= 8:
			achievements[p]["bench_all_of_em"]["event_and_date"] = benchem_data[p][-1][1]
	
	return achievements
		
		
def update_achievement_complete_status(achievements):
	for p in achievements:
		achievements[p]["total_score"] = 0
		for a in achievements[p]:
			if a == "total_score": continue
		
			achievements[p][a]["complete"] = "event_and_date" in achievements[p][a]
			if not achievements[p][a]["complete"]:
				achievements[p][a]["event_and_date"] = ""
			else:
				achievements[p]["total_score"] += achievements[p][a]["points"]
				
	return achievements
	
	
if __name__ == '__main__':
	## TODO: NAME REPLACEMENTS FOR COMMON MISPELLINGS ETC, KNOWN ALIASES
	with open("output_data_files/all_tto_matchups.json", newline='', encoding='utf-8') as json_file:
		matchup_data = json.load(json_file)
		
	data_dicts = listbot_data_dicts.get_data_dicts("all_global_events")
	fdata = data_dicts["faction_data"]
	pdata = data_dicts["player_data"]
	edata = data_dicts["event_data"]
	edata = event_landscape.populate_event_tier_lists(edata)
	
	a, factions = initialize_achievement_data(matchup_data, pdata)
	a = populate_achievement_data(a, matchup_data, fdata, pdata, edata, factions)
	a = update_achievement_complete_status(a) ## set all completed to true if there is a date
	
	for e in a["Jp Ganis"]:
		print(e, a["Jp Ganis"][e])
	print()
	
	a = {k:v for k,v in sorted(a.items(), key=lambda i: i[1]["total_score"], reverse=True)}
	
	with open(f'metabreakers/data/achievement_data.json', 'w') as json_file:
		json.dump(a, json_file)