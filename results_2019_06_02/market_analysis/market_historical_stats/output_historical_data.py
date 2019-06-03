'''
file name: output_historical_data.py
date: June 2, 2019
description: main() function reads input CSV data file with dates and closing prices and outputs a CSV file with dates, closing prices, and markets.
	The input file must be a CSV containing colums named "Date" and "Close", containing the measurement date and the closing price.
	The output file will be a CSV containing 3 columns: "Date", "Close" and "Market". Date will be in the format YYYY-MM-DD, and Market will
	have one of the following values: "undefined", "Bull", "Bull Correction", "Bull Pullback", "Bear", "Bear Correction", "Bear Pullback".
	The functions in this script can be imported into other scripts, or this script can be run as a standalone module, e.g.:
		python -m market_analysis.market_historical_stats.output_historical_data data/GSPC.csv output.csv
	When running this as a module the script input and output file paths can be passed as command line parameters, 
	with the second parameter being optional and defaulting to "*_bull_market.csv"

inputs:
	input_file_path, line 120, type str: path to the input file
	output_file_path, line 120, type str: path to the output file (optional)

outputs:
		csv_writer.writerows(sample_dataset_edit), line 116

Python version 3.6.7, modules used: 
	This package, copy, csv, datetime, os, sys.
'''

# Constants used in this script
DEFAULT_OUTPUT_PREFIX='_bull_market.' # Adjust this constant to set a different default output prefix

# module import
import copy # built-in, Python 3.6.7
import csv # version 1.0
from datetime import datetime # built-in, Python 3.6.7
import os # built-in, Python 3.6.7
import sys # built-in, Python 3.6.7

# import modules from this package
from .identify_markets import identify_markets
from . import market_adjustment

# One-liners used in this script:
# Define a short function to collapse a list of lists to a 1d-list.
flatten_list=lambda _: [_1 for _2 in _ for _1 in _2]


def get_data(input_file_path: str) -> "[[date, closing price], ...]":
	# ingest date and closing price data from a CSV file
	# inputs:
	# input_file_path is the path to the input file
	# outputs:
	# [[date as datetime.datetime, closing price as float], ...]

	# create empty list to store intermediate data
	data=[]
	# open input file as with csv reader, and add each row as a list to data variable
	with open(input_file_path,'r') as _:
		_=csv.reader(_)
		for _ in _:
			data.append(_)
	# extract columns "Date" and "Close" while parsing date as a datetime.datetime object and closing price as float
	sample_dataset=[[datetime.strptime(_[data[0].index('Date')],'%Y-%m-%d'),
		float(_[data[0].index('Close')])] for _ in data[1:]]
	# return parsed data set
	return sample_dataset

def compute_adjustments(market:'bull | bear', margin:float, sample_dataset:list, periods:list)->"adjustments, between_adjustments":
	# get lists of periods in adjustment (corrections, pullbacks) and list of periods of time between adjustments
	# inputs:
	# 	market is the market type, as str, either "bull" or "bear"
	#	margin is the detection threshold for adjustment, as float, e.g. 0.1 for 10%, 0.05 for 5%
	#	sample_dataset is the dataset under study, as list [[date as datetime.datetime, closing price as float], ...], returned by get_data()
	#	periods is the list of periods on a sample_dataset that should be checked for adjustments, 
	#		e.g. in order to find pullbacks time between corrections should be tested
	# outputs: 
	# 	adjustments as list data intervals [[[starting date as datetime.datetime, price as float],[ending date as datetime.datetime, price as float]], ...]
	# 	between_adjustments as list data intervals [[[starting date as datetime.datetime, price as float],[ending date as datetime.datetime, price as float]], ...]

	# create empty lists to store outputs
	adjustments, between_adjustments=[],[]
	# for each period compute data intervals for market adjustments and time between adjustments, 
	# then append results to the appropriate lists
	for _ in periods:
		results=market_adjustment.market_adjustment(market,margin,sample_dataset,_)
		adjustments.append(results['adjustments'])
		between_adjustments.append(results['between_adjustments'])
	# return lists containing market adjustments and time between adjustments
	return adjustments, between_adjustments

def compute_mrkt_intervals(sample_dataset:list, market_threshold_lower:float = 0.8, 
		market_threshold_higher:float = 1.2, corrections_margin:float = 0.1, pullbacks_margin:float = 0.05) -> dict:
	# compute bull markets, bear markets, bull corrections, bull pullback, bear corrections and bear pullbacks
	# inputs:
	#	sample_dataset is the dataset under study, as list [[date as datetime.datetime, closing price as float], ...], returned by get_data()
	#	market_threshold_lower is the threshold at which bear market is detected, defaults to 0.8 for 80%, as float
	#	market_threshold_higher is the threshold at which bull market is detected, defaults to 1.2 for 120%, as float
	#	corrections_margin is the margin at which corrections are detected, defaults to 0.1 for 10%, as float
	#	pullbacks_margin is the margin at which pullbacks are detected, defaults to 0.05 for 5%, as float
	# outputs:
	# 	a dict containing market intervals for bull markets, bear markets, bull corrections, bull pullback, bear corrections and bear pullbacks

	# create an empty dict to store the results
	mrkt_intervals={}
	# compute bull and bear markets
	all_markets = identify_markets(sample_dataset,market_threshold_lower,market_threshold_higher) # set margins to 80% and 120%
	# remove instances where the endpoint is None (latest market has not endpoint, because it is still ongoing)
	mrkt_intervals['bull_markets'] = [_ for _ in all_markets['bull_markets'] if _[1] is not None]
	mrkt_intervals['bear_markets'] = [_ for _ in all_markets['bear_markets'] if _[1] is not None]
	# compute corrections (>10%)and time between for bull markets
	mrkt_intervals['bull_mrkt_corrections'],mrkt_intervals['bull_mrkt_bw_corrections'] = compute_adjustments(
		'bull', corrections_margin, sample_dataset, mrkt_intervals['bull_markets'])
	# compute pullbacks (>5%)and time between for bull markets time between corrections
	mrkt_intervals['bull_mrkt_pullbacks'  ],mrkt_intervals['bull_mrkt_bw_pullbacks'  ] = compute_adjustments(
		'bull', pullbacks_margin, sample_dataset, flatten_list(mrkt_intervals['bull_mrkt_bw_corrections']))
	# do the same for bear markets
	mrkt_intervals['bear_mrkt_corrections'],mrkt_intervals['bear_mrkt_bw_corrections'] = compute_adjustments(
		'bear', corrections_margin, sample_dataset, mrkt_intervals['bear_markets'])
	mrkt_intervals['bear_mrkt_pullbacks'  ],mrkt_intervals['bear_mrkt_bw_pullbacks'  ] = compute_adjustments(
		'bear', pullbacks_margin, sample_dataset, flatten_list(mrkt_intervals['bear_mrkt_bw_corrections']))
	return mrkt_intervals

