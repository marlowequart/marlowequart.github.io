'''
This script finds consolidation patterns in OHLC price data
This works by finding the dates where a large delta hapened.
next an envelope filter is used starting at that date to determine
the number of days where the consolidation happend.

1. find dates with daily TR above x%
2. work forward from those points to find place where upper/lower bounds is broken using envelope


consider other ways to do envelope, maybe adjust strength of bounds depending
on how long the consolidation has happend.
also want to detect false breakouts. Consider searching up to x number of days
before and after to find if price re-entered envelope

'''

import pandas as pd
import os
import numpy as np
import csv

import matplotlib.pyplot as plt
from mpl_finance import candlestick2_ochl
import matplotlib.ticker as ticker

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
	
	
def gen_plot_mac(dataframe,startidx,endidx,fields):
	# fields = ['Date','Open','High','Low','Close']
	#####
	# plot just price
	#####
	endidx=endidx+1
	#dataframe is a pandas dataframe with open, high, low, close for each date
	
	open_day=dataframe[fields[1]][startidx:endidx].tolist()
	high=dataframe[fields[2]][startidx:endidx].tolist()
	low=dataframe[fields[3]][startidx:endidx].tolist()
	close=dataframe[fields[4]][startidx:endidx].tolist()
	date=dataframe[fields[0]][startidx:endidx].tolist()
	open_day.reverse()
	high.reverse()
	low.reverse()
	close.reverse()
	date.reverse()
	num_ticks=6


	# ~ def mydate(x,pos):
		# ~ try:
			# ~ return time[int(x)]
		# ~ except IndexError:
			# ~ return ''
	
	#####
	# plot just price
	#####
	fig = plt.figure()
	ax = plt.subplot()
	candlestick2_ochl(ax,open_day,close,high,low,width=0.5,colorup='blue',colordown='r',alpha=0.75)
	ax.xaxis.set_major_locator(ticker.MaxNLocator(num_ticks))
	ax.xaxis.set_major_formatter(ticker.FuncFormatter(date))
	fig.autofmt_xdate()
	fig.tight_layout()
	ax.set_ylabel('Price')
	ax.set_xlabel('Date/Time')
	ax.set_xlim(-1.0,len(open_day)-1.0)
	ax.xaxis.set_major_locator(ticker.MaxNLocator(num_ticks))
	ax.xaxis.set_major_formatter(ticker.FuncFormatter(date))
	ax.grid()
	plt.show()
	
	
def gen_plot_pc(dataframe,startidx,endidx,fields,indexes,upper_bounds):
	# fields = ['Date','Open','High','Low','Close']
	#####
	# plot just price
	#####
	endidx=endidx+1
	#dataframe is a pandas dataframe with open, high, low, close for each date
	# print(startidx,endidx)
	# print(dataframe['Date'][20:75])
	# return
	open_day=dataframe[fields[1]][startidx:endidx].tolist()
	high=dataframe[fields[2]][startidx:endidx].tolist()
	low=dataframe[fields[3]][startidx:endidx].tolist()
	close=dataframe[fields[4]][startidx:endidx].tolist()
	date=dataframe[fields[0]][startidx:endidx].tolist()
	#need to reverse data because dataframe has order from most recent to oldest
	open_day.reverse()
	high.reverse()
	low.reverse()
	close.reverse()
	date.reverse()
	
	# print(indexes)
	#need to reverse indexes too
	for i in range(len(indexes)):
		current_num=indexes[i]
		shift_num=endidx-current_num+startidx-1
		indexes[i]=shift_num
		
	for i in range(len(upper_bounds)):
		current_num=upper_bounds[i]
		shift_num=endidx-current_num+startidx-1
		upper_bounds[i]=shift_num
	
	
	# num_ticks=6
	# print(len(open_day))
	# return
	# ~ def mydate(x,pos):
		# ~ try:
			# ~ return time[int(x)]
		# ~ except IndexError:
			# ~ return ''
	
	#####
	# plot just price
	#####
	fig = plt.figure()
	ax = plt.subplot()
	candlestick2_ochl(ax,open_day,close,high,low,width=0.5,colorup='blue',colordown='r',alpha=0.75)
	
	#for 
	for idx in indexes:
		# ~ print(item)
		plt.axvline(x=idx-startidx, color='k', linestyle='--')
	for bd in upper_bounds:
		# ~ print(item)
		plt.axvline(x=bd-startidx, color='g', linestyle='--')
			
	
	# ax.xaxis.set_major_locator(ticker.MaxNLocator(num_ticks))
	# ax.xaxis.set_major_formatter(ticker.FuncFormatter(date))
	# fig.autofmt_xdate()
	# fig.tight_layout()
	ax.set_ylabel('Price')
	ax.set_xlabel('Date/Time')
	ax.set_xlim(-1.0,len(open_day)-1.0)
	# ax.xaxis.set_major_locator(ticker.MaxNLocator(num_ticks))
	# ax.xaxis.set_major_formatter(ticker.FuncFormatter(date))
	ax.grid()
	plt.show()
	
	
