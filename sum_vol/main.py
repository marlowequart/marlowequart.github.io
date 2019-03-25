'''
This script stitches together futures contract data from multiple contracts into one .csv file
This script will sum together the volume data during the overlap period when
trading volume is transitioning from the current contract to the next contract
as the current contract comes to the end of its life.
There is also an option to choose whether to use the ohlc data from the current contract
or the next contract during this overlap period

It is important that the files be listed in the directory in ascending order
the proper naming convention is:
18ESH...
18ESM...
18ESU...
18ESZ...
This ensures the oldest file is read first into the list structures


'''



import pandas as pd
import glob
import datetime
import time

# Combiner class
class combiner:
	def __init__(self, days):
		# Variable to test performance of the code, fixing start time
		self.start = time.time()
		# If input parameter for days to take is zero or NaN we just take default value 5
		if days == 0 or days != days:
			days = 5
		self.trading_days_in_deep = days

		# Cycle through all of the files in the folder, skipping created by previous runs final output,
		# load content into dataframes
		
		#initial_data_frames_from_input_files is a list of the dataframes from the files
		initial_data_frames_from_input_files = []
		file_ext = '*.csv'
		for fname in glob.glob(file_ext):
			# Will skip generated file, we suppose that market data files does not contain "_full_" and our result file does
			if "_full_" not in fname:
				# add a header to the file, only if there is no header
				self.add_header(fname)
				initial_data_frames_from_input_files.append(self.load_data_frame_from_file(fname))
		
		#########
		#
		# Split dataframes
		#
		#########
		
		
		# Now we must split loaded dataframes in right order. First dataframe is oldest
		# and we must just take last N days to work with.
		#  Second and further must be splitted into three dataframes:
		#   First dataframe (pre): from start of file to boundary date from previous file
		#   Second dataframe (mid): from previous boundary to this dataframe boundary
		#   Third dataframe (last): from this boundary to the end
		
		# cycle through each dataframe from the list of dataframes of each file
		# store the second and third dataframes in working_dataframes
		# there will be overlapping data for all the sections we want to have
		boundary_date = ''

		working_dataframes = []
		for i in range(len(initial_data_frames_from_input_files)):
			current_dataframe = initial_data_frames_from_input_files[i]
			pre = None
			mid = None
			last = None

			# If this is not first df, then we must take 'pre' part, the section that lay before 
			# the boundary_date and skip it.
			# Here we take previous boundary date, because we must skip everything before that date in order to
			#  sum volume data only for last "trading_days_in_deep" days
			if boundary_date != '':
				pre, mid = self.split_dataframe_by_date(current_dataframe, boundary_date)
			# Else, we just take whole dataframe
			# The else condition only applies to the first dataframe of the oldest section
			else:
				mid = current_dataframe

			# Now we get the "boundary date" from our dataframe with respect to the parameter self.trading_days_in_deep
			# Boundary date is the oldest trading day from the current dataframe that begins the overlapping volume
			 
			boundary_date = self.get_boundary_date(mid)
			# We split dataframe into two separate frames before and after that boundary date
			mid, last = self.split_dataframe_by_date(mid, boundary_date)
			
			# Save the two dataframes into working_dataframes
			working_dataframes.append(mid)#.iloc[::-1]) #may be used to add in reverse order
			working_dataframes.append(last)#.iloc[::-1]) #may be used to add in reverse order
		
		#########
		#
		# Sum dataframes
		#
		#########
		
		# Now after we split dataframes in desired order we must sum them
		# this function goes through the data frames and merges them one by one
		# the final merged dataframe includes the summed volume data as
		# well as the individual data frames from each time period. For each
		# date and time the row has both ohlc from all overlapping periods
		# plus summed volume data from those periods. The overlap should only occur
		# for the period defined by the number of trading days to select as the overlap
		final_dataframe = None
		for df in working_dataframes:
			# Reindex operation change indexing to day-time order, you can see it in the Jupiter notebook
			#  After that our dataframes can be merged. Without this operation we have fields in csv order, so in
			#  one dataframe date might be first record i.e. with index 1 and in second dataframe same date might be at
			#  index 1000.
			reindexed_df = df.set_index(['Date','Time'])
			# If this is first iteration then we just take whole first dataframe
			if final_dataframe is None:
				final_dataframe = reindexed_df.copy()
			# If this is not the first iteration then we just merge new dataframe into global one
			else:
				# Merging two dataframes generates new dataframe with columns with postfixes _x for first and _y for
				#  second. So in merged one instead of "Close" column we get "Close_x" and "Close_y" with values from
				#  merged columns, if there is no Date/Time value in one of merged we get NaN in all columns.
				#  Please take a look into Jupiter notebook.
				final_dataframe = pd.merge(final_dataframe, reindexed_df, how='outer', on=['Date', 'Time'])
				# Fill NaN's with 0
				final_dataframe.fillna(0,inplace=True)
				# We just sum this columns to get desired result
				final_dataframe['Adj Vol'] = final_dataframe['Adj Vol_x'] + final_dataframe['Adj Vol_y']
				final_dataframe['Volume'] = final_dataframe['Volume_x']+final_dataframe['Volume_y']
				# We take columns into separate lists to increase performance. Lists operates faster than dataframe-indexing
				o1 = final_dataframe['Open_x'].copy().tolist()
				o2 = final_dataframe['Open_y'].copy().tolist()
				h1 = final_dataframe['High_x'].copy().tolist()
				h2 = final_dataframe['High_y'].copy().tolist()
				l1 = final_dataframe['Low_x'].copy().tolist()
				l2 = final_dataframe['Low_y'].copy().tolist()
				c1 = final_dataframe['Close_x'].copy().tolist()
				c2 = final_dataframe['Close_y'].copy().tolist()

				# filter(lambda x: o1[x] == 0, range(len(o1))) - An "array" with all indexes where o1 equal to 0
				#  We fill "missed" data in first dataframe (previous contract) with data from second dataframe (future)
				
				#####
				# The following uses ohlc data from previous contract instead of future contract
				#####
				# ~ for i in filter(lambda x: o1[x] == 0, range(len(o1))):
					# ~ o1[i] = o2[i]
					# ~ h1[i] = h2[i]
					# ~ l1[i] = l2[i]
					# ~ c1[i] = c2[i]
				# ~ # Filling OHLC data with previous contract
				# ~ final_dataframe['Open'] = o1
				# ~ final_dataframe['High'] = h1
				# ~ final_dataframe['Low'] = l1
				# ~ final_dataframe['Close'] = c1
				#####
				# End previous instead of future
				#####
				
				#####
				# If we'd like to use data from the future contract instead of previous we just need to use o2 in lambda:
				#####
				for i in filter(lambda x: o2[x] == 0, range(len(o2))):
					o2[i] = o1[i]
					h2[i] = h1[i]
					l2[i] = l1[i]
					c2[i] = c1[i]
				# Filling OHLC data with future contract
				final_dataframe['Open'] = o2
				final_dataframe['High'] = h2
				final_dataframe['Low'] = l2
				final_dataframe['Close'] = c2
				#####
				# End future instead of previous
				#####
				
				# Now we just remove unused columns to get dataframe ready for new iteration and output
				final_dataframe = final_dataframe.drop(columns=['Open_x', 'High_x', 'Low_x', 'Close_x', 'Volume_x',
										'Adj Vol_x', 'Open_y', 'High_y', 'Low_y', 'Close_y', 'Volume_y', 'Adj Vol_y'])
		
		# Now we reset indexes, to make them visible for exporting.
		final_dataframe = final_dataframe.reset_index()
		# ~ print(len(final_dataframe))
		# ~ print(final_dataframe.loc[200495:200500,['Date','Time']])
		# ~ return
		# Our final dataframe unsorted after all our merges. Maybe if we run in another order we get it right way,
		#  but fortunately we can just sort dataframe by two index columns:
		final_dataframe = final_dataframe.sort_values(by=['Date','Time'], ascending=False)
		
		# Final step is to save it into new file
		self.save_to_csv(final_dataframe, "Final_full_data_20190308.csv")
		self.stop = time.time()
		print('Done!')
		print('Operation took: {}'.format(self.stop-self.start))

	# Find date with respect to full or not working day:
	
	# This function cycles through the dates starting from the top
	# of the .csv file and finds the boundary date that corresponds
	# to the nth actual trading date as specified at the beginning of the script (trading_days_in_deep)
	# this function filters out non-trading days. It does not consider half days
	# to skip half days, change the check_if_this_is_a_full_trading_day function
	def get_boundary_date(self, df):
		full_trading_days_passed = 0
		#total_trading_days_passed = 0
		boundary_date = ''
		# We move from last date step by step
		for i, x in df.groupby('Date', sort=False):
			boundary_date = i
			#total_trading_days_passed += 1
			# If this is fully traded day then we increase counter, if not then ignore and move on
			#  x here is the dataframe with all bars of the one day
			if self.check_if_this_is_a_full_trading_day(x):
				full_trading_days_passed+=1
			# If we have reached trading_days_in_deep then just stop:
			if full_trading_days_passed >= self.trading_days_in_deep:
				break
		return boundary_date

	# Split input dataframe into two dataframes by date
	def split_dataframe_by_date(selfself, df, boundary_date):
		# All records before days, sorted compared by string
		a = df[df.Date < boundary_date]
		# Last five days
		b = df[df.Date >= boundary_date]
		return a, b

	# Add header into csv
	def add_header(self, file_name):
		header = 'Date,Time,Adj Vol,Volume,Open,High,Low,Close\n'
		# Note need to check this is the right order for the header

		with open(file_name, 'r') as original:
			data = original.read()

		# Split file into parts with delimeter equal to header. If file already contains header - result would consist of
		#  few elements, first one is empty and then we just ignore adding
		if data.split(header)[0] != '':
			with open(file_name, 'w') as outfile:
				outfile.write(header + data)

	# Save into csv
	def save_to_csv(self, dataframe, filename):
		# save the dataframe to a csv file
		dataframe.to_csv(filename, sep=',', index=False)

	# Checking if any time of the current date is in the trading time,
	# i.e. this is a full trading day.
	# note this does not check for and ignore half days, but returns true for the first
	# minute that falls within the trading day range
	def check_if_this_is_a_full_trading_day(self, day):
		# We take every bar's Time parameter and check if it is traded in trading hours
		#  If it does - then this day is fully traded and we must count it otherwise skip
		for time in day.Time:
			# We use datetime package to parse string into Time
			startTradingTime = datetime.datetime.strptime('09:30:00', '%H:%M:%S')
			endTradingTime = datetime.datetime.strptime('15:00:00', '%H:%M:%S')
			curTime = datetime.datetime.strptime(time, '%H:%M:%S')
			# If single time is in trading range we decide that this is a fully traded day. And return True
			if curTime >= startTradingTime and curTime <= endTradingTime:
				return True
		#pass

	# Load dataframe from csv file
	def load_data_frame_from_file(self, file_name):
		df = pd.read_csv(file_name, header=0)
		return df

# Main body, just create combiner object with depth parameter

csv_combiner = combiner(10)
