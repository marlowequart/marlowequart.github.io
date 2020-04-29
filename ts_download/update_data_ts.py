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

wait_time=10


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
	global wait_time
	# Run this function to update for single symbol
	time.sleep(5)
	# go to symbol location input
	position=[25,87]
	input_data(position,symbol)
	time.sleep(wait_time)
	download_data(symbol,date)

def main():
	start_time = time.time()
	# mqdataw
	# currently starting with tradestation app open, chart view open and window maximized, timeframe set to daily
	# and the data window is open (ctrl-shift-d)
	# move from command prompt to tradestation app (must be the next window opened in alt tab)
	# change date in line 171
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
	
	#####
	# Use this to download historical data
	#####
	'''
	f_mo=['BTC','DA','CB','LB','OJ','FC']
	g_mo=['BTC','DA','CB','YI','LH','LC']
	h_mo=['ES','NK','NQ','RTY','BTC','VX','EC','AD','BP','CD','SF','JY','MP1','NE1','DX','CNH','ED','DA','CB','LB','CC','KC','CT','SB','OJ','FC']
	j_mo=['BTC','DA','CB','YI','LH','LC']
	k_mo=['BTC','DA','CB','LB','CC','KC','CT','SB','OJ','FC']
	m_mo=['ES','NK','NQ','RTY','BTC','VX','EC','AD','BP','CD','SF','JY','MP1','NE1','DX','CNH','ED','DA','CB','YI','LH','LC']
	n_mo=['BTC','DA','CB','LB','LH','CC','KC','CT','SB','OJ','FC']
	q_mo=['BTC','DA','CB','YI','LH','LC']
	u_mo=['ES','NK','NQ','RTY','BTC','VX','EC','AD','BP','CD','SF','JY','MP1','NE1','DX','CNH','ED','DA','CB','LB','CC','KC','OJ','FC']
	v_mo=['BTC','DA','CB','YI','LH','LC','SB','FC']
	x_mo=['BTC','DA','CB','LB','OJ','FC']
	z_mo=['ES','NK','NQ','RTY','BTC','VX','EC','AD','BP','CD','SF','JY','MP1','NE1','DX','CNH','ED','DA','CB','YI','LH','LC','CC','KC','CT']
	
	
	yr='18'
	
	f_str=[str(item+'F'+yr) for item in f_mo]
	g_str=[str(item+'G'+yr) for item in g_mo]
	h_str=[str(item+'H'+yr) for item in h_mo]
	j_str=[str(item+'J'+yr) for item in j_mo]
	k_str=[str(item+'K'+yr) for item in k_mo]
	m_str=[str(item+'M'+yr) for item in m_mo]
	n_str=[str(item+'N'+yr) for item in n_mo]
	q_str=[str(item+'Q'+yr) for item in q_mo]
	u_str=[str(item+'U'+yr) for item in u_mo]
	v_str=[str(item+'V'+yr) for item in v_mo]
	x_str=[str(item+'X'+yr) for item in x_mo]
	z_str=[str(item+'Z'+yr) for item in z_mo]
	
	symbols=j_str+k_str+m_str+n_str+q_str+u_str+v_str+x_str+z_str
	'''
	# 2/29/20: Create a list of symbols using the current roll dates
	non_futures=['$VIX.X']
	indexes=['ESM20','NKM20','NQM20','RTYM20','BTCM20','VXM20']
	currencies=['ECM20','ADM20','BPM20','CDM20','SFM20','JYM20','MP1M20','NE1M20','DXM20','CNHM20']
	rates=['EDM20']
	non_ags=['YIJ20','LBH20']
	ags=['DAH20','CBH20','LHJ20','LCJ20','FCH20','KCH20','CTH20','OJH20','CCH20','SBH20']
	symbols = indexes+currencies+rates+non_ags+ags
	
	# get todays date for saving files in format _YYYY_MM_DD
	# 2/29/20: Generate a new date for each day that data is downloaded
	date='2020_04_25'
	
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
	# downloaded data location: C:\Users\dell\Documents\
	# select all files and move files to folder: C:\python\transfer\trend\ts_data
	time.sleep(2)
	pg.write("""move C:\\Users\\dell\\Documents\\*.* C:\\python\\transfer\\trend\\ts_data\\""",interval=0.05)
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