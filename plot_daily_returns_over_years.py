'''
This script plots the average daily returns around a point of interest
over the course of many years.

This is useful to see if the TOM effect is stronger or weaker over time.

Using the previous 10 years of data, 120 months to get the avg daily % returns
using a specified TOM time frame, as if what would be the returns if you were
trading this idea over the last 10 years. We want to see how this might change over time

Inputs:


Output:
-plot of daily avg returns around that TOM over time


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


def gen_avg_daily_rtn(df,start_date,end_date,num_days,month,num_yrs):
	# get the mean of the average daily returns based on start and end around TOM
	# ex avg daily return over period of years for -1 to +4. can do this for a given month
	# or all months
	# num_days is the number of days to analyze before and after the TOM
	# num days is a range [start,end] so like [-1,4] or [-10,10]
	# note compared to ziemba, my-1 = ziemba-1, my+3 = ziemba+4
	# num_yrs is the number of years to look back over during test
	
	# Output is a list of the avg % daily returns over the previous 10 years
	# for the given info. It should have the same number of data points as years
	# between start date and end date
	
	'''
	# get avg % daily rtn for one year
	# choose start date as single year to test
	test_start_date='1982-04-08'
	test_end_date='1992-04-22'
	tot_mean_rtns,all_rtns=avg_returns(df,test_start_date,test_end_date,num_days,month)
	avg_daily_rtn=np.mean(tot_mean_rtns)
	print(round(avg_daily_rtn,4))
	'''
	
	# pick the start date and end date for the given year. We will use the first trading
	# day of the month as the beginning point.
	# use the current year being tested as the end date. The start_date month
	# will be the beginning month of the analysis. So if we want our 10 year period
	# to start on march 1, start_date should be 03-01-1985 or the first trading day
	# in march of whatever year we want to start the analysis with. Then we look back 10 years
	# from that date and get the start date based on that.
	
	# find how many years we will be testing
	first_yr=int(re.findall(r'(.+?)-',start_date)[0])
	last_yr=int(re.findall(r'(.+?)-',end_date)[0])
	num_yrs_tst=last_yr-first_yr
	# ~ print('Number of years to test is '+str(num_yrs_tst))
	test_month=re.findall(r'-(.+?)-',start_date)[0]
	# ~ return
	
	# cycle through each year and look back num_yrs to get avg % daily rtn over that period
	# then append to list
	list_of_avg_pct_rtns=[]
	for x in range(num_yrs_tst):
		end_date_yr=first_yr+x
		start_date_yr=end_date_yr-num_yrs
		# ~ print('testing from '+str(start_date_yr)+' to '+str(end_date_yr))
		
		
		# find the first trading day of the start date month/year
		# would be better to do this with a while loop and boolean
		if df['Date'].str.contains(str(start_date_yr)+'-'+test_month+'-01').any():
			# ~ print('1 is first trading day')
			test_start_date=str(start_date_yr)+'-'+test_month+'-01'
		elif df['Date'].str.contains(str(start_date_yr)+'-'+test_month+'-02').any():
			# ~ print('2 is first trading day')
			test_start_date=str(start_date_yr)+'-'+test_month+'-02'
		elif df['Date'].str.contains(str(start_date_yr)+'-'+test_month+'-03').any():
			# ~ print('3 is first trading day')
			test_start_date=str(start_date_yr)+'-'+test_month+'-03'
		elif df['Date'].str.contains(str(start_date_yr)+'-'+test_month+'-04').any():
			# ~ print('4 is first trading day')
			test_start_date=str(start_date_yr)+'-'+test_month+'-04'
		else:
			print('Error, did not find first trading day for start date')
			
			
		# find the first trading day of the end date month/year
		# would be better to do this with a while loop and boolean
		if df['Date'].str.contains(str(end_date_yr)+'-'+test_month+'-01').any():
			# ~ print('1 is first trading day')
			test_end_date=str(end_date_yr)+'-'+test_month+'-01'
		elif df['Date'].str.contains(str(end_date_yr)+'-'+test_month+'-02').any():
			# ~ print('2 is first trading day')
			test_end_date=str(end_date_yr)+'-'+test_month+'-02'
		elif df['Date'].str.contains(str(end_date_yr)+'-'+test_month+'-03').any():
			# ~ print('3 is first trading day')
			test_end_date=str(end_date_yr)+'-'+test_month+'-03'
		elif df['Date'].str.contains(str(end_date_yr)+'-'+test_month+'-04').any():
			# ~ print('4 is first trading day')
			test_end_date=str(end_date_yr)+'-'+test_month+'-04'
		else:
			print('Error, did not find first trading day for end date')
		
		tot_mean_rtns,all_rtns=avg_returns(df,test_start_date,test_end_date,num_days,month)
		
		list_of_avg_pct_rtns.append(np.mean(tot_mean_rtns))
	
	
	
	
	
	
	# ~ end_date_yr=int(re.findall(r'(.+?)-',start_date)[0])
	# ~ test_month=re.findall(r'-(.+?)-',start_date)[0]
	
	
	
	
	# ~ test_end_date=start_date
	
	
	# ~ print([round(x,4) for x in list_of_avg_pct_rtns])
	
	
	return list_of_avg_pct_rtns


def plot_returns(a_list,start_date,end_date):
	
	# get a list of years between start_date and end_date
	first_yr=int(re.findall(r'(.+?)-',start_date)[0])
	last_yr=int(re.findall(r'(.+?)-',end_date)[0])
	
	x_vals=[x for x in range(first_yr,last_yr,1)]
	
	set_base=int(len(x_vals)/6)
	# ~ print(x_vals)
	
	# ~ return
	fig = plt.figure()
	ax = plt.subplot()
	# ~ ax.plot(x_vals,a_list,color='b')
	ax.plot(x_vals,a_list,color='blue')
	ax.set_ylabel('avg daily % return')
	ax.set_xlabel('year-mo-day')
	
	loc=plticker.MultipleLocator(base=set_base)
	ax.xaxis.set_major_locator(loc)
	# ~ ax.set_xlim(num_days[0],num_days[1])
	
	# ~ ax.grid(which='major', axis='both')
	plt.show()
	
	
	return




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
	# ~ small_cap_file_name='^RUT.csv'
	large_cap_file_name='^GSPC.csv'
	
	# ~ SC_in_file= os.path.join(path,small_cap_file_name)
	LC_in_file= os.path.join(path,large_cap_file_name)
	
	
	# create dataframe from the data
	# ~ sc_df=import_data(SC_in_file,fields)
	lc_df=import_data(LC_in_file,fields)
	
	#####
	# input the date range of interest for overall analysis
	# this is the full number of years to do analysis over
	# the script will cycle through each year and look back 10 years behind
	# the year under test to get the avg % return of the TOM for the previous 10 years
	#####
	
	# ^GSPC data starts at 1950, need to start at least 10yrs ahead of that
	start_date='1960-02-01'
	# ~ start_date='1987-09-10'
	# ~ start_date='1988-01-08'
	# ~ start_date='2000-09-11'
	
	# ~ end_date='1970-02-02'
	# ~ end_date='1990-01-05'
	# ~ end_date='1995-01-05'
	# ~ end_date='2000-09-11'
	# ~ end_date='2001-10-12'
	end_date='2019-04-10'
	
	# input number of days to analyze before and after the TOM
	# num days is a range [start,end] so like [-1,4] or [-10,10]
	# note compared to ziemba, my-1 = ziemba-1, my+3 = ziemba+4
	num_days=[-4,1]
	print()
	
	# input the month, which is the two digit month if we want to test a specific month.
	# If we want to test all months, set month to 00
	month='00'
	# years is the number of years to look back over during test
	years=10
	
	
	daily_returns_list=gen_avg_daily_rtn(lc_df,start_date,end_date,num_days,month,years)
	
	# ~ print([round(x,4) for x in daily_returns_list])
	
	# plot the avg % daily returns around the TOM over the range of years
	
	print()
	print('%f seconds to run script' % (time.time() - start_time))
	print()
	
	plot_returns(daily_returns_list,start_date,end_date)
	
	return


main()
