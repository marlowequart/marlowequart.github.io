'''
file name: running_min_max.py
date: May 23, 2019
description: Class to store running minimum and maximum


inputs:
	__init__:
		data_point, line 27
	reset:
		data_point, line 31
	update:
		data_point, line 36
outputs:
	__init__:
		running_min_max object, line 16-17
	reset:
		Nothing, edits object properties
	update:
		Nothing, edits object properties

Python version 3.6.7, modules used: datetime.
'''

class running_min_max():
	""" Class to store running minimum and maximum for the market data """
	def __init__(self, data_point:"[date as datetime.datetime, price as float]"):
		""" Set both min and max to the current data point """
		self.reset(data_point)

	def reset(self, data_point:"[date as datetime.datetime, price as float]") -> None:
		""" Reset both min and max to the current data point """
		self.minimum = data_point.copy()
		self.maximum = data_point.copy()

	def update(self, data_point:"[date as datetime.datetime, price as float]") -> None:
		""" Update min and max if necessary """
		# if current price is more then running max
		#	 then update running maximum
		if data_point[1] > self.maximum[1]: 
			self.maximum = data_point.copy()
		# if current price is less than running min
		#	 then update running minimum
		if data_point[1] < self.minimum[1]: 
			self.minimum = data_point.copy()

