'''
This study is used to help determine the optimal stop loss for the TOM trade.

The biggest loss is calculated as the largest % decline during the trade from the opening price

Input: daily OHLC data for desired trading symbol

Output: 
1. Plot the histogram (bar plot) of each months returns.
2. Determine correlation between lowest low during the period while trade was on
	and winners/loosers. Want to find a way to eliminate the really big losses, maybe two std dev
	but also look at what is the biggest loss experienced on trades that were winners.
	Also consider when did that loss reach its maximum point, was it early on or later in the trade

	



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
	start_points_1=[]
	for mo in months:
		start_points_1.append(start_date_detect(df_2,idxl,idxh,mo))
	# print(start_points)
	
	# create one list with indexes in order
	start_points_2=[item for sublist in start_points_1 for item in sublist]
	start_points=sorted(start_points_2)

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
	abs_returns=[]
	pct_returns=[]
	dates=[]
	lows=[]
	for idx in adj_start_points:
		start_val=df_2['Open'][idx]
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
		lows.append(round(-100*(start_val-min(curr_lows))/start_val,2))
	
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
	lows_out=lows[::-1]
	
	return pct_returns_out,abs_returns_out,date_list_out,lows_out
	
	
def bar_plot(a_list,num_bins):
	# x_vals=[x for x in range(num_days[0],num_days[1]+1,1)]
	
	fig = plt.figure()
	ax = plt.subplot()
	# ~ ax.plot(x_vals,a_list,color='b')
	ax.hist(a_list,normed=False,bins=num_bins)
	ax.set_ylabel('Number of months')
	ax.set_xlabel('% Returns')
	
	# loc=plticker.MultipleLocator(base=1)
	# ax.xaxis.set_major_locator(loc)
	# ~ ax.set_xlim(num_days[0],num_days[1])
	
	ax.grid(which='major', axis='both')
	plt.show()
	
	
	return
	
	
	
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
	
	# ~ start_date='1950-01-04'
	start_date='1980-01-10'
	# ~ start_date='1987-09-10'
	# start_date='1999-09-10'
	# ~ start_date='2000-09-11'
	
	# end_date='2000-09-11'
	end_date='2019-05-10'
	
	
	# input month start date. 0=first day, 1=second day, -1=day before 1st day, etc
	start_day=-4
	# input end date. 0=first day, 1=second day, -1=day before 1st day, etc
	end_day=1
	
	
	#####
	# generate a list of returns over the desired period
	#####
	
	# this function generates the actual returns for each period over the given time frame
	# as if you bought and sold at the beginning and end.
	pct_rtns,abs_rtns,dates,lows=tot_returns(df,start_date,end_date,start_day,end_day)
	
	# print(len(dates))
	# ~ print(sc_pct_returns)
	# ~ print(pct_rtns[320:])
	
	#####
	# Print histogram of the returns over period
	#####
	
	# ~ bar_plot(pct_rtns,20)
	
	#####
	# Generate statistics
	#####
	
	print('Mean: '+str(round(np.mean(pct_rtns),2))+', std dev: '+str(round(np.std(pct_rtns),2)))
	
	#####
	# Find lowest low and average low corresponding to three bins:
	# losing months <-3%, -3% to +0.1%, >0.1%
	#####
	'''
	Notes: No month with a <-3% return had a low higher than -3%, so these could have all been eliminated by capping the loss at -3%.
	
	Could set stop loss at ~-3 to -4% and still have almost all winners.
	
	
	
	
	'''
	'''
	minus_three_bin=[]
	big_winner_bin=[]
	middle_pack_bin=[]
	for x in range(len(pct_rtns)):
		if pct_rtns[x]<=-3:
			minus_three_bin.append(lows[x])
		elif -3 < pct_rtns[x] <= 0.:
			middle_pack_bin.append(lows[x])
		else:
			big_winner_bin.append(lows[x])
			
	
	
	print('Big Winner Bin (>0% return): '+str(len(big_winner_bin))+' entries')
	# print(big_winner_bin)
	print('Mean low: '+str(round(np.mean(big_winner_bin),2)))
	print('Lowest Low: '+str(min(big_winner_bin)))
	print()
	
	print('Middle of the road bin (>-3%, <0% return): '+str(len(middle_pack_bin))+' entries')
	# print(middle_pack_bin)
	print('Mean low: '+str(round(np.mean(middle_pack_bin),2)))
	print('Lowest Low: '+str(min(middle_pack_bin)))
	print()
	
	print('Big loser bin (<-3% return): '+str(len(minus_three_bin))+' entries')
	# print(minus_three_bin)
	print('Mean low: '+str(round(np.mean(minus_three_bin),2)))
	print('Lowest Low: '+str(min(minus_three_bin)))
	
	'''
	####
	# Get data on ammt won/lost
	####
	'''
	winner_bin=[]
	loser_bin=[]
	for x in range(len(pct_rtns)):
		if pct_rtns[x]<=0:
			loser_bin.append(pct_rtns[x])
		else:
			winner_bin.append(pct_rtns[x])
			
	
	avg_pct_win=round(np.mean(winner_bin),2)
	avg_pct_loss=round(np.mean(loser_bin),2)
	print()
	print('Average % of win: '+str(avg_pct_win))
	print('Average % of loss: '+str(avg_pct_loss))
	
	print()
	print('%f seconds to run script' % (time.time() - start_time))
	print()
	'''
	'''
	# Plot a histogram of any set of lows
	fig = plt.figure()
	ax = plt.subplot()
	ax.hist(middle_pack_bin,normed=False,bins=10)
	ax.set_ylabel('Number of months')
	ax.set_xlabel('% lowest low')
	ax.grid(which='major', axis='both')
	plt.title('Lowest lows in months with <-3% return histogram')
	plt.show()
	'''
	
	return
	
main()
