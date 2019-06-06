# 6/2/19
# load data from csv
# Plot


# ~ import pprint
# ~ import copy

# ~ import csv
import os
import pandas as pd
from matplotlib import pyplot as plt
from datetime import datetime


flattenList=lambda _: [_1 for _2 in _ for _1 in _2] # collapse a list of lists to a 1d-list.
lTranspose=lambda _: list(map(list, zip(*_))) # transpose a list (pivot table)



def import_data(file_name):
	#only add items in fields list to dataframe
	
	#only add date, open, high, low, last to dataframe
	# fields = ['Date','Open','High','Low','Close']
	
	#open the file using pandas, use the first row as the header
	# ~ data = pd.read_csv(file_name,header=0,usecols=fields)
	data = pd.read_csv(file_name,header=0)
	
	#change the order to most recent date on top if necessary
	data=data.sort('Date',ascending=0)
	data=data.reset_index(drop=True)
	# ~ print(data.head(5))
	
	return data


def main():
	####
	# Open results datafile
	####

	#####
	# input main info here
	#####
	# Data location for PC:
	path = 'C:\\Python\\transfer\\results_2019_06_02\\'
	
	# Data location for mac:
	# path = '/Users/Marlowe/Marlowe/Securities_Trading/_Ideas/Data/'
	# path = '/Users/Marlowe/gitsite/transfer/results_2019_06_02/'

	#input file name of interest
	in_file_name='RUT_output.csv'

	in_file= os.path.join(path,in_file_name)


	# create dataframe from the data
	df=import_data(in_file)

	# ~ print(df.head())
	# ~ return

	# Go through df to output data in the following format:

	#	return {"bull_markets":bulls, "bear_markets":bears},
	#		type dict: {"bull_markets" : bull markets as [[date as datetime.datetime, closing price as float], ...], 
	#		"bear_markets": bear markets as [[date as datetime.datetime, closing price as float], ...]}

	data_dict={
				'undefined': [],
				'Bear': [],
				'Bull': [],
				'Bull Correction': [],
				'Bear Correction': [],
				'Bull Pullback': [],
				'Bear Pullback': []
	}
	
	sampleDataset=[]
	
	for idx in range(len(df)-1000,len(df)):
		curr_mkt=df['Market'][idx]
		curr_close=float(df['Close'][idx])
		curr_date=datetime.strptime(df['Date'][idx],"%Y-%m-%d")
		
		curr_add=[curr_date,curr_close]
		sampleDataset.append(curr_add)
		data_dict[curr_mkt].append(curr_add)
		
	# ~ print(data_dict['Bear'])
	
	# ~ return
	# ~ allBulls=[_ for _ in allMarkets['bull_markets'] if _[1] is not None]
	# ~ allBears=[_ for _ in allMarkets['bear_markets'] if _[1] is not None]
	
	# ~ allBulls=[data_dict['Bull']]
	# ~ allBears=[data_dict['Bear']]
	# ~ allBullPullbacks=[data_dict['Bull Pullback']]
	# ~ allBullCorrs=[data_dict['Bull Correction']]
	# ~ allBearPullbacks=[data_dict['Bear Pullback']]
	# ~ allBearCorrs=[data_dict['Bear Correction']]
	
	# ~ sampleDataset=
	
	# ~ print()
	# ~ print(allBearCorrs)
	
	# ~ return
	
	####
	# PLOT Data
	####
	#plot with line overlays
	####
	'''
	plt.figure()
	plt.title("Markets, corrections and pullbacks")
	plt.yscale('log')
	# ~ plt.plot(*lTranspose(sampleDataset))
	plt.plot(*lTranspose(sampleDataset))
	
	def plotMarket(market, color, label):
		for i,_ in enumerate(market): # PLOT BULL MARKETS
			if i==0: 
				plt.plot(*lTranspose(_), color=color, label=label)
			else: 
				plt.plot(*lTranspose(_), color=color)
	
	plotMarket(allBulls, 'green', 'bull market')
	plotMarket(allBears, 'red', 'bear market')
	plotMarket(flattenList(allBullCorrs), 'orange', 'bull correction')
	plotMarket(flattenList(allBullPullbacks), 'yellow', 'bull pullback')
	plotMarket(flattenList(allBearCorrs), 'orange', 'bull correction')
	plotMarket(flattenList(allBearPullbacks), 'yellow', 'bull pullback')
	
	plt.legend()
	plt.show()
	
	'''

	'''
	print("Latest price is %s" %sampleDataset[-1])
	if allBulls[-1][1]<allBears[-1][1]: 
		print("Currently we are in a bull market, \nlast bear market was %s"  %allBears[-1])
		marketAge=sampleDataset[-1][0]-allBears[-1][1][0]
	else:
		print("Currently we are in a bear market, \nlast bull market was %s"  %allBulls[-1])
		marketAge=sampleDataset[-1][0]-allBulls[-1][1][0]
	print("Market age is %s" %marketAge)
	'''

	#plot with markers
	'''
	import copy
	sampleDatasetEdit=copy.deepcopy(sampleDataset) # we wouldn't want to mess up our data

	for dp in sampleDatasetEdit:
		dp.append('undefined')# add a third column to store market type
		dp.append('undefined')# add a forth column to store corrections
		dp.append('undefined')# add a fifth column to store pullbacks

	# not a computationally efficient solution, but quick to implement
	def updateColumnTo(dset,states,columnNum,value):
		for dpoint in dset:
			if dpoint[0]==states[0][0] or dpoint[0]==states[1][0]:
				dpoint[columnNum]='undefined'
			if dpoint[0]>states[0][0] and dpoint[0]<states[1][0]:
				dpoint[columnNum]=value


	for bull in allBulls:
		updateColumnTo(sampleDatasetEdit,bull,2,'bull')
	for bear in allBears:
		updateColumnTo(sampleDatasetEdit,bear,2,'bear')
		
	for _ in flattenList(allBullCorrs):
		updateColumnTo(sampleDatasetEdit,_,3,'correction')
	for _ in flattenList(allBullBwCorrs):
		updateColumnTo(sampleDatasetEdit,_,3,'between_corrections')
	for _ in flattenList(allBearCorrs):
		updateColumnTo(sampleDatasetEdit,_,3,'correction')
	for _ in flattenList(allBullBwCorrs):
		updateColumnTo(sampleDatasetEdit,_,3,'between_corrections')
			
	for _ in flattenList(allBullPullbacks):
		updateColumnTo(sampleDatasetEdit,_,4,'pullback')
	for _ in flattenList(allBullBwPullbacks):
		updateColumnTo(sampleDatasetEdit,_,4,'between_pullbacks')
	for _ in flattenList(allBearPullbacks):
		updateColumnTo(sampleDatasetEdit,_,4,'pullback')
	for _ in flattenList(allBullBwPullbacks):
		updateColumnTo(sampleDatasetEdit,_,4,'between_pullbacks')
'''
	#set plot start and finish
	p_start=0
	p_finish=7823
	# ~ print(len(sampleDatasetEdit))

	# ~ test_bull_bw_pullbacks=[_[0:2] for _ in sampleDatasetEdit[p_start:p_finish] if _[2]=='bull' and _[4]=='between_pullbacks']
	# ~ test_bull_corrs=[_[0:2] for _ in sampleDatasetEdit[p_start:p_finish] if _[2]=='bull' and _[3]=='correction']
	# ~ test_bull_pullbacks=[_[0:2] for _ in sampleDatasetEdit[p_start:p_finish] if _[2]=='bull' and _[4]=='pullback']
	# ~ test_bear=[_[0:2] for _ in sampleDatasetEdit[p_start:p_finish] if _[2]=='bear']
	# ~ test_bear_corrs=[_[0:2] for _ in sampleDatasetEdit[p_start:p_finish] if _[2]=='bear' and _[3]=='correction']
	# ~ test_bear_pullbacks=[_[0:2] for _ in sampleDatasetEdit[p_start:p_finish] if _[2]=='bear' and _[4]=='pullback']
	
	test_bull=[data_dict['Bull']]
	test_bull_corrs=[data_dict['Bull Correction']]
	test_bull_pullbacks=[data_dict['Bull Pullback']]
	test_bear=[data_dict['Bear']]
	test_bear_corrs=[data_dict['Bear Correction']]
	test_bear_pullbacks=[data_dict['Bear Pullback']]
	
	# ~ allBulls=[data_dict['Bull']]
	# ~ allBears=[data_dict['Bear']]
	# ~ allBullPullbacks=
	# ~ allBullCorrs=
	# ~ allBearPullbacks=[data_dict['Bear Pullback']]
	# ~ allBearCorrs=
	
	# ~ print(test_bull)
	# ~ return
	
	# ~ plt.figure(figsize=(20,8))
	plt.figure()
	plt.title("Markets, bull corrections and bull pullbacks on ^GSPC")
	plt.yscale('log')
	plt.plot(*lTranspose(flattenList(test_bull)),'.', markersize=1, color='green')
	plt.plot(*lTranspose(flattenList(test_bear)),'.', markersize=1, color='red')
	plt.plot(*lTranspose(flattenList(test_bull_corrs)),'.', markersize=1, color='orange')
	plt.plot(*lTranspose(flattenList(test_bull_pullbacks)),'.', markersize=1, color='yellow')
	plt.plot(*lTranspose(flattenList(test_bear_corrs)),'.', markersize=1, color='orange')
	plt.plot(*lTranspose(flattenList(test_bear_pullbacks)),'.', markersize=1, color='yellow')
	plt.show()
	


if __name__ == '__main__': main()
# main()
