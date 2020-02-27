from surprise import KNNBaseline
from surprise import Dataset
from surprise import get_dataset_dir
from surprise import Reader
import json

def read_item_names():
	"""Read the u.item file from MovieLens 100-k dataset and return two
	mappings to convert raw ids into movie names and movie names into raw ids.
	"""
	with open('output_data_files/all_time_data/datahub_player_data.json') as json_file:
		pdata = json.load(json_file)
	
	with open('output_data_files/all_time_data/datahub_faction_data.json') as json_file:
		fdata = json.load(json_file)
		
	del fdata['-']
	for k in ["Death","Order","Chaos","Destruction","UNKNOWN_ARMY"]:
		del fdata[k]
		
	factions = list(fdata.keys())
	playerids = []
	
	rid_to_name = {}
	name_to_rid = {}
	
	for i,f in enumerate(factions):
		rid_to_name[str(i)] = f
		name_to_rid[f] = str(i)

	return rid_to_name, name_to_rid


# First, train the algortihm to compute the similarities between items
reader = Reader(line_format='user item rating', sep=',')
data = Dataset.load_from_file('ratings.csv', reader=reader)
trainset = data.build_full_trainset()
sim_options = {'name': 'pearson_baseline', 'user_based': False}
algo = KNNBaseline(sim_options=sim_options)
algo.fit(trainset)

# Read the mappings raw id <-> movie name
rid_to_name, name_to_rid = read_item_names()

# Retrieve inner id of the movie Toy Story
f = "Flesh Eater Courts"
toy_story_raw_id = name_to_rid[f]
toy_story_inner_id = algo.trainset.to_inner_iid(toy_story_raw_id)

# Retrieve inner ids of the nearest neighbors of Toy Story.
toy_story_neighbors = algo.get_neighbors(toy_story_inner_id, k=10)

# Convert inner ids of the neighbors into names.
toy_story_neighbors = (algo.trainset.to_raw_iid(inner_id)
					   for inner_id in toy_story_neighbors)
toy_story_neighbors = (rid_to_name[rid]
					   for rid in toy_story_neighbors)

print()
print(f'The 10 nearest neighbors of {f} are:')
for movie in toy_story_neighbors:
	print(movie)