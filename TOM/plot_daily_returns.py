'''
This script plots the daily returns around a point of interest
It can be used for average returns from many sample periods or just one
sample period.

Inputs:
-daily OHLC data for an asset (Alternate input: list of daily returns)
-date of interest
-number of days before and after

Output:
-plot of daily returns around that date


Per:
"The Turn-of-the-Month Effect in the U.S. Stock index Futures Markets, 1982-1992"
Hensel, Sick, Ziemba

test period: May 1982-April 1992


pandas version: 0.18.1
matplotlib version: 2.0.0
numpy version: 1.10.1
scipy version: 0.16.0

'''

import pandas as pd
import os
import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import datetime


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


def bar_plot(a_list,num_days):
	x_vals=[x for x in range(num_days[0],num_days[1]+1,1)]
	
	fig = plt.figure('May2009_April2019')
	ax = plt.subplot()
	# ~ ax.plot(x_vals,a_list,color='b')
	ax.bar(x_vals,a_list,align='center',color='gray')
	ax.set_ylabel('Daily Percent Return')
	ax.set_xlabel('Day')
	
	loc=plticker.MultipleLocator(base=1)
	ax.xaxis.set_major_locator(loc)
	# ~ ax.set_xlim(num_days[0],num_days[1])
	
	ax.grid(which='major', axis='both')
	plt.show()
	
	
	return



'''
def start_date_detect(df,index_l,index_h,month):
	#return a list of the index of the first day of the desired month over
	#the given period
	
	index_locations=[]
	for idx in range(index_l+1,index_h-1):
		
		cur_date=df['Date'][idx]
		prev_date=df['Date'][idx+1]
		next_date=df['Date'][idx-1]
		
		cur_date_mo=re.findall(r'-(.+?)-',cur_date)[0]
		prev_date_mo=re.findall(r'-(.+?)-',prev_date)[0]
		next_date_mo=re.findall(r'-(.+?)-',next_date)[0]
		
		#if current date has month in it and prev date doesnt,append
		
		if cur_date_mo != prev_date_mo:
			if cur_date_mo == month:
				index_locations.append(idx)
			
	return index_locations
'''



def get_returns(df,idx_ut,num_days):
	# this function will generate a list of the percent returns over the +/-num_days range for the given index.
	# each entry in the list will be the return for the given day with respect to that day
	
	fields = ['Date','Open','High','Low','Close']
	
	
	# get the index of the test_date
	# ~ test_day_df=df.loc[df['Date'] == test_date]
	# ~ test_date_idx=test_day_df.index[0].tolist()
	
	# for 1995-01-03, index is 6133
	
	#adjust index start
	# ~ if num_days[0] < 0:
		# ~ idx_start_adj=
	# ~ idx_end_adj=
	
	#get the return, the closing price at the last trading day minus the closing price
	#at the first trading day over the given period.
	abs_returns=[]
	pct_returns=[]
	for idx in range(idx_ut-num_days[0],idx_ut-num_days[1]-1,-1):
		days_close=df['Close'][idx]
		days_open=df['Open'][idx]
		abs_returns.append(days_close-days_open)
		pct_returns.append(round(100*(days_close-days_open)/days_open,2))
		# ~ print('Index: '+str(idx)+', Date: '+str(df['Date'][idx])+', return: '+str(round(100*(days_close-days_open)/days_open,2)))
	
	
	
	return pct_returns


def start_of_month_detect(df,index_l,index_h,month):
	#return a list of the index of the first day of the select month over
	#the given period. if month is 00, test all months.
	
	index_locations=[]
	for idx in range(index_l+1,index_h-1):
		
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
				index_locations.append(idx-1)
			elif next_date_mo == month:
				index_locations.append(idx-1)
	
	#test the dates
	# ~ for idx in index_locations:
		# ~ print(df['Date'][idx])
	
	return index_locations


