'''
The purpose of this script is to develop a position size fraction based on various inputs that have
an impact on the likelihood of success of a given trade.


Input: daily OHLC data for desired trading symbol

Output: the modified kelly fraction



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
	
		
	# Create indexes for daym4
	index_locations_daym4=[idx+4 for idx in index_locations_day0]
	
	return index_locations_day0,index_locations_daym4,df



def get_returns_full_trade(df,idx_list,start,end,stop):
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
		if ((trade_open-trade_low)/trade_open) < -stop:
			pct_returns.append(-100*stop)
		elif ((trade_close-trade_open)/trade_open) < -stop:
			pct_returns.append(-100*stop)
		else:
			pct_returns.append(round(100*(trade_close-trade_open)/trade_open,2))
		
		# Use the following for no stop loss
		# pct_returns.append(round(100*(trade_close-trade_open)/trade_open,2))
	
	return pct_returns

def prev_move_filt(idx_list,high_low,num_days,df,pct_range):
	# This function checks the num_days previous to each index in the idx_list
	# and returns the indexes that are within pct_range of the num_days 
	# previous range to the high_low side
	
	# pct_range=0.005
	
	# idx list is the day0 of the trades we are interested in
	# we want to start out on the day m4
	idx_list_m4=[idx+4 for idx in idx_list]
	
	# get the high of the period of interest
	idx_list_filt=[]
	for idx in idx_list_m4:
		#for each idx under test, first get the period high and low
		period_high=0
		period_low=1000000
		for i in range(num_days):
			idx_ut=idx+i
			day_high=df['High'][idx_ut]
			day_low=df['Low'][idx_ut]
			if period_high < day_high:
				period_high=day_high
			if period_low > day_low:
				period_low=day_low
		# if the opening price is within pct_range of the period high/low
		# add the start index to the new list
		opening_val=df['Open'][idx]
		if high_low == 'high':
			opening_range=period_high-pct_range*period_high
			if opening_val >= opening_range:
				idx_list_filt.append(idx)
		if high_low == 'low':
			opening_range=period_low+pct_range*period_low
			if opening_val <= opening_range:
				idx_list_filt.append(idx)
			
	idx_list_out=[idx-4 for idx in idx_list_filt]
	# print(idx_list_out)
	return idx_list_out
	
	
	
	
def main():
	start_time = time.time()
	#####
	# input main info here
	#####
	
	# Data location for mac:
	# path = '/Users/Marlowe/Marlowe/Securities_Trading/_Ideas/Data/'
	# path = '/Users/Marlowe/gitsite/TOM/'
	
	# Data location for PC:
	# ~ path = 'C:\\Python\\transfer\\TOM\\'
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
	
	# ~ start_date='1950-01-04'
	# start_date='1987-09-10'
	start_date='1999-09-10'
	# ~ start_date='2000-09-11'
	
	# end_date='2000-09-11'
	end_date='2019-05-10'
	
	print()
	
	#####
	# generate the odds and payoff for each given input
	# We are interested in the odds/probabililty of wins (number of wins, number of losses)
	# and we are interested in the payoff (mean of wins/stop loss)
	#####
	# set stop loss size
	stop_loss=0.025
	# kelly_fraction is the fraction of full kelly to use for smoother returns
	kelly_fraction=0.5
	# input current equity size
	equity=100000
	
	#####
	# Generate overall tom kelly info
	#####
	
	# generate a list of indexes of first days of all months in test period
	idx_list_day0,idx_list_daym4,df_sliced=start_of_month_detect(df,start_date,end_date,'00')
	# get returns
	all_rtns=get_returns_full_trade(df_sliced,idx_list_day0,-4,1,stop_loss)
	# count wins and losses and mean return of wins
	wins=[rtn for rtn in all_rtns if rtn >= 0]
	
	#calculate kelly
	num_wins_tot=len(wins)
	num_loss_tot=len(all_rtns)-len(wins)
	win_prob_tot=num_wins_tot/(num_wins_tot+num_loss_tot)
	loss_prob_tot=1.-win_prob_tot
	avg_win_tot=round(np.mean(wins),2)
	payoff_tot=avg_win_tot/stop_loss
	# kelly = the percentage of equity to bet on this trade
	kelly_frac_tot=(payoff_tot*win_prob_tot-loss_prob_tot)/payoff_tot
	kelly_tot=kelly_fraction*equity*kelly_frac_tot
	
	# here we classify a win as >=0. We may consider making a win >= mean
	print('number of wins: '+str(len(wins))+', number of samples: '+str(len(all_rtns)))
	print('mean of wins: '+str(avg_win_tot)+', kelly fraction: '+str(round(kelly_frac_tot,3))+', total equity to bet: '+str(round(kelly_tot,2))+' of '+str(equity))
	
	return
	
	#####
	# Generate kelly based on 10d high/low nearness
	#####
	
	# divide the range between 10d high and low into quartiles.
	# develop a unique probability based on which section of that range we start
	# the bet in.
	
	
	#Set the percentage closeness to the high or low
	pct_close=0.005
	# Find index locations occuring at 5d and 10d highs and get returns
	idx_list_5d_high=prev_move_filt(idx_list_day0,'high',5,df_sliced,pct_close)
	idx_list_10d_high=prev_move_filt(idx_list_day0,'high',10,df_sliced,pct_close)
	
	
	# Find index locations occuring at 5d and 10d lows and get returns
	idx_list_5d_low=prev_move_filt(idx_list_day0,'low',5,df_sliced,pct_close)
	idx_list_10d_low=prev_move_filt(idx_list_day0,'low',10,df_sliced,pct_close)
	
	# get overall returns
	
	rtns_5d_high=get_returns_full_trade(df_sliced,idx_list_5d_high,-4,1)
	rtns_5d_low=get_returns_full_trade(df_sliced,idx_list_5d_low,-4,1)
	rtns_10d_high=get_returns_full_trade(df_sliced,idx_list_10d_high,-4,1)
	rtns_10d_low=get_returns_full_trade(df_sliced,idx_list_10d_low,-4,1)
	
	
	print('Mean return of tom: '+str(round(np.mean(all_rtns),2))+', num samps: '+str(len(idx_list_day0)))
	print('Max return of tom: '+str(max(all_rtns)))
	print()
	print('Mean return of 5d high start: '+str(round(np.mean(rtns_5d_high),2))+', num samps: '+str(len(idx_list_5d_high)))
	print('Max return of 5d high start: '+str(max(rtns_5d_high)))
	print('Number of rtns > tom mean: '+str(len([rtn for rtn in rtns_5d_high if (rtn > np.mean(all_rtns))])))
	print('Mean return of 10d high start: '+str(round(np.mean(rtns_10d_high),2))+', num samps: '+str(len(idx_list_10d_high)))
	print()
	print('Mean return of 5d low start: '+str(round(np.mean(rtns_5d_low),2))+', num samps: '+str(len(idx_list_5d_low)))
	print('Mean return of 10d low start: '+str(round(np.mean(rtns_10d_low),2))+', num samps: '+str(len(idx_list_10d_low)))
	
	
	# consider returns without starting on 10d high
	idx_list_m10d_high=[idx for idx in idx_list_day0]
	for idx in idx_list_10d_high:
		if idx in idx_list_m10d_high:
			idx_list_m10d_high.remove(idx)
	rtns_m10d_high=get_returns_full_trade(df_sliced,idx_list_m10d_high,-4,1)
	print()
	print('Mean return of tom minus starts on 10d high: '+str(round(np.mean(rtns_m10d_high),2))+', num samps: '+str(len(idx_list_m10d_high)))
	
	
	print()
	print('%f seconds to run script' % (time.time() - start_time))
	print()
	
	
	return
	
	
	
	# Equity curve with stop loss, and Kelly position sizing
	# Optimum strategy seems to be around 5x leverage $/point and 1/2 Kelly
	# I will want to run this strategy through some more monte carlo type testing
	# set stop loss to 3% drop
	stop_loss=3
	start_equity=10000
	# leverage factor is $ per point
	levg_fact=5
	
	# input ratios for calculating kelly position sizing
	num_wins=245
	num_loss=135
	win_prob=num_wins/(num_wins+num_loss)
	loss_prob=1.-win_prob
	# payoff calculated by avg profit/stop loss
	avg_win=1.75
	payoff=avg_win/stop_loss
	# kelly_fraction is the fraction of full kelly to use for smoother returns
	kelly_fraction=0.5
	
	print()
	kelly_equity=[start_equity]
	for i in range(len(abs_rtns)):
		# kelly = the percentage of equity to bet on this trade
		kelly=kelly_fraction*kelly_equity[i]*(payoff*win_prob-loss_prob)/payoff
		# bet_size = the factor to multiply by the absolute win
		# (i.e. this represents the number of contracts. Using fractional contracts)
		bet_size=kelly/(levg_fact*trade_open[i]*(stop_loss/100))
		if pct_low[i]<-stop_loss:
			kelly_equity.append(kelly_equity[i]-levg_fact*stop_loss/100*trade_open[i])
		else:
			kelly_equity.append(kelly_equity[i]+bet_size*levg_fact*abs_rtns[i])
		# ~ if i==20:
			# ~ print('previous equity: '+str(kelly_equity[i])+', equity to risk based on kelly: '+str(kelly)+
					# ~ ', open price of trade: '+str(trade_open[i])+', stop loss: '+str(trade_open[i]*(stop_loss/100))+
					# ~ ', bet_size: '+str(bet_size)+
					# ~ ', absolute points return: '+str(abs_rtns[i])+', ammt won: '+str(bet_size*levg_fact*abs_rtns[i]))
	kelly_equity=kelly_equity[1:]
	
	# Calculate CAGR
	tot_months=len(abs_rtns)
	tot_yrs=tot_months/12
	cagr=round(100*((kelly_equity[-1]/start_equity)**(1/tot_yrs)-1),1)
	print()
	print('The CAGR of this strategy is '+str(cagr))
	
main()