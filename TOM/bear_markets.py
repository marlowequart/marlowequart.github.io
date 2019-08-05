'''
This script looks at bear markets and times of high vix to find out if there
is an advantage to halting trading during these periods.


Input: daily OHLC data for desired trading symbol

Output: correlation between time periods of bear markets or high vix and losses

Notes/Observations:
During bear markets, there is a higher percentage of losses with this strategy:
% losses bear market: 55%
% losses overall: 36%
and the losses are also more severe: -2.6% vs -1.59% on overall

However, the trading edge is actually higher during the bear market periods,
and that is actually due to the fact that the wins have a higher % gain.
Expected Value Overall: 1.72
Expected Value Bear Market: 2.65
Expected Value Non bear market: 1.55

This strategy actually performs better during bear markets than it does during bull markets!
Truly an antifragile strategy!

Bottom line: Trade away during both bull and bear markets!




Since 1929 bear markets occured during the following periods:
Sep 1929 to June 1932
May 1946 to June 1949
Dec 1961 to June 1962
Nov 1968 to May 1970
Jan 1973 to Oct 1974
Nov 1980 to Aug 1982
Aug 1987 to Dec 1987
March 2000 to Oct 2002
Oct 2007 to March 2009

bear_periods=[[datetime.date(1929,9,1),datetime.date(1932,6,1)],
				[datetime.date(1946,5,1),datetime.date(1949,6,1)],
				[datetime.date(1961,12,1),datetime.date(1962,6,1)],
				[datetime.date(1968,11,1),datetime.date(1970,5,1)],
				[datetime.date(1973,1,1),datetime.date(1974,10,1)],
				[datetime.date(1980,11,1),datetime.date(1982,8,1)],
				[datetime.date(1987,8,1),datetime.date(1987,12,1)],
				[datetime.date(2000,3,1),datetime.date(2002,10,1)],
				[datetime.date(2007,10,1),datetime.date(2009,3,1)]]


This script uses actual returns and determines a buy and sell price based on actual data


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
	
	
def start_date_detect(df,index_l,index_h,months):
	#return a list of the index of the first day of the desired month over
	#the given period. this function takes a list of months as the input
	#and finds the index of all of those months start dates. This is done to
	#help reduce processing time when checking for multiple months so you can
	#only cycle through the dataframe once.
	
	index_locations=[]
	idx=index_l+1
	while idx < index_h-1:
	# ~ for idx in range(index_l+1,index_h-1):
		
		cur_date=df['Date'][idx]
		prev_date=df['Date'][idx+1]
		next_date=df['Date'][idx-1]
		
		# get the month value from the current, previous and next date
		cur_date_mo=re.findall(r'-(.+?)-',cur_date)[0]
		prev_date_mo=re.findall(r'-(.+?)-',prev_date)[0]
		next_date_mo=re.findall(r'-(.+?)-',next_date)[0]
		
		#if current date has month in it and prev date doesnt,append
		# advance the counter by 15 days to move through df faster
		if cur_date_mo != prev_date_mo:
			if cur_date_mo in months:
				index_locations.append(idx)
				idx+=15
		else:
			idx+=1
	return index_locations
	
	
	
	
def tot_returns(df,start_date,end_date,start_day,end_day):
	# this function will generate a list of the returns for each month over the given period (start_date/end_date)
	# with the given start_day and end_day of the month. For example the start/end day might be -4 to +1
	# and the period will be from Jan 2001 to Jan 2019.
	#
	# each entry in the list will be the overall return for each month in % or absolute terms if you
	# bought on the open of start_day and sold on the open of end_day
	#
	# Is this method of calculation more accurate than taking the mean of each days returns over the given period?
	
	fields = ['Date','Open','High','Low','Close']
	
	#get the low and high index of the dataframe based on the start and end dates
	df_2,idxl,idxh=slice_df(df,start_date,end_date)
	
	
	#create a list of the index of the first trading day of the desired month in each year in the new dataframe
	months=['01','02','03','04','05','06','07','08','09','10','11','12']
	
	
	# generate start points cycling through months
	# ~ for mo in months:
		# ~ start_points_1.append(start_date_detect_one_mo(df_2,idxl,idxh,mo))
	# create one list with indexes in order
	# ~ start_points_2=[item for sublist in start_points_1 for item in sublist]
	# ~ start_points=sorted(start_points_2)
	
	# generate start points using faster method
	start_points=[]
	start_points=start_date_detect(df_2,idxl,idxh,months)
	
	# print(start_points)
	
	# print(df.loc[[start_points[4]-1]])
	# return
	
	
	
	
	# next adjust those indexes by the start_day factor
	# moving down in index (ex: from 4786 to 4785) increases the date
	# moving up in index decreases date
	# using subtraction to change start date takes into consideration negative start dates
	adj_start_points=[idx-start_day for idx in start_points]
	
	# total number of days held
	
	hold_days=abs(start_day-end_day)
	
	
	#print the start date and end date of analysis
	# ~ for idx in adj_start_points:
		# ~ print('start date: '+df_2['Date'][idx]+', end date: '+df_2['Date'][idx-num_days])
	
	
	
	#get the return, the opening price at the last trading day minus the opening price
	#at the first trading day over the given period.
	# 2019_08_04 I am changing this script to capture data from opening price of first day
	# to closing price of last day
	abs_returns=[]
	pct_returns=[]
	dates=[]
	pct_low=[]
	trade_open=[]
	for idx in adj_start_points:
		start_val=df_2['Open'][idx]
		trade_open.append(start_val)
		end_val=df_2['Close'][idx-hold_days]	# 2019_08_04 changed from 'Open' to 'Close'
		# ~ print('start date: '+df_2['Date'][idx]+', value: '+str(round(start_val,2))+', end date: '+df_2['Date'][idx-num_days]+', value: '+str(round(end_val,2)))
		abs_returns.append(end_val-start_val)
		pct_returns.append(round(100*(end_val-start_val)/start_val,2))
		# Generate list of dates for plotting purposes
		dates.append(df_2['Date'][idx-hold_days+end_day])
		curr_lows=[]
		for idx_l in range(idx-hold_days,idx):
			curr_lows.append(df_2['Low'][idx_l])
		# get the largest percent decline from the opening value of this months trade
		pct_low.append(round(-100*(start_val-min(curr_lows))/start_val,2))
	
	#print the start date and returns of analysis
	# ~ for x in range(len(adj_start_points)):
		# ~ print('start date: '+df_2['Date'][adj_start_points[x]]+', end date: '+df_2['Date'][adj_start_points[x]-num_days]+', pct return: '+str(pct_returns[x]))
	
	
	# make list of dates into datetime objects
	date_list_r = [datetime.datetime.strptime(date_item,"%Y-%m-%d").date() for date_item in dates]
	
	# Reverse all lists to go from start date to end date
	# Transpose lists
	date_list_out=date_list_r[::-1]
	pct_returns_out=pct_returns[::-1]
	abs_returns_out=abs_returns[::-1]
	pct_low_out=pct_low[::-1]
	trade_open_out=trade_open[::-1]
	
	return pct_returns_out,abs_returns_out,date_list_out,pct_low_out,trade_open_out
	
	
	
	
def main():
	start_time = time.time()
	#####
	# input main info here
	#####
	
	# Data location for mac:
	# path = '/Users/Marlowe/Marlowe/Securities_Trading/_Ideas/Data/'
	path = '/Users/Marlowe/gitsite/transfer/TOM/'
	
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
	
	start_date='1950-01-04'
	# ~ start_date='1987-09-10'
	# start_date='1999-09-10'
	# ~ start_date='2000-09-11'
	
	# end_date='2000-09-11'
	end_date='2019-05-10'
	
	
	# 2019_08_04, I believe we want to capture all of day -4 and all of day +1
	# This still needs to be verified
	
	# input month start date. 0=first day, 1=second day, -1=day before 1st day, etc
	start_day=-4
	# input end date. 0=first day, 1=second day, -1=day before 1st day, etc
	end_day=1
	
	#####
	# generate a list of returns over the desired period
	#####
	
	# this function generates the actual returns for each period over the given time frame
	# as if you bought and sold at the beginning and end.
	pct_rtns,abs_rtns,dates,pct_low,trade_open=tot_returns(df,start_date,end_date,start_day,end_day)
	
	
	
	####
	# Get overall data on ammt won/lost and EV
	####
	
	winner_bin=[]
	loser_bin=[]
	for x in range(len(pct_rtns)):
		if pct_rtns[x]<=0:
			loser_bin.append(pct_rtns[x])
		else:
			winner_bin.append(pct_rtns[x])
			
	
	avg_pct_win=round(np.mean(winner_bin),2)
	avg_pct_loss=round(np.mean(loser_bin),2)
	num_wins=len(winner_bin)
	num_loss=len(loser_bin)
	print()
	print('Overall Average % of win: '+str(avg_pct_win)+', Number of wins: '+str(len(winner_bin)))
	print('Overall Average % of loss: '+str(avg_pct_loss)+', Number of losses: '+str(len(loser_bin)))
	
	# This output represents the expected value of this strategy in percent terms
	win_prob=num_wins/(num_wins+num_loss)
	loss_prob=1.-win_prob
	
	edge=avg_pct_win*win_prob-avg_pct_loss*loss_prob
	print('Trading edge(gain expectancy) is '+str(round(edge,2)))
	
	
	####
	# Looking only in bear market periods, ammt won/lost and EV
	####
	
	
	
	bear_periods=[[datetime.date(1961,11,25),datetime.date(1962,6,5)],
					[datetime.date(1968,10,25),datetime.date(1970,5,5)],
					[datetime.date(1972,12,25),datetime.date(1974,10,5)],
					[datetime.date(1980,10,25),datetime.date(1982,8,5)],
					[datetime.date(1987,7,25),datetime.date(1987,12,5)],
					[datetime.date(2000,2,25),datetime.date(2002,10,5)],
					[datetime.date(2007,9,25),datetime.date(2009,3,5)]]
	
	bm_winner_bin=[]
	bm_loser_bin=[]
	bm_dates=[]
	non_bm_winner_bin=[]
	non_bm_loser_bin=[]
	non_bm_dates=[]
	# ~ print()
	# ~ return
	for x in range(len(pct_rtns)):
		is_bear=0
		for y in range(len(bear_periods)):
			if bear_periods[y][0] <= dates[x] <= bear_periods[y][1]:
				is_bear=1
				bm_dates.append(dates[x])
				if pct_rtns[x]<=0:
					bm_loser_bin.append(pct_rtns[x])
				else:
					bm_winner_bin.append(pct_rtns[x])
		if is_bear==0:
			non_bm_dates.append(dates[x])
			if pct_rtns[x]<=0:
				non_bm_loser_bin.append(pct_rtns[x])
			else:
				non_bm_winner_bin.append(pct_rtns[x])
	
	# ~ print(bm_dates)
	# ~ return
	
	bm_avg_pct_win=round(np.mean(bm_winner_bin),2)
	bm_avg_pct_loss=round(np.mean(bm_loser_bin),2)
	bm_num_wins=len(bm_winner_bin)
	bm_num_loss=len(bm_loser_bin)
	print()
	print('Bear Market Average % of win: '+str(bm_avg_pct_win)+', Number of wins: '+str(len(bm_winner_bin)))
	print('Bear Market Average % of loss: '+str(bm_avg_pct_loss)+', Number of losses: '+str(len(bm_loser_bin)))
	
	bm_win_prob=bm_num_wins/(bm_num_wins+bm_num_loss)
	bm_loss_prob=1.-bm_win_prob
	
	bm_edge=bm_avg_pct_win*bm_win_prob-bm_avg_pct_loss*bm_loss_prob
	print('Bear Market Trading edge(gain expectancy) is '+str(round(bm_edge,2)))
	
	non_bm_avg_pct_win=round(np.mean(non_bm_winner_bin),2)
	non_bm_avg_pct_loss=round(np.mean(non_bm_loser_bin),2)
	non_bm_num_wins=len(non_bm_winner_bin)
	non_bm_num_loss=len(non_bm_loser_bin)
	print()
	print('Non Bear Market Average % of win: '+str(non_bm_avg_pct_win)+', Number of wins: '+str(len(non_bm_winner_bin)))
	print('Non Bear Market Average % of loss: '+str(non_bm_avg_pct_loss)+', Number of losses: '+str(len(non_bm_loser_bin)))
	
	non_bm_win_prob=non_bm_num_wins/(non_bm_num_wins+non_bm_num_loss)
	non_bm_loss_prob=1.-non_bm_win_prob
	
	non_bm_edge=non_bm_avg_pct_win*non_bm_win_prob-non_bm_avg_pct_loss*non_bm_loss_prob
	print('Non Bear Market Trading edge(gain expectancy) is '+str(round(non_bm_edge,2)))
	
	
	####
	# Next want to consider periods of high volatility (VIX)
	####
	
	
	
	print()
	print('%f seconds to run script' % (time.time() - start_time))
	print()
	
	return

main()

