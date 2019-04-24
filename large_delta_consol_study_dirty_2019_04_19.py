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

pandas version: 0.18.1
matplotlib version: 2.0.0
mpl_finance version: 0.10.0
numpy version: 1.10.1
scipy version: 0.16.0

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
	# ~ ax.xaxis.set_major_locator(ticker.MaxNLocator(num_ticks))
	# ~ ax.xaxis.set_major_formatter(ticker.FuncFormatter(date))
	fig.autofmt_xdate()
	fig.tight_layout()
	ax.set_ylabel('Price')
	ax.set_xlabel('Date/Time')
	ax.set_xlim(-1.0,len(open_day)-1.0)
	# ~ ax.xaxis.set_major_locator(ticker.MaxNLocator(num_ticks))
	# ~ ax.xaxis.set_major_formatter(ticker.FuncFormatter(date))
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
	
def large_delta_detect(df,index_l,index_h,pct_delta):
	
	index_locations=[]
	for idx in range(index_l,index_h-1):
		cur_high=float(df['High'][idx])
		cur_low=float(df['Low'][idx])
		yest_close=float(df['Close'][idx+1])
		# print('test idx: '+str(idx)+' date: '+df['Date'][idx]+' yest close: '+str(yest_close))
		
		delta_h=100.*abs(cur_high-yest_close)/yest_close
		delta_l=100.*abs(yest_close-cur_low)/yest_close
		# print('delta_h: '+str(delta_h)+' delta_l: '+str(delta_l))
		# print()
		if delta_h > pct_delta or delta_l > pct_delta:
			index_locations.append(idx)
			
	return index_locations
	
