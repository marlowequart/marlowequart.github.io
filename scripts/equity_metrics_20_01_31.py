'''
The purpose of this script is to output a series of metrics to show the quality of
the equity growth.


Input: daily equity value (use output of various trading strategies)

Output: the important metrics:
-CAGR
-Max Drawdown
-Longest Drawdown Period
-MAR ratio
-Sharpe Ratio
-Sortino Ratio
-Skew
-Kurtosis



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


import csv
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import math
import datetime
from scipy.stats import skew,kurtosis


PRINT=True
PLOT=False


input_file='equity1_output.csv'
risk_free_input='data/risk_free_1yr_2yr_clean.csv'
trades_input='sim1_out.csv'

data_df = pd.read_csv(input_file,header=0)
date=data_df['Date'].tolist()
equity=data_df['Equity1'].tolist()

rf_df = pd.read_csv(risk_free_input,header=0)
rf_date=rf_df['Date'].tolist()
rf_rate=rf_df['Rate'].tolist()

trades_df = pd.read_csv(trades_input,header=0)
trades_data=trades_df['profit/loss'].tolist()
trades_dates=trades_df['purchase date'].tolist()
trades_end_dates=trades_df['sale date'].tolist()


#use entire series
'''
start_idx=2
end_idx=17420
'''

#use date range

start_date='1976-06-01'
end_date='2019-03-11'
start_idx=date.index(start_date)
end_idx=date.index(end_date)

rf_start_date='1976-06-01'
rf_end_date='2019-03-11'
rf_start_idx=rf_date.index(rf_start_date)
rf_end_idx=rf_date.index(rf_end_date)

# ~ trades_start_date='1959-07-15'
# ~ trades_end_date='2019-03-11'
# ~ trades_start_idx=rf_date.index(rf_start_date)
# ~ trades_end_idx=rf_date.index(rf_end_date)

print()
#####
# Generate metrics
#####

# elapsed time
start_date_obj=datetime.datetime.strptime(start_date,'%Y-%m-%d')
end_date_obj=datetime.datetime.strptime(end_date,'%Y-%m-%d')
# ~ start_date_obj=datetime.datetime.strptime(start_date,'%m/%d/%y')
# ~ end_date_obj=datetime.datetime.strptime(end_date,'%m/%d/%y')
num_days_obj=end_date_obj-start_date_obj
num_days=num_days_obj.days
num_yrs=num_days/365.25

# CAGR
final_value=equity[end_idx]
initial_value=equity[start_idx]
CAGR=100*((final_value/initial_value)**(1/num_yrs)-1)
if PRINT: print('CAGR: ',round(CAGR,2))
if PRINT: print()

# Max Drawdown and length
new_high=0
new_low=10000000
new_high_day=0
new_low_day=0
max_dd_pct=0
max_dd_length=0
max_dd_start_date_idx=0
for i in range(start_idx,end_idx):
	# check for new high
	if equity[i] > new_high:
		new_high=equity[i]
		new_high_day=i
		new_low=100000000
		new_low_day=0
	else:
		# Check for new low
		if equity[i] < new_low:
			new_low=equity[i]
			new_low_day=i
		# measure the length of this drawdown and determine longest drawdown
		this_dd_length=new_low_day-new_high_day
		if this_dd_length > max_dd_length:
			max_dd_length=this_dd_length
		# check for max drawdown
		today_dd=abs(equity[new_high_day]-equity[i])
		today_dd_pct=today_dd/equity[new_high_day]
		if today_dd_pct > max_dd_pct:
			max_dd_pct=today_dd_pct
			max_dd_start_date_idx=new_high_day
			max_dd_end_date_idx=new_low_day

max_dd=100*max_dd_pct
if PRINT: print('Max drawdown: ',round(max_dd,2),'%')
if PRINT: print('Length of max drawdown is ',max_dd_length,' days, or ',round(max_dd_length/365.25,2),' years')
if PRINT: print('Start date of max drawdown is ',date[max_dd_start_date_idx],', end date is ',date[max_dd_end_date_idx])
if PRINT: print()


# MAR ratio (CAGR/Largest Drawdown)
MAR_ratio=CAGR/max_dd
if PRINT: print('MAR ratio is: ',round(MAR_ratio,2))
if PRINT: print()

#####
# Sharpe/Sortino Ratio based on monthly returns
#####

# Get monthly return info
prev_yr=0
prev_mo=0
day_cnt=0
month_beg=1
month_end=0
equity_returns_pct=[]
for i in range(start_idx,end_idx):
	today=datetime.datetime.strptime(date[i],'%Y-%m-%d')
	# ~ today=datetime.datetime.strptime(date[i],'%m/%d/%y')
	if today.month != prev_mo:
		month_end=equity[i-1]
		equity_returns_pct.append([prev_mo,prev_yr,(month_end-month_beg)/month_beg])
		month_beg=equity[i]
		prev_mo=today.month
		prev_yr=today.year
#remove first two entries
equity_rtns=equity_returns_pct[2:]

# Get monthly avg risk free rate
prev_mo=0
prev_yr=0
month_beg=0
month_end=0
rf_rate_monthly=[]
for i in range(rf_start_idx,rf_end_idx):
	today=datetime.datetime.strptime(rf_date[i],'%Y-%m-%d')
	if today.month != prev_mo:
		month_end=i-1
		rf_rate_monthly.append([prev_mo,prev_yr,np.mean(rf_rate[month_beg:month_end])/100/12])
		prev_mo=today.month
		prev_yr=today.year
		month_beg=i
#remove first two entries
rf_monthly=rf_rate_monthly[2:]

# Get monthly excess return
excess_return_monthly=[]
for x in range(len(equity_rtns)-1):
	if equity_rtns[x][0] != rf_monthly[x][0]:
		print('error, dates do not match')
	elif equity_rtns[x][1] != rf_monthly[x][1]:
		print('error, dates do not match')
	else:
		excess_return_monthly.append(equity_rtns[x][2]-rf_monthly[x][2])
mean_rtns_mo=np.mean(excess_return_monthly)

# Sharpe Ratio
sharpe_monthly=mean_rtns_mo/np.std(excess_return_monthly)
if PRINT: print('Sharpe ratio based on monthly data is: ',round(sharpe_monthly,2))
# ~ if PRINT: print()

# Sortino Ratio
# calculate downside variance
var=[]
for i in range(len(excess_return_monthly)):
	if excess_return_monthly[i] < mean_rtns_mo:
		var.append(abs(excess_return_monthly[i])**2)

downside_std=np.sqrt(np.mean(var))
sortino_monthly=mean_rtns_mo/downside_std
if PRINT: print('Sortino ratio based on monthly data is: ',round(sortino_monthly,2))
# ~ if PRINT: print()


#####
# Sharpe/Sortino Ratio based on yearly returns
#####

# Get yearly return info
prev_yr=0
yr_beg=1
yr_end=0
equity_returns_pct_yr=[]
for i in range(start_idx,end_idx):
	today=datetime.datetime.strptime(date[i],'%Y-%m-%d')
	# ~ today=datetime.datetime.strptime(date[i],'%m/%d/%y')
	if today.year != prev_yr:
		yr_end=equity[i-1]
		equity_returns_pct_yr.append([prev_yr,(yr_end-yr_beg)/yr_beg])
		yr_beg=equity[i]
		prev_yr=today.year
#remove first two entries
equity_rtns_yr=equity_returns_pct_yr[2:]

# Get yearly avg risk free rate
prev_yr=0
yr_beg=0
yr_end=0
rf_rate_yearly=[]
for i in range(rf_start_idx,rf_end_idx):
	today=datetime.datetime.strptime(rf_date[i],'%Y-%m-%d')
	if today.year != prev_yr:
		yr_end=i-1
		rf_rate_yearly.append([prev_yr,np.mean(rf_rate[yr_beg:yr_end])/100])
		prev_yr=today.year
		yr_beg=i
#remove first two entries
rf_yearly=rf_rate_yearly[2:]

# Get yearly excess return
excess_return_yearly=[]
for x in range(len(equity_rtns_yr)):
	if equity_rtns_yr[x][0] != rf_yearly[x][0]:
		print('error, dates do not match')
	else:
		excess_return_yearly.append(equity_rtns_yr[x][1]-rf_yearly[x][1])
mean_rtns_yr=np.mean(excess_return_yearly)

# Sharpe Ratio
sharpe_yearly=mean_rtns_yr/np.std(excess_return_yearly)
if PRINT: print('Sharpe ratio based on yearly data is: ',round(sharpe_yearly,2))
# ~ if PRINT: print()

# Sortino Ratio
# calculate downside variance
var=[]
for i in range(len(excess_return_yearly)):
	if excess_return_yearly[i] < mean_rtns_yr:
		var.append(abs(excess_return_yearly[i])**2)

downside_std=np.sqrt(np.mean(var))
sortino_yearly=mean_rtns_yr/downside_std
if PRINT: print('Sortino ratio based on yearly data is: ',round(sortino_yearly,2))
if PRINT: print()


# Skew/Kurtosis

# first generate list of monthly returns
return_monthly=[]
for x in range(len(equity_rtns)):
	return_monthly.append(equity_rtns[x][2])

rtn_skew=skew(return_monthly)
rtn_kurtosis=kurtosis(return_monthly)

if PRINT: print('The monthly return skew is: ',round(rtn_skew,2))
if PRINT: print('The monthly return kurtosis is: ',round(rtn_kurtosis,2))
if PRINT: print()

####
# Total number of trades over the time frame
####
num_trades=len(trades_data)
trades_per_yr=num_trades/num_yrs

profitable=[]
trade_result_sequence=[]
loss_streak=[]
loss_streak_idx=[]
for i in range(len(trades_data)):
	if trades_data[i] > 0:
		# ~ print('profitable trade started on ',trades_dates[i],', total profit: ',trades_data[i])
		trade_result_sequence.append([trades_dates[i],1])
		profitable.append(trades_data[i])
	else:
		# ~ print('losing trade started on ',trades_dates[i],', total loss: ',trades_data[i])
		if i==0:
			loss_streak.append(0)
			loss_streak_idx.append(i)
		else:
			if trade_result_sequence[i-1][1]==0:
				# ~ print('losing streak increase by one')
				loss_streak.append(loss_streak[-1]+1)
				loss_streak_idx.append(i)
			else:
				# ~ print('start of new streak')
				loss_streak.append(0)
				loss_streak_idx.append(i)
		trade_result_sequence.append([trades_dates[i],0])
		

num_profitable=len(profitable)
longest_loss_streak=max(loss_streak)+1

# find longest losing streak in time

end_idx_idx=[loss_streak.index(max(loss_streak))]

loss_streak_end_idx=[loss_streak_idx[x] for x in end_idx_idx]
loss_streak_start_idx=[]
time_deltas=[]
for idx in loss_streak_end_idx:
	loss_streak_start_idx=idx-longest_loss_streak+1
	loss_start_date=trades_dates[loss_streak_start_idx]
	loss_end_date=trades_end_dates[idx]
	# ~ print('loss streak starts on date: ',loss_start_date,', and ends on date ',loss_end_date)
	# get time delta with datetime objects
	loss_start_date_obj=datetime.datetime.strptime(loss_start_date,'%Y-%m-%d')
	loss_end_date_obj=datetime.datetime.strptime(loss_end_date,'%Y-%m-%d')
	loss_diff=round((loss_end_date_obj-loss_start_date_obj).days/365.25,2)
	time_deltas.append(loss_diff)

# ~ print(loss_streak)



# how long between profitable trades?


# ~ if PRINT: print()
if PRINT: print('Number of profitable trades: ',num_profitable,', win percentage: ',round(100*num_profitable/num_trades,1))
if PRINT: print('Avg trades per year: ',round(trades_per_yr,1),', longest losing streak num trades: ',longest_loss_streak,', longest losing streak in yrs: ',max(time_deltas))


if PRINT: print()
#####
# Plot data
#####
if PLOT:
	# generate plots
	fig = plt.figure()
	# plot equity
	ax = fig.add_subplot(111)
	plt.plot(date[start_idx:end_idx], equity[start_idx:end_idx],color='b')
	plt.ylabel('Dollars')
	plt.xlabel(r'Date')
	plt.title(r'Equity Value')

	grid_num=15
	time_step=int((end_idx-start_idx)/grid_num)
	steps=np.arange(start_idx,end_idx,time_step)
	dates=[date[step] for step in steps]
	ax.set_xticks(dates)

	#use the following to hide dates
	'''
	empty_string_labels = ['']*len(dates)
	ax.set_xticklabels(empty_string_labels)
	'''
	plt.xticks(rotation=90)
	plt.grid()

	plt.show()

