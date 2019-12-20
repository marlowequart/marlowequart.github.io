import csv
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import math


sp_input_file='data/^GSPC.csv'
vol_input_file='data/volatility40.csv'
vol2_input_file='data/volatility40_2.csv'
volmq_input_file='data/vixmq_dec08_to_nov18.csv'


sp_data_df = pd.read_csv(sp_input_file,header=0)
vol_data_df = pd.read_csv(vol_input_file,header=0)
volmq_data_df = pd.read_csv(volmq_input_file,header=0)
vol2_data_df = pd.read_csv(vol2_input_file,header=0)


sp_date=sp_data_df['Date'].tolist()
sp_price=sp_data_df['Close'].tolist()

vol_date=vol_data_df['Date'].tolist()
vol_price=vol_data_df['Volatility'].tolist()

vol2_date=vol2_data_df['Date'].tolist()
vol2_price=vol2_data_df['Volatility'].tolist()

volmq_date=volmq_data_df['Date'].tolist()
volmq_price=volmq_data_df['Close'].tolist()


#plot entire series
'''
sp_start_idx=2
sp_end_idx=17420
vol_start_idx=2
vol_end_idx=17420
'''

#plot 20 days around given date
'''
date='2018-11-15'
sp_date_idx=sp_date.index(date)
vol_date_idx=vol_date.index(date)
volmq_date_idx=volmq_date.index(date)
sp_start_idx=sp_date_idx-10
sp_end_idx=sp_date_idx+10
vol_start_idx=vol_date_idx-10
vol_end_idx=vol_date_idx+10
volmq_start_idx=volmq_date_idx-10
volmq_end_idx=volmq_date_idx+10
'''

#plot 100 days around given date

date='2018-02-01'
sp_date_idx=sp_date.index(date)
vol_date_idx=vol_date.index(date)
vol2_date_idx=vol2_date.index(date)
volmq_date_idx=volmq_date.index(date)
sp_start_idx=sp_date_idx-50
sp_end_idx=sp_date_idx+50
vol_start_idx=vol_date_idx-50
vol_end_idx=vol_date_idx+50
vol2_start_idx=vol2_date_idx-50
vol2_end_idx=vol2_date_idx+50
volmq_start_idx=volmq_date_idx-50
volmq_end_idx=volmq_date_idx+50


#plot 200 days around given date
'''
date='2018-02-01'
sp_date_idx=sp_date.index(date)
vol_date_idx=vol_date.index(date)
vol2_date_idx=vol2_date.index(date)
volmq_date_idx=volmq_date.index(date)
sp_start_idx=sp_date_idx-100
sp_end_idx=sp_date_idx+100
vol_start_idx=vol_date_idx-100
vol_end_idx=vol_date_idx+100
vol2_start_idx=vol2_date_idx-100
vol2_end_idx=vol2_date_idx+100
volmq_start_idx=volmq_date_idx-100
volmq_end_idx=volmq_date_idx+100
'''

#plot date range
'''
start_date='2008-12-10'
end_date='2018-11-14'
sp_start_idx=sp_date.index(start_date)
sp_end_idx=sp_date.index(end_date)
vol_start_idx=vol_date.index(start_date)
vol_end_idx=vol_date.index(end_date)
vol2_start_idx=vol2_date.index(start_date)
vol2_end_idx=vol2_date.index(end_date)
volmq_start_idx=volmq_date.index(start_date)
volmq_end_idx=volmq_date.index(end_date)
'''

# remove extras

volmq_date_plot=volmq_date[volmq_start_idx:volmq_end_idx]
volmq_price_plot=volmq_price[volmq_start_idx:volmq_end_idx]
'''
volmq_range=np.arange(volmq_start_idx,volmq_end_idx)
vol_range=np.arange(vol_start_idx,vol_end_idx)
i=0
for y in range(len(vol_range)):
	vol_date_i=vol_date[vol_range[y]]
	volmq_date_i=volmq_date[volmq_range[y+i]]
	# print('y: ',y,'i: ',i,' ',vol_date_i,volmq_date_i)
	if vol_date_i != volmq_date_i:
		# print('delete volmq data')
		del volmq_date_plot[volmq_range[i]]
		del volmq_price_plot[volmq_range[i]]
		i += 1
	
'''
# print(len(volmq_date_plot))
# print(len(vol_date[vol_start_idx:vol_end_idx]))

fig = plt.figure()
# plot s&p
ax = fig.add_subplot(211)
plt.plot(sp_date[sp_start_idx:sp_end_idx], sp_price[sp_start_idx:sp_end_idx],color='b')
plt.ylabel('Price')
# plt.xlabel(r'Date')
plt.title(r'S&P Price')

grid_num=15
time_step=int((sp_end_idx-sp_start_idx)/grid_num)
steps=np.arange(sp_start_idx,sp_end_idx,time_step)
dates=[sp_date[step] for step in steps]
ax.set_xticks(dates)
empty_string_labels = ['']*len(dates)
ax.set_xticklabels(empty_string_labels)
# plt.xticks(rotation=90)
plt.grid()

#plot vol
ax = fig.add_subplot(212)
plt.plot(vol_date[vol_start_idx:vol_end_idx], vol_price[vol_start_idx:vol_end_idx],color='b')
plt.plot(vol_date[vol_start_idx:vol_end_idx],volmq_price_plot ,color='r')
plt.plot(vol2_date[vol2_start_idx:vol2_end_idx], vol2_price[vol2_start_idx:vol2_end_idx],color='g')
plt.ylabel('Vol')
plt.xlabel(r'Date')
plt.title(r'Volatility')

grid_num=15
time_step=int((vol_end_idx-vol_start_idx)/grid_num)
steps=np.arange(vol_start_idx,vol_end_idx,time_step)
dates=[vol_date[step] for step in steps]
ax.set_xticks(dates)
plt.xticks(rotation=90)
plt.grid()



plt.show()