def env_detector_revert(df,date_idxs,direction):
	#starting from the date of interest, look forward/backward in the listed direction
	#output index of date of breakout from envelope
	
	#####
	# Using a breakout detection envelope to set upper and lower bound
	#####
	'''
	determine max envelope size:
	store highest/lowest price. Use open/close, not high or low
	
	Use range for the first 5 days after large move to set initial range for envelope
	
	1. Move up to new date.
	2. Check for breakout (see below).
	3. If no breakout detected, check for new high/low bounds, and reset limits.
		Iterate to next date
	4. If yes breakout detected, set date as last date in envelope. Finish loop.
	
	
	
	
	-Check for breakout:
	look forward x number of days to see if there is a lower high or higher low than current bounds.
	if yes, keep iterating, otherwise the current bound is max/min before breakout.
	Basically want to test all the way up until the end of the consolidation and look out from that point
	x number of days to verify that the price has not moved back into the consolidation range.
	
	
	
	
	
	for each envelope:
	return number of days in envelope
	return number of days before returning to the detected envelope, i.e.
	'''
	
	# Set the number of days to look foward/backward for new high/low
	# this tells you how many days you need to move away from your current bounds
	# to consider it a breakout
	num_days=20
	
	if direction == 'up':
	
		upper_bds=[]
		# This for loop iterates through the date_idxs list which is the index values of the
		# dates that have a large delta.
		for idx in date_idxs:
			
			##########
			# for the initial bounds, use the first five days highest/lowest open/close
			# all bounds after the initial day will be based on open and close values
			# This variable, how many days to use for initial bounds is impactful
			##########
			high_init=0
			low_init=1000*df['Close'][idx]
			for h in range(5):
				
				close_init=df['Close'][idx-h]
				open_init=df['Open'][idx-h]
				# ~ print('h is '+str(h)+', close_init='+str(close_init)+', open_init='+str(open_init))
				# ~ high_init=df['High'][idx]
				# ~ low_init=df['Low'][idx]
				max_init=max(open_init,close_init)
				min_init=min(open_init,close_init)
				# ~ print('max_init='+str(max_init)+', min_init='+str(min_init)+', low_init='+str(low_init)+', high_init='+str(high_init))
				if max_init > high_init:
					high_init=max_init
				if min_init < low_init:
					low_init=min_init
			# print('index: '+str(idx))
			# print('close_init: '+str(close_init))
			# print('high_init: '+str(high_init))
			# print('low_init: '+str(low_init))
			
			
			bd_upper=high_init
			bd_lower=low_init
			
			# check for lower bound. If there is a higher low than the current lower bound in the next x num days,
			# keep iterating
			bound_break=False
			final_day_test=4
			last_day=False
			i=0
			x=0
			while (bound_break==False) & (last_day==False):
			# ~ while (bound_break==False) & (idx-i-x>105):
				
				# 2. iterate through next x (num_days) to find higher low or lower high
				# x is representing the days counting outward. Each time you do not find a day in the range
				# x should increment.
				# i is representing how many days you have gone up in your search.
				# Once you do find a day in the range, i should increment and x should start over
				for x in range(num_days):
					# ~ print('')
					# ~ print('index: '+str(idx-i-x)+', x: '+str(x)+', i: '+str(i))
					# ~ print('current max bound: '+str(bd_upper)+', current min bound: '+str(bd_lower))
					low=df['Low'][idx-i-x]
					high=df['High'][idx-i-x]
					curr_open=df['Open'][idx-i-x]
					curr_close=df['Close'][idx-i-x]
					curr_max=max(curr_open,curr_close)
					curr_min=min(curr_open,curr_close)
					# ~ print('current high '+str(high)+', current low '+str(low))
					# ~ print('current open '+str(curr_open)+', current close '+str(curr_close))
					
					
					# 3.if any day in next x num days is found to be in the range,
					# increment i and start over with new x
					# we define "in the range" as having both days open and days close within bounds
					
					if (curr_open > bd_lower) & (curr_open < bd_upper) & (curr_close > bd_lower) & (curr_close < bd_upper):
						# print('step to next day to iterate from')
						# when moving to a new day to start iterating x from, check to see if the current day
						# has a higher/lower open/close to reset the bounds
						# This should only happen if we have looked forward x number of days
						# and found something in the current range
						next_open=df['Open'][idx-i]
						next_close=df['Close'][idx-i]
						next_max=max(next_open,next_close)
						next_min=min(next_open,next_close)
						if next_max > bd_upper:
							bd_upper=next_max
							# ~ print('set new bound upper')
						if next_min < bd_lower:
							bd_lower=next_min
							# ~ print('set new bound lower')
						i=i+1
						break
					
					# 4.if no day in next x num days is found to be in the range (i.e. x reaches max(x)),
					# set current day as last date before breakout
					if x==(num_days-1):
						# ~ print('')
						# ~ print('reached max num days, we have a breakout')
						upper_bds.append(idx-i+1)
						bound_break=True
						break
						
					# if you hit the last date and have not found a breakout
					# just input the index of the original price move to be the breakout point.
					# these values will be disregarded in a later function
					if (idx-x-i) < final_day_test:
						# ~ print('')
						# ~ print('hit last day with no breakout, '+str(final_day_test)+' days from final day')
						last_day=True
						upper_bds.append(idx)
						break
	
	
	

	
	'''
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
	'''
	return upper_bds
	
def mid_idx_prefilter(start_indexes,end_indexes):
	#this function finds pairs of indexes where both the start and end index
	#are inside of another start/end index, and removes them from the list.
	
	start_indexes.reverse()
	end_indexes.reverse()
	
	start_indexes_filt=[]
	end_indexes_filt=[]
	
	#check the next index to make sure it is at a position that is greater than the current index
	#if so pass the pair, if not ignore them.
	end_index_store=end_indexes[0]
	
	for x in range(len(end_indexes)):
		if end_indexes[x] <= end_index_store:
			start_indexes_filt.append(start_indexes[x])
			end_indexes_filt.append(end_indexes[x])
			end_index_store=end_indexes[x]
	
	start_indexes_filt.reverse()
	end_indexes_filt.reverse()
	
	return start_indexes_filt,end_indexes_filt
	
	
