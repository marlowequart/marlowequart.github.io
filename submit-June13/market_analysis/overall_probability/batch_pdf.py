'''
file name: batch_pdf.py
date: June 12, 2019
description: Script calculates current probability for a list of files.
	Please create a CSV file with two columns. 
	Place input file paths into the left column and the output file paths
	into the right colum. Provide this script with the path to the newly
	created CSV file.

inputs:
	sys.argv[1], line 25, type str: path to the input file containing list of inputs and outputs.

outputs:
	current_probability.main(input_file_path,output_file_path), line 24, writes to PDFs on a loop

Python version 3.6.7, modules used: 
	This package, csv, sys.
'''

import csv
import sys

from market_analysis.current_probability import current_probability

with open(sys.argv[1]) as f:
	for l in f.readlines():
		input_file_path,output_file_path=l[:-1].split(',')
		current_probability.main(input_file_path,output_file_path)