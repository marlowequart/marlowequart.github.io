import csv
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import math
import statistics
import datetime
import time

pd.options.mode.chained_assignment = None

def true_range_calc(df,lowidx,highidx,num_days):
	#cycle through dataframe, using ohlc data
	#output the df with new column with TR data
	#true range is max(todays high-low,todays high-yesterdays close,yesterdays close-todays low)
	
	# ~ print(df.head())
	
	df_out=df[lowidx-10:highidx]
	#add column for true range
	df_out['true_range']=''
	df_out['ATR']=''
	df_out['Annual pct ATR']=''
	
	for idx in range(lowidx,highidx):
		day_high=df_out['High'][idx]
		yest_close=df_out['Close'][idx-1]
		day_low=df_out['Low'][idx]
		true_r=max(day_high-day_low,day_high-yest_close,yest_close-day_low)
		true_r=float(true_r)
		df_out['true_range'][idx]=true_r
	
	for idx in range(lowidx+num_days,highidx):
		atr=0
		for x in range(num_days):
			atr=atr+df_out['true_range'][idx-x]
		atr_av=atr/num_days
		days_close=df_out['Close'][idx]
		df_out['ATR'][idx]=atr_av
		df_out['Annual pct ATR'][idx]=100*(atr_av/days_close)*16
	
	return df_out


def std_dev_calc(df,lowidx,highidx,num_days):
	#cycle through dataframe, using ohlc data
	#output the df with new column with TR data
	#true range is max(todays high-low,todays high-yesterdays close,yesterdays close-todays low)
	
	# ~ print(df.head())
	
	df_out=df[lowidx-10:highidx]
	#add column for true range
	df_out['day pct rtn']=''
	df_out['std dev']=''
	
	for idx in range(lowidx,highidx):
		day_close=df_out['Close'][idx]
		yest_close=df_out['Close'][idx-1]
		df_out['day pct rtn'][idx]=(day_close-yest_close)/day_close
	
	# df_pct_rtn=df_out['day pct rtn']
	# print(df_pct_rtn.tail(20))
	# print()
	# print(df_pct_rtn.iloc[[11086-lowidx]])
	# print(df_pct_rtn.iloc[[11102-lowidx]])
	
	for idx in range(lowidx+num_days,highidx):
		# print()
		# print('todays index: ',idx,', std_dev index is ',idx-num_days,' to ',idx)
		# print('value at index ',idx-num_days,' is ',df_out.iloc[[(idx-lowidx+10)-num_days],7])
		# print('value at index ',idx,' is ',df_out.iloc[[(idx-lowidx+10)],7])
		days_list=df_out.iloc[(idx-lowidx+10)-num_days:(idx-lowidx+10),7].tolist()
		#days_list=df_out.iloc[(idx-num_days):idx,7].tolist()
		# print(days_list)
		# output the annualised std dev as a percent
		df_out['std dev'][idx]=statistics.stdev(days_list)*100*16
	
	# print(df_out.tail(30))
	return df_out


def main(df):
	
	pd.options.mode.chained_assignment = None

	# input_file='data/ES_RAD.CSV'

	# input the names of the fields if they are different from ['Date','Open','High','Low','Close'], use that order
	# fields = ['Date','Open','High','Low','Close','Open Interest','Volume']

	# df = pd.read_csv(input_file,names=fields)

	# calculate the max and mean for the 100d ATR
	num_years=2
	num_days_avg=25

	idx_delta=252*num_years+num_days_avg
	end_idx=df.tail(1).index.item()
	start_idx=end_idx-idx_delta

	df2=true_range_calc(df,start_idx,end_idx,num_days_avg)
	
	# print(df2.tail(20))

	# find max and mean ATR
	# df3=df2.loc[start_idx+num_days_avg:end_idx]['ATR']
	# print(df3)

	max_atr=df2.loc[start_idx+num_days_avg:end_idx]['ATR'].max()
	mean_atr=df2.loc[start_idx+num_days_avg:end_idx]['ATR'].mean()
	max_atr_pct=df2.loc[start_idx+num_days_avg:end_idx]['Annual pct ATR'].max()
	mean_atr_pct=df2.loc[start_idx+num_days_avg:end_idx]['Annual pct ATR'].mean()
	# print()
	# print('max atr: '+str(round(max_atr,2)))
	# print('mean atr: '+str(round(mean_atr,2)))
	# print('max annualised atr (in %): '+str(round(max_atr_pct,2)))
	# print('mean annualised atr (in %): '+str(round(mean_atr_pct,2)))
	
	
	# Calculate max a mean std dev
	df3=std_dev_calc(df,start_idx,end_idx,num_days_avg)
	# print(df3.tail(20))
	max_stdev=df3.loc[start_idx+num_days_avg:end_idx]['std dev'].max()
	mean_stdev=df3.loc[start_idx+num_days_avg:end_idx]['std dev'].mean()
	# print()
	# print('max annualised std dev (in %): '+str(round(max_stdev,2)))
	# print('mean annualised std dev (in %): '+str(round(mean_stdev,2)))

	return mean_atr_pct,mean_stdev


# The following code is only executed if this is run as a stand-alone script,
# when this program is imported as a module the following will be ignored:
if __name__ == "__main__":
	
	print('Start time to run script:')
	print(datetime.datetime.now())
	print()
	
	
	# Load the desired commodity list
	sym_input_file='active_symbols.csv'
	# input the names of the fields if they are different from ['Date','Open','High','Low','Close'], use that order
	sym_fields = ['symbol','description']
	sym_df = pd.read_csv(sym_input_file,names=sym_fields)
	symbols=sym_df['symbol'].tolist()
	descripts=sym_df['description'].tolist()
	
	
	#simulation dates
	# sim_input_dates='1990to2000_02_07_20'

	# ~ start_date='1959-07-15'
	# start_date='1990-01-02'

	# end_date='1969-11-10'
	# ~ end_date='1989-12-29'
	# end_date='2000-03-10'
	# end_date='2019-06-05'
	
	fields = ['Date','Open','High','Low','Close','Volume','Open Interest']
	
	sym=symbols[5]
	desc=descripts[5]
	
	# Run for single symbol
	# input_file='CLCDATA_ratio_adj/'+sym+'_RAD.CSV'
	# df = pd.read_csv(input_file,names=fields)
	
	# print('Testing symbol ',sym,', ',desc)
	# results=main(df)
	
	
	
	# Use for loops
	# data output is [symbol,mean annualised pct atr, mean annualised pct std dev]
	data=[]
	for i in range(1,len(symbols)):
		sym=symbols[i]
		input_file='CLCDATA_ratio_adj/'+sym+'_RAD.CSV'
		df = pd.read_csv(input_file,names=fields)
		
		results=main(df)
		data.append([sym,results[0],results[1]])
		
		# results=main(SIM_NUM=sim_num,
			# SIM_DATES=sim_input_dates,
			# START_DATE=start_date,
			# END_DATE=end_date,
			# PRINT=False,
			# PLOT=False)
			
		# print(sym)
		
	# output to .csv
	f=open('all_volatility.csv','w',newline='\n')
	csv_writer=csv.writer(f)
	csv_writer.writerow(['symbol','mean annualised pct atr', 'mean annualised pct std dev'])
	for item in data:
		sym=item[0]
		atr=item[1]
		stddev=item[2]
		csv_writer.writerow([sym,round(atr,2),round(stddev,2)])
	
	f.close
	
	
	
	print()
	print('%f seconds to run script' % (time.time() - start_time))
	print(datetime.datetime.now())
	print()