def export_intervals_to_csv(sample_dataset, mrkt_intervals, output_file_path):
	# Write out a CSV file containing 3 columns: Date, Close, Market creating one row for each data point on the dataset
	# Date is in the format YYYY-MM-DD, while Market can be one of the following:
	# "undefined", "Bull", "Bull Correction", "Bull Pullback", "Bear", "Bear Correction", "Bear Pullback".
	# inputs:
	#	sample_dataset is the dataset under study, as list [[date as datetime.datetime, closing price as float], ...], returned by get_data()
	#	mrkt_intervals is a dict containing market intervals for 
	#		bull markets, bear markets, bull corrections, bull pullback, bear corrections and bear pullbacks
	#		as returned by compute_mrkt_intervals()
	#	output_file_path is a path to the output file, as str
	# outputs:
	#	returns nothing, saves dataset as a CSV

	# Create a deep copy of the sample dataset for editing in-place 
	# (protect the dataset for cases when this function is imported into another script)
	sample_dataset_edit=copy.deepcopy(sample_dataset)
	# add a third column to store market type
	for dp in sample_dataset_edit:
		dp.append('undefined')
	# create a small local function to update a column
	def update_column_by_interval(data_set,interval,column_num,value):
		# updates values in a particular column if they fall within a market iterval,
		# meaning that the data point date is more than the start date, but less then the end date
		# inputs:
		#	data_set is the dataset being edited, as list [[date as datetime.datetime, closing price as float], ...], returned by get_data()
		#	interval is a market interval, as list or tuple [[starting date as datetime.datetime, price as float],[ending date as datetime.datetime, price as float]]
		#	column_num is the column index, as int
		#	value is the value to which the column should be updated
		# outputs:
		#	None, edits list in-place
		for data_point in data_set:
			if data_point[0]>interval[0][0] and data_point[0]<interval[1][0]:
				data_point[column_num]=value
	# write out bull and bear markets
	for interval in mrkt_intervals['bull_markets']:
		update_column_by_interval(sample_dataset_edit,interval,2,'Bull')
	for interval in mrkt_intervals['bear_markets']:
		update_column_by_interval(sample_dataset_edit,interval,2,'Bear')
	# write out corrections and pullbacks
	for interval in flatten_list(mrkt_intervals['bull_mrkt_corrections']):
		update_column_by_interval(sample_dataset_edit,interval,2,'Bull Correction')
	for interval in flatten_list(mrkt_intervals['bull_mrkt_pullbacks']):
		update_column_by_interval(sample_dataset_edit,interval,2,'Bull Pullback')
	for interval in flatten_list(mrkt_intervals['bear_mrkt_corrections']):
		update_column_by_interval(sample_dataset_edit,interval,2,'Bear Correction')
	for interval in flatten_list(mrkt_intervals['bear_mrkt_pullbacks']):
		update_column_by_interval(sample_dataset_edit,interval,2,'Bear Pullback')
	# update date format
	for dp in sample_dataset_edit:
		dp[0]=dp[0].strftime('%Y-%m-%d') 
	# save as csv
	with open(output_file_path, 'w') as output_file:
		csv_writer=csv.writer(output_file)
		csv_writer.writerows([["Date", "Close", "Market"]])
		csv_writer.writerows(sample_dataset_edit)

def main(input_file_path,output_file_path):
	# This function will load data from the CSV file, compute intervals, and write out a new CSV file containing results
	# inputs:
	#	input_file_path is the path to the input CSV, as str
	# 	output_file_path is the path to the output CSV, as str
	# outputs:
	#	returns nothing, saves dataset as a CSV

	# load data
	sample_dataset=get_data(input_file_path)
	# compute intervals
	mrkt_intervals=compute_mrkt_intervals(sample_dataset)
	# export to csv
	export_intervals_to_csv(sample_dataset,mrkt_intervals,outputFilePath)


# Check whether the module runs as a main script or is imported into another module.
# If module is run as a main script, then command line arguments are captured and used as parameters for the main() function
# to provide paths to the input and output files. 
# If the second argument is omitted, the script will use default prefix 
# which can be changed by editing the DEFAULT_OUTPUT_PREFIX at the top of this script.
if __name__ == "__main__":
	input_file_path=sys.argv[1]
	if len(sys.argv)>2:
		outputFilePath=sys.argv[2]
	else:
		# in case a path has multiple .'s, replace only the last occurence with new prefix
		outputFilePath=input_file_path[::-1].replace('.',DEFAULT_OUTPUT_PREFIX[::-1],1)[::-1]
	main(input_file_path,outputFilePath)

