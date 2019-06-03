'''
This script compares the returns of small cap (russell 2000) vs large cap (S&P 500)
over a given number of years for a desired time frame.

Input: daily OHLC data for S&P500 and Russell 2000

Output: returns over period


pandas version: 0.18.1
matplotlib version: 2.0.0
mpl_finance version: 0.10.0
numpy version: 1.10.1
scipy version: 0.16.0

'''

import pandas as pd
import os
import numpy as np
import re
# ~ import csv

# ~ import matplotlib.pyplot as plt
# ~ from mpl_finance import candlestick2_ochl
# ~ import matplotlib.ticker as ticker

from scipy import stats


#open csv file, return the data in a pandas dataframe
def import_data(file_name,fields):
	#only add items in fields list to dataframe
	
	#only add date, open, high, low, last to dataframe
	# fields = ['Date','Open','High','Low','Close']
	
	#open the file using pandas, use the first row as the header
	data = pd.read_csv(file_name,header=0,usecols=fields)
	
	#change the order to most recent date on top if necessary
	data=data.sort(fields[0],ascending=0)
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


def start_date_detect(df,index_l,index_h,month):
	#return a list of the index of the first day of the desired month over
	#the given period
	
	index_locations=[]
	for idx in range(index_l+1,index_h-1):
		
		cur_date=df['Date'][idx]
		prev_date=df['Date'][idx+1]
		next_date=df['Date'][idx-1]
		
		# get the month value from the current, previous and next date
		cur_date_mo=re.findall(r'-(.+?)-',cur_date)[0]
		prev_date_mo=re.findall(r'-(.+?)-',prev_date)[0]
		next_date_mo=re.findall(r'-(.+?)-',next_date)[0]
		
		#if current date has month in it and prev date doesnt,append
		
		if cur_date_mo != prev_date_mo:
			if cur_date_mo == month:
				index_locations.append(idx)
			
	return index_locations



def get_returns(df,start_date,end_date,month,start_day,num_days):
	# this function will generate a list of the returns over the num_days for the given month.
	# each entry in the list will be the return for the given month over the number of years
	# between start_date and end_date
	
	fields = ['Date','Open','High','Low','Close']
	
	#get the low and high index of the dataframe based on the start and end dates
	
	df_2,idxl,idxh=slice_df(df,start_date,end_date)
	
	#create a list of the index of the first trading day of the desired month in each year in the new dataframe
	start_points=[]
	start_points=start_date_detect(df_2,idxl,idxh,month)
	# ~ print(start_points)
	
	#next adjust those indexes by the start_day factor
	adj_start_points=[idx-start_day for idx in start_points]
	# ~ print(adj_start_points)
	
	#print the start date and end date of analysis
	# ~ for idx in adj_start_points:
		# ~ print('start date: '+df_2['Date'][idx]+', end date: '+df_2['Date'][idx-num_days])
	
	#5/22/19: want to do statistical analysis by searching through first of year -10 days to feb 1st +10 days and find
	#the optimal holding period for start date and end date
	
	#get the return, the closing price at the last trading day minus the closing price
	#at the first trading day over the given period.
	abs_returns=[]
	pct_returns=[]
	for idx in adj_start_points:
		start_val=df_2['Close'][idx]
		end_val=df_2['Close'][idx-num_days]
		# ~ print('start date: '+df_2['Date'][idx]+', value: '+str(round(start_val,2))+', end date: '+df_2['Date'][idx-num_days]+', value: '+str(round(end_val,2)))
		abs_returns.append(end_val-start_val)
		pct_returns.append(round(100*(end_val-start_val)/start_val,2))
	
	#print the start date and returns of analysis
	# ~ for x in range(len(adj_start_points)):
		# ~ print('start date: '+df_2['Date'][adj_start_points[x]]+', end date: '+df_2['Date'][adj_start_points[x]-num_days]+', pct return: '+str(pct_returns[x]))
	
	
	return pct_returns,adj_start_points,abs_returns
	



