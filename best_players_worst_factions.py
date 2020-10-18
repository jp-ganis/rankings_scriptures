import json
import matplotlib.pyplot as plt
plt.style.use('seaborn-whitegrid')
import statistics
import random


if __name__ == '__main__':
	with open('output_data_files/recent_events/datahub_player_data.json') as json_file:
		pdata = json.load(json_file)
	
	with open('output_data_files/recent_events/datahub_faction_data.json') as json_file:
		fdata = json.load(json_file)
		
	fdelts = {f:int(fdata[f]["mean_delta"]) for f in fdata if len(fdata[f]["events"]) > 10}
	fdelts = {k:v for k,v in sorted(fdelts.items(), key=lambda i: i[1], reverse=True)}
	
	x = []
	y = []
	y2= []
	dy= []
	dy2=[]
	
	for f in fdelts:
		print(f'{f:35} {fdelts[f]}')
		
	pdata = {k:v for k,v in sorted(pdata.items(), key=lambda i: i[1]["gaussian_score"], reverse=True)}
	
	for player in pdata:
		print(f'{player:35} {int(pdata[player]["gaussian_score"])}')
	
	print(pdata["Jack Armstrong"]["gaussian_score"])
	
	print(pdata["Jp Ganis"]["gaussian_score"])
	
	i = 0
	for p in pdata:	
		i+=1
		# if i % 5 < 4: continue
		
		ld = []
		for e in pdata[p]["events"]:
			f = e["faction"]
			ld.append( fdata[f]["mean_delta"] )
		
		ld = statistics.mean(ld)
		
		## if ld = 10 and best faction is +14 should be 4
		## if ld = 10 and worst faction is -14 should be -24
		
		top_delta = (14 - ld)/2
		bottom_delta = abs(-14 - ld)/2
		
		if ((top_delta + bottom_delta) - 28) > 2: continue
		
		s=pdata[p]["gaussian_score"]/3
		
		dy.append(top_delta)
		dy2.append(bottom_delta)
		
		x.append(i)
		y.append(s)
		y2.append(s-ld)
		# print(f'{p:35} {int(pdata[p]["gaussian_score"])}')
		
	# y2 = sorted(y2, reverse=True)
		
	# plt.scatter(x,y,s=2,c='blue')
	# plt.scatter(x,y2,s=2,c='red')
	
	plt.errorbar(x, y, yerr=[dy2,dy], fmt='o', color='black',ecolor='lightgray', elinewidth=1, capsize=2, ms=1)
	
	# plt.plot(x,y,c='blue')
	# plt.plot(x,y2,c='red')
	plt.show()