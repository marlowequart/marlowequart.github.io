'''
The purpose of this script is to update the desired data files


Input: list of .csv files contained in separate .csv file
input desired ranges to calculate over in lines 122 & 123

Output: Volatility over given ranges




Notes:
python version: 3.5.5

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

import pyautogui as pg


# Using resolution 1366x768 (windows 10 laptop)
# pyautogui.size()
# current location pyautogui.position()

	

def input_data(location,data):
	# go to desired location on screen and input data and press enter
	# location is list [x,y]
	
	# move cursor to position
	pg.moveTo(location[0],location[1],duration = 1)
	# click on position
	pg.click(location[0],location[1])
	time.sleep(2)
	# input data
	pg.write(data,interval=0.25)
	# press enter
	time.sleep(2)
	pg.press('enter')
	
def download_data(symbol,date):
	# this section is run after input_data function and chart has been pulled up
	# for the desired contract
	
	# move to chart location on screen
	# pg.moveTo(20,125,duration = 1)
	
	# click on eye icon
	# pg.click(362,269,duration = 2)
	# click on save icon to pull up save as window
	pg.click(300,270,duration = 2)
	# save data as .csv file
	# data saved to location: C:\Users\dell\Documents\TradeStation 10.0\Data
	# type file name
	time.sleep(2)
	pg.write(symbol+'_'+date+'.csv',interval=0.25)
	# press enter
	time.sleep(1)
	pg.press('enter')
	
# def place_data_window():
	# use this function to place the data window in the proper location

def update_sing_symbol(symbol,date):
	# Run this function to update for single symbol
	time.sleep(5)
	# go to symbol location input
	position=[25,87]
	input_data(position,symbol)
	time.sleep(5)
	download_data(symbol,date)

def main():
	start_time = time.time()
	# currently starting with tradestation app open, chart view open and window maximized, timeframe set to daily
	# and the data window is open
	# move from command prompt to tradestation app (must be the next window opened in alt tab)
	time.sleep(2)
	pg.hotkey('alt','tab')
	
	# first open tradestation app
	
	# second log in to live trading
	
	# third navigate to chart view by pressing ctrl-alt-c
	# 2/29/20, this works, but the window opens in a new place every time. I need to figure out a way to maximize the window
	# pg.hotkey('ctrl','alt','c')
	# time.sleep(5)
	# return
	# change time frame to daily
	'''
	pg.click(125,90,duration = 1)	# click on timeframe button
	pg.click(125,425,duration = 2)	# click on daily button
	time.sleep(5)
	# Type ctrl+shift+D to bring up data window, only want to do this on the first symbol
	pg.hotkey('ctrl','shift','d')
	'''
	
	# fourth, download data
	# Tradestation has 2 years of data down to 1 minute increments
	# 2/29/20: Create a list of symbols using the current roll dates
	indexes=['RTYH20','BTCH20','VXH20']
	currencies=['ECH20','ADH20','BPH20','CDH20','SFH20','JYH20','MP1H20','NE1H20','DXH20','CNHH20']
	ags=['DAK19','CBK19','LHQ19','LCV19','FCU19','OJU19']
	ags1=['DAM19','CBM19','LHV19','LCZ19','FCV19','OJX19']
	ags2=['DAN19','CBN19','LHZ19','FCX19','DAQ19','CBQ19','DAU19','CBU19','DAV19','CBV19','DAX19','CBX19','DAZ19','CBZ19','DAF20','CBF20','DAG20','CBG20','DAH20','CBH20']
	ags3=['LHG20','LHJ20','LCG20','LCJ20','FCF20','FCH20','OJF20','OJH20']
	finish=[]
	non_futures=['$VIX.X']
	# indexes=['ESU19','NKU19','NQU19','RTYU19','BTCU19','VXU19']
	# currencies=['ECU19','ADU19','BPU19','CDU19','SFU19','JYU19','MP1U19','NE1U19','DXU19',CNHU19']
	# rates=['EDU19']
	# non_ags=['YIM19','LBK19']
	# ags=['DAH19','CBH19','LHM19','LCM19','FCK19','KCN19','CTN19','OJK19','CCN19','SBN19']
	# symbols = indexes+currencies+rates+non_ags+ags
	symbols = indexes+currencies+ags+finish+ags1+ags2+ags3
	# get todays date for saving files in format _YYYY_MM_DD
	# 2/29/20: Generate a new date for each day that data is downloaded
	date='2020_02_28'
	
	# update_sing_symbol(symbols[0],date)
	
	for sym in symbols:
		print('now updating ',sym)
		update_sing_symbol(sym,date)
	
	# After we are done downloading data, move the files to the transfer folder
	# open a new command prompt
	pg.click(135,750,duration = 1)
	pg.write('cmd',interval=0.25)
	time.sleep(0.5)
	pg.press('enter')
	# downloaded data location: C:\Users\dell\Documents\TradeStation 10.0\Data
	# select all files and move files to folder: C:\python\transfer\trend\ts_data
	time.sleep(2)
	pg.write("""move C:\\Users\\dell\\Documents\\"TradeStation 10.0"\\Data\\*.* C:\\python\\transfer\\trend\\ts_data""",interval=0.05)
	pg.press('enter')
	
	# upload to git site
	# navigate to transfer folder
	pg.write('cd C:\\python\\transfer',interval=0.05)
	pg.press('enter')
	time.sleep(0.5)
	pg.write('git add *',interval=0.05)
	pg.press('enter')
	time.sleep(5)
	pg.write('git commit -m \"adding downloaded data from date '+date+' now\"',interval=0.05)
	pg.press('enter')
	time.sleep(2)
	pg.write('git push origin master',interval=0.05)
	pg.press('enter')
	time.sleep(10)
	
	# tell us that we are done downloading and transfering data
	pg.press('enter')
	pg.write('Data is done downloading and has been uploaded to gitsite!',interval=0.05)
	
	print()
	print('%f seconds to run script' % (time.time() - start_time))
	print()
	

main()