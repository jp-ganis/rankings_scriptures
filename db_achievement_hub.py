from collections import defaultdict
import dateutil.parser as dp
import listbot_data_dicts
import spot_achievements
import db_check_aliases
import event_landscape
import gaussian_fitter
import dataset
import os.path
import json
import glob

def initialize_achievement_data(db):
	a = defaultdict(dict)
	
	ps = db['player'].all()
	
	with open("output_data_files/recent_events/datahub_player_data.json", newline='', encoding='utf-8') as json_file:
		pdata = json.load(json_file)
	
	other_ps=[]
	for p in pdata:
		other_ps.append( db_check_aliases.predefined_aliases(p) )

	for p in [p['name'] for p in ps]+other_ps:
		## matchups
		factions = {}
		factions["Lumineth Realmlords"] = "actually_i_kinda_like_the_teclis_model"
		factions["Legion of Blood"] = "bite_me"
		factions["Nighthaunt"] = "black_coach_down"
		factions["Blades of Khorne"] = "blood_of_the_blood_god"
		factions["Daughters Of Khaine"] = "bringing_the_pain_train_to_the_khaine_dame"
		factions["Flesh Eater Courts"] = "chew_on_this"
		factions["Ogor Mawtribes"] = "count_as_zero_models_when_their_dead_though"
		factions["Idoneth Deepkin"] = "eels_whyd_it_have_to_be_eels"
		factions["Beasts Of Chaos"] = "goat"
		factions["Kharadron Overlords"] = "im_gonna_pay_you_100_aethergold"
		factions["Sons Of Behemat"] = "jack"
		factions["Ironjawz"] = "jawbreakers"
		factions["Disciples Of Tzeentch"] = "just_as_planned"
		factions["Seraphon"] = "life_uh_finds_a_way"
		factions["Slaves To Darkness"] = "light_be_with_you"
		factions["Stormcast Eternals"] = "lightning_doesnt_even_strike_once"
		factions["Legion Of Grief"] = "literally_griefing"
		factions["Gloomspite Gitz"] = "lots_o_grots"
		factions["Legion Of Sacrament"] = "more_like_arkhant"
		factions["Fyreslayers"] = "nobody_tosses_a_wait"
		factions["Skaven"] = "ratcatchin"
		factions["Maggotkin Of Nurgle"] = "that_was_sick"
		factions["Legion of Night"] = "the_real_fake_mortarch"
		factions["Grand Host Of Nagash"] = "this_is_my_boomstick"
		factions["Ossiarch Bonereapers"] = "tithe_evasion"
		factions["Hedonites Of Slaanesh"] = "wait_were_you_enjoying_that"
		factions["Cities Of Sigmar"] = "we_did_it_rage_kage"
		factions["Bonesplitterz"] = "winners_dont_split_and_splitters_dont_win"
		factions["Sylvaneth"] = "wyld_wyld_west"
		
		wfactions = {}
		wfactions["Lumineth Realmlords"] = dict(id="realmlord", title="Realmlord")
		wfactions["Legion of Blood"] = dict(id="fang_you_very_much", title="Fang you very much!")
		wfactions["Nighthaunt"] = dict(id="high_spirits", title="High Spirits")
		wfactions["Blades of Khorne"] = dict(id="under_hooves_of_brass", title="Under Hooves Of Brass")
		wfactions["Daughters Of Khaine"] = dict(id="khaint_stop_wont_stop", title="Khaint Stop Won't Stop")
		wfactions["Flesh Eater Courts"] = dict(id="whos_delusional_now", title="Who's Delusional Now?")
		wfactions["Ogor Mawtribes"] = dict(id="stay_hungry_stay_humble", title="Stay Hungry, Stay Humble")
		wfactions["Idoneth Deepkin"] = dict(id="an_eely_good_time", title="An Eely Good Time")
		wfactions["Beasts Of Chaos"] = dict(id="wait_its_all_chaff_always_has_been", title="Wait, it's all chaff? Always has been")
		wfactions["Kharadron Overlords"] = dict(id="steam_power", title="Full Steam Ahead")
		wfactions["Sons Of Behemat"] = dict(id="rubble_rousin", title="Rubble Rousin'")
		wfactions["Ironjawz"] = dict(id="mad_as_hell", title="Mad As Hell")
		wfactions["Disciples Of Tzeentch"] = dict(id="fun_and_interactive", title="Fun AND Interactive")
		wfactions["Seraphon"] = dict(id="clever_girl", title="Clever Girl")
		wfactions["Slaves To Darkness"] = dict(id="chaos_is_inevitable", title="Chaos Is Inevitable")
		wfactions["Stormcast Eternals"] = dict(id="thunderstruck", title="Thunderstruck")
		wfactions["Legion Of Grief"] = dict(id="grievance_procedure", title="Grievance Procedure")
		wfactions["Gloomspite Gitz"] = dict(id="da_best", title="Da Best")
		wfactions["Legion Of Sacrament"] = dict(id="the_masters_teachings", title="The Master's Teachings")
		wfactions["Fyreslayers"] = dict(id="fyre_other_players_doesnt_matter", title="Fyre, other players, doesn't matter")
		wfactions["Skaven"] = dict(id="more_more_win_power", title="More More Win Power!")
		wfactions["Maggotkin Of Nurgle"] = dict(id="seven", title="Seven!")
		wfactions["Legion of Night"] = dict(id="under_the_cover_of_darkness", title="Under The Cover Of Darkness")
		wfactions["Grand Host Of Nagash"] = dict(id="bow_before_the_god_of_death", title="Bow, Before The God Of Death")
		wfactions["Ossiarch Bonereapers"] = dict(id="the_collector", title="The Collector")
		wfactions["Hedonites Of Slaanesh"] = dict(id="pleasure_from_pain", title="Pleasure From Pain")
		wfactions["Cities Of Sigmar"] = dict(id="from_now_on_we_will_travel_in_tubes", title="From Now On We Will Travel In Tubes!")
		wfactions["Bonesplitterz"] = dict(id="oh_you_brought_a_monster", title="Oh, you brought a monster?")
		wfactions["Sylvaneth"] = dict(id="branching_out", title="Branching Out")
		
		for f in factions:
			a[p][factions[f]] = {"id":factions[f], "category":"matchups", "points":10}
			
		for f in wfactions:
			a[p][wfactions[f]["id"]] = {"id":wfactions[f]["id"], "title":wfactions[f]["title"], "description": f'Win a game as {f}', "category":"matchups", "points":10}
			wfactions[f] = wfactions[f]["id"]
			

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
		a[p]["youre_gonna_need_a_bigger_bench"] = {"id":"youre_gonna_need_a_bigger_bench", "category": "scotland", "points":60}
		a[p]["squad_goals"] = {"id":"squad_goals", "category": "scotland", "points":30}
		a[p]["two_heads_are_better_than_one"] = {"id":"two_heads_are_better_than_one", "category": "scotland", "points":30}
		a[p]["theyll_never_take_our_freedom"] = {"id":"theyll_never_take_our_freedom", "category": "scotland", "points":10}
		a[p]["never_meet_your_heroes"] = {"id":"never_meet_your_heroes", "category": "scotland", "points":10}
		
		## kill_points
		a[p]["objectives"] = {"id":"objectives", "category": "kill_points", "points":10}
		a[p]["objectives_2"] = {"id":"objectives_2", "category": "kill_points", "points":20}
		a[p]["objectives_3"] = {"id":"objectives_3", "category": "kill_points", "points":50}
		a[p]["objectives_4"] = {"id":"objectives_4", "category": "kill_points", "points":100}
		
		a[p]["what_is_best_in_life"] = {"id":"what_is_best_in_life", "category": "kill_points", "points":10, "title":"What is best in life?", "description":"Score 2000+ kill points in a single game"}
		a[p]["yeah_ok_technically"] = {"id":"yeah_ok_technically", "category": "kill_points", "points":30, "title":"Yeah OK technically...", "description":"Lose a game while scoring 2000+ kill points"}
		a[p]["calm_objective_based_gameplay"] = {"id":"calm_objective_based_gameplay", "category": "kill_points", "points":30, "title":"Calm Objective-Based Gameplay", "description":"Win a game while scoring 0 kill points"}
		a[p]["let_none_stand_before_me"] = {"id":"let_none_stand_before_me", "category": "kill_points", "points":50, "title":"Let None Stand Before Me", "description":"Win 5 games and score 10,000+ kill points at a single event"}
		
		
	return a, factions, wfactions
	
