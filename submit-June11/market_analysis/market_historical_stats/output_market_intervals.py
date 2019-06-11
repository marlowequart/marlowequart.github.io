#TODO: update annotations
'''
file name: output_market_intervals.py
date: June 6, 2019
description: ____ function reuses functions from the output_historical_data 
	When running this as a module the script input and output file paths can be passed as command line parameters, 
	with the second parameter being optional and defaulting to "*_bull_market.csv"

inputs:
	input_file_path, line ___, type str: path to the input file
	output_file_path, line ___, type str: path to the output file (optional)

outputs:
		csv_writer.writerows(______), line ___

Python version 3.6.7, modules used: 
	This package, copy, csv, datetime, os, sys. #TODO: confirm this is correct
'''
# Constants used in this script
DEFAULT_OUTPUT_PREFIX='_bull_market.' # Adjust this constant to set a different default output prefix

# module import
#import copy # built-in, Python 3.6.7
import csv # version 1.0
from datetime import datetime # built-in, Python 3.6.7
import os # built-in, Python 3.6.7
import sys # built-in, Python 3.6.7

from . import output_historical_data

# One-liners used in this module:
flattenList=lambda _: [_1 for _2 in _ for _1 in _2] # collapse a list of lists to a 1d-list.

# Get input arguments
input_file_path=sys.argv[1]
if len(sys.argv)>2:
	output_file_path=sys.argv[2]
else:
	# in case a path has multiple .'s, replace only the last occurence with new prefix
	output_file_path=input_file_path[::-1].replace('.',DEFAULT_OUTPUT_PREFIX[::-1],1)[::-1]

#get source data
sample_dataset=output_historical_data.get_data(input_file_path)
# compute intervals
mrkt_intervals=output_historical_data.compute_mrkt_intervals(sample_dataset)

with open(output_file_path,'w') as outfile:
	csv_writer=csv.writer(outfile)
	csv_writer.writerow(['Type of move', 'start date', 'end date', '% change', 'duration (days)'])# check spelling
#	for market in mrkt_intervals['bull_markets']:
#		csv_writer.writerow(['bull market', market[0][0].strftime('%Y-%m-%d'), market[1][0].strftime('%Y-%m-%d'), '%.3f'%(100.*(market[1][1]-market[0][1])/market[0][1]), (market[1][0]-market[0][0]).days])
#	for market in mrkt_intervals['bear_markets']:
#		csv_writer.writerow(['bear market', market[0][0].strftime('%Y-%m-%d'), market[1][0].strftime('%Y-%m-%d'), '%.3f'%(100.*(market[1][1]-market[0][1])/market[0][1]), (market[1][0]-market[0][0]).days])
#	for market in mrkt_intervals['bull_mrkt_corrections']:
#		csv_writer.writerow(['bull market corrections', market[0][0].strftime('%Y-%m-%d'), market[1][0].strftime('%Y-%m-%d'), '%.3f'%(100.*(market[1][1]-market[0][1])/market[0][1]), (market[1][0]-market[0][0]).days])

	for human_name, market_ivals in [
		['bull market',mrkt_intervals['bull_markets']],
		['bear market',mrkt_intervals['bear_markets']],
		['bull market correction', flattenList(mrkt_intervals['bull_mrkt_corrections'])],
		['bear market correction', flattenList(mrkt_intervals['bear_mrkt_corrections'])],
		['bull market pullback', flattenList(mrkt_intervals['bull_mrkt_pullbacks'])],
		['bear market pullback', flattenList(mrkt_intervals['bear_mrkt_pullbacks'])],
		['bull market between corrections', flattenList(mrkt_intervals['bull_mrkt_bw_corrections'])],
		['bear market between corrections', flattenList(mrkt_intervals['bear_mrkt_bw_corrections'])],
		['bull market between pullbacks', flattenList(mrkt_intervals['bull_mrkt_bw_pullbacks'])],
		['bear market between pullbacks', flattenList(mrkt_intervals['bear_mrkt_bw_pullbacks'])]
		]:
		for market in market_ivals:
			csv_writer.writerow([human_name, market[0][0].strftime('%Y-%m-%d'), market[1][0].strftime('%Y-%m-%d'), '%.3f'%(100.*(market[1][1]-market[0][1])/market[0][1]), (market[1][0]-market[0][0]).days])











	
