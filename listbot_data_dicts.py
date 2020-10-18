import json

def get_data_dicts(dataset="recent_events"):
		
	with open(f'output_data_files/{dataset}/datahub_player_data.json', newline='', encoding='utf-8') as json_file:
		player_data = json.load(json_file)
		
	with open(f'output_data_files/{dataset}/datahub_faction_data.json', newline='', encoding='utf-8') as json_file:
		faction_data = json.load(json_file)
		
	with open(f'output_data_files/{dataset}/datahub_event_data.json', newline='', encoding='utf-8') as json_file:
		event_data = json.load(json_file)
		
	return {"player_data": player_data, "faction_data": faction_data, "event_data": event_data}