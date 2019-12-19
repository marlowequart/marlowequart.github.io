'''
file name: volatility_calculator_191204.py
date: December 4, 2019
description: Script calculates realized volatilty as the standard deviation over a moving 
	window across the dataset. The size of the window (in trading days) can be changed.

inputs:
	TIME_WINDOW, line 26, type int: the size of the window (in trading days)
	INPUT_CSV, line 27, type string: path to output csv file
	OUTPUT_CSV, line 28, type string: path to output csv file

outputs:
	w.writerow({'Date':out_date,'Volatility':out_v}), lines 43-58, writes output to CSV

Python version 3.6.9, used: 
	csv, # version 1.0
	datetime, # built-in, Python 3.6.9
	numpy, # version 1.16.4
'''

import csv
import datetime
import numpy as np

## INPUT CONSTANTS ##
TIME_WINDOW = 40 # days
INPUT_CSV = 'data/^GSPC.csv'
OUTPUT_CSV = 'data/volatility40.csv'

# Define helper functions
## to convert from string to datetime and vice-versa
get_DT_obj=lambda _: datetime.datetime.strptime(_,'%Y-%m-%d')
get_DT_str=lambda _: datetime.datetime.strftime(_,'%Y-%m-%d')
## to calculate price change given start and end data points
get_priceChange=lambda dp_start,dp_end: (float(dp_end['Close'])-float(dp_start['Close']))/float(dp_start['Close'])

# Read input data from CSV into a dict
with open(INPUT_CSV) as f:
	r=csv.DictReader(f)
	data=[_ for _ in r]

# Write results to CSV
with open(OUTPUT_CSV,'w') as f:
	# Write headers to output CSV
	w=csv.DictWriter(f, ['Date','Volatility'])
	w.writeheader()
	# For every subset of the dataset the size of the moving window
	for i in range(1,len(data)-TIME_WINDOW-1):
		# Get start and end indices of the moving window
		start, stop = i, i+TIME_WINDOW
		# Get the date from the last element of the subset
		out_date=data[stop+1]['Date']
		# Compute price changes from subset
		price_changes = np.asarray([get_priceChange(data[_-1],data[_]) for _ in range(i,i+30)])
		# Compute annualized volatility from price changes
		out_volatility= np.std(price_changes)*np.sqrt(252)*100 
		# Write row to output CSV
		w.writerow({'Date':out_date,'Volatility':out_volatility})