def list_gen(df,start_date,end_date,fields):
	#generate a list of dates (x axis) and values (y axis) for given inputs
	#fields order = ['Date','Open','High','Low','Close']
	
	start_day_df=df.loc[df[fields[0]] == start_date]
	end_day_df=df.loc[df[fields[0]] == end_date]
	# end_date_idx is an int
	startidx=end_day_df.index[0].tolist()
	endidx=start_day_df.index[0].tolist()
	
	
	date=df[fields[0]][startidx:endidx].tolist()
	close=df[fields[4]][startidx:endidx].tolist()
	#order lists from oldest to newest
	close.reverse()
	date.reverse()
	
	
	return date,close
	
	
def true_range_calc(df,lowidx,highidx,num_days):
	#cycle through dataframe, using ohlc data
	#output the df with new column with TR data
	#true range is max(todays high-low,todays high-yesterdays close,yesterdays close-todays low)
	
	# ~ print(df.head())
	
	#add column for true range
	df['true_range']=''
	df['ATR']=''
	
	for idx in range(lowidx,highidx-1):
		day_high=df['High'][idx]
		yest_close=df['Last'][idx+1]
		day_low=df['Low'][idx]
		true_r=max(day_high-day_low,day_high-yest_close,yest_close-day_low)
		true_r=float(true_r)
		df['true_range'][idx]=true_r
	
	for idx in range(lowidx,highidx-num_days-1):
		atr=0
		for x in range(num_days):
			atr=atr+df['true_range'][idx+x]
		atr_av=atr/num_days
		df['ATR'][idx]=atr_av
	
	return df
	
def slice_df(df,start_date,end_date):
	start_day_df=df.loc[df['Date'] == start_date]
	end_day_df=df.loc[df['Date'] == end_date]
	
	startidx=end_day_df.index[0].tolist()
	endidx=start_day_df.index[0].tolist()
	# print(startidx,endidx)
	# return
	return df[startidx:endidx],startidx,endidx
	
def env_detector_simple(df,date_idxs,direction):
	#starting from the date of interest, look forward/backward in the listed direction
	#output index of date of breakout from envelope
	
	#####
	# Using a basic percentage envelope to set upper and lower bound
	#####
	env_size_pct=8
	
	if direction == 'up':
	
		upper_bds=[]
		for idx in date_idxs:
			close_init=df['Close'][idx]
			env_size=env_size_pct/100*close_init
			bd_upper=close_init+env_size
			bd_lower=close_init-env_size
			z=0
			while (df['Close'][idx-z] < bd_upper) & (df['Close'][idx-z] > bd_lower):
				z=z+1
				if idx-z < 1:
					print('no upper bound found')
					break
				# print(z)
			upper_bds.append(idx-z)
			
	if direction == 'down':
	
		upper_bds=[]
		for idx in date_idxs:
			#start with the previous day to skip large delta
			close_init=df['Close'][idx+1]
			env_size=env_size_pct/100*close_init
			bd_upper=close_init+env_size
			bd_lower=close_init-env_size
			z=1
			while (df['Close'][idx+z] < bd_upper) & (df['Close'][idx+z] > bd_lower):
				z=z+1
				if idx+z < 2:
					print('no lower bound found')
					break
				# print(z)
			upper_bds.append(idx+z)

	# print(upper_bds)
	return upper_bds
	
def env_detector_revert(df,date_idxs,direction):
	#starting from the date of interest, look forward/backward in the listed direction
	#output index of date of breakout from envelope
	
	#####
	# Using a breakout detection envelope to set upper and lower bound
	#####
	'''
	1. determine max envelope size:
	store highest/lowest price
	move up to new date. Check if higher or lower price is detected
	look forward x number of days to see if there is a lower high or higher low.
	if yes, keep iterating, otherwise found max before breakout.
	
	2. get date where leaving of the envelope was detected
	for each envelope:
	return number of days in envelope
	return number of days before returning to the detected envelope, i.e.
	'''
	
	env_size_pct=8
	
	if direction == 'up':
	
		upper_bds=[]
		for idx in date_idxs:
			close_init=df['Close'][idx]
			env_size=env_size_pct/100*close_init
			bd_upper=close_init+env_size
			bd_lower=close_init-env_size
			z=0
			while (df['Close'][idx-z] < bd_upper) & (df['Close'][idx-z] > bd_lower):
				z=z+1
				if idx-z < 1:
					print('no upper bound found')
					break
				# print(z)
			upper_bds.append(idx-z)
			
	if direction == 'down':
	
		upper_bds=[]
		for idx in date_idxs:
			#start with the previous day to skip large delta
			close_init=df['Close'][idx+1]
			env_size=env_size_pct/100*close_init
			bd_upper=close_init+env_size
			bd_lower=close_init-env_size
			z=1
			while (df['Close'][idx+z] < bd_upper) & (df['Close'][idx+z] > bd_lower):
				z=z+1
				if idx+z < 2:
					print('no lower bound found')
					break
				# print(z)
			upper_bds.append(idx+z)

	# print(upper_bds)
	return upper_bds
	
	