def mid_idx_filter(start_indexes,end_indexes):
	# this function will cycle through the start and end indexes. If it finds
	# a start index that shares an end index with a previous start index, it will
	# remove those pairs. The input indexes are lists.
	
	# ~ print('start_indexes length is : '+str(len(start_indexes)))
	# ~ print('end_indexes length is : '+str(len(end_indexes)))
	# ~ print(end_indexes[2])
	# ~ return
	
	start_indexes.reverse()
	end_indexes.sort()
	end_indexes.reverse()
	start_indexes_filt=[]
	end_indexes_filt=[]
	# if there is only one index in the list and the start/end are the same, ignore both
	# otherwise pass them through
	if len(start_indexes)==1:
		# ~ print('adjust for only one index')
		if end_indexes[0]==start_indexes[0]:
			start_indexes_filt.append(start_indexes[0])
			#dont append to end_indexes_filt in order to remove the data
		else:
			start_indexes_filt.append(start_indexes[0])
			end_indexes_filt.append(end_indexes[0])
			
			
	# if there are only two indexes, check for a start/end matching pair, and ignore
	# or pass accordingly
	elif len(start_indexes)==2:
		# ~ print('adjust for only two indexes')
		
		#check to see if two starts have the same end. If so, ignore the middle starting point
		if end_indexes[0]==end_indexes[1]:
			start_indexes_filt.append(start_indexes[0])
			#dont append to end_indexes_filt in order to remove the data
		elif end_indexes[0]!=end_indexes[1]:
			start_indexes_filt.append(start_indexes[0])
			end_indexes_filt.append(end_indexes[0])
		
		# if the last two are matching, this means you hit the end of the df, ignore the end index
		if end_indexes[1]==start_indexes[1]:
			start_indexes_filt.append(start_indexes[1])
			#dont append to end_indexes_filt in order to remove the data
		elif end_indexes[1]!=start_indexes[1]:
			start_indexes_filt.append(start_indexes[1])
			end_indexes_filt.append(end_indexes[1])
			
	elif len(start_indexes)==3:
		# ~ print('adjust for only three indexes')
		match1=0
		match2=0
		#check to see if two starts have the same end. If so, ignore the middle starting point
		if end_indexes[0]==end_indexes[1]:
			# ~ start_indexes_filt.append(start_indexes[0])
			match1=1
			# ~ print('match1 positive')
			# ~ skip_line=0
			#dont append to end_indexes_filt in order to remove the data
			#append to start_indexes_filt because it will always be in the data
		elif end_indexes[0]!=end_indexes[1]:
			# ~ start_indexes_filt.append(start_indexes[0])
			end_indexes_filt.append(end_indexes[0])
			
		if end_indexes[1]==end_indexes[2]:
			# ~ start_indexes_filt.append(start_indexes[1])
			match2=1
			# ~ print('match2 positive')
			# ~ skip_line=0
			#dont append to end_indexes_filt in order to remove the data
			#dont append to start_indexes_filt in order to remove the data if they are equal
		elif end_indexes[1]!=end_indexes[2]:
			#if they are not equal, need to add the previous start index
			# ~ start_indexes_filt.append(start_indexes[1])
			end_indexes_filt.append(end_indexes[1])
		
		# ~ print('match1: '+str(match1)+', match2: '+str(match2))
		
		if match1==1 and match2==1:
			# ~ print('first if')
			#if end_index1=endindex2=endindex3 just put the first start index
			start_indexes_filt.append(start_indexes[0])
		elif match1==0 and match2==1:
			# ~ print('second if')
			#if end_index2=endindex3 but not endindex1, add first and second but not third
			start_indexes_filt.append(start_indexes[0])
			start_indexes_filt.append(start_indexes[1])
		elif match1==1 and match2==0:
			# ~ print('third if')
			#if end_index1=endindex2 but not endindex3, add first and third but not second
			start_indexes_filt.append(start_indexes[0])
			start_indexes_filt.append(start_indexes[2])
			
			
			
		# if the last two are matching, this means you hit the end of the df, ignore the end index
		if end_indexes[2]==start_indexes[2]:
			skip=0
			# ~ start_indexes_filt.append(start_indexes[2])
			#dont append to end_indexes_filt in order to remove the data
		elif end_indexes[2]!=start_indexes[2]:
			# ~ start_indexes_filt.append(start_indexes[2])
			end_indexes_filt.append(end_indexes[2])

	elif len(start_indexes)>3:
		# ~ print('filtering on > 3 indexes')
		# ~ print('')
		
		#if all of the end_indexes are the same, just add the first start index
		#and one end index and get out of this elif.
		samesies=1
		for q in range(len(end_indexes)-1):
			if end_indexes[q]!=end_indexes[q+1]:
				samesies=0
		if samesies==1:
			start_indexes_filt.append(start_indexes[0])
			end_indexes_filt.append(end_indexes[0])
			# ~ print('outta this loop')
			return start_indexes_filt,end_indexes_filt
		
		#want to add logic for first two start/end pairs
		#should only add both if they are outside of interactions with others
		if end_indexes[0]>start_indexes[1]:
			start_indexes_filt.append(start_indexes[0])
			end_indexes_filt.append(end_indexes[0])
		# ~ else:
			
		# ~ end_indexes_filt.append(end_indexes[1])
		
		matching_idx=False
		if end_indexes[0]==end_indexes[1]:
			matching_idx=1
		for x in range(1,len(start_indexes)-1):
			# ~ print('x='+str(x)+', matchingidx= '+str(matching_idx))
			# ~ print('start_filt='+str(start_indexes_filt)+', end_filt='+str(end_indexes_filt))
			# ~ print('start_indexes['+str(x)+']='+str(start_indexes[x])+', start_indexes['+str(x+1)+']='+str(start_indexes[x+1]))
			# ~ print('end_indexes['+str(x)+']='+str(end_indexes[x])+', end_indexes['+str(x+1)+']='+str(end_indexes[x+1]))
			
			# ~ print('end_indexes['+str(x)+']='+str(end_indexes[x]))
			# ~ print('end_indexes['+str(x+1)+']='+str(end_indexes[x+1]))
			
			#if the current start and end match, ignore the end index, add the start index
			#this will happen if you reach the end of the data and do not find a breakout.
			if end_indexes[x]==start_indexes[x]:
				start_indexes_filt.append(start_indexes[x])
			
			
			#if the current and next end_indexes match, attach both the start and end index if there is not
			# a previous match on the end index
			#need to add a way to filter out subsequent matching end_indexes
			if end_indexes[x]==end_indexes[x+1]:
				if matching_idx==False:
					start_indexes_filt.append(start_indexes[x])
					end_indexes_filt.append(end_indexes[x])
					matching_idx=True
				# ~ if matching_idx=1:
					# ~ matching_idx=0
			#if the end indexes dont match, do logic to add start/end index values to filtered lists
			elif end_indexes[x]!=end_indexes[x+1]:
				#if normal conditions, add both the start and end indexes
				if matching_idx==False:
					start_indexes_filt.append(start_indexes[x])
					end_indexes_filt.append(end_indexes[x])
					# ~ matching_idx=0
				#if the previous end indexes matched the current one, dont add either
				elif matching_idx==True:
					# ~ end_indexes_filt.append(end_indexes[x])
					matching_idx=False
				
				
			
		#look up the last start index and if it is matching the last end index,add the start index
		# if not matching, add both
		j=len(start_indexes)-1
		if end_indexes[j]==start_indexes[j]:
			start_indexes_filt.append(start_indexes[j])
		else:
			start_indexes_filt.append(start_indexes[j])
			end_indexes_filt.append(end_indexes[j])
	
	
	start_indexes_filt.reverse()
	end_indexes_filt.reverse()
	return start_indexes_filt,end_indexes_filt
	
	
