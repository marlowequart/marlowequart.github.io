'''
This script is used to pull historical price data from yahoo finance
and then store that data as a csv file.



'''

import pandas as pd
from yahoofinancials import YahooFinancials as yf
import numpy as np
import datetime
import os



#open csv file, return list of symbols
def import_data(file_name):
	#open the file using pandas, use the first row as the header
	data = pd.read_csv(file_name,header=0)
	
	#add a column for the end date to be todays date
	today=datetime.datetime.today()
	end_dt_str=datetime.datetime.strftime(today,'%Y-%m-%d')
	
	return pd.np.array(data[['Symbol','Start_Date','End_Date']])



def save_data(file_name,df):
	#Save the data as a .csv file
	# ~ df=pd.DataFrame(symbol_list)
	df.columns=['Date','Close']
	os.chdir('/Users/Marlowe/Marlowe/Securities_Trading/Trading_Ideas/Short_IPO_Study/price_data/')
	df.to_csv(file_name, index=False, float_format='%.4f')



def main():
	
	# generate a list of symbols to get the data for
	file_name='IPO_symbols.csv'
	symbol_list=import_data(file_name)
	# ~ print(symbol_list)
	
	#for testing use one symbol
	# ~ symbol_list=np.array([['FB','2018-01-06','2018-03-01'],['SNAP','2018-01-01','2018-03-01']])
	
	# ~ print(symbol_list)
	
	#Update the each companies data
	print('now updating data')
	
	total_syms=len(symbol_list)
	i=0
	
	#use below to update subset of rows
	# ~ for row in doc.index[23:]:
	#use below to update all rows
	for i in range(total_syms):
		print('updating data for company '+str(symbol_list[i][0])+' row '+str(i+1)+' of '+str(total_syms))
		sym=symbol_list[i][0]
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
	
	

main()
