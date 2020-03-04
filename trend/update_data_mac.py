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
import datetime
import time
import glob
import pyautogui as pg
import re


def get_filename_and_date(filename):
	#input a file name string date in format SYM_YYYY_MM_DD.csv
	#output symbol, year, month, day
	new_name=re.sub('.csv','',filename)
	# ~ print(new_name)
	
	# get everything up to the first underscore
	sym=re.search('^[^_]+(?=_)',new_name)
	symbol=sym.group(0)
	# ~ print(symbol)
	
	# get everything after the first underscore
	regexp=re.compile('_(.*)$')
	full_date=regexp.search(new_name).group(1)
	# ~ print(full_date)
	
	# get everything up to the first underscore
	yr=re.search('^[^_]+(?=_)',full_date)
	year=int(yr.group(0))
	# ~ print(year)
	
	# get everything after the first underscore
	mo_day_date=regexp.search(full_date).group(1)
	mo=re.search('^[^_]+(?=_)',mo_day_date)
	month=int(mo.group(0))
	# ~ print(month)
	
	# get everything after the last underscore
	day_date=re.search('(?<=_).*',mo_day_date)
	day=int(day_date.group(0))
	# ~ print(day)
	
	return symbol,year,month,day

def get_file_list(directory):
	# get the list of files in the directory
	file_list=glob.glob(directory+'*.csv')
	# ~ print(file_list)
	
	files=[]
	for file_name in file_list:
		files.append(re.sub(directory,'',file_name))
	
	return files

def create_dict(list_of_files):
	# create a dictionary with symbol:[date,file_name]
	out_dict={}
	
	for item in list_of_files:
		sym,yr,mo,day=get_filename_and_date(item)
		out_dict[sym]=[datetime.datetime(yr,mo,day),item]
	
	return out_dict


def main():
	# wait 5 seconds before beginning
	# ~ time.sleep(1)
	
	current_working_dir='/Users/Marlowe/gitsite/transfer/trend/data/working_dir/'
	download_data_dir='/Users/Marlowe/gitsite/transfer/trend/ts_data/'
	
	# Open a new terminal window
	# ~ pg.hotkey('command','n')
	# ~ time.sleep(1)
	
	# update folders from github
	# ~ pg.write('git pull origin master',interval=0.05)
	# ~ pg.press('enter')
	# ~ time.sleep(10)
	
	# ~ # Navigate to the download dir
	# ~ pg.write('cd '+download_data_dir,interval=0.05)
	# ~ pg.press('enter')
	# ~ time.sleep(2)
	
	# Get list of file names in the download_data_dir
	# create a dictionary of files with symbol:download date
	new_files=get_file_list(download_data_dir)
	new_files_dict=create_dict(new_files)
	
	# Get list of file names in the current_working_dir
	# create a dictionary of files with symbol:download date
	old_files=get_file_list(current_working_dir)
	old_files_dict=create_dict(old_files)
	
	# check for duplicate files in the current working dir
	
	
	# remove the duplicates from the current working dir
	
	# replace the duplicates in the current working dir, remove the old file and replace with the current file
	
	# if we are starting on a new contract, if we are in the roll period, move the file from 2yrs ago
	# into the historical data folder
	

main()
