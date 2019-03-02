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

        # Cycle through all of the files in the folder and find the last date listed in the file.
        # The last listed date in each .csv file represents the contract closing date
        # Next make a list with the file name and last recorded date of each file
        # list structure: dates=[[file_name,last_date,last_time]]
        files = []
        data_frames = []
        file_ext = '*.csv'
        for fname in glob.glob(file_ext):
            # Will skip generated file, we suppose that market data files does not contain "_full_" and our result file does
            if "_full_" not in fname:
                files.append(fname)
                # add a header to the file, only if there is no header
                self.add_header(fname)
                data_frames.append(self.load_data_frame_from_file(fname))

        # Now we must split loaded dataframes in right order. First dataframe is oldest
        # and we must just take last N days to work with.
        #  Second and further must be splitted into three dataframes:
        #   First dataframe: from start to boundary date from previous
        #   Second dataframe: from previous boundary to this dataframe boundary
        #   Third dataframe: from this boundary to the end
        boundary_date = ''

        working_dataframes = []
        for i in range(len(data_frames)):
            current_dataframe = data_frames[i]
            pre = None
            mid = None
            last = None

            # If this is not first df, then we must take 'pre' part, that lay before boundary_date and skip it.
            # Here we take previous boundary date, because we must skip everything before that date in order to
            #  sum volume data only for last "trading_days_in_deep" days
            if boundary_date != '':
                pre, mid = self.split_dataframe_by_date(current_dataframe, boundary_date)
            # Else, we just take whole dataframe
            else:
                mid = current_dataframe

            # Now we take "boundary date" from our dataframe with respect to the parameter self.trading_days_in_deep
            # Boundary date is the first trading day from dataframe that overlaps previous
            boundary_date = self.get_boundary_date(mid)
            # We split dataframe into two separate frames before and after that date
            mid, last = self.split_dataframe_by_date(mid, boundary_date)
            working_dataframes.append(mid)#.iloc[::-1]) #may be used to add in reverse order
            working_dataframes.append(last)#.iloc[::-1]) #may be used to add in reverse order

        # Now after we split dataframes in desired order we must sum them
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
                final_dataframe['Volume']=final_dataframe['Volume_x']+final_dataframe['Volume_y']
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
                #  This is "missed" data in first dataframe
                for i in filter(lambda x: o1[x] == 0, range(len(o1))):
                    o1[i] = o2[i]
                    h1[i] = h2[i]
                    l1[i] = l2[i]
                    c1[i] = c2[i]

                final_dataframe['Open'] = o1
                final_dataframe['High'] = h1
                final_dataframe['Low'] = l1
                final_dataframe['Close'] = c1
                # Now we just remove unused columns to get dataframe ready for new iteration and output
                final_dataframe = final_dataframe.drop(columns=['Open_x', 'High_x', 'Low_x', 'Close_x', 'Volume_x',
                                        'Adj Vol_x', 'Open_y', 'High_y', 'Low_y', 'Close_y', 'Volume_y', 'Adj Vol_y'])

        # Now we reset indexes, to make them visible for exporting.
        final_dataframe = final_dataframe.reset_index()
		
		# 3/1/19 Need to add header to final dataframe
		#final_dataframe = final_dataframe.add_header(
		
        # Our final dataframe unsorted after all our merges. Maybe if we run in another order we get it right way,
        #  but fortunately we can just sort dataframe by two index columns:
        final_dataframe = final_dataframe.sort_values(by=['Date','Time'], ascending=False)

        # Final step is to save it into new file
        self.save_to_csv(final_dataframe, "Final_full_data.csv")
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
        total_trading_days_passed = 0
        boundary_date = ''
        for i, x in df.groupby('Date', sort=False):
            boundary_date = i
            total_trading_days_passed += 1
            if self.check_if_this_is_a_full_trading_day(x):
                full_trading_days_passed+=1
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

        # Split file into parts with delimeter equal to header. If file already contains header - result wold consist of
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
        for time in day.Time:
            startTradingTime = datetime.datetime.strptime('09:30:00', '%H:%M:%S')
            endTradingTime = datetime.datetime.strptime('15:00:00', '%H:%M:%S')
            curTime = datetime.datetime.strptime(time, '%H:%M:%S')
            if curTime >= startTradingTime and curTime <= endTradingTime:
                return True
        pass

    # Load dataframe from csv file
    def load_data_frame_from_file(self, file_name):
        df = pd.read_csv(file_name, header=0)
        return df

# Main body, just create combiner object with depth parameter

csv_combiner = combiner(5)