def main():
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
	small_cap_file_name='^RUT.csv'
	large_cap_file_name='^GSPC.csv'
	
	SC_in_file= os.path.join(path,small_cap_file_name)
	LC_in_file= os.path.join(path,large_cap_file_name)
	
	
	# add a header to the file if no header exists
	#add_header(in_file)
	
	#use csv module to pull out proper data
	#file_noblanks=remove_blanks(in_file)
	
	
	# create dataframe from the data
	sc_df=import_data(SC_in_file,fields)
	lc_df=import_data(LC_in_file,fields)
	
	#####
	# input the date range of interest for overall analysis
	#####
	
	#first date in russell: 1987-09-10
	start_date='1987-09-10'
	# ~ start_date='2000-09-11'
	
	end_date='2000-09-11'
	# ~ end_date='2019-05-10'
	
	# input the desired 2 digit month to analyze. Jan=01, Feb=02 etc
	test_month='01'
	# input month start date. 0=first day, 1=second day, -1=day before 1st day, etc
	start_day=-2
	# input number of days to analyze. On average 20 trading days in jan
	num_days=10
	
	
	#####
	# generate a list of returns for the given month over the desired period
	#####
	
	sc_pct_returns,sc_start_idxs,sc_abs_rtn=get_returns(sc_df,start_date,end_date,test_month,start_day,num_days)
	lc_pct_returns,lc_start_idxs,lc_abs_rtn=get_returns(lc_df,start_date,end_date,test_month,start_day,num_days)
	# ~ return
	# ~ print(sc_pct_returns)
	# ~ print(lc_pct_returns)
	
	# ~ for x in range(len(sc_start_idxs)):
		# ~ print('Month start date: '+sc_df['Date'][sc_start_idxs[x]]+', sc pct return: '+str(sc_pct_returns[x])+', lc pct return: '
			# ~ +str(lc_pct_returns[x]))
	# ~ return
	#####
	# provide statistics on returns
	#####
	'''
	mean_sc_returns=round(np.mean(sc_pct_returns),2)
	std_dev_sc_returns=round(np.std(sc_pct_returns),2)
	
	mean_lc_returns=round(np.mean(lc_pct_returns),2)
	std_dev_lc_returns=round(np.std(lc_pct_returns),2)
	
	win_count=0
	sc_minus_lc_wins=[]
	sc_minus_lc_losses=[]
	for r in range(len(lc_pct_returns)):
		sc_minus_lc=round(sc_pct_returns[r]-lc_pct_returns[r],1)
		if sc_pct_returns[r] > lc_pct_returns[r]:
			win_count=win_count+1
			sc_minus_lc_wins.append(sc_minus_lc)
		if sc_pct_returns[r] <= lc_pct_returns[r]:
			sc_minus_lc_losses.append(sc_minus_lc)
		
	bankroll=10000
	edge=sum(sc_minus_lc_wins)-sum(sc_minus_lc_losses)
	odds=round(win_count/len(sc_pct_returns),1)
	
	print()
	print('Period under consideration: '+start_date+' to '+end_date)
	print('Mean small cap returns: '+str(mean_sc_returns)+', std_dev: '+str(std_dev_sc_returns))
	print('Mean large cap returns: '+str(mean_lc_returns)+', std_dev: '+str(std_dev_lc_returns))
	print('Number of years tested: '+str(len(sc_pct_returns)))
	print()
	print('Number of years sc > lc: '+str(win_count)+', odds of win '+str(odds))
	print('Expected edge: '+str(edge))
	print('Current bankroll: '+str(bankroll)+', bet size: '+str(bankroll*edge/odds))
	'''
	
	#####
	# Look at returns of strategy and equity curve
	#####
	
	#set the ratio of SC to LC
	ratio=1.9
	yearly_abs_return=[]
	for x in range(len(sc_abs_rtn)):
		#find the baseline value
		sc_start_val=sc_df['Close'][sc_start_idxs[x]]*ratio
		lc_start_val=lc_df['Close'][lc_start_idxs[x]]
		baseline=sc_start_val-lc_start_val
		curr_rtn_sc=sc_abs_rtn[x]*ratio
		curr_rtn_lc=lc_abs_rtn[x]
		yearly_abs_return.append(curr_rtn_sc-curr_rtn_lc)
		
	
	worst_case_return=min(yearly_abs_return)
	mean_return=round(np.mean(yearly_abs_return),2)
	std_dev_return=round(np.std(yearly_abs_return),2)
	
	print()
	print('Mean returns: '+str(mean_return)+', std_dev: '+str(std_dev_return))
	print()
	# ~ print(yearly_abs_return)
	return
	



main()
