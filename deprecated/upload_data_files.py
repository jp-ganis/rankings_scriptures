import shutil
import glob

if __name__ == '__main__':
	northern_files = glob.glob('data_files/northern_events/*')
	
	file_locations = {}
	
	for nf in northern_files:
		file_locations[nf] = 'metabreakers/data/northern_events'
		

	for file in file_locations:
		print(shutil.copy(file, file_locations[file]))
