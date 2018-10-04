'''
This script is used to pull the first trade date for a list of symbols in a csv file
and then update that csv file with the first trade date and use today as the end date

This script only works for actively traded companies.

'''

import pandas as pd
from yahoofinancials import YahooFinancials as yf
import numpy as np
import datetime


#open csv file, return np array of data
def import_data(file_name):
	#open the file using pandas, use the first row as the header
	data = pd.read_csv(file_name,header=0)
	# ~ print(data.head())
	
	#set an arbitrary start date as a place holder for now
	st_dt_str='2018-01-01'
	#set today as the end date
	today=datetime.datetime.today()
	end_dt_str=datetime.datetime.strftime(today,'%Y-%m-%d')
	
	#update the pandas dataframe start date and end date with this info
	data['Start_Date']=data['Start_Date'].replace(np.nan,st_dt_str)
	data['End_Date']=data['End_Date'].replace(np.nan,end_dt_str)
	
	# ~ print(data.head())
	return pd.np.array(data[['Symbol','Start_Date','End_Date']])



def save_data(file_name,symbol_list):
	#Save the data as a .csv file
	df=pd.DataFrame(symbol_list)
	df.columns=['Symbol','Start_Date','End_Date']
	# ~ print(df.head())
	
	df.to_csv(file_name, index=False)
	
	


def pull_start_date(symbol):
	data=yf(symbol[0])
	historical_prices = data.get_historical_price_data(symbol[1],symbol[2],'daily')
	# ~ print(historical_prices[symbol[0]]['firstTradeDate']['formatted_date'])
	return historical_prices[symbol[0]]['firstTradeDate']['formatted_date']



def main():
	
	# generate a list of symbols to get the data for
	file_name='IPO_symbols.csv'
	symbol_list=import_data(file_name)
	
	#for testing use one symbol
	# ~ symbol_list=np.array([['FB','2018-01-01','2018-03-01'],['SNAP','2018-01-01','2018-03-01']])
	
	
	#Update the each companies data
	print('now updating data')
	
	total_syms=len(symbol_list)
	
	ipo_date=[]
	#use below to update all rows
	for i in range(total_syms):
		print('updating data for company '+str(symbol_list[i][0])+' row '+str(i+1)+' of '+str(total_syms))
		sym=symbol_list[i]
		#update symbol_list array to include the actual ipo date under 'Start_Date' column
		symbol_list[i][1]=pull_start_date(sym)
	
	print('Boom!')
	#save the updated np array into the csv file
	save_data(file_name,symbol_list)





main()
