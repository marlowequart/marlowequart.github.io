'''
This script finds consolidation patterns in OHLC price data
This works by finding the points where the slope changes from
negative to positive, and then doing an envelope filter around that point

1. filter the price data
2. find the zero slope points
3. work out from those points to find upper and lower bounds using envelope


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


def plot_price_df(dataframe,startidx,endidx):
	#plot price data from dataframe
	num_ticks=6
	
	close=dataframe['Last'][startidx:endidx].tolist()
	date=dataframe['Date'][startidx:endidx].tolist()
	close.reverse()
	date.reverse()
	
	
	fig=plt.figure()
	ax1=fig.add_subplot(111)
	ax1.xaxis.set_major_locator(ticker.MaxNLocator(num_ticks))
	
	ax1.plot(date, close, color='k', label='price')
	ax1.set_ylabel('Price')
	ax1.set_xlabel('Date')
	ax1.set_title('S&P Emini Price')
	
	plt.show()
	
	
	
def plot_price_list(date,close):
	#plot price data using lists as inputs
	num_ticks=6

	fig=plt.figure()
	ax1=fig.add_subplot(111)
	ax1.xaxis.set_major_locator(ticker.MaxNLocator(num_ticks))
	
	ax1.plot(date, close, color='k', label='price')
	ax1.set_ylabel('Price')
	ax1.set_xlabel('Date')
	ax1.set_title('S&P Emini Price')
	
	plt.show()
	
def plot_price_list_2(date,close,filt):
	#plot price data using lists as inputs
	num_ticks=6

	fig=plt.figure()
	ax1=fig.add_subplot(111)
	ax1.xaxis.set_major_locator(ticker.MaxNLocator(num_ticks))
	
	ax1.plot(date, close, color='k', label='price')
	ax1.plot(date, filt, color='g', label='SMA')
	ax1.set_ylabel('Price')
	ax1.set_xlabel('Date')
	ax1.set_title('S&P Emini Price')
	
	plt.show()
	
def plot_price_list_2axes(date,list1,list2):
	#plot price data using lists as inputs
	num_ticks=6

	fig=plt.figure()
	ax1=fig.add_subplot(111)
	ax1.xaxis.set_major_locator(ticker.MaxNLocator(num_ticks))
	
	ax1.plot(date, list1, color='k', label='price')
	
	ax2 = ax1.twinx()
	ax2.plot(date,list2,'-r')
	ax2.xaxis.set_major_locator(ticker.MaxNLocator(num_ticks))
	
	plt.axhline(y=0, color='k', linestyle='--')
	
	ax1.set_ylabel('Price')
	ax1.set_xlabel('Date')
	ax1.set_title('S&P Emini Price')
	
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
	
def sma_gen_lb(price,num_days):
	#create a list of price data with the simple moving average
	#using the previous x num_days looking back
	out_list=price[0:num_days]
	# ~ for x in range(num_days-1,len(price)-num_days):
	for x in range(num_days-1,len(price)-1):
		price_sum=0
		for y in range(num_days):
			price_sum=price_sum+price[x-y]
		out_list.append(price_sum/num_days)
	
	# ~ print(len(price))
	# ~ print(len(out_list))
	return out_list
	
def sma_gen_bisect(price,num_days):
	#create a list of price data with the simple moving average
	#using the previous x num_days/2 on either side of the current date
	
	
	bis_num=int(num_days/2)
	
	out_list=price[0:bis_num]
	# ~ for x in range(num_days-1,len(price)-num_days):
	for x in range(bis_num,len(price)-(bis_num)):
		# ~ print(x)
		price_sum_plus=0
		price_sum_minus=0
		for y in range(bis_num):
			# ~ print(y)
			price_sum_minus=price_sum_minus+price[x-y]
			price_sum_plus=price_sum_plus+price[x+y]
		out_list.append((price_sum_plus+price_sum_minus)/num_days)
	
	out_list=out_list+price[(len(price)-bis_num):]
	
	
	#Also output the slope at each point using the data from +/- num_days around point
	# ~ num_range=[x for x in range(0,len(price))]
	num_range=[x for x in range(0,num_days)]
	slope_list=price[0:bis_num]
	for x in range(bis_num,len(price)-(bis_num)):
		data=out_list[(x-bis_num):(x+bis_num)]
		# ~ print(num_range)
		# ~ print(data)
		# ~ exes=num_range[x-bis_num:x+bis_num]
		#get the overall slope of the current graph
		slope, intercept, r_value, p_value, std_err  = stats.linregress(num_range,data)
		slope_list.append(slope)
	
	
	slope_list=slope_list+price[(len(price)-bis_num):]
	# ~ print(len(slope_list))
	# ~ print(len(out_list))
	# ~ print(len(price))
	# ~ print(len(out_list))
	return out_list, slope_list

	
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

	start_date='2018-05-01'
	end_date='2018-11-01'
	
	
	#####
	# generate price data and filtered price data
	#####
	
	num_days_avg=20
	date_list,close_list=list_gen(df,start_date,end_date)
	
	# Generate SMA data using lookback filter
	# ~ close_filt=sma_gen_lb(close_list,num_days_avg)
	# ~ date_list=date_list[num_days_avg:]
	# ~ close_list=close_list[num_days_avg:]
	# ~ close_filt=close_filt[num_days_avg:]
	
	
	# Generate SMA data using bisect method
	close_filt,slopes=sma_gen_bisect(close_list,num_days_avg)
	rmv_num=int(num_days_avg/2)
	date_list=date_list[rmv_num:(len(date_list)-rmv_num)]
	close_list=close_list[rmv_num:(len(close_list)-rmv_num)]
	close_filt=close_filt[rmv_num:(len(close_filt)-rmv_num)]
	slopes=slopes[rmv_num:(len(slopes)-rmv_num)]
	
	
	
	#####
	# find zero slope points using the filtered data for number of days around
	# each point
	#####
	
	#get the indexes for the zero crossings of the slope
	z_c=np.where(np.diff(np.sign(slopes)))[0].tolist()
	#get the dates for the zero crossings of the slope
	z_c_dates=[]
	for idx in z_c:
		z_c_dates.append(date_list[idx])
	
	
	#####
	# Using the zero slope crossings, and a pre-determined envelope size,
	# work outwards to find how long the price remains within that envelope
	#####
	env_size=20
	
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
	for idx in z_c:
		bounds[idx]=[]
		
	# ~ print(bounds)
	# ~ return
	
	for idx in z_c:
		#find lower bounds
		y=0
		while (close_list[idx-y] < close_list[idx]+env_size) & (close_list[idx-y] > close_list[idx]-env_size):
			y=y+1
		lwr_idx=idx-y
		bounds[idx].append(lwr_idx)
		
		#find upper bounds
		z=0
		while (close_list[idx+z] < close_list[idx]+env_size) & (close_list[idx+z] > close_list[idx]-env_size):
			z=z+1
		upper_idx=idx+z
		bounds[idx].append(upper_idx)
	
	# ~ print(bounds)
	
	
	# ~ print(len(slopes))
	# ~ print(len(date_list))
	
	# ~ gen_plot(df,3,100)
	# ~ plot_price_df(df,end_date_idx,start_date_idx)
	
	# ~ plot_price_list(date_list,close_list)
	# ~ plot_price_list(date_list,close_filt)
	# ~ plot_price_list_2(date_list,close_filt,close_list)
	# ~ plot_price_list_2axes(date_list,close_filt,slopes)
	
	num_ticks=6
	fig = plt.figure()
	ax1 = fig.add_subplot(111)
	
	#draw vertical lines at bounds
	for key,value in bounds.items():
		for item in value:
			# ~ print(item)
			plt.axvline(x=item, color='k', linestyle='--')
	
	ax1.xaxis.set_major_locator(ticker.MaxNLocator(num_ticks))
	ax1.plot(date_list, close_list, color='k', label='price')
	ax1.plot(date_list, close_filt, color='g')
	
	plt.show()
	
	
main()
