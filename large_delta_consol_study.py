'''
This script finds consolidation patterns in OHLC price data
This works by finding the dates where a large delta hapened.
next an envelope filter is used starting at that date to determine
the number of days where the consolidation happend.

1. find dates with ATR above x%
2. work forward from those points to find upper bounds using envelope


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
def import_data(file_name):
	#only add date, open, high, low, last to dataframe
	fields = ['Date','Open','High','Low','Last']
	
	#open the file using pandas, use the first row as the header
	data = pd.read_csv(file_name,header=0,usecols=fields)
	
	# ~ print(data.head(5))
	
	return data
	
	
def gen_plot(dataframe,startidx,endidx):
	#####
	# plot just price
	#####
	endidx=endidx+1
	#dataframe is a pandas dataframe with open, high, low, close for each date
	
	open_day=dataframe['Open'][startidx:endidx].tolist()
	high=dataframe['High'][startidx:endidx].tolist()
	low=dataframe['Low'][startidx:endidx].tolist()
	close=dataframe['Last'][startidx:endidx].tolist()
	date=dataframe['Date'][startidx:endidx].tolist()
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
	candlestick2_ochl(ax,open_day,close,high,low,width=0.5,colorup='b',colordown='r',alpha=0.75)
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
	
	
	
	
def list_gen(df,start_date,end_date):
	#generate a list of dates (x axis) and values (y axis) for given inputs
	
	start_day_df=df.loc[df['Date'] == start_date]
	end_day_df=df.loc[df['Date'] == end_date]
	# end_date_idx is an int
	startidx=end_day_df.index[0].tolist()
	endidx=start_day_df.index[0].tolist()
	
	
	date=df['Date'][startidx:endidx].tolist()
	close=df['Last'][startidx:endidx].tolist()
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
	
	return df[startidx:endidx],startidx,endidx
	
	
def main():
	#####
	# input the file name and info here
	#####
	
	# Data location for mac:
	path = '/Users/Marlowe/Marlowe/Securities_Trading/_Ideas/Data/'
	
	in_file_name='Emini_Daily_1998_2018.csv'
	
	in_file= os.path.join(path,in_file_name)
	
	# add a header to the file if no header exists
	#add_header(in_file)
	
	#use csv module to pull out proper data
	#file_noblanks=remove_blanks(in_file)
	
	# create dataframe from the data
	#headers=file_noblanks[0]
	df=import_data(in_file)
	
	
	#####
	# input the date range of interest
	#####
	start_date='2018-06-28'
	end_date='2018-08-31'
	
	#generate price data for plotting
	date_list,close_list=list_gen(df,start_date,end_date)
	
	#create new dataframe with new range
	
	df,idxl,idxh=slice_df(df,start_date,end_date)
	
	
	#add true range column and column for 10 day atr
	num_day_av=10
	df=true_range_calc(df,idxl,idxh,num_day_av)
	# ~ print(df.head(5))
	# ~ print(df.tail(15))
	
	idxh=idxh-num_day_av
	# ~ return
	
	
	#####
	# detect the dates with a large true range delta
	#####
	
	#try a daily delta of true range of >50%, how many?
	cutoff=float(50.0)
	idx_locs=[]
	for idx in range(idxl,idxh-2):
		cur_tr=float(df['true_range'][idx])
		prev_tr=float(df['true_range'][idx+1])
		## ~ print('current '+str(cur_tr))
		## ~ print('prev '+str(prev_tr))
		
		delta=100.*abs(cur_tr-prev_tr)/prev_tr
		## ~ print(delta)
		if delta > cutoff:
			idx_locs.append(idx)
			
	
	#try a delta from atr >50%, how many incidents?
	cutoff=float(50.0)
	idx_locs=[]
	for idx in range(idxl,idxh-1):
		cur_tr=float(df['true_range'][idx])
		atr=float(df['ATR'][idx])
		
		delta=100.*abs(cur_tr-atr)/atr
		# ~ print(delta)
		if delta > cutoff:
			idx_locs.append(idx)
	
	
	#try a price delta form yesterdays close to todays high
	#>10%. I think we want to use this method for jumps in indiv equities
	cutoff=float(1.0)
	idx_locs=[]
	for idx in range(idxl,idxh-1):
		cur_high=float(df['High'][idx])
		yest_close=float(df['Last'][idx+1])
		
		delta=100.*abs(cur_high-yest_close)/yest_close
		# ~ print(delta)
		if delta > cutoff:
			idx_locs.append(idx)
			
	
	# ~ print(idx_locs)
	# ~ print(len(idx_locs))
	
	
	#####
	# Using the indexes from the large deltas, and a pre-determined envelope size,
	# work forwards in date to find how long the price remains within that envelope
	#####
	env_size=30
	
	# ~ print('')
	# ~ print('envelope detection')
	# ~ print('zero crossing indexes: '+str(z_c))
	# ~ print('closing price at idx 27: '+str(close_list[27]))
	# ~ print('upper envelope: '+str(close_list[27]+env_size))
	# ~ print('lower envelope: '+str(close_list[27]-env_size))
	
	# ~ u=0
	# ~ for item in close_list[10:50]:
		# ~ print('close at idx: '+str(u+10)+' is '+str(item))
		# ~ u=u+1
	
	# ~ print('lower bound idx is 22, upper bound idx is 36')
	# ~ print('closing price at idx 22: '+str(close_list[22]))
	# ~ print('closing price at idx 36: '+str(close_list[36]))
	
	
	# create dictionary for each index. syntax will be:
	# {index:[lower bound,upper bound],index:[lower bound, upper bound]}
	bounds={}
	for idx in idx_locs:
		bounds[idx]=[]
		
	# ~ print(bounds)
	# ~ return
	
	for idx in idx_locs:
		#find lower bounds
		# ~ y=0
		# ~ while (close_list[idx-y] < close_list[idx]+env_size) & (close_list[idx-y] > close_list[idx]-env_size):
			# ~ y=y+1
		# ~ lwr_idx=idx-y
		# ~ bounds[idx].append(lwr_idx)
		
		#find upper bounds, moving forwards in date with historical data
		#in this case lower bounds is the date where significant price move happened
		# ~ print('idx under test: '+str(idx))
		z=0
		#####
		# need to use the df data rather than close list 3/22/19
		#####
		while (df['Last'][idx-z] < df['Last'][idx]+env_size) & (df['Last'][idx-z] > df['Last'][idx]-env_size):
			z=z+1
			# ~ print(z)
		upper_idx=idx-z
		bounds[idx].append(upper_idx)
		# ~ bounds[idx].append(0)
	
	print(df['Date'][upper_idx])
	return
	
	# ~ print(len(slopes))
	# ~ print(len(date_list))
	
	# ~ gen_plot(df,3,100)
	# ~ plot_price_df(df,end_date_idx,start_date_idx)
	
	# ~ plot_price_list(date_list,close_list)
	# ~ plot_price_list(date_list,close_filt)
	# ~ plot_price_list_2(date_list,close_filt,close_list)
	# ~ plot_price_list_2axes(date_list,close_filt,slopes)
	
	#shift indexes to absolute zero
	#subtract idxh from index
	
	
	num_ticks=6
	fig = plt.figure()
	ax1 = fig.add_subplot(111)
	
	#draw vertical lines at bounds
	for key,value in bounds.items():
		plt.axvline(x=df['Date'][key], color='g', linestyle='--')
		plt.axvline(x=df['Date'][value[0]], color='k', linestyle='--')
		# ~ print(type(key))
		# ~ print(type(value[0]))
		# ~ for item in key:
			# ~ print('key: '+str(item))
			# ~ plt.axvline(x=item-idxh, color='g', linestyle='--')
		# ~ for item in value:
			# ~ print('value: '+str(item))
			# ~ plt.axvline(x=item-idxh, color='k', linestyle='--')
	ax1.xaxis.set_major_locator(ticker.MaxNLocator(num_ticks))
	ax1.plot(date_list, close_list, color='k', label='price')
	# ~ ax1.plot(date_list, close_filt, color='g')
	
	plt.show()
	
	
main()
