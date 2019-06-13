'''
file name: output_market_intervals.py
date: June 12, 2019
description: main() function reuses functions from the output_historical_data to output market intervals to CSV.
	When running this as a module the script input and output file paths must be passed as command line parameters.

inputs:
	input_file_path, line 30, type str: path to the input file
	output_file_path, line 30, type str: path to the output file (optional)

outputs:
	with open(output_file_path,'w') as outfile ..., lines 36-53, writes to CSV

Python version 3.6.7, modules used: 
	This package, copy, csv, sys.
'''

# module import
import csv # version 1.0
import sys # built-in, Python 3.6.7

# import from this package
from . import output_historical_data

# One-liners used in this module:
flattenList=lambda _: [_1 for _2 in _ for _1 in _2] # collapse a list of lists to a 1d-list.


def main(input_file_path,output_file_path):
	#get source data
	sample_dataset=output_historical_data.get_data(input_file_path)
	# compute intervals
	mrkt_intervals=output_historical_data.compute_mrkt_intervals(sample_dataset)
	
	with open(output_file_path,'w') as outfile:
		csv_writer=csv.writer(outfile)
		csv_writer.writerow(['Type of move', 'start date', 'end date', '% change', 'duration (days)'])
	
		# write all intervals to a single CSV file
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



# Check whether the module runs as a main script or is imported into another module.
# If module is run as a main script, then command line arguments are captured and used as parameters for the main() function
# to provide paths to the input and output files. 
if __name__ == "__main__":
	# Get input arguments
	input_file_path=sys.argv[1]
	output_file_path=sys.argv[2]
	main(input_file_path,output_file_path)







	
