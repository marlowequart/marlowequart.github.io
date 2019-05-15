'''
This script finds consolidation patterns in OHLC price data
This works by finding the dates where a large delta hapened.
next an envelope filter is used starting at that date to determine
the number of days where the consolidation happend.

When generating statistics of interest, want to consider the single issue, the sector and
the overall market

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
	
	
	
def plot_hist(a_list):
	#this funciton will plot a histogram to bring out the data in the tails
	#the limit val will limit the top of the bars in order to bring out the tail values
	
	#create bins of data
	n_bins=20
	max_data=max(a_list)
	min_data=min(a_list)
	dx=(max_data-min_data)/n_bins
	xs = np.arange(min_data,max_data+dx,dx).round(decimals=1)
	
	#####
	#Plot a histogram of the normalized (%) number of values in each range
	#####
	df=pd.DataFrame(a_list)
	# ~ out=pd.cut(df[0],bins=xs,include_lowest=True)
	# ~ out_norm = out.value_counts(sort=False, normalize=True).mul(100)
	# ~ ax=out_norm.plot.bar(color="b")
	# ~ plt.show()
	
	#####
	#Plot a histogram with the frequency of values in each range
	#####
	out, bins  = pd.cut(df[0], bins=xs, include_lowest=True, right=False, retbins=True)
	ax=out.value_counts(sort=False).plot.bar()
	plt.show()
	
	#####
	#print the frequency for each interval, mean, std deviation
	#####
	# ~ print(out.value_counts(sort=False))
	# ~ print('The mean is '+str(round(np.mean(a_list),4)))
	# ~ print('The std dev is '+str(round(np.std(a_list),4)))
	
	
	
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
		
		delta_h=100.*abs(cur_high-yest_close)/yest_close
		delta_l=100.*abs(yest_close-cur_low)/yest_close
		
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
					# print('')
					# print('index: '+str(idx-i-x)+', x: '+str(x)+', i: '+str(i)+', idx: '+str(idx))
					# print('current max bound: '+str(bd_upper)+', current min bound: '+str(bd_lower))
					low=df['Low'][idx-i-x]
					high=df['High'][idx-i-x]
					curr_open=df['Open'][idx-i-x]
					curr_close=df['Close'][idx-i-x]
					curr_max=max(curr_open,curr_close)
					curr_min=min(curr_open,curr_close)
					# ~ print('current high '+str(high)+', current low '+str(low))
					# ~ print('current open '+str(curr_open)+', current close '+str(curr_close))
					
					
					# if you hit the last date and have not found a breakout
					# just input the index of the original price move to be the breakout point.
					# these values will be disregarded in a later function
					# print('check last day')
					if (idx-i-x) < final_day_test:
						# print('')
						# print('hit last day with no breakout, '+str(final_day_test)+' days from final day')
						last_day=True
						upper_bds.append(idx)
						break
					
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
						
					
	
	'''
	if direction == 'down':
	
	04/19/19-need to complete this section to match the above section if we desire to look
	in the reverse direction.
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
	
	# now filter out the pairs that have less than 5 days in the consolidation
	start_indexes_filt_1=[]
	end_indexes_filt_1=[]
	for x in range(len(end_indexes_filt)):
		if (start_indexes_filt[x]-end_indexes_filt[x])>5:
			start_indexes_filt_1.append(start_indexes_filt[x])
			end_indexes_filt_1.append(end_indexes_filt[x])
	
	start_indexes_filt_1.reverse()
	end_indexes_filt_1.reverse()
	
	return start_indexes_filt_1,end_indexes_filt_1
	
	
