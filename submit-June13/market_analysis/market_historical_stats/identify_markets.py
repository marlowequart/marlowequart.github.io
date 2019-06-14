'''
file name: identify_markets.py
date: June 12, 2019
description: identify_markets() function identifies bull and bear market conditions over historical data. 
	Script goes sequentially through the sample dataset and stores running maximum and minimum (extrema) values, 
	it compares each new datapoint with the extrema values to see if the difference exceeds the lower or upper margin.
	If present state is bull market and new value exceeds the lower margin from the running maximum, 
	this indicates transition to the bear market, and the time period between the running minimum and 
	the running maximum is recorded as bull market occurence.
	Similarly, if present state is bear market and new value exceeds the upper margin from the running minimum, 
	this indicates transition to the bull market, and the time period between the running maximum and 
	the running minimum is recorded as bear market occurence.
	If present state is unknown (as in the beginning of the data set), 
	the state is identified as soon as either lower or upper margin is exceeded.
	The script returns a list of bull and bear market occurences as a dict.

inputs:
	data_set, line 31,  type list: [[date as datetime.datetime, price as float], ...]
	lower, line 32, type float: fraction of recent maximum price to be used as an indicator of transition from bear to bull market as float
	upper, line 33, type float: fraction of recent minimum price to be used as an indicator of transition from bull to bear market as float

outputs:
	return {"bull_markets":bulls, "bear_markets":bears}, line 117, type dict: {"bull_markets" : bull markets as [[date as datetime.datetime, closing price as float], ...], "bear_markets": bear markets as [[date as datetime.datetime, closing price as float], ...]}

Python version 3.6.7, modules used:
	This module, datetime.
'''

from . import running_min_max

def identify_markets(data_set: "[[datetime.datetime, float], ...]", 
		lower: float, 
		upper: float) -> {"bull_markets":list,"bear_markets":list}:  
	"""Identify bull and bear markets over sample dataset."""
	# Identify bull and bear markets over sample dataset.
	# Inputs:
	#	data_set: list of [date, price] pairs, where
	#		date: datetime.datetime
	#		price: float
	#	lower: limit for bear market detection as a 
	#		decimal fraction of a price, e.g. 0.8 for 80%
	#	upper: limit for bull market detection as a 
	#		decimal fraction of a price, e.g. 1.2 for 120%
	# Outputs: 
	#	Dict of bull and bear markets in the format
	#	{
	#		"bull_markets":[[[start_date, price],[end_date, price]], ...]
	#		"bear_markets":[[[start_date, price],[end_date, price]], ...]
	#	}
	in_bear,in_bull = False,False # starting conditions are unknown
	min_max=running_min_max.running_min_max(data_set[0]) # initialize min/max to the first point in the data set
	bears,bulls=[],[] # initialize empty lists to store the results

	# loop through each data point in the data set
	for data_point in data_set:
		# update minimum and maximum value at every step
		min_max.update(data_point)

		# if we do not know yet the type of the market
		if not (in_bear or in_bull):
			# if the current price is below running maximum by the lower margin, 
			#	 then we are now in the bear market
			#	 we mark this as a starting point for the bear market
			#	 and reset the running min/max
			if (data_point[1] < min_max.maximum[1]*lower):
				in_bear,in_bull=True,False
				bears.append([min_max.maximum.copy(),None])
				min_max.reset(data_point)

			# if the current price is above running maximum by the upper margin, 
			#	 then we are now in the bull market
			#	 we mark this as a starting point for the bull market
			#	 and reset the running min/max
			if (data_point[1]>min_max.minimum[1]*upper):
				in_bear,in_bull=False,True # we are now in bull market
				bulls.append([min_max.minimum.copy(),None]) # starting point for bull market
				min_max.reset(data_point)

		# if we do know what the current market is 
		else:
			# if we are in bull market and 
			# if current price is below running maximum by the lower margin, 
			#	 then we are now in the bear market
			#	 we mark this as a starting point for the bear market
			#	 we mark this as an ending point for the bull market
			#	 and reset the running min/max
			if in_bull and (data_point[1] < min_max.maximum[1]*lower):
				in_bear,in_bull=True,False
				bears.append([min_max.maximum.copy(),None])# starting point for bear market
				bulls[-1][1]=min_max.maximum.copy() # end point for bull market
				min_max.reset(data_point)

			# if we are in bear market and 
			# if current price is below running maximum by the lower margin, 
			#	 then we are now in the bull market
			#	 we mark this as a starting point for the bull market
			#	 we mark this as an ending point for the bear market
			#	 and reset the running min/max
			if in_bear and (data_point[1]>min_max.minimum[1]*upper):
				in_bear,in_bull=False,True
				bears[-1][1]=min_max.minimum.copy() # end point for bear market
				bulls.append([min_max.minimum.copy(),None]) # starting point for bull market

				min_max.reset(data_point)

	# If first market endpoint is not the same as the first date, 
	# add one more market to the opposite type starting from the first point
	if bulls[0][0][0]<bears[0][0][0] and (bulls[0][0][0] > data_set[0][0]):
		bears.insert(0,[data_set[0],bulls[0][0]])
	elif bears[0][0][0]<bulls[0][0][0] and (bears[0][0][0] > data_set[0][0]):
		bulls.insert(0,[data_set[0],bears[0][0]])
	# Last market endpoint is changed from None to the last date
	if bulls[-1][1]==None:
		bulls[-1][1]=data_set[-1]
	if bears[-1][1]==None:
		bears[-1][1]=data_set[-1]
	return {"bull_markets":bulls, "bear_markets":bears}




