'''
This script looks at a day 0 and day 1 returns after weekends and holidays.
Is it better to close out positions before long holiday weekends or hold through?



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
	
	index_locations=[]
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
				index_locations.append(idx-1)
			elif next_date_mo == month:
				index_locations.append(idx-1)
			idx+=15
		else:
			idx+=1
	
	#test the dates
	# ~ for idx in index_locations:
		# ~ print(df['Date'][idx])
	
	# For each index location and date, return the day of the week
	# the integer value 0 is monday, 6 is sunday
	day_of_week=[]
	for indx in index_locations:
		the_date=datetime.datetime.strptime(df['Date'][indx],'%Y-%m-%d')
		weekday=datetime.datetime.weekday(the_date)
		day_of_week.append(weekday)
	
	
	return index_locations,df,day_of_week


def get_returns(df,idx_list):
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

def main():
	start_time = time.time()
	#####
	# input main info here
	#####
	
	# Data location for mac:
	# path = '/Users/Marlowe/Marlowe/Securities_Trading/_Ideas/Data/'
	path = '/Users/Marlowe/gitsite/TOM/'
	
	# Data location for PC:
	# ~ path = 'C:\\Python\\transfer\\TOM\\'
	
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
	idx_list_day0,df_sliced,weekdays=start_of_month_detect(df,start_date,end_date,'00')
	
	
	# first check all day 0 returns
	all_day0_rtns=get_returns(df_sliced,idx_list_day0)
	print('Mean return of all day 0 returns: '+str(round(np.mean(all_day0_rtns),2))+', number of days: '+str(len(all_day0_rtns)))
	
	# next get all day 1 returns
	# shift idx_list, increasing index is going backwards in time, decreasing is going forwards
	idx_list_day1=[idx-1 for idx in idx_list_day0]
	all_day1_rtns=get_returns(df_sliced,idx_list_day1)
	print('Mean return of all day 1 returns: '+str(round(np.mean(all_day1_rtns),2))+', number of days: '+str(len(all_day1_rtns)))
	
	
	
	# next get all day 0 and day 1 returns that fall on a monday
	day0_monday_idxs=[]
	day0_tuesday_idxs=[]
	day1_monday_idxs=[]
	for i in range(len(idx_list_day0)):
		# create list of indexes where day 0 falls on monday
		if weekdays[i]==0:
			day0_monday_idxs.append(idx_list_day0[i])
		# create list of indexes where day 1 falls on monday
		if weekdays[i]==4:
			day1_monday_idxs.append(idx_list_day0[i]-1)
	
	all_day0_monday_rtns=get_returns(df_sliced,day0_monday_idxs)
	print('Mean return of day 0 on Monday: '+str(round(np.mean(all_day0_monday_rtns),2))+', number of days: '+str(len(all_day0_monday_rtns)))
	all_day1_monday_rtns=get_returns(df_sliced,day1_monday_idxs)
	print('Mean return of day 1 on Monday: '+str(round(np.mean(all_day1_monday_rtns),2))+', number of days: '+str(len(all_day1_monday_rtns)))
	
	# get day 0 returns on a tuesday
	idx_list_day0_tuesday=[idx-1 for idx in day0_monday_idxs]
	all_day1_tuesday_rtns=get_returns(df_sliced,idx_list_day1_tuesday)
	print('Mean return of day 1 on Tuesday: '+str(round(np.mean(all_day1_tuesday_rtns),2))+', number of days: '+str(len(all_day1_tuesday_rtns)))
	
	# get day 1 returns on a tuesday
	idx_list_day1_tuesday=[idx-1 for idx in day0_monday_idxs]
	all_day1_tuesday_rtns=get_returns(df_sliced,idx_list_day1_tuesday)
	print('Mean return of day 1 on Tuesday: '+str(round(np.mean(all_day1_tuesday_rtns),2))+', number of days: '+str(len(all_day1_tuesday_rtns)))
	
	# ~ pct_rtns,abs_rtns,dates=tot_returns(df_sliced,start_date,end_date,start_day,end_day)
	
	# input a list of indexes and get the average returns of those dates
	
	
	
	
	
	
	print()
	print('%f seconds to run script' % (time.time() - start_time))
	print()
	
	
	return

main()