def main():
	#####
	# input the file name and info here
	#####
	
	# Data location for mac:
	# path = '/Users/Marlowe/Marlowe/Securities_Trading/_Ideas/Data/'
	path = '/Users/Marlowe/gitsite/transfer/'
	# in_file_name='Emini_Daily_1998_2018.csv'
	# in_file= os.path.join(path,in_file_name)
	
	# Data location for PC:
	# ~ path = 'C:\\Python\\transfer\\'
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
	# ~ start_date='2012-07-03'
	# ~ start_date='2014-01-03'
	start_date='2015-01-05'
	# ~ start_date='2017-01-04'
	# ~ start_date='2018-06-04'
	# ~ start_date='2018-01-02'
	
	
	# ~ end_date='2013-01-03'
	# ~ end_date='2014-01-03'
	# ~ end_date='2016-06-01'
	# ~ end_date='2017-01-03'
	# ~ end_date='2018-08-31'
	end_date='2018-10-01'
	
	
	#generate price data for plotting
	# date_list,close_list=list_gen(df,start_date,end_date,fields)
	# print(df.head())
	# print(df.tail())
	
	#create new dataframe with new range
	
	df_2,idxl,idxh=slice_df(df,start_date,end_date)
	# ~ print(idxh,idxl)
	# print(df['Date'][20:75])
	
	# plot using dataframe, start date, end date
	
	# ~ gen_plot_mac(df,idxl,idxh,fields)
	# ~ return

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
	
	# set days percent change
	
	pct_delta=float(8.0)
	
	idx_locs=large_delta_detect(df,idxl,idxh,pct_delta)
	
	# ~ print(idx_locs)
	# ~ return
	
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
	#upper_bds=env_detector_simple(df,idx_locs,'down')
	
	
	# use env_detector_revert to find breakouts based on creating bounds by look forward method
	# up/down sets direction to look in moving days
	# 04-15-19: consider putting a minimum on number of days in an envelope. Maybe 5-10 days
	
	# ~ idx_locs=[46,109,200,300,320]
	# ~ idx_locs=[46,109,136]
	# ~ idx_locs=[1306,1427,1472,1510,1555]
	# ~ upper_bds=[1286,1350,1460,1446,1446]
	upper_bds=env_detector_revert(df,idx_locs,'up')
	# ~ print('start index locations: '+str(idx_locs))
	# ~ print('end index locations: '+str(upper_bds))
	# ~ return
	
	# compare the start index locations and end index locations. if two start index locations
	# share the same end index location, remove the middle start index.
	idx_locs_filt1,upper_bds_filt1=mid_idx_prefilter(idx_locs,upper_bds)
	# ~ print('')
	# ~ print('start index locations: '+str(idx_locs_filt1))
	# ~ print('end index locations: '+str(upper_bds_filt1))
	# ~ print('')
	idx_locs_filt,upper_bds_filt=mid_idx_filter(idx_locs_filt1,upper_bds_filt1)
	
	# ~ print('')
	# ~ print('start index locations: '+str(idx_locs_filt))
	# ~ print('end index locations: '+str(upper_bds_filt))
	# ~ return
	# ~ upper_bds=[109]
	
	gen_plot_pc(df,idxl,idxh,fields,idx_locs,upper_bds)
	gen_plot_pc(df,idxl,idxh,fields,idx_locs_filt,upper_bds_filt)
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
	
	# compare the idx_locs and idx_locs_filt to see strength of breakouts. If multiple
	# large delta price moves all correspond to the same breakout point, that breakout
	# point has a higher weight
	
	
	# when a breakout is detected, how much does it move in either direction away from the initial breakout point?
	# how long does it take to find the top/bottom of the range?
	# how often is the top/bottom of the range found in the first couple days?
	# on consolidations where the top/bottom is found in the first couple days, how strongly does it get held?
	# how many times is a top/bottom tested before a breakout occurs? (within a few percent of the top/bottom?
	# how many times is a new high/low for the range found, and in what quartile of the consolidation does
	# that generally occur?
	
	# if the price drops by XX ammt within XX days after large delta, this usually happens.
	# if it drops by even more, then other things happen?
	
	
	
	# ~ print(len(slopes))
	# ~ print(len(date_list))
	
	# ~ gen_plot(df,3,100)
	# ~ plot_price_df(df,end_date_idx,start_date_idx)
	
	# ~ plot_price_list(date_list,close_list)
	# ~ plot_price_list(date_list,close_filt)
	# ~ plot_price_list_2(date_list,close_filt,close_list)
	# ~ plot_price_list_2axes(date_list,close_filt,slopes)
	
	
	
	
	
main()