def mid_idx_filter(start_indexes,end_indexes):
	# this function will cycle through the start and end indexes. If it finds
	# a start index that shares an end index with a previous start index, it will
	# remove those pairs. The input indexes are lists.
	
	
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
			match1=1
			# ~ print('match1 positive')
			
			#dont append to end_indexes_filt in order to remove the data
			#append to start_indexes_filt because it will always be in the data
		elif end_indexes[0]!=end_indexes[1]:
			end_indexes_filt.append(end_indexes[0])
			
		if end_indexes[1]==end_indexes[2]:
			match2=1
			# ~ print('match2 positive')
			
			#dont append to end_indexes_filt in order to remove the data
			#dont append to start_indexes_filt in order to remove the data if they are equal
		elif end_indexes[1]!=end_indexes[2]:
			#if they are not equal, need to add the previous start index
			end_indexes_filt.append(end_indexes[1])
		
		
		if match1==1 and match2==1:
			#if end_index1=endindex2=endindex3 just put the first start index
			start_indexes_filt.append(start_indexes[0])
		elif match1==0 and match2==1:
			#if end_index2=endindex3 but not endindex1, add first and second but not third
			start_indexes_filt.append(start_indexes[0])
			start_indexes_filt.append(start_indexes[1])
		elif match1==1 and match2==0:
			#if end_index1=endindex2 but not endindex3, add first and third but not second
			start_indexes_filt.append(start_indexes[0])
			start_indexes_filt.append(start_indexes[2])
			
			
		# if the last two are matching, this means you hit the end of the df, ignore the end index
		if end_indexes[2]==start_indexes[2]:
			skip=0
			#dont append to end_indexes_filt in order to remove the data
		elif end_indexes[2]!=start_indexes[2]:
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
		
		matching_idx=False
		if end_indexes[0]==end_indexes[1]:
			matching_idx=True
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
	
def get_idxs(df,start_date,end_date,adj_dates,lens):
	#this function will get the start and end indexes for the consolidation points from a
	#series of dates and a data set.
	# The output of this function is two lists of indexes which represent the start
	# and end indexes of the consolidation periods.
	
	
	fields = ['Date','Open','High','Low','Close']
	
	#get the low and high index of the dataframe based on the start and end dates
	index_list=df.index.values.tolist()
	
	if adj_dates:
		idxl=0
		idxh=index_list[-1]
	else:
		df_2,idxl,idxh=slice_df(df,start_date,end_date)
	
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
	
	pct_delta=float(10.0)
	
	idx_locs=large_delta_detect(df,idxl,idxh,pct_delta)
	# print(idx_locs)
	# return
	
	# if multiple dfs merged, remove the idx_locs that correspond with the start
	# of the merges
	for num in lens:
		if num-1 in idx_locs:
			idx_locs.remove(num-1)
	
	# print(idx_locs)
	# return
	
	# want to include some filter to look at x number of days before a large change to
	# determine that there was a consolidation/price agreement before the change happened
	# i.e. it was a significant event that caused the price change
	
	# Want to include some filter that looks at significant changes over a several day period
	# rather than just a single day. This could include data that is part of a trend movement.
	# need to filter out based on price agreement before the several day price delta.
	
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
	
	
	upper_bds=env_detector_revert(df,idx_locs,'up')
	# print('start index locations: '+str(idx_locs))
	# print('end index locations: '+str(upper_bds))
	# return
	
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
	
	# Here we can generate two plots to compare the difference between the filtered and
	# non filtered index locations
	
	# gen_plot_pc(df,idxl,idxh,fields,idx_locs,upper_bds)
	gen_plot_pc(df,idxl,idxh,fields,idx_locs_filt,upper_bds_filt)
	# ~ return
	
	return idx_locs_filt,upper_bds_filt
	
	
	
	
	