def main():
	#####
	# input the file name and info here
	#####
	
	# Data location for mac:
	# path = '/Users/Marlowe/Marlowe/Securities_Trading/_Ideas/Data/'
	# in_file_name='Emini_Daily_1998_2018.csv'
	# in_file= os.path.join(path,in_file_name)
	
	# Data location for PC:
	path = 'C:\\Python\\transfer\\'
	in_file_name='FB.csv'
	# input the names of the fields if they are different from ['Date','Open','High','Low','Close'], use that order
	fields = ['Date','Open','High','Low','Close']
	in_file= os.path.join(path,in_file_name)
	
	# add a header to the file if no header exists
	#add_header(in_file)
	
	#use csv module to pull out proper data
	#file_noblanks=remove_blanks(in_file)
	
	# create dataframe from the data
	#headers=file_noblanks[0]
	df=import_data(in_file,fields)
	
	
	#####
	# input the date range of interest
	#####
	# start_date='2017-01-04'
	# start_date='2018-06-04'
	start_date='2018-01-02'
	# end_date='2018-08-31'
	end_date='2018-10-01'
	
	#generate price data for plotting
	# date_list,close_list=list_gen(df,start_date,end_date,fields)
	# print(df.head())
	# print(df.tail())
	
	#create new dataframe with new range
	
	df_2,idxl,idxh=slice_df(df,start_date,end_date)
	# print(idxh,idxl)
	# print(df['Date'][20:75])
	# return

	#add true range column and column for 10 day atr
	# num_day_av=10
	# df=true_range_calc(df,idxl,idxh,num_day_av)
	# ~ print(df.head(5))
	# ~ print(df.tail(15))
	
	# idxh=idxh-num_day_av
	# ~ return
	
	
	#####
	# detect the dates of interest
	#####
	
	# Find dates with a large price delta form yesterdays close to todays high/low
	# This designates jumps from a significant news event or earnings release
	
	# set daily percent change
	pct_delta=float(10.0)
	
	idx_locs=[]
	for idx in range(idxl,idxh-1):
		cur_high=float(df['High'][idx])
		cur_low=float(df['Low'][idx])
		yest_close=float(df['Close'][idx+1])
		# print('test idx: '+str(idx)+' date: '+df['Date'][idx]+' yest close: '+str(yest_close))
		
		delta_h=100.*abs(cur_high-yest_close)/yest_close
		delta_l=100.*abs(yest_close-cur_low)/yest_close
		# print('delta_h: '+str(delta_h)+' delta_l: '+str(delta_l))
		# print()
		if delta_h > pct_delta or delta_l > pct_delta:
			idx_locs.append(idx)
	
	
	
	
	
	# want to include some filter to look at x number of days before a large change to
	# determine that there was a consolidation/price agreement before the change happened
	# i.e. it was a significant event that caused the price change
	
	
	
	# Want to include some filter that looks at significant changes over a several day period
	# rather than just a single day. This could include data that is part of a trend movement.
	# need to filter out based on price agreement before the several day price delta.
	
	
	
	
	# print(idx_locs)
	# print(idxl,idxh)
	# print(df['Date'][46])
	# print(df['Close'][47])
	# print(df['Close'][46])
	# print(df['Close'][45])
	# return
	# gen_plot_pc(df,idxl,idxh,fields,idx_locs)
	# gen_plot_mac(df,idxl,idxh,fields)
	
	
	#####
	# Using the indexes from the large deltas, and a pre-determined envelope size,
	# work forwards in date to find how long the price remains within that envelope
	#####
	
	# use env_detector_simple to find breakouts based on simple percent bounds
	# up/down sets direction to look in moving days
	upper_bds=env_detector_simple(df,idx_locs,'down')
	
	gen_plot_pc(df,idxl,idxh,fields,idx_locs,upper_bds)
	return
	
	
	# print(upper_bds)
	# gen_plot_pc(df,idxl,idxh,fields,idx_locs,upper_bds)
	# return

	#####
	# Determine statistics about the indexes and upper bounds
	# -How long on average does the consolidation last?
	# -How often is there a false breakout?
	# -Once the breakout occurs, how quickly does price move away?
	# -How often is the peak price movement on the day of the large move?
	#####
	
	
	
	
	# ~ print(len(slopes))
	# ~ print(len(date_list))
	
	# ~ gen_plot(df,3,100)
	# ~ plot_price_df(df,end_date_idx,start_date_idx)
	
	# ~ plot_price_list(date_list,close_list)
	# ~ plot_price_list(date_list,close_filt)
	# ~ plot_price_list_2(date_list,close_filt,close_list)
	# ~ plot_price_list_2axes(date_list,close_filt,slopes)
	
	
	
	
	
main()
