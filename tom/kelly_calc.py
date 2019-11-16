'''
The purpose of this script is to develop a position size fraction based on various inputs that have
an impact on the likelihood of success of a given trade.


Input: daily OHLC data for desired trading symbol

Output: the modified kelly fraction



Notes:
11/4/19: I want to do more research into the high/low starting ranges and optimize this section alittle

for more info on coumpound kelly fraction see: math.stackexchange.com/questions/662104/kelly-criterion-with-more-than-two-outcomes


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
from yahoofinancials import YahooFinancials as yf

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
	
def update_data(file_name):
	# first check data if most recent date is updated
	
	
	#Update the each companies data
	print('now updating data')

	

	#use below to update all rows
	print('updating data for symbol '+str(file_name))
	sym=file_name
	#pull data from yahoo finance
	data=yf(sym)
	historical_prices = data.get_historical_price_data(symbol_list[i][1], symbol_list[i][2], 'daily')
	#create pandas dataframe with the date and price
	df = pd.DataFrame(historical_prices[sym]['prices'])
	df = df[['formatted_date','close']]
	# ~ print(df.head())
	#create filename
	filename=sym+'_prices_'+symbol_list[i][1]+'_'+symbol_list[i][2]+'.csv'
	#save data to csv file
	# ~ print('saving data')
	save_data(filename,df)
		
	print('Complete!')

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
	# index_locations_daym4=[idx+4 for idx in index_locations_day0]
	
	# return index_locations_day0,index_locations_daym4,df
	return index_locations_day0,df



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
	# pct_range = [upper,lower], ex: pct_range=[5%,20%]
	# for setting pct_range to 0, use 0.001% (input 0.00001)
	
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
		range_10d=period_high-period_low
		if high_low == 'high':
			opening_range_h=period_high-pct_range[0]*range_10d
			opening_range_l=period_high-pct_range[1]*range_10d
			if opening_range_h > opening_val >= opening_range_l:
				idx_list_filt.append(idx)
		if high_low == 'low':
			opening_range_h=period_low+pct_range[0]*range_10d
			opening_range_l=period_low+pct_range[1]*range_10d
			if opening_range_l < opening_val <= opening_range_h:
				idx_list_filt.append(idx)
			
	idx_list_out=[idx-4 for idx in idx_list_filt]
	# print(idx_list_out)
	return idx_list_out
	
def kelly_results(rtns,kelly_fraction,equity,stop_loss,yes_print):
	wins=[rtn for rtn in rtns if rtn >= 0]
	num_wins=len(wins)
	num_loss=len(rtns)-len(wins)
	win_prob=num_wins/(num_wins+num_loss)
	loss_prob=1.-win_prob
	avg_win=round(np.mean(wins),2)
	payoff=avg_win/stop_loss
	# kelly = the percentage of equity to bet on this trade
	kelly_frac=(payoff*win_prob-loss_prob)/payoff
	kelly=kelly_fraction*equity*kelly_frac
	if yes_print:
		print('Win probability: '+str(round(win_prob,2))+', mean of wins: '+str(avg_win))
		print('Kelly fraction: '+str(round(kelly_frac,3))+', total equity to bet: '+str(round(kelly,2))+' of '+str(equity))
		# print('kelly frac: '+str(round(kelly_frac,3))+', win prob: '+str(win_prob))
		print()
	return win_prob,avg_win
	
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
	
	####
	# Update GSPC file
	# Check first if date is most recent
	# other wise update
	####
	
	
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
	end_date='2019-04-25'
	
	#input the date of opening the trade
	trade_date='2019-02-25'
	trade_month='03'
	
	# option to input data for open price
	# if trade_open=0, then default to previous close
	trade_open=0
	open_price=2790
	
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
	equity=30000
	
	#####
	# Generate overall tom kelly info
	#####
	
	# generate a list of indexes of first days of all months in test period
	# Remove daym4 11/4/19
	idx_list_day0,df_sliced=start_of_month_detect(df,start_date,end_date,'00')
	# get returns
	all_rtns=get_returns_full_trade(df_sliced,idx_list_day0,-4,1,stop_loss)
	# count wins and losses and mean return of wins
	print('Kelly results for overall:')
	kelly_results(all_rtns,kelly_fraction,equity,stop_loss,1)
	# return
	
	#####
	# Generate kelly based on 10d high/low nearness
	#####
	
	# divide the range between 10d high and low into 5 ranges.
	# develop a unique probability based on which section of that range we start
	# the bet in.
	
	# range 1 is within 5% of 10 day high
	pct_close=[0.00001,0.05]
	idx_list_range1=prev_move_filt(idx_list_day0,'high',10,df_sliced,pct_close)
	rtns_range1=get_returns_full_trade(df_sliced,idx_list_range1,-4,1,stop_loss)
	# range 2 is between 5%-20% of 10 day high
	pct_close=[0.05,0.2]
	idx_list_range2=prev_move_filt(idx_list_day0,'high',10,df_sliced,pct_close)
	rtns_range2=get_returns_full_trade(df_sliced,idx_list_range2,-4,1,stop_loss)
	# range 4 is between 5%-20% of 10 low
	pct_close=[0.2,0.05]
	idx_list_range4=prev_move_filt(idx_list_day0,'low',10,df_sliced,pct_close)
	rtns_range4=get_returns_full_trade(df_sliced,idx_list_range4,-4,1,stop_loss)
	# range 5 is within 5% of 10 day low
	pct_close=[0.05,0.00001]
	idx_list_range5=prev_move_filt(idx_list_day0,'low',10,df_sliced,pct_close)
	rtns_range5=get_returns_full_trade(df_sliced,idx_list_range5,-4,1,stop_loss)
	
	
	
	# range 3 is between 20%-80% of 10 day high/low
	idx_list_range3=[idx for idx in idx_list_day0]
	# print(len(idx_list_range3))
	for idx in idx_list_range1:
		if idx in idx_list_range3:
			idx_list_range3.remove(idx)
	# print(len(idx_list_range3))
	for idx in idx_list_range2:
		if idx in idx_list_range3:
			idx_list_range3.remove(idx)
	# print(len(idx_list_range3))
	for idx in idx_list_range4:
		if idx in idx_list_range3:
			idx_list_range3.remove(idx)
	# print(len(idx_list_range3))
	for idx in idx_list_range5:
		if idx in idx_list_range3:
			idx_list_range3.remove(idx)
	# print(len(idx_list_range3))
	rtns_range3=get_returns_full_trade(df_sliced,idx_list_range3,-4,1,stop_loss)
	
	# print('Mean return of tom: '+str(round(np.mean(all_rtns),2))+', num samps: '+str(len(idx_list_day0)))
	# print('Mean return of range1: '+str(round(np.mean(rtns_range1),2))+', num samps: '+str(len(idx_list_range1)))
	# print('Mean return of range2: '+str(round(np.mean(rtns_range2),2))+', num samps: '+str(len(idx_list_range2)))
	# print('Mean return of range3: '+str(round(np.mean(rtns_range3),2))+', num samps: '+str(len(idx_list_range3)))
	# print('Mean return of range4: '+str(round(np.mean(rtns_range4),2))+', num samps: '+str(len(idx_list_range4)))
	# print('Mean return of range5: '+str(round(np.mean(rtns_range5),2))+', num samps: '+str(len(idx_list_range5)))
	# print('number of samples ignored: '+str(len(idx_list_day0)-len(idx_list_range1)-len(idx_list_range2)-len(idx_list_range3)-len(idx_list_range4)-len(idx_list_range5)))
	# return
	
	
	
	# calculate kelly range1
	# print('Kelly results for range 1:')
	rng1_prob,rng1_avg_win=kelly_results(rtns_range1,kelly_fraction,equity,stop_loss,0)
	rng1_samps=len(rtns_range1)
	# calculate kelly range2
	# print('Kelly results for range 2:')
	rng2_prob,rng2_avg_win=kelly_results(rtns_range2,kelly_fraction,equity,stop_loss,0)
	rng2_samps=len(rtns_range2)
	# calculate kelly range3
	# print('Kelly results for range 3:')
	rng3_prob,rng3_avg_win=kelly_results(rtns_range3,kelly_fraction,equity,stop_loss,0)
	rng3_samps=len(rtns_range3)
	# calculate kelly range4
	# print('Kelly results for range 4:')
	rng4_prob,rng4_avg_win=kelly_results(rtns_range4,kelly_fraction,equity,stop_loss,0)
	rng4_samps=len(rtns_range4)
	# calculate kelly range5
	# print('Kelly results for range 5:')
	rng5_prob,rng5_avg_win=kelly_results(rtns_range5,kelly_fraction,equity,stop_loss,0)
	rng5_samps=len(rtns_range5)
	
	# return
	
	# find the previous 10 day range and where we currently fall in that range.
	# next calculate the probability of win and mean win based on that range location.
	
	#####
	# Generate kelly based on month of trade
	#####
	print('Kelly results modified for trade month and 10d range:')
	
	
	# generate a list of indexes of first days of all months in test period
	months=['01','02','03','04','05','06','07','08','09','10','11','12']
	month_lists=[]
	month_rtns=[]
	for month in months:
		idxs,df_sliced=start_of_month_detect(df,start_date,end_date,month)
		month_lists.append(idxs)
		months_rtns=get_returns_full_trade(df_sliced,idxs,-4,1,stop_loss)
		month_rtns.append(months_rtns)
		num_gt_1=len([rtn for rtn in months_rtns if (rtn > 2.0)])
		# print('Data on month '+month)
		# kelly_results(months_rtns,kelly_fraction,equity,stop_loss,1)
		# print('Mean return of month '+month+' is '+str(round(np.mean(get_returns_full_trade(df_sliced,idxs,-4,1,stop_loss)),2)))
		# print('Number above 2%: '+str(num_gt_1)+', pct of total: '+str(round(100*num_gt_1/len(idxs),1)))
		# print('Max return: '+str(max(months_rtns)))
	
	# output the probability of win and the mean win
	
	#####
	# Combined mean: xc=(m*xa+n*xb)/(m+n), where m=mean1, n=mean2, xa=sample num1, xb=sample num2
	# I think the conclusion I have come to is that finding the probability there is not enough info to put
	# the two probabilities together and come up with a better probability.
	# Try averaging the two probabilities together to find a reasonable approximation
	#####
	
	#####
	# Generate Kelly data for month
	#####
	
	mo_idx=months.index(trade_month)
	mo_prob,mo_avg_win=kelly_results(month_rtns[mo_idx],kelly_fraction,equity,stop_loss,0)
	mo_samps=len(month_rtns[mo_idx])
	
	print('Win probability of trade month '+trade_month+' is '+str(round(mo_prob,2))+', mean of wins: '+str(mo_avg_win))
	print()
	
	#####
	# Generate Kelly data for 10 day range
	#####
	
	#Get 10d high and low
	trade_date_df=df.loc[df['Date'] == trade_date]
	trade_date_idx=trade_date_df.index[0].tolist()
	
	period_high=0
	period_low=1000000
	for i in range(1,10):
		idx_ut=trade_date_idx+i
		day_high=df['High'][idx_ut]
		day_low=df['Low'][idx_ut]
		if period_high < day_high:
			period_high=day_high
		if period_low > day_low:
			period_low=day_low
	

	#Get previous close
	if trade_open==0:
		opening_val=df['Close'][trade_date_idx+1]
		# print(opening_val)
	else:
		opening_val=open_price
	
	#See where we are in the range
	# range 1 is within 5% of 10 day high
	# range 2 is between 5%-20% of 10 day high
	# range 3 is between 20%-80% of 10 day high/low
	# range 4 is between 5%-20% of 10 low
	# range 5 is within 5% of 10 day low
	range_10d=period_high-period_low
	high_dist=abs(period_high-opening_val)
	low_dist=abs(period_low-opening_val)
	dist_to_low=round(100*low_dist/range_10d,2)
	dist_to_high=round(100*high_dist/range_10d,2)
	
	# print('open is close of '+str(opening_val)+' on date '+df['Date'][end_date_idx+1])
	# print('10d high is '+str(period_high)+', 10d low is '+str(period_low))
	# print('open is within '+str(dist_to_high)+'% of high and within '+str(dist_to_low)+'% of low')
	# print()
	
	#return probability and avg win based on that range
	rng_prob=0
	rng_avg_win=0
	rng_samps=0
	#range1
	if dist_to_high < 5:
		print('open is within '+str(dist_to_high)+'% of high')
		print('Win prob of range1: '+str(round(rng1_prob,2))+', mean of wins range1: '+str(rng1_avg_win))
		rng_prob=rng1_prob
		rng_avg_win=rng1_avg_win
		rng_samps=rng1_samps

	#range2
	elif 5<dist_to_high<20:
		print('open is within '+str(dist_to_high)+'% of high')
		print('Win prob of range2: '+str(round(rng2_prob,2))+', mean of wins range2: '+str(rng2_avg_win))
		rng_prob=rng2_prob
		rng_avg_win=rng2_avg_win
		rng_samps=rng2_samps

	#range5
	elif dist_to_low < 5:
		print('open is within '+str(dist_to_low)+'% of low')
		print('Win prob of range5: '+str(round(rng5_prob,2))+', mean of wins range5: '+str(rng5_avg_win))
		rng_prob=rng5_prob
		rng_avg_win=rng5_avg_win
		rng_samps=rng5_samps
	
	#range4
	elif 5<dist_to_low<20:
		print('open is within '+str(dist_to_low)+'% of low')
		print('Win prob of range4: '+str(round(rng4_prob,2))+', mean of wins range4: '+str(rng4_avg_win))
		rng_prob=rng4_prob
		rng_avg_win=rng4_avg_win
		rng_samps=rng4_samps
	
	#range3
	else:
		print('open is in the middle, within '+str(dist_to_high)+'% of high and within '+str(dist_to_low)+'% of low')
		print('Win prob of range3: '+str(round(rng3_prob,2))+', mean of wins range3: '+str(rng3_avg_win))
		rng_prob=rng3_prob
		rng_avg_win=rng3_avg_win
		rng_samps=rng3_samps
	
	#####
	# compound probability and avg win
	#####
	overall_prob_win=(rng_prob*rng_samps+mo_prob*mo_samps)/(rng_samps+mo_samps)
	overall_prob_loss=1-overall_prob_win
	overall_avg_win=(rng_avg_win*rng_samps+mo_avg_win*mo_samps)/(rng_samps+mo_samps)
	payoff=overall_avg_win/stop_loss
	# kelly = the percentage of equity to bet on this trade
	overall_kelly_frac=(payoff*overall_prob_win-overall_prob_loss)/payoff
	overall_kelly=kelly_fraction*equity*overall_kelly_frac
	print()
	print('Modified Kelly:')
	print('Win probability: '+str(round(overall_prob_win,2))+', mean of wins: '+str(round(overall_avg_win,2)))
	print('Kelly fraction: '+str(round(overall_kelly_frac,3))+', total equity to bet: '+str(round(overall_kelly,2))+' of '+str(equity))
	
	micro_lvg=5
	mini_lvg=50
	stop_set=round(opening_val-opening_val*stop_loss,2)
	potential_loss=round(opening_val-stop_set,2)
	num_contracts_nolvg=round(overall_kelly/potential_loss,2)
	num_contracts_micro=round(num_contracts_nolvg/micro_lvg,2)
	num_contracts_mini=round(num_contracts_nolvg/mini_lvg,2)
	print()
	print('Opening price of '+str(round(opening_val,2))+' set stop loss to '+str(stop_set))
	print('Purchase '+str(num_contracts_mini)+' mini contracts or '+str(num_contracts_micro)+' micro contracts')
	
	
	
	
	print()
	print('%f seconds to run script' % (time.time() - start_time))
	print()
	
	
	return
	
def main2():
	#####
	# Create compound kelly fraction
	# want to maximize SUM(pi*log(1+bi*x)) where x is the overall kelly fraction and pi=[p1,p2,p3], bi=[b1,b2,b3]
	# where pi is the probability of win and bi is the payoff of the win.
	# want to find the maximum of SUM(pi*bi/(1+bix))=0
	#####
	
	probs=[0.69,0.31]
	payoffs=[1.93,-2.5]
	
	threshold=0.00001
	initial_frac=0.8
	
	val_past=0
	val_next=initial_frac
	
	bump=0
	while abs(val_past-val_next) > threshold:
		val_past=val_next
		num=0
		denom=0
		for i in range(len(probs)):
			num=num+((probs[i]*payoffs[i])/(1+payoffs[i]*val_past))
			denom=denom+(-payoffs[i]**2*probs[i]/((1+payoffs[i]*val_past)**2))
		
		val_next=val_past-(num/denom)
		print('val_next: '+str(round(val_next,3))+', val_past: '+str(round(val_past,3))+', num/den: '+str(round(num/denom,3)))
		if val_next < 0 & bump==0:
			val_next=0
			bump=1
		if val_next > 1000:
			print('exponential')
			break
		
	fraction=val_next
	
main()