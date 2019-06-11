'''
file name: market_adjustment.py
date: May 27, 2019
description: Function identify_market_adjustments() identifies market adjustments such as pullbacks and corrections 
	provided a data interval and a list of historical market data.
	The data interval is used to crop the historical market data as start and end points.
	Script picks goes sequentually through each data point in the dataset and stores running minimum and maximum values.
	If market type is bull it checks if current value is lower than the running maximum by the user-defined margin, 
	and when this happends, it records running maximum as the beginning of an adjustment period. 
	When bull market is in adjustment and the new data point value exceeds the running maximum, 
	the running minimum is marked as the end point of an adjustment.
	If market type is bear it checks if current value is higher than the running minimum by the user-defined margin, 
	and when this happends, it records running minimum as the beginning of an adjustment period. 
	When bear market is in adjustment and the new data point value exceeds the running minimum, 
	the running maximum is marked as the end point of an adjustment.
	The function returns a dict containing a list of adjustments and a list of times between adjustments.

inputs:
	market_type, line 32, type str: market condtions as either "bull" or "bear"
	margin, line 32, type float: a fraction to be used as a cut-off margin exceeding of which indicates adjustment
	data_set, line 33, type list: [[date as datetime.datetime, closing price as float], ...]
	data_interval, line 34, type list or tuple: [[starting date as datetime.datetime, price as float], [ending date as datetime.datetime, price as float]]

outputs:
	return {"adjustments":adjustments,"between_adjustments":between_adjustments}, line 128, type dict: {"adjustments":adjustments as [[date as datetime.datetime, closing price as float], ...], "between_adjustments": time between adjustments as [[date as datetime.datetime, closing price as float], ...]}

Python version 3.6.7, modules used: This module, datetime.
'''

from . import running_min_max

def market_adjustment(market_type: "bull | bear", margin: float, 
		data_set: "[[datetime.datetime, float], ...]", 
		data_interval:"[[datetime.datetime, float],[datetime.datetime, float]]") -> {"adjustments":list,"between_adjustments":list}:
	""" Identify corrections and pullbacks within an interval of market data. """
	# Identify corrections and pullbacks in intervals of market data.
	# Market interval are the start and end points used to crop the list of the market data. 
	# Adjustment is any move beyound the margin within a market 
	# that is opposite to the market direction (such as correction or pullback).
	# Inputs:
	#	market_type: either "bull" or "bear"
	#	margin: detection limit as a decimal fraction of a price, e.g. 0.1 for 10%, or 0.05 for 5%
	#	data_set: list of [date, price] pairs, where
	#		date: datetime.datetime
	#		price: float
	#	data_interval: a pair of data points in the format [[date, price],[date, price]] 
	#			between which the market adjustments will be searched for. 
	#			These points must exist in the data_set.
	# Outputs: 
	#	Dict of adjustments and time between in the format
	#	{
	#		"adjustments":[[[start_date, price],[end_date, price]], ...]
	#		"between_adjustments":[[[start_date, price],[end_date, price]], ...]
	#	}

	# Get data subset from the data set using the data interval
	data_subset=data_set[data_set.index(data_interval[0]):data_set.index(data_interval[1])+1]
	# We always start between adjustments
	in_adjustment=False
	# Initialize min/max to the first point in the data set
	min_max=running_min_max.running_min_max(data_subset[0])
	# Initialize lists to store the results, 
	# the first point in the data subset contains the starting point of between_adjustments
	adjustments,between_adjustments = [],[[data_subset[0],None]]
	# Finding adjustments for bull and bear markets is almost the same except for polarity inversion
	# if in bull market
	if market_type=='bull':
	# for each data point in the data set
		for data_point in data_subset:

			# if current point is between adjustments and current price is below the margin from running maximum,
			#	then we are now in adjustment
			#	we mark this as a starting point of an adjustment
			#	we mark this as an end point of an interval between_adjustments
			#	and reset the running minimum
			if (not in_adjustment) and (data_point[1]<min_max.maximum[1]*(1-margin)):
				in_adjustment=True
				adjustments.append([min_max.maximum.copy(),None])
				between_adjustments[-1][1]=min_max.maximum.copy()
				min_max.minimum=data_point.copy()

			# if current point is in adjustments and current price is above the previous maximum,
			#	then we are now between adjustments
			#	we mark this as a starting point of an interval between_adjustments
			#	we mark this as an end point of an adjustment
			#	and reset the running minimum
			if in_adjustment and (data_point[1]>min_max.maximum[1]): # adjustment ends when we reach new maximum
				in_adjustment=False
				between_adjustments.append([min_max.minimum.copy(),None])
				adjustments[-1][1]=min_max.minimum.copy()

			# update minimum and maximum value at the end of every step
			min_max.update(data_point)

	# if in bear market
	elif market_type=='bear':
		# for each data point in the data set
		for data_point in data_subset: 

			# if current point is between adjustments and current price is above the margin from running minimum,
			#	then we are now in adjustment
			#	we mark this as a starting point of an adjustment
			#	we mark this as an end point of an interval between_adjustments
			#	and reset the running minimum
			if (not in_adjustment) and (data_point[1]>min_max.minimum[1]*(1+margin)):
				in_adjustment=True
				adjustments.append([min_max.minimum.copy(),None])
				between_adjustments[-1][1]=min_max.minimum.copy()
				min_max.maximum=data_point.copy()

			# if current point is in adjustments and current price is below the previous minimum,
			#	then we are now between adjustments
			#	we mark this as a starting point of an interval between_adjustments
			#	we mark this as an end point of an adjustment
			#	and reset the running maximum
			if in_adjustment and (data_point[1]<min_max.minimum[1]):
				in_adjustment=False
				between_adjustments.append([min_max.maximum.copy(),None])
				adjustments[-1][1]=min_max.maximum.copy()
			min_max.update(data_point)

	# if type of the market was provided incorrectly we output a message to the user to help with debugging
	else:
		print("WRONG MARKET TYPE, USE 'bull' OR 'bear'")

	# we set the end point of between_adjustments to the last point on the data_subset
	#between_adjustments[-1][1]=data_subset[-1]
	#return {"adjustments":adjustments,"between_adjustments":between_adjustments}
	# Note that the last market will have end point as None.
	# and if the market correction is ongoing at that time, its endpoint will also be none
	# DONE: if still in adjustment when we reach the end, set the adjustments[-1][1] to the last point
	if in_adjustment==False:
		between_adjustments[-1][1]=data_subset[-1]
	else:
		adjustments[-1][1]=data_subset[-1]
	return {"adjustments":adjustments,"between_adjustments":between_adjustments}




