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
import os
import shutil

# Global variable
# using='mac'
using='pc'

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
	global using
	# get the list of files in the directory
	file_list=glob.glob(directory+'*.csv')
	# print(file_list)
	
	# remove extra slashes from directory name when using PC
	if using=='pc':
		directory=directory.replace("\\","\\\\")
	
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
	
	global using
	
	#####
	# File locations
	#####
	# for mac
	if using=='mac':
		current_working_dir='/Users/Marlowe/gitsite/transfer/trend/data/working_dir/'
		download_data_dir='/Users/Marlowe/gitsite/transfer/trend/ts_data/'
		long_term_sorage='/Users/Marlowe/gitsite/transfer/trend/data/historical_data/'
	
	# for PC
	elif using=='pc':
		current_working_dir='C:\\Python\\transfer\\trend\\data\\working_dir\\'
		download_data_dir='C:\\Python\\transfer\\trend\\ts_data\\'
		long_term_sorage='C:\\Python\\transfer\\trend\\data\\historical_data\\'
	
	
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
	# create a dictionary of files with symbol:[download date,file name]
	new_files=get_file_list(download_data_dir)
	new_files_dict=create_dict(new_files)
	
	# Get list of file names in the current_working_dir
	# create a dictionary of files with symbol:[download date,file name]
	# 3/4/20, need to include a method if file name does not contain date
	old_files=get_file_list(current_working_dir)
	old_files_dict=create_dict(old_files)
	
	
	# Get a list of currently trading contracts
	# 3/4/20, this will be a function eventually, for now manual input
	# non_futures=['$VIX.X']
	# indexes=['ESU19','NKU19','NQU19','RTYU19','BTCU19','VXU19']
	# currencies=['ECU19','ADU19','BPU19','CDU19','SFU19','JYU19','MP1U19','NE1U19','DXU19','CNHU19']
	# rates=['EDU19']
	# non_ags=['YIM19','LBK19']
	# ags=['DAH19','CBH19','LHM19','LCM19','FCK19','KCN19','CTN19','OJK19','CCN19','SBN19']
	# current_symbols = indexes+currencies+rates+non_ags+ags
	
	###
	# Move files from download dir to working dir
	###
	# check for duplicates of current files from download folder in the current working dir
	# i.e.: if the files in download folder match current working dir,
	# and file in download folder is newer, remove old files from working dir
	# and move new file from download dir to working dir
	for key in new_files_dict:
		if key in old_files_dict:
			if old_files_dict[key][0]<new_files_dict[key][0]:
				# print('found old file, removing ',old_files_dict[key][1],', moving ',new_files_dict[key][1])
				#remove the duplicates from the current working dir
				os.remove(current_working_dir+old_files_dict[key][1])
				# move the current file from download folder to the working dir
				shutil.move(download_data_dir+new_files_dict[key][1],current_working_dir+new_files_dict[key][1])
			else:
				# if the file in the download folder is older (this technically shouldnt happen)
				# then leave the file in the download folder and output error notice
				print('Error, the old file: ',old_files_dict[key][1],' is newer than the newly downloaded file: ',new_files_dict[key][1])
		# Next, move any other files from the download folder that are not in the current working directory
		# These could be historic files that were downloaded
		else:
			shutil.move(download_data_dir+new_files_dict[key][1],current_working_dir+new_files_dict[key][1])
	
	
	return
	
	
	
	# if we are starting on a new contract, if we are in the roll period, move the file from 2yrs ago
	# into the historical data folder. At this point, remove the date from the file name
	for key in new_files_dict:
		if key in old_files_dict:
			take_no_action=1
		else:
			take_some_action=1
	

main()
