import csv
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import math


sp_input_file='data/^GSPC.csv'
vol_input_file='data/volatility40.csv'


sp_data_df = pd.read_csv(sp_input_file,header=0)
vol_data_df = pd.read_csv(vol_input_file,header=0)


sp_date=sp_data_df['Date'].tolist()
sp_price=sp_data_df['Close'].tolist()

vol_date=vol_data_df['Date'].tolist()
vol_price=vol_data_df['Volatility'].tolist()


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
sp_start_idx=sp_date_idx-10
sp_end_idx=sp_date_idx+10
vol_start_idx=vol_date_idx-10
vol_end_idx=vol_date_idx+10
'''

#plot 100 days around given date

date='2018-11-09'
sp_date_idx=sp_date.index(date)
vol_date_idx=vol_date.index(date)
sp_start_idx=sp_date_idx-50
sp_end_idx=sp_date_idx+50
vol_start_idx=vol_date_idx-50
vol_end_idx=vol_date_idx+50


#plot 200 days around given date
'''
date='2018-12-11'
sp_date_idx=sp_date.index(date)
vol_date_idx=vol_date.index(date)
sp_start_idx=sp_date_idx-100
sp_end_idx=sp_date_idx+100
vol_start_idx=vol_date_idx-100
vol_end_idx=vol_date_idx+100
'''

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