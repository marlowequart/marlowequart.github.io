'''
This script looks at the TOM effect over a given period and generates the 
expected return, and plots the equity curve

The purpose is to compare different start and end dates around tom.

Input: daily OHLC data for desired trading symbol

Output: returns over period and plot of equity


8/3/19
Want to include a monte carlo simulation aspect to this strategy in order to find
the possiblity of total ruin

Notes:
In order to calculate the average(mean) of the % daily returns over a given period.
For a single TOM, this is the mean of the daily returns on that particular TOM.
For extended periods, you would take the mean of each TOM's mean over the given period.

For example, for a 2 year period, you first calculate the mean of the % daily returns
around the TOM of each month in that period. Then you take the mean of all of the means
over that given period.

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


def start_date_detect_one_mo(df,index_l,index_h,month):
	#return a list of the index of the first day of the desired month over
	#the given period. This function uses a single month as the input
	
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

def start_date_detect_mo_list(df,index_l,index_h,months):
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
	start_points=start_date_detect_mo_list(df_2,idxl,idxh,months)
	
	# print(start_points)
	
	# print(df.loc[[start_points[4]-1]])
	# return
	
	
	'''
	# Compare two methods of generating the monthly starting points:
	test_1_time=time.time()
	start_points_test1=[]
	for mo in months:
		start_points_test1.append(start_date_detect_one_mo(df_2,idxl,idxh,mo))
	print()
	print('%f seconds for test 1' % (time.time() - test_1_time))
	print()
	test_2_time=time.time()
	start_points_test2=[]
	start_points_test2=start_date_detect_mo_list(df_2,idxl,idxh,months)
	print()
	print('%f seconds for test 2' % (time.time() - test_2_time))
	print()
	start_points_test_11=[item for sublist in start_points_test1 for item in sublist]
	start_points_test_12=sorted(start_points_test_11)
	# ~ print(start_points_test_12[10:50])
	print()
	# ~ print(start_points_test2[10:50])
	print('The two lists are the same: '+str(start_points_test_12==start_points_test2))
	'''
	
	
	
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
	abs_returns=[]
	pct_returns=[]
	dates=[]
	pct_low=[]
	trade_open=[]
	for idx in adj_start_points:
		start_val=df_2['Open'][idx]
		trade_open.append(start_val)
		end_val=df_2['Open'][idx-hold_days]
		# ~ print('start date: '+df_2['Date'][idx]+', value: '+str(round(start_val,2))+', end date: '+df_2['Date'][idx-num_days]+', value: '+str(round(end_val,2)))
		abs_returns.append(end_val-start_val)
		pct_returns.append(round(100*(end_val-start_val)/start_val,2))
		# Generate list of dates for plotting purposes
		dates.append(df_2['Date'][idx])
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
	
	# ~ start_date='1950-01-04'
	start_date='1987-09-10'
	# start_date='1999-09-10'
	# ~ start_date='2000-09-11'
	
	# end_date='2000-09-11'
	end_date='2019-05-10'
	
	
	# input month start date. 0=first day, 1=second day, -1=day before 1st day, etc
	start_day=-4
	# input end date. 0=first day, 1=second day, -1=day before 1st day, etc
	end_day=1
	
	
	
	# ~ start_date_yr=int(re.findall(r'(.+?)-',start_date)[0])
	# ~ end_date_yr=int(re.findall(r'(.+?)-',end_date)[0])
	# ~ start_date_mo=int(re.findall(r'-(.+?)-',start_date)[0])
	# ~ end_date_mo=int(re.findall(r'-(.+?)-',end_date)[0])
	# ~ tot_months=12*(end_date_yr-start_date_yr)+(end_date_mo-start_date_mo)
	# ~ print(start_date_yr,start_date_mo)
	# ~ print(end_date_yr,end_date_mo)
	# ~ print(tot_months)
	# ~ return
	
	
	#####
	# generate a list of returns over the desired period
	#####
	
	# this function generates the actual returns for each period over the given time frame
	# as if you bought and sold at the beginning and end.
	pct_rtns,abs_rtns,dates,pct_low,trade_open=tot_returns(df,start_date,end_date,start_day,end_day)
	
	
	# print(len(dates))
	# ~ for item in pct_rtns:
		# ~ print(item)
	# ~ print(pct_low[20:50])
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
	# Look at possible returns of strategy
	#####
	'''
	worst_case_return=min(pct_rtns)
	mean_return=round(np.mean(pct_rtns),2)
	std_dev_return=round(np.std(pct_rtns),2)
	
	print()
	print('Testing from '+start_date+' to '+end_date)
	print('Purchase on day '+str(start_day)+', sell on day '+str(end_day))
	print('Mean returns: '+str(mean_return)+', std_dev: '+str(std_dev_return)+', worst case return: '+str(worst_case_return))
	print()
	# ~ print(yearly_abs_return)
	
	'''
	
	#####
	# Generate EV of strategy
	#####
	'''
	# This output represents the expected value of this strategy in percent terms
	num_wins=245
	num_loss=135
	
	win_prob=num_wins/(num_wins+num_loss)
	loss_prob=1.-win_prob
	
	avg_pct_win=1.73
	avg_pct_loss=1.5
	
	edge=avg_pct_win*win_prob-avg_pct_loss*loss_prob
	print()
	print('Trading edge (gain expectancy) is '+str(round(edge,2)))
	print()
	'''
	#####
	# Generate sharpe ratio and gain to pain of strategy
	#####
	
	# gain to pain ratio: sum of all returns/abs(sum of all losses)
	# Sharpe ratio: Return-Risk Free rate/stand dev of returns
	
	losing=[]
	winning=[]
	for item in pct_rtns:
		if item < 0:
			losing.append(item)
		else:
			winning.append(item)
	
	
	
	
	gain_pain=round(sum(winning)/abs(sum(losing)),2)
	
	print()
	print('Gain to pain ratio is '+str(gain_pain))
	print()
	
	
	#####
	# Plot equity curve
	#####
	
	# Simple normalized equity curve, purchase 1 unit each trade (no position sizing),
	# no stop loss
	# ~ start_equity=10000
	# leverage factor is $ per point
	# ~ levg_fact=5
	# ~ basic_equity=[start_equity]
	# ~ for i in range(len(abs_rtns)):
		# ~ basic_equity.append(equity[i]+levg_fact*abs_rtns[i])
	# ~ basic_equity=equity[1:]
	
	# Calculate CAGR
	# ~ tot_months=len(abs_rtns)
	# ~ tot_yrs=tot_months/12
	# ~ cagr=round(100*((basic_equity[-1]/start_equity)**(1/tot_yrs)-1),1)
	# ~ print()
	# ~ print('The CAGR of this strategy is '+str(cagr))
	
	
	# Equity curve with stop loss, purchase 1 unit each trade (no position sizing)
	# set stop loss to 9% drop
	# ~ stop_loss=9
	# ~ start_equity=10000
	# leverage factor is $ per point
	# ~ levg_fact=5
	# ~ stopped_equity=[start_equity]
	# ~ for i in range(len(abs_rtns)):
		# ~ if pct_low[i]<-stop_loss:
			# ~ stopped_equity.append(stopped_equity[i]-levg_fact*stop_loss/100*trade_open[i])
		# ~ else:
			# ~ stopped_equity.append(stopped_equity[i]+levg_fact*abs_rtns[i])
	# ~ stopped_equity=stopped_equity[1:]
	
	# Calculate CAGR
	# ~ tot_months=len(abs_rtns)
	# ~ tot_yrs=tot_months/12
	# ~ cagr=round(100*((stopped_equity[-1]/start_equity)**(1/tot_yrs)-1),1)
	# ~ print()
	# ~ print('The CAGR of this strategy is '+str(cagr))
	
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
	
	
	# ~ return
	
	
	
	print()
	print('%f seconds to run script' % (time.time() - start_time))
	print()
	
	# ~ return
	
	# Plot returns over dates
	fig = plt.figure()
	ax = plt.subplot()
	
	# ~ ax.plot(dates,basic_equity,color='b',label='Basic Equity')
	# ~ ax.plot(dates,stopped_equity,color='c',label='Equity with Stop Losses')
	ax.plot(dates,kelly_equity,color='r',label='Equity using Kelly')
	
	ax.set_ylabel('Equity')
	ax.set_xlabel('Date')
	
	
	ax.grid()
	plt.legend()
	plt.show()
	
	
	return

main()
