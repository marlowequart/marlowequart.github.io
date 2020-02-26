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


# Using resolution 1920x1200
	

def input_data(location,data):
	# go to desired location on screen and input data and press enter
	# location is list [x,y]
	
	# move cursor to position
	pg.moveTo(location[0],location[1],duration = 1)
	# click on position
	pg.click(location[0],location[1])
	# input data
	pg.typewrite(data)
	# press enter
	time.sleep(1)
	pg.press('enter')
	
def download_data():
	# this section is run after input_data function and chart has been pulled up
	# for the desired contract
	
	# move to chart location on screen
	
	# right click on chart
	
	# select data
	
	# select data window
	
	# click on eye icon
	
	# click on save icon to pull up save as window
	
	# save data as .csv file
	
	


def main():
	# wait 5 seconds before beginning
	time.sleep(5)
	
	# go to browser bar and input website
	position=[580,50]
	website='https://www.google.com/search?q=%24SPX&rlz=1C1GCEA_enUS867US867&oq=%24SPX&aqs=chrome..69i57j0l3j69i59j0.846j0j4&sourceid=chrome&ie=UTF-8'
	input_data(position,website)
	
	# wait 10 seconds
	time.sleep(5)
	
	# click the back button
	back=[20,50]
	pg.click(20,50)
	

main()