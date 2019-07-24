'''
This script compares the small cap (russell 2000) vs large cap (S&P 500)
over a given number of years for a desired time frame.

Input: daily OHLC data for S&P500 and Russell 2000

Output: ratio of large cap to small cap


pandas version: 0.18.1
matplotlib version: 2.0.0
numpy version: 1.10.1
scipy version: 0.16.0

'''

import pandas as pd
import os
import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import datetime


#open csv file, return the data in a pandas dataframe
def import_data(file_name,fields):
	#only add items in fields list to dataframe
	
	#only add date, open, high, low, last to dataframe
	# fields = ['Date','Open','High','Low','Close']
	
	#open the file using pandas, use the first row as the header
	data = pd.read_csv(file_name,header=0,usecols=fields)
	
	
	
	# drop rows with period in Yield column
	# convert yield column to strings
	data['YIELD'] = data['YIELD'].apply(str)
	# ~ list_of_idxs=data.index[data['YIELD'] == '.'].tolist()
	# ~ print(list_of_idxs)
	# remove periods
	filtered_data = data[~data['YIELD'].str.startswith(".")]
	# ~ print(filtered_data.head(25))
	#convert back to integers
	filtered_data['YIELD'] = pd.to_numeric(filtered_data['YIELD'], errors='coerce')
	
	#change the order to most recent date on top if necessary
	filtered_data=filtered_data.sort(fields[0],ascending=0)
	filtered_data=filtered_data.reset_index(drop=True)
	
	return filtered_data


# input dataframe, return lists of data specified
def return_list(df):
	# Create a dictionary of the dataframe where each column
	# is transposed to a list.
	df = df.reset_index(drop=True)
	the_dict = df.to_dict('list')
	
	# Create lists
	date_list=the_dict['DATE']
	yield_list=the_dict['YIELD']
	
	# Transpose lists
	date_list_r=date_list[::-1]
	yield_list_r=yield_list[::-1]
	
	# make list of dates into datetime objects
	date_list_out = [datetime.datetime.strptime(date_item,"%Y-%m-%d").date() for date_item in date_list_r]
	
	return date_list_out,yield_list_r


def slice_df(df,start_date,end_date,col_name):
	
	start_day_df=df.loc[df[col_name] == start_date]
	end_day_df=df.loc[df[col_name] == end_date]
	# print()
	# print(df[45:75])
	
	
	startidx=end_day_df.index[0].tolist()
	endidx=start_day_df.index[0].tolist()
	
	# print(df[startidx:endidx])
	# ~ return
	return df[startidx:endidx],startidx,endidx


def plot_data_sing(data,xdates,start_date,end_date):
	
	#####
	# plot a single dataset
	# inputs:
	# data: full list of price data
	# xdates: full list of corresponding dates
	# start/end_date: dates wanted to plot (string in YYYY-MM-DD format)
	#####
	
	start_date_dt=datetime.datetime.strptime(start_date,"%Y-%m-%d")
	start_date_yr=start_date_dt.year
	end_date_dt=datetime.datetime.strptime(end_date,"%Y-%m-%d")
	end_date_yr=end_date_dt.year
	
	fig = plt.figure()
	ax = plt.subplot()
	ax.plot(xdates,data,color='b')
	ax.set_ylabel('Ratio S&P/Russell')
	ax.set_xlabel('Date/Time')
	#plot a vertical line at jan1 each year
	# ~ while start_date_yr < end_date_yr:
		# ~ start_date_yr=start_date_yr+1
		# ~ plt.axvline(datetime.datetime(start_date_yr,1,1),color='y')
		# ~ plt.axvline(datetime.datetime(start_date_yr,1,31),color='k')
	
	ax.grid()
	plt.show()
	
	
	return
	
def plot_data_multi(data,xdates,start_date,end_date):
	
	#####
	# plot a single dataset
	# inputs:
	# data: list of lists of price data
	# xdates: full list of corresponding dates
	# start/end_date: dates wanted to plot (string in YYYY-MM-DD format)
	#####
	
	start_date_dt=datetime.datetime.strptime(start_date,"%Y-%m-%d")
	start_date_yr=start_date_dt.year
	end_date_dt=datetime.datetime.strptime(end_date,"%Y-%m-%d")
	end_date_yr=end_date_dt.year
	
	fig = plt.figure()
	ax = plt.subplot()
	for item in data:
		ax.plot(xdates,item)
	ax.set_ylabel('Ratio S&P/Russell')
	ax.set_xlabel('Date/Time')
	#plot a vertical line at jan1 each year
	# ~ while start_date_yr < end_date_yr:
		# ~ start_date_yr=start_date_yr+1
		# ~ plt.axvline(datetime.datetime(start_date_yr,1,1),color='y')
		# ~ plt.axvline(datetime.datetime(start_date_yr,1,31),color='k')
	
	ax.grid()
	plt.show()
	return


