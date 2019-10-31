'''
This script looks at returns grouped by months.



Notes:
10/30/19
There does seem to be an impact from the specific month and that can be included in the probability calculation

the strategy works when we can capture large gains and eleminate large losses because of the fat tails


Output: Compare returns for each month to see if there are good months to take off




pandas version: 0.18.1
matplotlib version: 3.0.3
mpl_finance version: 0.10.0
numpy version: 1.10.1
scipy version: 0.16.0

python version: 3.5.4

'''


import pandas as pd
import os
import numpy as np
import re
import datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import time


#open csv file, return the data in a pandas dataframe
def import_data(file_name,fields):
	#only add items in fields list to dataframe
	
	#only add date, open, high, low, last to dataframe
	# fields = ['Date','Open','High','Low','Close']
	
	#open the file using pandas, use the first row as the header
	data = pd.read_csv(file_name,header=0,usecols=fields)
	
	#change the order to most recent date on top if necessary
	data=data.sort_values(fields[0],ascending=0)
	data=data.reset_index(drop=True)
	# ~ print(data.head(5))
	
	return data
	
def slice_df(df,start_date,end_date):
	start_day_df=df.loc[df['Date'] == start_date]
	end_day_df=df.loc[df['Date'] == end_date]
	
	startidx=end_day_df.index[0].tolist()
	endidx=start_day_df.index[0].tolist()
	# print(startidx,endidx)
	# return
	return df[startidx:endidx],startidx,endidx



def start_of_month_detect(df_in,start_date,end_date,month):
	#return a list of the index of the first day of the select month over
	#the given period. if month is 00, test all months.
	#start_date and end_date inputs are strings
	
	#get the low and high index of the dataframe based on the start and end dates
	df,index_l,index_h=slice_df(df_in,start_date,end_date)
	
	index_locations_day0=[]
	idx=index_l+1
	while idx < index_h-1:
		
		cur_date=df['Date'][idx]
		prev_date=df['Date'][idx+1]
		next_date=df['Date'][idx-1]
		
		# get the month value from the current, previous and next date
		cur_date_mo=re.findall(r'-(.+?)-',cur_date)[0]
		prev_date_mo=re.findall(r'-(.+?)-',prev_date)[0]
		next_date_mo=re.findall(r'-(.+?)-',next_date)[0]
		
		#if the month of the current date does not match month of next date append
		
		if cur_date_mo != next_date_mo:
			if month == '00':
				index_locations_day0.append(idx-1)
			elif next_date_mo == month:
				index_locations_day0.append(idx-1)
			idx+=15
		else:
			idx+=1
	
	#test the dates
	# ~ for idx in index_locations:
		# ~ print(df['Date'][idx])
	
	
	return index_locations_day0,df


	
def get_returns_full_trade(df,idx_list,start,end):
	# this function will generate a list of the percent returns of all the trades with the day0's listed in idx_list.
	# using -4 to +1 time frame
	# start=-4
	# end=1
	
	fields = ['Date','Open','High','Low','Close']
	
	
	#get the return, the closing price at the last trading day minus the closing price
	#at the first trading day over the given period.
	abs_returns=[]
	pct_returns=[]
	for idx in idx_list:
		trade_close=df['Close'][idx-end]
		trade_open=df['Open'][idx-start]
		min_vals=[]
		# print(range(idx-end,idx-start))
		for indx in range(idx-end,idx-start):
			min_vals.append(df['Low'][indx])
		
		trade_low=min(min_vals)
		# abs_returns.append(days_close-days_open)
		# print((trade_open-trade_low)/trade_open)
		
		# use the following to include a stop loss
		if ((trade_open-trade_low)/trade_open) < -0.025:
			pct_returns.append(-2.5)
		elif ((trade_close-trade_open)/trade_open) < -0.025:
			pct_returns.append(-2.5)
		else:
			pct_returns.append(round(100*(trade_close-trade_open)/trade_open,2))
		
		# Use the following for no stop loss
		# pct_returns.append(round(100*(trade_close-trade_open)/trade_open,2))
	
	return pct_returns
	
	

def main():
	start_time = time.time()
	#####
	# input main info here
	#####
	
	# Data location for mac:
	# path = '/Users/Marlowe/Marlowe/Securities_Trading/_Ideas/Data/'
	# path = '/Users/Marlowe/gitsite/TOM/'
	
	# Data location for PC:
	path = 'C:\\Python\\transfer\\'
	
	# input the names of the fields if they are different from ['Date','Open','High','Low','Close'], use that order
	fields = ['Date','Open','High','Low','Close']
	
	
	#####
	# Input files to analyze
	#####
	
	#input file names of interest
	# file_name='^RUT.csv'
	file_name='^GSPC.csv'
	
	
	in_file= os.path.join(path,file_name)
	
	
	# add a header to the file if no header exists
	#add_header(in_file)
	
	#use csv module to pull out proper data
	#file_noblanks=remove_blanks(in_file)
	
	
	# create dataframe from the data
	df=import_data(in_file,fields)
	
	
	
	#####
	# input the date range of interest for overall analysis
	#####
	
	#first date in russell: 1987-09-10
	#first date in GSPC: 1950-01-04
	
	# start_date='1950-01-04'
	start_date='1987-09-10'
	# start_date='1999-09-10'
	# ~ start_date='2000-09-11'
	
	# end_date='2000-09-11'
	end_date='2019-05-10'
	
	
	
	print()
	
	#####
	# generate the pct returns for each month in the desired period
	#####
	idx_list_day0,df_sliced=start_of_month_detect(df,start_date,end_date,'00')
	all_rtns=get_returns_full_trade(df_sliced,idx_list_day0,-4,1)
	print('Mean return of tom: '+str(round(np.mean(all_rtns),2))+', num samps: '+str(len(idx_list_day0)))
	print()
	print('Avg num samps in month: '+str(round(len(idx_list_day0)/12,1)))
	
	# generate a list of indexes of first days of all months in test period
	months=['01','02','03','04','05','06','07','08','09','10','11','12']
	month_lists=[]
	month_rtns=[]
	for month in months:
		idxs,df_sliced=start_of_month_detect(df,start_date,end_date,month)
		month_lists.append(idxs)
		months_rtns=get_returns_full_trade(df_sliced,idxs,-4,1)
		month_rtns.append(months_rtns)
		num_gt_1=len([rtn for rtn in months_rtns if (rtn > 2.0)])
		print('Mean return of month '+month+' is '+str(round(np.mean(get_returns_full_trade(df_sliced,idxs,-4,1)),2)))
		print('Number above 2%: '+str(num_gt_1)+', pct of total: '+str(round(100*num_gt_1/len(idxs),1)))
		print('Max return: '+str(max(months_rtns)))
	
	
	
	
	
	
	
	print()
	print('%f seconds to run script' % (time.time() - start_time))
	print()
	
	
	return

main()