def complete_achievement(db, achievement, event_id):
	event = db["event"].find_one(id=event_id)
	date = event["date"]
	
	if "event_id" in achievement:
		old_event = db["event"].find_one(id=achievement["event_id"])
		old_date = old_event["date"]
		
		if dp.parse(date) < dp.parse(old_date):
			achievement["event_id"] = event_id
		else:
			date = old_date
			event = old_event
	else:
		achievement["event_id"] = event_id
		
	achievement["event_and_date"] = f'{event["name"]} - {dp.parse(date).strftime("%B %Y")}'
	achievement["complete"] = True
		
def populate_achievement_data(achievements, db, defeat_achis, victory_achis):
	## matchup
	scotland_6n_players = ["Leigh Martin", "Andy Currie", "David Jack", "Nathan Watson", "Jp Ganis", "Paul DiDuca", "Mike Callaghan", "John Bayliss"]
	benchem_data = defaultdict(list)
	win_counts = defaultdict(int)
	grudges = defaultdict(list)
	melee_armies = ["Lumineth Realmlords", "Legion of Blood", "Nighthaunt", "Khorne", "Daughters" "Courts", "Mawtribes", "Deepkin", "Beasts", "Sons of Behemat", "Ironjawz", "Skaven", "Grief", "Fyreslayers", "Nurgle","Slaanesh","Bonereapers","Bonesplitter","Sylvaneth"]
	shooting_armies = ["Lumineth Realmlords", "Kharadron", "Tzeentch", "Seraphon", "Skaven","Cities","Bonesplitter","Sylvaneth"]
	magic_armies = ["Lumineth Realmlords", "Tzeentch", "Seraphon", "Sacrement", "Sacrament", "Skaven", "Gitz","Cities","Sylvaneth"]
	asf_armies = ["Slaanesh", "Idoneth Deepkin", "Fyreslayers", "Courts"]
	event_counts = defaultdict(int)

	for p in achievements:
		if "\"" in p: continue
		count_6n = set({})
		
		## all won games
		statement = f'SELECT DISTINCT loser_name, loser_faction, event_id, winner_faction FROM game WHERE winner_name="{p}"'
		rows = db.query(statement)
		
		for n,row in enumerate(rows):
			if row["loser_faction"] in defeat_achis:
				complete_achievement( db, achievements[p][defeat_achis[row["loser_faction"]]], row['event_id'] )
				
			if row["winner_faction"] in victory_achis:
				complete_achievement( db, achievements[p][victory_achis[row["winner_faction"]]], row['event_id'] )
				
			if n >= 0:
				complete_achievement( db, achievements[p]["this_game_is_entirely_skill"], row["event_id"] )
			
			if n >= 5:
				complete_achievement( db, achievements[p]["its_5_and_0_somewhere"], row["event_id"] )
							
			#################################
			if row["loser_name"] == "John Harper":
				complete_achievement( db, achievements[p]["never_meet_your_heroes"], row["event_id"] )
			
			if row["loser_name"] in scotland_6n_players:
				count_6n.add(row["loser_name"])
				complete_achievement( db, achievements[p]["bench_em"], row["event_id"] )
				
				if len(list(count_6n)) >= 8:
					complete_achievement( db, achievements[p]["bench_all_of_em"], row["event_id"] )
					
				if len(list(count_6n)) >= 16:
					complete_achievement( db, achievements[p]["youre_gonna_need_a_bigger_bench"], row["event_id"] )
				
				
			#################################
			if row["loser_faction"] in melee_armies:
				complete_achievement( db, achievements[p]["i_am_sigmars_sixes_to_hit"], row["event_id"] )
				
			if row["loser_faction"] in shooting_armies:
				complete_achievement( db, achievements[p]["i_declare_im_jinking"], row["event_id"] )
				
			if row["loser_faction"] in magic_armies:
				complete_achievement( db, achievements[p]["trust_aethermatics_not_superstition"], row["event_id"] )
				
			if row["loser_faction"] in asf_armies:
				complete_achievement( db, achievements[p]["the_activation_wars"], row["event_id"] )
				
			
			#################################
			if '"' not in row["loser_name"]:
				statement = f'SELECT DISTINCT loser_name, loser_faction, event_id, winner_faction, winner_name FROM game WHERE winner_name="{row["loser_name"]}" AND loser_name="{p}"'
				new_rows = [g["winner_name"] for g in db.query(statement)]
				
				counts = sorted([(g, new_rows.count(g)) for g in new_rows], key=lambda i:i [1], reverse=True)
				
				if len(counts) > 0:
					complete_achievement( db, achievements[p]["grudge_bearer"], row["event_id"] )
					
				if len(counts) > 0 and counts[0][1] >= 3:
					complete_achievement( db, achievements[p]["grudge_bearer_2"], row["event_id"] )
					
				if len(counts) > 0 and counts[0][1] >= 5:
					complete_achievement( db, achievements[p]["grudge_bearer_3"], row["event_id"] )
	
		## all lost games
		statement = f'SELECT DISTINCT winner_name, winner_faction, event_id FROM game WHERE loser_name="{p}"'
		rows = db.query(statement)
		
		for n,row in enumerate(rows):
			if n >= 0:
				complete_achievement( db, achievements[p]["this_game_is_entirely_luck"], row["event_id"] )
				
			if row["winner_name"] == "John Harper":
				complete_achievement( db, achievements[p]["never_meet_your_heroes"], row["event_id"] )
				
		## all games
		statement = f'SELECT DISTINCT event_id FROM game WHERE loser_name="{p}" OR winner_name="{p}"'
		rows = db.query(statement)
		
		for n,row in enumerate(rows):
			if n >= 0:
				complete_achievement( db, achievements[p]["just_play"], row["event_id"] )
			if n >= 3:
				complete_achievement( db, achievements[p]["just_play_2"], row["event_id"] )
			if n >= 5:
				complete_achievement( db, achievements[p]["just_play_3"], row["event_id"] )
			if n >= 10:
				complete_achievement( db, achievements[p]["just_play_4"], row["event_id"] )
			if n >= 50:
				complete_achievement( db, achievements[p]["just_play_5"], row["event_id"] )
		
		## single event
		statement = f'SELECT DISTINCT event_id FROM game WHERE loser_name="{p}" OR winner_name="{p}"'
		rows = db.query(statement)
		
		for row in rows:
			new_statement = f'SELECT DISTINCT event_id, winner_kp FROM game WHERE winner_name="{p}" AND event_id={row["event_id"]}'
			new_rows = list(db.query(new_statement))
			pwins = len(new_rows)
			
			if pwins >= 1:
				complete_achievement( db, achievements[p]["on_the_board"], row["event_id"] )
			if pwins >= 2:
				complete_achievement( db, achievements[p]["double_up"], row["event_id"] )
			if pwins >= 3:
				complete_achievement( db, achievements[p]["triple_threat"], row["event_id"] )
			if pwins >= 4:			
				complete_achievement( db, achievements[p]["quadratic_equations"], row["event_id"] )
			if pwins >= 5:
				complete_achievement( db, achievements[p]["iambic_pentameter"], row["event_id"] )
				
			## placing
			new_statement = f'SELECT DISTINCT winner_name, winner_kp FROM game WHERE event_id={row["event_id"]}'
			new_rows = list(db.query(new_statement))
			
			if len(new_rows) > 0 and new_rows[0]["winner_name"] == p:
				complete_achievement( db, achievements[p]["ok_but_sometimes_you_just_gotta_let_em_know"], row["event_id"] )
				
			if len(new_rows) > 3 and (new_rows[1]["winner_name"] == p or new_rows[2]["winner_name"] == p):
				complete_achievement( db, achievements[p]["i_coulda_been_somebody"], row["event_id"] )
				
			# if sum([k['winner_kp'] for k in new_rows if k['winner_name']==p]) >= 10000:
				# complete_achievement( db, achievements[p]["let_none_stand_before_me"], row["event_id"] )
			
				
		## kill_points
		kp = 0
		for res in ["winner", "loser"]:
			statement = f'SELECT DISTINCT event_id, {res}_kp FROM game WHERE {res}_name="{p}"'
			rows = db.query(statement)
			
			for row in rows:
				kp += row[f'{res}_kp']
				
				if res == "winner" and kp == 0:
					complete_achievement( db, achievements[p]["calm_objective_based_gameplay"], row["event_id"] )
					
				if res == "loser" and kp == 2000:
					complete_achievement( db, achievements[p]["yeah_ok_technically"], row["event_id"] )
				
			if kp > 10000:
				complete_achievement( db, achievements[p]["objectives"], row["event_id"] )
			if kp > 20000:
				complete_achievement( db, achievements[p]["objectives_2"], row["event_id"] )
			if kp > 50000:
				complete_achievement( db, achievements[p]["objectives_3"], row["event_id"] )
			if kp > 100000:
				complete_achievement( db, achievements[p]["objectives_4"], row["event_id"] )
				
		
	## faction tiers
	with open("output_data_files/recent_events/datahub_event_data.json", newline='', encoding='utf-8') as json_file:
		edata = json.load(json_file)
	edata.reverse()
	edata = event_landscape.populate_event_tier_lists(edata)
		
	for e in edata:
		date = dp.parse(e["std_date"])
		event = e["name"]
		a_date = f'{event} - {date.strftime("%B %Y")}'
		
		tl = {k:v for k,v in sorted(e["tier_list"].items(),key=lambda i:i[1],reverse=True)}
		if len(tl) < 20: continue
		
		for n,p in enumerate(e["ladder"]):
			name = db_check_aliases.predefined_aliases(p["player_name"])
			if name not in achievements:
				continue
			
			fff= db_check_aliases.predefined_faction_aliases(p["faction"])
			if fff in victory_achis:
				achievements[name][victory_achis[fff]]["event_and_date"] = a_date
			
			##faction_tiers
			if p["faction"] in tl:	
				for n,t in enumerate(tl):
					if t in ["-", "UNKNOWN_ARMY"]: continue
					if t == p["faction"] and n < 3:
						achievements[name]["at_all_costs"]["event_and_date"] = a_date

					if t == p["faction"] and n > len(tl) - 3:
						achievements[name]["challenge_mode"]["event_and_date"] = a_date

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
	
