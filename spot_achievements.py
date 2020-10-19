import dateutil.parser as dp
import achievement_rarities
import json

def complete_achievement(a, event_name, date):
	a["complete"] = True
	a["event_id"] = -1
	a["event_and_date"] =  f'{event_name} - {dp.parse(date).strftime("%B %Y")}'
	
def update_achievements_table(a):
	complete_achievement( a["Jp Ganis"]["calm_objective_based_gameplay"], "The Howling", "06-10-2018" )
	complete_achievement( a["Jp Ganis"]["bench_all_of_em"], "Northern Masters 2019", "08-12-2019" )
	complete_achievement( a["Jp Ganis"]["below_budget"], "Tempest - Legion Of Sacrament", "01-01-2019" )
	complete_achievement( a["Jp Ganis"]["can_cope"], "Ulster Warlords - Gloomspite Gitz", "08-08-2019" )
	complete_achievement( a["Jp Ganis"]["challenge_mode"], "The Howling - Nighthaunt", "01-10-2018" )
	
	complete_achievement( a["Liam Watt"]["blood_of_the_blood_god"], "Masters ", "06-06-2019" )
	complete_achievement( a["Liam Watt"]["chew_on_this"], "Some Event Somewhere", "06-06-2019" )
	complete_achievement( a["Liam Watt"]["bench_all_of_em"], "Northern Masters 2019", "08-12-2019" )
	complete_achievement( a["Liam Watt"]["theyll_never_take_our_freedom"], "Facehammer GT", "06-05-2018" )
	
	complete_achievement( a["Grant Fraser"]["lovable"], "Tempest", "19-01-2019" )
	
	complete_achievement( a["Andrew Stephen"]["rage_against_the_machine"], "Onslaught", "08-08-2020" )
	complete_achievement( a["Andrew Stephen"]["blood_of_the_blood_god"], "Fall of the Old World VI", "03/2020" )
	complete_achievement( a["Andrew Stephen"]["goat"], "Fall of the Old World VI", "03/2020" )
	complete_achievement( a["Andrew Stephen"]["ratcatchin"], "Cry Havoc", "06/2019" )
	complete_achievement( a["Andrew Stephen"]["lots_o_grots"], "Cry Havoc", "06/2019" )
	complete_achievement( a["Andrew Stephen"]["that_was_sick"], "Winter War", "11/2019" )
	complete_achievement( a["Andrew Stephen"]["wait_were_you_enjoying_that"], "Warlords Revenge", "11/2019" )
	complete_achievement( a["Andrew Stephen"]["wyld_wyld_west"], "Renegade", "10/2019" )
	complete_achievement( a["Andrew Stephen"]["stay_hungry_stay_humble"], "Warlords Revenge", "11/2019" )
	complete_achievement( a["Andrew Stephen"]["ok_but_sometimes_you_just_gotta_let_em_know"], "Renegade", "10/2019" )
	complete_achievement( a["Andrew Stephen"]["just_play_4"], "Northern Invasion", "09/2020" )
	complete_achievement( a["Andrew Stephen"]["trust_aethermatics_not_superstition"], "Onslaught 2020", "08/2020" )
	complete_achievement( a["Andrew Stephen"]["theyll_never_take_our_freedom"], "Warlords Revenge", "11/2019" )
	complete_achievement( a["Andrew Stephen"]["calm_objective_based_gameplay"], "Fall of the Old World VI", "03/2020" )

	complete_achievement( a["Nathan Watson"]["blood_of_the_blood_god"], "Northern invasion 2019", "06-06-2019" )
	
	complete_achievement( a["Kevin Low"]["this_is_my_boomstick"], "Bobo 2019", "06-05-2019" )
	complete_achievement( a["Kevin Low"]["winners_dont_split_and_splitters_dont_win"], "Bobo 2019", "06-05-2019" )
	complete_achievement( a["Kevin Low"]["wait_its_all_chaff_always_has_been"], "Bobo 2019", "06-06-2019" )
	complete_achievement( a["Kevin Low"]["theyll_never_take_our_freedom"], "Bobo 2019", "06-06-2019" )
	complete_achievement( a["Kevin Low"]["bite_me"], "Northern Masters 2019", "08-12-2019" )
	
	complete_achievement( a["Tom Bell"]["blood_of_the_blood_god"], "Some Event Somewhere", "06-06-2019" )
	complete_achievement( a["Tom Bell"]["eels_whyd_it_have_to_be_eels"], "Bobo", "06-06-2019" )
	complete_achievement( a["Tom Bell"]["goat"], "Blackout IV", "06-06-2019" )
	complete_achievement( a["Tom Bell"]["jawbreakers"], "Sheffield slaughter 2019", "06-06-2019" )
	complete_achievement( a["Tom Bell"]["life_uh_finds_a_way"], "Some Event Somewhere", "06-06-2019" )
	complete_achievement( a["Tom Bell"]["literally_griefing"], "Bloodshed in the shores 2019", "06-06-2019" )
	complete_achievement( a["Tom Bell"]["nobody_tosses_a_wait"], "EGGS 2019", "06-06-2019" )
	complete_achievement( a["Tom Bell"]["that_was_sick"], "Blood and Glory 2017", "06-06-2019" )
	complete_achievement( a["Tom Bell"]["wyld_wyld_west"], "Bloodshed in the shires 2019", "06-06-2019" )
	complete_achievement( a["Tom Bell"]["quadratic_equations"], "Blackout IV", "06-06-2019" )
	complete_achievement( a["Tom Bell"]["just_play_4"], "Some Event Somewhere", "06-06-2019" )
	complete_achievement( a["Tom Bell"]["i_coulda_been_somebody"], "Rising Sun GT", "06-06-2019" )
	complete_achievement( a["Tom Bell"]["two_heads_are_better_than_one"], "Crimbobo 2019", "06-06-2019" )
	complete_achievement( a["Tom Bell"]["objectives_2"], "Blackout IV", "06-06-2019" )
	complete_achievement( a["Tom Bell"]["theyll_never_take_our_freedom"], "Some Event Somewhere", "06-06-2019" )
	complete_achievement( a["Tom Bell"]["i_am_sigmars_sixes_to_hit"], "Some Event Somewhere", "06-06-2019" )
	
	complete_achievement( a["Reece West"]["yeah_ok_technically"], "Bobo", "06-06-2019" )
	complete_achievement( a["Reece West"]["life_uh_finds_a_way"], "Scribes of War Showdown", "06-06-2019" )
	
	complete_achievement( a["John B"]["black_coach_down"], "NI 2018", "06-06-2019" )
	complete_achievement( a["John B"]["blood_of_the_blood_god"], "FOTOW 2020", "06-06-2019" )
	complete_achievement( a["John B"]["black_coach_down"], "Some Event Somewhere", "06-06-2019" )
	complete_achievement( a["John B"]["im_gonna_pay_you_100_aethergold"], "Some Event Somewhere", "06-06-2019" )
	complete_achievement( a["John B"]["we_did_it_rage_kage"], "Some Event Somewhere", "06-06-2019" )
	complete_achievement( a["John B"]["jawbreakers"], "Tempest 2019", "06-06-2019" )
	complete_achievement( a["John B"]["lightning_doesnt_even_strike_once"], "Some Event Somewhere", "06-06-2019" )
	complete_achievement( a["John B"]["lots_o_grots"], "Some Event Somewhere", "06-06-2019" )
	complete_achievement( a["John B"]["under_hooves_of_brass"], "FOTOW 2020", "06-03-2020" )
	complete_achievement( a["John B"]["at_all_costs"], "Masters 2019", "06-12-2019" )
	complete_achievement( a["John B"]["just_play_4"], "Some Event Somewhere", "06-06-2019" )
	complete_achievement( a["John B"]["squad_goals"], "2019 6 N", "06-06-2019" )
	complete_achievement( a["John B"]["never_meet_your_heroes"], "Tempest 2018", "06-01-2018" )
	complete_achievement( a["John B"]["what_is_best_in_life"], "Onslaught", "06-08-2020" )
	complete_achievement( a["John B"]["bringing_the_pain_train_to_the_khaine_dame"], "NI 2018", "07/2018" )
	complete_achievement( a["John B"]["high_spirits"], "NI 2018", "07/2018" )
	complete_achievement( a["John B"]["an_eely_good_time"], "Tempest 2020", "01/2020" )
	
	complete_achievement( a["Mike Callaghan"]["iambic_pentameter"], "Heat 2 2018", "06-06-2019" )
	complete_achievement( a["Mike Callaghan"]["ok_but_sometimes_you_just_gotta_let_em_know"], "Tempest 2016", "06-06-2016" )
	complete_achievement( a["Mike Callaghan"]["two_thin_coats"], "Onslaught 2020", "06-08-2020" )
	
	complete_achievement( a["Benjamin Savva"]["blood_of_the_blood_god"], "GT Final", "14/10/18" )
	complete_achievement( a["Benjamin Savva"]["bringing_the_pain_train_to_the_khaine_dame"], "GT Final", "14/10/18" )
	complete_achievement( a["Benjamin Savva"]["chew_on_this"], "Brotherhood", "18/01/2020" )
	complete_achievement( a["Benjamin Savva"]["im_gonna_pay_you_100_aethergold"], "Blood Tithe", "03/03/18" )
	complete_achievement( a["Benjamin Savva"]["iambic_pentameter"], "GT Final", "14/10/18" )
	complete_achievement( a["Benjamin Savva"]["two_thin_coats"], "Warhammer Fest", "28/05/17" )
	complete_achievement( a["Benjamin Savva"]["squad_goals"], "Brotherhood", "18/01/2020" )
	complete_achievement( a["Benjamin Savva"]["calm_objective_based_gameplay"], "GT Final", "14/10/18" )
	complete_achievement( a["Benjamin Savva"]["what_is_best_in_life"], "Brotherhood", "18/01/2020" )
	
	complete_achievement( a["Stephen Mitchell"]["bringing_the_pain_train_to_the_khaine_dame"], "Ulster Warlords", "01/02/2020" )
	complete_achievement( a["Stephen Mitchell"]["jawbreakers"], "Ulster Warlords", "01/02/2020" )
	complete_achievement( a["Stephen Mitchell"]["high_spirits"], "Ulster Warlords", "01/02/2020" )
	complete_achievement( a["Stephen Mitchell"]["jawbreakers"], "Ulster Warlords", "01/02/2020" )
	
	complete_achievement( a["Mathew Davies"]["blood_of_the_blood_god"], "Da Great South Waaagh", "02/2020" )
	complete_achievement( a["Mathew Davies"]["calm_objective_based_gameplay"], "Sigmar First Blood", "08/2019" )
	
	
	for p in a:
		a[p]["total_score"] = sum([a[p][achi]["points"] for achi in a[p] if achi != "total_score" and a[p][achi]["complete"]])
		
	a = {k:v for k,v in sorted(a.items(), key=lambda i: i[1]["total_score"], reverse=True)}
	achievement_rarities.update_rarities_file()
	
	return a
	
if __name__ == '__main__':
	with open("metabreakers/data/achievement_data.json", newline='', encoding='utf-8') as json_file:
		a_data = json.load(json_file)
	
	a_data = update_achievements_table(a_data)
	
	print("dumping output")
	with open(f'metabreakers/data/achievement_data.json', 'w') as json_file:
		json.dump(a_data, json_file)