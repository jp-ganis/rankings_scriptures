import statistics
import json


if __name__ == '__main__':
	with open('output_data_files/uk_events/datahub_player_data.json', newline='') as json_file:
		pdata = json.load(json_file)

	with open('output_data_files/uk_events/datahub_faction_data.json', newline='') as json_file:
		fdata = json.load(json_file)

	faction_players = {}

	for f in fdata:
		for e in fdata[f]["events"]:
			p = pdata[e["player_name"]]
			pscores = []
			
			for ep in p["events"]:
				if ep["faction"] == f: continue
				pscores.append(ep["gaussian_score"])

			if len(pscores) < 3: continue

			if f not in faction_players:
				faction_players[f] = []
			faction_players[f].append(statistics.mean(pscores))
	
	faction_scores = {f: statistics.mean(faction_players[f]) for f in faction_players}
	faction_scores = {k:v for k,v in sorted(faction_scores.items(), key=lambda i:i[1], reverse=True)}

	faction_total = sum([faction_scores[f] for f in faction_scores])
	faction_norms = {f:faction_scores[f]/faction_total*fdata[f]["mean_gaussian_score"] for f in faction_scores}

	faction_norms = {k:v for k,v in sorted(faction_norms.items(), key=lambda i:i[1], reverse=True)}

	for f in faction_scores:
		if len(faction_players[f]) < 20: continue
		print(f'{f:35} {int(faction_scores[f])} {int(fdata[f]["mean_gaussian_score"])}')

	for f in faction_norms:
		if len(faction_players[f]) < 20: continue
		print(f'{f:35} {int(faction_norms[f]*100)} {int(fdata[f]["mean_gaussian_score"])}')



