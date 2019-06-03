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
import numpy as np
import matplotlib.pyplot as plt
import datetime


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

def stock_ratio(df1,df2,start_date,end_date):
	#over the given period, find the ratio of the two stocks
	#return a list of the rounded ratios and the dates for plotting
	
	#get the low and high index of the dataframe based on the start and end dates
	df_1,idxl_1,idxh_1=slice_df(df1,start_date,end_date)
	df_2,idxl_2,idxh_2=slice_df(df2,start_date,end_date)
	
	#create a list of the daily ratio of sym1 to sym2
	ratios=[]
	dates=[]
	for y in range(len(df_1)):
		date1=df_1['Date'][idxl_1+y]
		date2=df_2['Date'][idxl_2+y]
		close1=df_1['Close'][idxl_1+y]
		close2=df_2['Close'][idxl_2+y]
		# ~ print('df1 date:'+str(date1)+', '+str(close1))
		# ~ print('df2 date:'+str(date2)+', '+str(close2))
		ratios.append(close2/close1)
		dates.append(date1)
		
	# ~ print('Mean ratio: '+str(round(np.mean(ratios),2))+', std dev is: '+str(round(np.std(ratios),2)))
	ratios_rnd=[round(x,2) for x in ratios]
	xdates=[datetime.datetime.strptime(date,"%Y-%m-%d") for date in dates]
	
	return ratios_rnd,xdates


def plot_data(data,xdates,start_date,end_date):
	
	#####
	# plot ratio
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
	while start_date_yr < end_date_yr:
		start_date_yr=start_date_yr+1
		plt.axvline(datetime.datetime(start_date_yr,1,1),color='y')
		plt.axvline(datetime.datetime(start_date_yr,1,31),color='k')
	
	ax.grid()
	plt.show()
	
	
	return

def main():
	#####
	# input main info here
	#####
	
	# Data location for mac:
	# path = '/Users/Marlowe/Marlowe/Securities_Trading/_Ideas/Data/'
	path = '/Users/Marlowe/gitsite/transfer/'
	
	# Data location for PC:
	# ~ path = 'C:\\Python\\transfer\\'
	
	# input the names of the fields if they are different from ['Date','Open','High','Low','Close'], use that order
	fields = ['Date','Open','High','Low','Close']
	
	
	#####
	# Input files to analyze
	#####
	
	#input file names of interest
	small_cap_file_name='^RUT.csv'
	large_cap_file_name='^GSPC.csv'
	
	SC_in_file= os.path.join(path,small_cap_file_name)
	LC_in_file= os.path.join(path,large_cap_file_name)
	
	
	# add a header to the file if no header exists
	#add_header(in_file)
	
	#use csv module to pull out proper data
	#file_noblanks=remove_blanks(in_file)
	
	
	# create dataframe from the data
	sc_df=import_data(SC_in_file,fields)
	lc_df=import_data(LC_in_file,fields)
	
	
	#####
	# input the date range of interest for overall analysis
	#####
	
	#first date in russell: 1987-09-10
	# ~ start_date='1987-09-10'
	start_date='2000-09-11'
	
	end_date='2019-05-10'
	
	#over the given period, find the ratio of the two stocks
	#return a list of the rounded ratios and the dates for plotting
	ratios,dates=stock_ratio(sc_df,lc_df,start_date,end_date)
	
	plot_data(ratios,dates,start_date,end_date)
	



main()
