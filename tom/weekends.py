'''
This script looks at a day 0 and day 1 returns after weekends and holidays.
Is it better to close out positions before long holiday weekends or hold through?


Notes: Holiday and Holiday weekend trades are actually above average returns
Best averages are trades that end on a monday and friday
the actual day of monday and friday also have the highest percent of large gains

the strategy works when we can capture large gains and eleminate large losses because of the fat tails


Output: Compare day 0 and day 1 returns on mondays and after holidays


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
	
	# For each index location and date, return the day of the week
	# the integer value 0 is monday, 6 is sunday
	day_of_week_day0=[]
	day_of_week_day1=[]
	day_of_week_daym1=[]
	for indx in index_locations_day0:
		daym1_date=datetime.datetime.strptime(df['Date'][indx+1],'%Y-%m-%d')
		day0_date=datetime.datetime.strptime(df['Date'][indx],'%Y-%m-%d')
		day1_date=datetime.datetime.strptime(df['Date'][indx-1],'%Y-%m-%d')
		
		# weekday_daym1=datetime.datetime.weekday(daym1_date)
		# weekday_day0=datetime.datetime.weekday(day0_date)
		# weekday_day1=datetime.datetime.weekday(day1_date)
		
		day_of_week_daym1.append(datetime.datetime.weekday(daym1_date))
		day_of_week_day0.append(datetime.datetime.weekday(day0_date))
		day_of_week_day1.append(datetime.datetime.weekday(day1_date))
		
	# Create indexes for daym1 and day1
	index_locations_daym1=[idx+1 for idx in index_locations_day0]
	index_locations_day1=[idx-1 for idx in index_locations_day0]
	
	return index_locations_day0,index_locations_daym1,index_locations_day1,day_of_week_day0,day_of_week_daym1,day_of_week_day1,df


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
		if ((trade_open-trade_low)/trade_open) < -0.03:
			pct_returns.append(-3.0)
		elif ((trade_close-trade_open)/trade_open) < -0.03:
			pct_returns.append(-3.0)
		else:
			pct_returns.append(round(100*(trade_close-trade_open)/trade_open,2))
	
	
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
	# generate the pct returns on the given day in the desired period
	#####
	
	# generate a list of indexes of first days of all months in test period
	idx_list_day0,idx_list_daym1,idx_list_day1,weekdays_day0,weekdays_daym1,weekdays_day1,df_sliced=start_of_month_detect(df,start_date,end_date,'00')
	
	print('Single trading day returns:')
	# first check all day 0 returns
	all_day0_rtns=get_returns_sing_day(df_sliced,idx_list_day0)
	print('Mean return of all day 0 returns: '+str(round(np.mean(all_day0_rtns),2))+', number of days: '+str(len(all_day0_rtns)))
	
	# next get all day 1 returns
	# shift idx_list, increasing index is going backwards in time, decreasing is going forwards
	all_day1_rtns=get_returns_sing_day(df_sliced,idx_list_day1)
	print('Mean return of all day 1 returns: '+str(round(np.mean(all_day1_rtns),2))+', number of days: '+str(len(all_day1_rtns)))
	
	
	
	# next get all day 0 and day 1 returns that fall on a monday or tuesday
	day0_monday_idxs=[]
	day0_tuesday_idxs=[]
	day1_monday_idxs=[]
	day1_mon_idx0=[]
	day1_tuesday_idxs=[]
	day1_tuesday_idx0=[]
	day1_wed_idxs=[]
	day1_thu_idxs=[]
	day1_fri_idxs=[]
	day1_wed_idx0=[]
	day1_thu_idx0=[]
	day1_fri_idx0=[]
	for i in range(len(idx_list_day0)):
		# create list of indexes where day 0 falls on monday
		if weekdays_day0[i]==0:
			day0_monday_idxs.append(idx_list_day0[i])
		# create list of indexes where day 0 falls on tuesday
		if weekdays_day0[i]==1:
			day0_tuesday_idxs.append(idx_list_day0[i])
		# create list of indexes where day 1 falls on monday
		if weekdays_day1[i]==0:
			day1_monday_idxs.append(idx_list_day1[i])
			day1_mon_idx0.append(idx_list_day1[i]+1)
		# create list of indexes where day 1 falls on tuesday
		if weekdays_day1[i]==1:
			day1_tuesday_idxs.append(idx_list_day1[i])
			day1_tuesday_idx0.append(idx_list_day1[i]+1)
		if weekdays_day1[i]==2:
			day1_wed_idxs.append(idx_list_day1[i])
			day1_wed_idx0.append(idx_list_day1[i]+1)
		if weekdays_day1[i]==3:
			day1_thu_idxs.append(idx_list_day1[i])
			day1_thu_idx0.append(idx_list_day1[i]+1)
		if weekdays_day1[i]==4:
			day1_fri_idxs.append(idx_list_day1[i])
			day1_fri_idx0.append(idx_list_day1[i]+1)
	
	# day 0 on monday returns
	all_day0_monday_rtns=get_returns_sing_day(df_sliced,day0_monday_idxs)
	print('Mean return of day 0 on Monday: '+str(round(np.mean(all_day0_monday_rtns),2))+', number of days: '+str(len(all_day0_monday_rtns)))
	# day 1 on monday returns
	all_day1_monday_rtns=get_returns_sing_day(df_sliced,day1_monday_idxs)
	print('Mean return of day 1 on Monday: '+str(round(np.mean(all_day1_monday_rtns),2))+', number of days: '+str(len(all_day1_monday_rtns)))
	
	# get day 0 on a tuesday returns
	all_day0_tuesday_rtns=get_returns_sing_day(df_sliced,day0_tuesday_idxs)
	print('Mean return of day 0 on Tuesday: '+str(round(np.mean(all_day0_tuesday_rtns),2))+', number of days: '+str(len(all_day0_tuesday_rtns)))
	# get day 1 returns on a tuesday
	all_day1_tuesday_rtns=get_returns_sing_day(df_sliced,day1_tuesday_idxs)
	print('Mean return of day 1 on Tuesday: '+str(round(np.mean(all_day1_tuesday_rtns),2))+', number of days: '+str(len(all_day1_tuesday_rtns)))
	# print('Largest gain day1 on Tuesday: '+str(round(max(all_day1_tuesday_rtns),2)))
	
	print()
	print('Number of day1 on Monday gains > 0.7%: '+str(sum(1 for x in all_day1_monday_rtns if x > 0.7))+', pct of total num trades: '+str(round(100*sum(1 for x in all_day1_monday_rtns if x > 0.7)/len(all_day1_monday_rtns),1)))
	print('Number of day1 on Tuesday gains > 0.7%: '+str(sum(1 for x in all_day1_tuesday_rtns if x > 0.7))+', pct of total num trades: '+str(round(100*sum(1 for x in all_day1_tuesday_rtns if x > 0.7)/len(all_day1_tuesday_rtns),1)))
	all_day1_wed_rtns=get_returns_sing_day(df_sliced,day1_wed_idxs)
	print('Number of day1 on Wednesday gains > 0.7%: '+str(sum(1 for x in all_day1_wed_rtns if x > 0.7))+', pct of total num trades: '+str(round(100*sum(1 for x in all_day1_wed_rtns if x > 0.7)/len(all_day1_wed_rtns),1)))
	all_day1_thu_rtns=get_returns_sing_day(df_sliced,day1_thu_idxs)
	print('Number of day1 on Thursday gains > 0.7%: '+str(sum(1 for x in all_day1_thu_rtns if x > 0.7))+', pct of total num trades: '+str(round(100*sum(1 for x in all_day1_thu_rtns if x > 0.7)/len(all_day1_thu_rtns),1)))
	all_day1_fri_rtns=get_returns_sing_day(df_sliced,day1_fri_idxs)
	print('Number of day1 on Friday gains > 0.7%: '+str(sum(1 for x in all_day1_fri_rtns if x > 0.7))+', pct of total num trades: '+str(round(100*sum(1 for x in all_day1_fri_rtns if x > 0.7)/len(all_day1_fri_rtns),1)))
	
	
	
	
	all_holidays=[]
	long_weekends=[]
	day1_holiday=[] # check for gap day between day1 and day0
	day0_holiday=[] # check for gap day between day0 and day-1
	for i in range(len(idx_list_day0)):
		# This test represents day0 on a friday with monday being a holiday and day1 on tuesday or later
		if (weekdays_day0[i]==4) & (weekdays_day1[i]!=0):
			day1_holiday.append(idx_list_day0[i])
			all_holidays.append(idx_list_day0[i])
			long_weekends.append(idx_list_day0[i])
			# print('index location '+str(idx_list_day0[i])+' is a holiday. day0: '+str(df_sliced['Date'][idx_list_day0[i]])+', day1: '+str(df_sliced['Date'][idx_list_day0[i]-1]))
			# print('weekdays_day0: '+str(weekdays_day0[i])+', weekdays_day1: '+str(weekdays_day1[i]))
		# This test represents daym1 on a friday with monday being a holiday and day0 on tuesday or later
		if (weekdays_daym1[i]==4) & (weekdays_day0[i]!=0):
			day0_holiday.append(idx_list_day0[i])
			all_holidays.append(idx_list_day0[i])
			long_weekends.append(idx_list_day0[i])
			# print('index location '+str(idx_list_day0[i])+' is a holiday. daym1: '+str(df_sliced['Date'][idx_list_daym1[i]])+', day0: '+str(df_sliced['Date'][idx_list_day0[i]])+', day1: '+str(df_sliced['Date'][idx_list_day0[i]-1]))
			# print('weekdays_daym1: '+str(weekdays_daym1[i])+', weekdays_day0: '+str(weekdays_day0[i])+', weekdays_day1: '+str(weekdays_day1[i]))
		
		# If day1 is on a friday or earlier and day0 is more than 1 day away, middle of the week holiday
		if (weekdays_day1[i]<=4) & ((weekdays_day1[i]-weekdays_day0[i])>1):
			all_holidays.append(idx_list_day0[i])
			day1_holiday.append(idx_list_day0[i])
			# print('index location '+str(idx_list_day0[i])+' is a holiday. day0: '+str(df_sliced['Date'][idx_list_day0[i]])+', day1: '+str(df_sliced['Date'][idx_list_day0[i]-1]))
			# print('weekdays_day0: '+str(weekdays_day0[i])+', weekdays_day1: '+str(weekdays_day1[i]))
		
	
	# Generate some overall mean returns of different strategies
	print()
	print('Full trading period returns:')
	all_longweekend_rtns=get_returns_full_trade(df_sliced,long_weekends,-4,1)
	print('Mean return of trades with holiday weekends: '+str(round(np.mean(all_longweekend_rtns),2))+', number of trades: '+str(len(all_longweekend_rtns)))
	
	all_holidays_rtns=get_returns_full_trade(df_sliced,all_holidays,-4,1)
	print('Mean return of trades with holidays: '+str(round(np.mean(all_holidays_rtns),2))+', number of trades: '+str(len(all_holidays_rtns)))
	
	all_rtns=get_returns_full_trade(df_sliced,idx_list_day0,-4,1)
	print('Mean return of all trades: '+str(round(np.mean(all_rtns),2))+', number of trades: '+str(len(all_rtns)))
	
	print()
	all_rtns_mon_day1=get_returns_full_trade(df_sliced,day1_mon_idx0,-4,1)
	print('Mean return of all trades with day 1 on Monday: '+str(round(np.mean(all_rtns_mon_day1),2))+', number of trades: '+str(len(all_rtns_mon_day1)))
	all_rtns_tues_day1=get_returns_full_trade(df_sliced,day1_tuesday_idx0,-4,1)
	print('Mean return of all trades with day 1 on Tuesday: '+str(round(np.mean(all_rtns_tues_day1),2))+', number of trades: '+str(len(all_rtns_tues_day1)))
	all_rtns_wed_day1=get_returns_full_trade(df_sliced,day1_wed_idx0,-4,1)
	print('Mean return of all trades with day 1 on Wednesday: '+str(round(np.mean(all_rtns_wed_day1),2))+', number of trades: '+str(len(all_rtns_wed_day1)))
	all_rtns_thu_day1=get_returns_full_trade(df_sliced,day1_thu_idx0,-4,1)
	print('Mean return of all trades with day 1 on Thursday: '+str(round(np.mean(all_rtns_thu_day1),2))+', number of trades: '+str(len(all_rtns_thu_day1)))
	all_rtns_fri_day1=get_returns_full_trade(df_sliced,day1_fri_idx0,-4,1)
	print('Mean return of all trades with day 1 on Friday: '+str(round(np.mean(all_rtns_fri_day1),2))+', number of trades: '+str(len(all_rtns_fri_day1)))
	
	print()
	all_rtns_tues_day1m1=get_returns_full_trade(df_sliced,day1_tuesday_idx0,-4,0)
	print('Mean return of all trades with day 1 on Tuesday(close trade on monday): '+str(round(np.mean(all_rtns_tues_day1m1),2))+', number of trades: '+str(len(all_rtns_tues_day1m1)))
	
	print()
	print('%f seconds to run script' % (time.time() - start_time))
	print()
	
	
	return

main()
