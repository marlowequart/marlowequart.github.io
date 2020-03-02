'''
The purpose of this script is to take the data from the download folder from update_data_ts.py and
update the current working directory with the most recent data

The current working directory holds the previous 2 years (500 days) of futures data for determining
trading signals.





Notes:
python version: 3.5.5?

pandas version: 0.23.4
matplotlib version: 2.2.2
numpy version: 1.11.3
scipy version: 1.1.0
datetime, # built-in, Python 3.5.5
csv, # built-in, Python 3.5.5
math, # built-in, Python 3.5.5


'''


# import csv
# from matplotlib import pyplot as plt
# import pandas as pd
# import numpy as np
# import math
# import statistics
# import datetime
import time

# ~ import pyautogui as pg





def main():
	# wait 5 seconds before beginning
	time.sleep(10)
	
	current_working_dir='/Users/Marlowe/gitsite/transfer/trend/data/working_dir/'
	download_data_dir='/Users/Marlowe/gitsite/transfer/trend/ts_data/'
	
	# Get list of file names in the download_data_dir
	
	# Remove the date from the file names
	
	# check for duplicate files in the current working dir
	
	# remove the duplicates from the current working dir
	
	# replace the duplicates in the current working dir, remove the old file and replace with the current file
	
	# if we are starting on a new contract, if we are in the roll period, move the file from 2yrs ago
	# into the historical data folder
	

main()
