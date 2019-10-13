'''
This script looks at largest single day losses and the results of the overall trade
The idea is to cut the trade short if a large enough loss occurs.





Output:


Notes:




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
# ~ import matplotlib.pyplot as plt
# ~ import matplotlib.ticker as plticker
import time
from operator import itemgetter


#open csv file, return the data in a pandas dataframe
def import_data(file_name,fields):
	#only add items in fields list to dataframe
	
	#only add date, open, high, low, last to dataframe
	# fields = ['Date','Open','High','Low','Close']
	
	#open the file using pandas, use the first row as the header
	data = pd.read_csv(file_name,header=0,usecols=fields)
	
	#change the order to most recent date on top if necessary
	data=data.sort_index(axis=0,ascending=0)
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
	
	# Create indexes for daym1 and day1
	index_locations_daym4=[idx+4 for idx in index_locations_day0]

	
	return index_locations_day0,df


def get_returns_sing_day(df,idx_list):
	# this function will generate a list of the percent returns of all the days in idx_list.
	
	fields = ['Date','Open','High','Low','Close']
	
	
	#get the return, the closing price at the last trading day minus the closing price
	#at the first trading day over the given period.
	abs_returns=[]
	pct_returns=[]
	for idx in idx_list:
		days_close=df['Close'][idx]
		days_open=df['Open'][idx]
		abs_returns.append(days_close-days_open)
		pct_returns.append(round(100*(days_close-days_open)/days_open,2))
	
	
	return pct_returns
	
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
		
		# the following section includes a stop loss of 3%
		'''
		if ((trade_open-trade_low)/trade_open) < -0.03:
			pct_returns.append(-3.0)
		elif ((trade_close-trade_open)/trade_open) < -0.03:
			pct_returns.append(-3.0)
		else:
			pct_returns.append(round(100*(trade_close-trade_open)/trade_open,2))
		'''
		#use this section for no stop loss
		pct_returns.append(round(100*(trade_close-trade_open)/trade_open,2))
	
	
	return pct_returns

def main():
	start_time = time.time()
	#####
	# input main info here
	#####
	
	# Data location for mac:
	# path = '/Users/Marlowe/Marlowe/Securities_Trading/_Ideas/Data/'
	path = '/Users/Marlowe/gitsite/transfer/'
	
	# Data location for PC:
	# ~ path = 'C:\\Python\\transfer\\'
	
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
	
	# ~ start_date='1950-01-04'
	# ~ start_date='1987-09-10'
	start_date='1999-09-10'
	# ~ start_date='2000-09-11'
	
	# ~ end_date='2000-09-11'
	end_date='2019-05-10'
	
	
	
	print()
	
	#####
	# Lets look at the average daily returns of each day for periods ending monday-friday
	#####
	
	# generate a list of indexes of first days of all months in test period
	idx_list_day0,df_sliced=start_of_month_detect(df,start_date,end_date,'00')
	
	
	# Generate a dictionary of all trading returns
	# dict contains: dict key(days_idx):day_0_idx,day_of_trade,days_%_rtn,overall_trade_rtn
	
	#create list of all indexes
	return_dict={}
	for item in idx_list_day0:
		full_trade_rtn=get_returns_full_trade(df_sliced,[item],-4,1)
		
		sing_day_m4_rtn=get_returns_sing_day(df_sliced,[item+4])
		return_dict[item+4]=[item,-4,sing_day_m4_rtn[0],full_trade_rtn[0]]
		sing_day_m3_rtn=get_returns_sing_day(df_sliced,[item+3])
		return_dict[item+3]=[item,-3,sing_day_m3_rtn[0],full_trade_rtn[0]]
		sing_day_m2_rtn=get_returns_sing_day(df_sliced,[item+2])
		return_dict[item+2]=[item,-2,sing_day_m2_rtn[0],full_trade_rtn[0]]
		sing_day_m1_rtn=get_returns_sing_day(df_sliced,[item+1])
		return_dict[item+1]=[item,-1,sing_day_m1_rtn[0],full_trade_rtn[0]]
		sing_day_0_rtn=get_returns_sing_day(df_sliced,[item])
		return_dict[item]=[item,0,sing_day_0_rtn[0],full_trade_rtn[0]]
		sing_day_p1_rtn=get_returns_sing_day(df_sliced,[item-1])
		return_dict[item-1]=[item,1,sing_day_p1_rtn[0],full_trade_rtn[0]]
	
	
	
	
	# create list of single day losses by rank, and associated overall trade loss
	losses_un_sorted=[]
	for key in return_dict:
		losses_un_sorted.append([return_dict[key][2],return_dict[key][3]])
	
	losses_sorted=sorted(losses_un_sorted,key=itemgetter(0))
	for item in losses_sorted:
		if item[0] < 0:
			print(item)
	
	
	
	print()
	print('%f seconds to run script' % (time.time() - start_time))
	print()
	
	
	return

main()