def setup_photoshop_variables(achievements):
	achievements = achievements["Jp Ganis"]
	
	##Description,Icon,PointsValue,Title
	##Do a thing,"photoshop_icons/lumineth.png",30,Did the thing!
	
	with open("metabreakers/photoshop_variables.txt", "w", encoding='utf-8') as file:		
		file.write("Description,Icon,PointsValue,Title\n")
		
		for id in achievements:
			if id == "total_score": continue
			a = achievements[id]
			image_exists = os.path.isfile(f'metabreakers/achievements/{id}.png') 
			
			if image_exists: continue
			print("photo needed for", id)
			file.write(f'\"{a["description"]}\",photoshop_icons/{id}.png,{a["points"]},\"{a["title"]}\"\n')

if __name__ == '__main__':
	db = dataset.connect("sqlite:///__tinydb.db")
	
	a, factions, wfactions = initialize_achievement_data(db)
	a = populate_achievement_data(a, db, factions, wfactions)
	a = update_achievement_complete_status(a)
	
	setup_photoshop_variables(a)
	
	a = spot_achievements.update_achievements_table(a);
	
	a = {k:v for k,v in sorted(a.items(), key=lambda i: i[1]["total_score"], reverse=True)}
	
	confirm = input("overwrite metabreakers data file? y/n ")
	if 'y' in confirm.lower():
		with open(f'metabreakers/data/achievement_data.json', 'w') as json_file:
			json.dump(a, json_file)
	else:
		print("aborted")