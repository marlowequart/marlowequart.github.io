'''
The purpose of this script is to look up data in the futures contracts


Input: list of futures contracts

Output: Desired data




Notes:
python version: 3.5.5

pandas version: 0.23.4
matplotlib version: 2.2.2
numpy version: 1.11.3
scipy version: 1.1.0
datetime, # built-in, Python 3.5.5
csv, # built-in, Python 3.5.5
math, # built-in, Python 3.5.5


'''


import csv
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import math
import datetime
import glob


def true_range_calc(df,lowidx,highidx,num_days):
	#cycle through dataframe, using ohlc data
	#output the df with new column with TR data
	#true range is max(todays high-low,todays high-yesterdays close,yesterdays close-todays low)
	
	# ~ print(df.head())
	
	df_out=df[lowidx-10:highidx]
	#add column for true range
	df_out['true_range']=''
	df_out['ATR']=''
	
	for idx in range(lowidx,highidx):
		day_high=df_out['High'][idx]
		yest_close=df_out['Close'][idx-1]
		day_low=df_out['Low'][idx]
		true_r=max(day_high-day_low,day_high-yest_close,yest_close-day_low)
		true_r=float(true_r)
		df_out['true_range'][idx]=true_r
	
	for idx in range(lowidx+num_days,highidx):
		atr=0
		for x in range(num_days):
			atr=atr+df_out['true_range'][idx-x]
		atr_av=atr/num_days
		df_out['ATR'][idx]=atr_av
	
	return df_out


pd.options.mode.chained_assignment = None

# input the names of the fields if they are different from ['Date','Open','High','Low','Close'], use that order
fields = ['Date','Open','High','Low','Close','Open Interest','Volume']


PRINT=False
PLOT=False


data_folder='CLCDATA_rev_adj/'


# Open folder and get all file names
files=glob.glob("CLCDATA_rev_adj/*.CSV")
# ~ print(files)

# ~ df = pd.read_csv(files[10],header=0)
# ~ last_line=df.iloc[[-1]].values.flatten().tolist()
# ~ print(last_line)

# get the closing price and date of the last line in each file
'''
prices=[]
for file_name in files:
	# ~ print(file_name)
	df = pd.read_csv(file_name,header=0)
	last_line=df.iloc[[-1]].values.flatten().tolist()
	# ~ print('Date: '+last_line[0])
	# ~ print('Close: '+str(last_line[4]))
	prices.append(last_line[4])
	print(last_line[4])
'''

# get the atr in each file
# calculate the max and mean for the 100d ATR
num_years=2
num_days_avg=100

atr=[]
for file_name in files:
	# ~ print(file_name)
	df = pd.read_csv(file_name,names=fields)
	
	idx_delta=252*num_years+num_days_avg
	end_idx=df.tail(1).index.item()
	start_idx=end_idx-idx_delta
	
	df2=true_range_calc(df,start_idx,end_idx,num_days_avg)
	
	max_atr=df2.loc[start_idx+num_days_avg:end_idx]['ATR'].max()
	mean_atr=df2.loc[start_idx+num_days_avg:end_idx]['ATR'].mean()
	
	atr.append([max_atr,mean_atr])
	print(file_name)
	print('max atr: '+str(round(max_atr,2)))
	print('mean atr: '+str(round(mean_atr,2)))