def main():
	#####
	# input main info here
	#####
	
	# Data location for mac:
	# path = '/Users/Marlowe/Marlowe/Securities_Trading/_Ideas/Data/'
	# path = '/Users/Marlowe/gitsite/transfer/'
	
	# Data location for PC:
	path = 'C:\\Python\\transfer\\'
	
	# input the names of the fields if they are different from ['Date','Open','High','Low','Close'], use that order
	fields = ['Date','Open','High','Low','Close']
	
	
	
	#####
	# Run analysis with one dataset
	# (comment out this section to run with multiple datasets)
	#####
	
	#input file name of interest
	in_file_name='NFLX.csv'
	
	in_file= os.path.join(path,in_file_name)
	
	# add a header to the file if no header exists
	#add_header(in_file)
	
	#use csv module to pull out proper data
	#file_noblanks=remove_blanks(in_file)
	
	
	
	# create dataframe from the data
	df=import_data(in_file,fields)
	
	#####
	# input the date range of interest
	#####
	
	
	#####
	# the following dates are for FB.csv
	#####
	# ~ start_date='2012-07-03'
	# ~ start_date='2014-01-03'
	# start_date='2015-01-05'
	# ~ start_date='2017-01-04'
	# ~ start_date='2018-06-04'
	# ~ start_date='2018-01-02'
	
	# ~ end_date='2013-01-03'
	# ~ end_date='2014-01-03'
	# ~ end_date='2016-06-01'
	# ~ end_date='2017-01-03'
	# ~ end_date='2018-08-31'
	# end_date='2018-10-01'
	
	#####
	# the following dates are for NKE.csv
	#####
	# start_date='1980-12-02'
	# ~ start_date='1995-01-03'
	# ~ start_date='2018-01-02'
	
	# ~ end_date='2004-01-05'
	# ~ end_date='2014-01-03'
	# end_date='2018-09-13'
	
	
	#####
	# the following dates are for AAPL.csv
	#####
	# start_date='2013-09-11'
	
	# end_date='2018-09-11'
	
	#####
	# the following dates are for NFLX.csv
	#####
	start_date='2002-05-28'
	
	end_date='2019-04-30'
	
	full_set=False
	lengths=[]
	
	#####
	# generate price data for plotting and analysis
	#####
	
	
	start_idx_locs,end_idx_locs=get_idxs(df,start_date,end_date,full_set,lengths)
	
	# print(start_idx_locs)
	# print(end_idx_locs)
	return
	
	
	
	#####
	# Run analysis with multiple datasets
	# (comment out this section to run with single datasets
	#####
	'''
	#input file names of interest
	in_file_names=['NKE.csv','FB.csv','AAPL.csv','MHK.csv']
	
	start_dates=['1980-12-02','2012-07-03','2013-09-11','1992-04-01']
	# ~ start_dates=['1995-01-03','2017-01-04']
	end_dates=['2018-09-13','2018-10-01','2018-09-11','2018-09-13']
	
	# initialize dataframe
	df = pd.DataFrame()
	df_lengths=[]
	# merge dataframes from given input files
	for i in range(len(in_file_names)):
		in_file= os.path.join(path,in_file_names[i])
		df_store=import_data(in_file,fields)
		df_store_trim,startidx,endidx=slice_df(df_store,start_dates[i],end_dates[i])
		df_lengths.append(len(df_store_trim))
		df=df.append(df_store_trim)
	
	#renumber indexes
	df = df.reset_index(drop=True)
	
	index_list=df.index.values.tolist()
	# ~ print(index_list[-1])
	full_set=True
	# ~ print(df_lengths)
	# ~ print(df['Close'][index_list[-1]])
	# ~ return
	
	#####
	# generate price data for plotting and analysis
	#####
	
	start_idx_locs,end_idx_locs=get_idxs(df,start_dates[0],end_dates[0],full_set,df_lengths)
	
	
	
	# ~ print(start_idx_locs)
	# ~ print(end_idx_locs)
	# ~ return
	
	'''
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
	
	# Is behavior different when price goes up vs down after breakout?
	
	###
	# was the move into the consolidation up or down?
	###
	
	# first get the value of the large delta at the initial day
	move_dir=[]
	for idx in start_idx_locs:
		today_close=float(df['Close'][idx])
		yest_close=float(df['Close'][idx+1])
		
		if today_close < yest_close:
			move_dir.append('Down')
		if yest_close < today_close:
			move_dir.append('Up')
		
		# print('index is '+str(idx))
		# print('delta high: '+str(round(delta_h,3))+', delta low: '+str(round(delta_l,3)))
		# print('max delta: '+str(max_pct_delta))
		# print()

	
	###
	# Average length of consolidations
	###
	
	# if the last start index has no end index, remove it.
	if len(start_idx_locs) > len(end_idx_locs):
		start_idx_locs=start_idx_locs[1:]
	
	deltas=[]
	for y in range(len(start_idx_locs)):
		deltas.append(start_idx_locs[y]-end_idx_locs[y])
	
	# ~ print(deltas)
	# ~ return
	# plot_hist(deltas)
	# ~ return
	
	print()
	# ~ print('full list of deltas: ')
	# ~ print(deltas)
	print('min length of consol is '+str(min(deltas))+', max is '+str(max(deltas)))
	print('mean length of consol is '+str(round(np.mean(deltas),3))+', std dev is '+str(round(np.std(deltas),3)))
	# print('number of samples: '+str(len(deltas)))
	# print()
	
	# ~ idx_locs_filt,upper_bds_filt
	
	###
	# Average range of consolidations
	###
	'''
	# if the last start index has no end index, remove it.
	if len(start_idx_locs) > len(end_idx_locs):
		start_idx_locs=start_idx_locs[1:]
	
	
	ranges=[]
	ranges_pct=[]
	for p in range(len(start_idx_locs)):
		#find the min and max in each consolidation period
		#cycle through the indexes from start to end index and find min and max
		start_idx=start_idx_locs[p]
		end_idx=end_idx_locs[p]
		# ~ print(df['Close'][303])
		# ~ break
		start_close=df['Close'][start_idx]
		# ~ print(start_close)
		
		minval=1000000
		maxval=0
		# ~ print('start_idx='+str(start_idx)+', end_idx='+str(end_idx))
		for m in range(end_idx,start_idx):
			day_high=df['High'][m]
			day_low=df['Low'][m]
			# ~ print('day high='+str(day_high)+', day low='+str(day_low))
			# ~ print('min val='+str(minval)+', max val='+str(maxval))
			if day_low < minval:
				minval=day_low
			if day_high > maxval:
				maxval=day_high
		# ~ print()
		consol_range=maxval-minval
		consol_range_pct=100*consol_range/start_close
		ranges.append(round(consol_range,4))
		ranges_pct.append(round(consol_range_pct,2))
	
	# ~ print(ranges_pct)
	# ~ return
	# ~ plot_hist(ranges_pct)
	# ~ return
	
	print()
	# ~ print('full list of ranges by percent: ')
	# ~ print(ranges_pct)
	print('min percent range is '+str(min(ranges_pct))+', max percent range is '+str(max(ranges_pct)))
	print('mean range is '+str(round(np.mean(ranges_pct),3))+', std dev is '+str(round(np.std(ranges_pct),3)))
	print('number of samples: '+str(len(deltas)))
	print()
	'''
	###
	# largest single day move during consolidation, compared to initial move into consolidation
	###
	'''
	# print(start_idx_locs)
	# print(end_idx_locs)
	print()
	# return
	# first get the value of the large delta at the initial day
	pct_delta_val=[]
	for idx in start_idx_locs:
		cur_high=float(df['High'][idx])
		cur_low=float(df['Low'][idx])
		yest_close=float(df['Close'][idx+1])
		
		delta_h=100.*abs(cur_high-yest_close)/yest_close
		delta_l=100.*abs(yest_close-cur_low)/yest_close
		max_pct_delta=round(max(delta_h,delta_l),2)
		pct_delta_val.append(max_pct_delta)
		
		# print('index is '+str(idx))
		# print('delta high: '+str(round(delta_h,3))+', delta low: '+str(round(delta_l,3)))
		# print('max delta: '+str(max_pct_delta))
		# print()
		
	# next search through the consolidation range and find the max daily delta
	# start_idx is a higher number than end_idx, need to reverse these and work backwards
	# most recent date is lowes idx
	consol_max_pct_delta=[]
	for x in range(len(start_idx_locs)):
		start_idx=start_idx_locs[x]
		end_idx=end_idx_locs[x]
		# print(start_idx,end_idx)
		max_pct_delta_range=0
		for num in range(start_idx-1,end_idx,-1):
			cur_high=float(df['High'][num])
			cur_low=float(df['Low'][num])
			yest_close=float(df['Close'][num+1])
			
			delta_h=100.*abs(cur_high-yest_close)/yest_close
			delta_l=100.*abs(yest_close-cur_low)/yest_close
			max_pct_delta=round(max(delta_h,delta_l),2)
			
			# print('index is '+str(num)+', date is '+df['Date'][num]+', yest close: '+str(yest_close)+', cur high: '+str(cur_high))
			# print('delta high: '+str(round(delta_h,3))+', delta low: '+str(round(delta_l,3)))
			# print('max delta: '+str(max_pct_delta))
			# print()
			
			if max_pct_delta > max_pct_delta_range:
				max_pct_delta_range=max_pct_delta
		# print(max_pct_delta_range)
		consol_max_pct_delta.append(max_pct_delta_range)
		
	# output results of study
	for z in range(len(start_idx_locs)):
		print()
		print('Considering consolidation from '+df['Date'][start_idx_locs[z]]+' to '+df['Date'][end_idx_locs[z]])
		print('The impulse into the consolidation was '+str(pct_delta_val[z])+' and the max daily delta during consol was '+str(consol_max_pct_delta[z]))
	# print(pct_delta_val)
	# print(consol_max_pct_delta)
	'''
	
	###
	# largest multi day move during consolidation, compared to initial move into consolidation
	###
	'''
	# first get the value of the large delta at the initial day
	pct_delta_val=[]
	for idx in start_idx_locs:
		cur_high=float(df['High'][idx])
		cur_low=float(df['Low'][idx])
		yest_close=float(df['Close'][idx+1])
		
		delta_h=100.*abs(cur_high-yest_close)/yest_close
		delta_l=100.*abs(yest_close-cur_low)/yest_close
		max_pct_delta=round(max(delta_h,delta_l),2)
		pct_delta_val.append(max_pct_delta)
		
		# print('index is '+str(idx))
		# print('delta high: '+str(round(delta_h,3))+', delta low: '+str(round(delta_l,3)))
		# print('max delta: '+str(max_pct_delta))
		# print()
		
	# next search through the consolidation range and find the min and the max
	# calculate the total range
	# also calculate the delta to min and max from start of consolidation
	
	consol_max=[]
	consol_min=[]
	consol_pct_range=[]
	for x in range(len(start_idx_locs)):
		start_idx=start_idx_locs[x]
		end_idx=end_idx_locs[x]
		# print(start_idx,end_idx)
		highest_high=0
		lowest_low=100000.
		for num in range(start_idx-1,end_idx,-1):
			cur_high=float(df['High'][num])
			cur_low=float(df['Low'][num])
			
			if cur_high > highest_high:
				highest_high=cur_high
			if cur_low < lowest_low:
				lowest_low=cur_low
				
			# print('index is '+str(num)+', date is '+df['Date'][num]+', yest close: '+str(yest_close)+', cur high: '+str(cur_high))
			# print('delta high: '+str(round(delta_h,3))+', delta low: '+str(round(delta_l,3)))
			# print('max delta: '+str(max_pct_delta))
			# print()
			
		# print(max_pct_delta_range)
		consol_max.append(highest_high)
		consol_min.append(lowest_low)
		
		# total pct range
		mid_price=lowest_low+((highest_high-lowest_low)/2)
		consol_pct_range.append(round(100*(highest_high-lowest_low)/mid_price,2))
	# output results of study
	for z in range(len(start_idx_locs)):
		print()
		print('Considering consolidation from '+df['Date'][start_idx_locs[z]]+' to '+df['Date'][end_idx_locs[z]])
		print('The impulse into the consol was '+str(pct_delta_val[z])+' and the pct range during consol was '+str(consol_pct_range[z]))
	# print(pct_delta_val)
	# print(consol_max_pct_delta)
	'''
	###
	# Number of days before min/max of consolidation are reached
	###
	
	consol_max_delta_idx=[]
	consol_min_delta_idx=[]
	for x in range(len(start_idx_locs)):
		start_idx=start_idx_locs[x]
		end_idx=end_idx_locs[x]
		# print(start_idx,end_idx)
		highest_high=0
		lowest_low=100000.
		high_idx=0
		low_idx=0
		for num in range(start_idx-1,end_idx,-1):
			cur_high=float(df['High'][num])
			cur_low=float(df['Low'][num])
			
			if cur_high > highest_high:
				highest_high=cur_high
				high_idx=num
			if cur_low < lowest_low:
				lowest_low=cur_low
				low_idx=num
				
			# print('index is '+str(num)+', date is '+df['Date'][num]+', yest close: '+str(yest_close)+', cur high: '+str(cur_high))
			# print('delta high: '+str(round(delta_h,3))+', delta low: '+str(round(delta_l,3)))
			# print('max delta: '+str(max_pct_delta))
			# print()
			
		# print(max_pct_delta_range)
		consol_max_delta_idx.append(start_idx-high_idx)
		consol_min_delta_idx.append(start_idx-low_idx)
		
		
	##### output results of study	
	
	# print results for each consol period
	# for z in range(len(start_idx_locs)):
		# print()
		# print('Considering consolidation from '+df['Date'][start_idx_locs[z]]+' to '+df['Date'][end_idx_locs[z]])
		# print('number of days in consolidation: '+str(start_idx_locs[z]-end_idx_locs[z]))
		# print('The direction into the move was '+move_dir[z])
		# print('The num days to high was '+str(consol_max_delta_idx[z])+' num days to low was '+str(consol_min_delta_idx[z]))
		
	# Output averages of results
	# overall averages:
	#average days to high
	print()
	print('Overall min days to high is '+str(min(consol_max_delta_idx))+', max days to high is '+str(max(consol_max_delta_idx)))
	print('Overall mean days to high is '+str(round(np.mean(consol_max_delta_idx),3))+', std dev is '+str(round(np.std(consol_max_delta_idx),3)))
	
	#average days to low
	print('Overall min days to low is '+str(min(consol_min_delta_idx))+', max days to low is '+str(max(consol_min_delta_idx)))
	print('Overall mean days to low is '+str(round(np.mean(consol_min_delta_idx),3))+', std dev is '+str(round(np.std(consol_min_delta_idx),3)))
	print('Overall number of samples: '+str(len(consol_min_delta_idx)))
	
	# Get data to produce directional dependent averages
	up_idxs=[]
	down_idxs=[]
	for p in range(len(start_idx_locs)):
		if move_dir[p] == 'Up':
			up_idxs.append(p)
		if move_dir[p] == 'Down':
			down_idxs.append(p)
			
	up_dates_lows=[]
	up_dates_highs=[]
	down_dates_lows=[]
	down_dates_highs=[]
	for idx in up_idxs:
		up_dates_lows.append(consol_min_delta_idx[idx])
		up_dates_highs.append(consol_max_delta_idx[idx])
	
	for idx in down_idxs:
		down_dates_lows.append(consol_min_delta_idx[idx])
		down_dates_highs.append(consol_max_delta_idx[idx])
		
	# Averages if move into consol was up
	#average days to high
	print()
	print('On Up into consol, min days to high is '+str(min(up_dates_highs))+', max days to high is '+str(max(up_dates_highs)))
	print('On Up into consol, mean days to high is '+str(round(np.mean(up_dates_highs),3))+', std dev is '+str(round(np.std(up_dates_highs),3)))
	
	# average days to low
	print('On Up into consol, min days to low is '+str(min(up_dates_lows))+', max days to low is '+str(max(up_dates_lows)))
	print('On Up into consol, mean days to low is '+str(round(np.mean(up_dates_lows),3))+', std dev is '+str(round(np.std(up_dates_lows),3)))
	print('On Up into consol, number of samples: '+str(len(up_idxs)))
	
	
	# Averages if move into consol was down
	# average days to high
	print()
	print('On Down into consol, min days to high is '+str(min(down_dates_highs))+', max days to high is '+str(max(down_dates_highs)))
	print('On Down into consol, mean days to high is '+str(round(np.mean(down_dates_highs),3))+', std dev is '+str(round(np.std(down_dates_highs),3)))
	
	# average days to low
	print('On Down into consol, min days to low is '+str(min(down_dates_lows))+', max days to low is '+str(max(down_dates_lows)))
	print('On Down into consol, mean days to low is '+str(round(np.mean(down_dates_lows),3))+', std dev is '+str(round(np.std(down_dates_lows),3)))
	print('On Down into consol, number of samples: '+str(len(down_idxs)))

	
	###### How often does the high of the consol period come after the low?
	
	high_b4_low=[]
	low_b4_high=[]
	for n in range(len(start_idx_locs)):
		if consol_max_delta_idx[n] > consol_min_delta_idx[n]:
			low_b4_high.append(n)
		if consol_max_delta_idx[n] < consol_min_delta_idx[n]:
			high_b4_low.append(n)
			
	print()
	print('Number of consolidations with high before low is: '+str(len(high_b4_low)))
	print('Number of consolidations with low before high is: '+str(len(low_b4_high)))
	print('Probability that the low of consolidation is reached before the high is: '+str(round(100*len(low_b4_high)/len(start_idx_locs),2)))
	
	
	
	
	
	###
	# Correlation between direction of large move and how much that move follows through
	###


		
	
main()