def main():
	#####
	# input main info here
	#####
	
	# Data location for mac:
	# path = '/Users/Marlowe/Marlowe/Securities_Trading/_Ideas/Data/'
	# path = '/Users/Marlowe/gitsite/transfer/bond/'
	
	# Data location for PC:
	path = 'C:\\Python\\transfer\\Bond\\'
	
	# input the names of the fields (top column)
	fields = ['DATE','YIELD']
	
	
	#####
	# Input files to analyze
	#####
	
	#input file names of interest
	fed_funds_file_name='FEDFUNDS_daily.csv'
	ten_minus_two_file_name='T10Y2Y.csv'
	two_year_file_name='DGS2.csv'
	ten_year_file_name='DGS10.csv'
	
	fed_in_file= os.path.join(path,fed_funds_file_name)
	TUT_in_file= os.path.join(path,ten_minus_two_file_name)
	tyr_in_file= os.path.join(path,two_year_file_name)
	tenyr_in_file= os.path.join(path,ten_year_file_name)
	
	
	# add a header to the file if no header exists
	#add_header(in_file)
	
	#use csv module to pull out proper data
	#file_noblanks=remove_blanks(in_file)
	# ~ file_noblanks=remove_dots(in_file)
	
	
	# create dataframe from the data
	fed_df=import_data(fed_in_file,fields)
	TUT_df=import_data(TUT_in_file,fields)
	tyr_df=import_data(tyr_in_file,fields)
	tenyr_df=import_data(tenyr_in_file,fields)
	
	# print(fed_df[30:45])
	# print(TUT_df[30:45])
	# print(tyr_df[30:45])
	
	# return
	
	
	
	
	#return list of price data and date data
	
	#####
	# input the date range of interest for overall analysis
	#####
	
	####
	# Some interesting date ranges:
	# 1985-01-04 to 1991-01-11
	# 1998-01-05 to 2002-07-09
	# 2004-01-06 to 2009-12-14
	# current:
	####
	# start_date='1985-01-04'
	# start_date='1998-01-05'
	start_date='2004-01-06'
	# end_date='1991-01-11'
	# end_date='2002-07-09'
	# end_date='2009-12-14'
	end_date='2019-07-16'
	fed_df_2,startidx_fed,endidx_fed=slice_df(fed_df,start_date,end_date,'DATE')
	tut_df_2,startidx_tut,endidx_tut=slice_df(TUT_df,start_date,end_date,'DATE')
	tyr_df_2,startidx_tyr,endidx_tyr=slice_df(tyr_df,start_date,end_date,'DATE')
	tenyr_df_2,startidx_tenyr,endidx_tenyr=slice_df(tenyr_df,start_date,end_date,'DATE')
	
	# print(fed_df_2)
	# print(tut_df_2)
	# print(tyr_df_2)
	
	# return
	
	fed_dates,fed_yields=return_list(fed_df_2)
	tut_dates,tut_yields=return_list(tut_df_2)
	tyr_dates,tyr_yields=return_list(tyr_df_2)
	tenyr_dates,tenyr_yields=return_list(tenyr_df_2)
	
	# print(fed_dates)
	# print(tut_dates)
	# print(tyr_dates)
	
	# return
	########
	# Plot data
	########
	
	fig = plt.figure()
	ax = plt.subplot()
	
	ax.plot(fed_dates,fed_yields,color='b',label='Fed Funds Yield')
	ax.plot(tut_dates,tut_yields,color='r',label='10yr - 2yr Yield')
	ax.plot(tyr_dates,tyr_yields,color='g',label='2yr Yield')
	ax.plot(tenyr_dates,tenyr_yields,color='k',label='10yr Yield')
	
	ax.set_ylabel('Yields')
	ax.set_xlabel('Date')
	
	
	#plot a vertical line at jan1 each year
	# ~ while start_date_yr < end_date_yr:
		# ~ start_date_yr=start_date_yr+1
		# ~ plt.axvline(datetime.datetime(start_date_yr,1,1),color='y')
		# ~ plt.axvline(datetime.datetime(start_date_yr,1,31),color='k')
	
	#####
	# Fix date xaxis
	#####
	# get a list of years between start_date and end_date
	# first_yr=int(re.findall(r'(.+?)-',start_date)[0])
	# last_yr=int(re.findall(r'(.+?)-',end_date)[0])
	
	# x_vals=[x for x in range(first_yr,last_yr,1)]
	
	# set_base=int(len(x_vals)/1)
	# print(x_vals)
	# loc=plticker.MultipleLocator(base=set_base)
	# print(loc)
	# ax.xaxis.set_major_locator(loc)
	
	ax.grid()
	plt.legend()
	plt.show()



main()