def avg_returns(df,start_date,end_date,num_days,month):
	# get the average daily returns on the num_days around the first of the month
	# over a specified date range
	
	
	#get the low and high index of the dataframe based on the start and end dates
	df_2,idxl,idxh=slice_df(df,start_date,end_date)
	
	#create a list of the index of the first trading day of each month in the new dataframe
	start_idxs=[]
	start_idxs=start_of_month_detect(df_2,idxl,idxh,month)
	
	# ~ print('Number of months tested: '+str(len(start_idxs)))
	
	# cycle through the start indexes and get the returns +/- num_days over each period
	# result will be a list of lists
	all_pct_returns=[]
	for idx in start_idxs:
		all_pct_returns.append(get_returns(df,idx,num_days))
	
	
	# create a list of lists where each list is all of the percent returns
	# for each day within the desired num_days range. i.e. take all of the
	# day 1 returns from all_pct_returns and put into a unique list inside of
	# list_of_rtns_by_day
	len_num_days=abs(num_days[1]-num_days[0])
	list_of_rtns_by_day=[]
	a_range=[z for z in range(len_num_days+1)]
	for r in a_range:
		day_list=[]
		for x_list in all_pct_returns:
			day_list.append(x_list[r])
		list_of_rtns_by_day.append(day_list)
	
	# ~ print(list_of_rtns_by_day)
	
	# go through all the lists of the daily pct returns and get the mean value
	# of the return for each day
	mean_rtns=[]
	for y_list in list_of_rtns_by_day:
		mean_rtns.append(np.mean(y_list))
	
	
	# ~ print([round(x,4) for x in mean_rtns])
	
	
	return mean_rtns,all_pct_returns




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
	# ~ start_date='1987-09-10'
	# ~ start_date='1988-01-08'
	# ~ start_date='2000-09-11'
	
	# ~ end_date='1995-01-05'
	# ~ end_date='2000-09-11'
	# ~ end_date='2001-10-12'
	# ~ end_date='2019-04-10'
	
	#####
	# Input date range per Ziemba study, May 1982-April 1992
	# Use ^GSPC for cash market data (lc_df)
	#####
	start_date='1982-04-08'
	end_date='1992-04-22'
	
	#####
	# Test last 10 years, May 2009-April 2019
	# Use ^GSPC for cash market data (lc_df)
	#####
	# ~ start_date='2009-04-08'
	# ~ end_date='2019-04-22'
	
	
	'''
	#input the 4 digit year to analyze
	test_year='1995'
	# input the desired 2 digit month to analyze. Jan=01, Feb=02 etc
	test_month='01'
	# input 2 digit date to analyze
	test_day='05'
	'''
	
	# input number of days to analyze before and after
	# num days is a range [start,end] so like [-1,4] or [-10,10]
	# note compared to ziemba, my-1 = ziemba-1, my+3 = ziemba+4
	num_days=[-1,3]
	print()
	#####
	# get the daily returns on the days around given date
	#####
	# ~ test_date='1995-01-03'
	
	# get the index of the test_date
	# ~ test_day_df=sc_df.loc[sc_df['Date'] == test_date]
	# ~ test_date_idx=test_day_df.index[0].tolist()
	
	# ~ returns=get_returns(sc_df,test_date_idx,num_days)
	# ~ print(returns)
	# ~ bar_plot(returns,num_days)
	# ~ return
	#####
	# get the average daily returns on the days around the first of the month
	# over a specified date range
	#####
	# inputs are the dataframe, start date of period under test, end date of period under test
	# num_days is the range around the FOM day we want to test, month is the two digit month
	# if we want to test a specific month. If we want to test all months, set month to 00
	month='00'
	tot_mean_rtns,all_rtns=avg_returns(lc_df,start_date,end_date,num_days,month)
	
	
	# plot the returns
	# ~ bar_plot(tot_mean_rtns,num_days)
	
	# get the average daily returns based on start and end around TOM
	# ex avg daily return over period for -1 to +4
	avg_daily_rtn=np.mean(tot_mean_rtns)
	print(round(avg_daily_rtn,4))
	
	
	return

'''
5/24/19
I want to plot the TOM avg daily return for -1 to 4 over the years doing 10 year
historical data analysis. The point of this is to see if the TOM effect has become
less profitable over time
'''

main()
