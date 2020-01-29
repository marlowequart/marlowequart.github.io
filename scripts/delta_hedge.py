'''
file name: delta_hedge.py
date: Jan 5, 2020
description: This program runs a simulation for applying a delta hedge strategy over historical data.
	Delta hedge strategy attempts to minimize risks with stock market crashes.
	Stock equity is hedged with put options during times when Faustmann ratio 
	(market cap / net worth) is above a threshold.
	The program can be run in two modes - either as a standalone script, 
	in which case the parameters can be modified on lines 454 onwards.
	Alternatively, the program can be imported as a module and functions 
	delta_hedge.main(), delta_hedge.get_DT_obj() and delta_hedge.get_DT_str()
	can be reused in other scripts.

inputs:
	SIM_START_DATE, line 80, type string YYYY-MM-DD: date on which to start the simulation
	OUTPUT_CSV, line 81, type string: path to output csv file
	STARTING_EQUITY, line 82, type float: starting equity, in $
	STRIKE_AT, line 83, type float: strike price as fraction of underlying
	EXIT_THRESHOLD, line 84, type float: profit threshold at which to exit option trade, in multipliers to purchase price
	SIM_NAME, line 85, type str: simulation name,
	OPT_FRACTION_K, line 86:'constant option fraction',
	OPT_FRACTION_M, line 87:'multiplier to increase option fraction based on volatility'=0,
	FAUSTMANN_R_MIN, line 88:'minimum Faustmann ratio (market cap/net worth) at which to buy options'=0,
	DEBUG, line 89:'set to true to print out full debug info'=False,
	TRADE_DAY_MIN, line 90:'make a trade on a first trading day after this day of the month, YYYY-mm-dd, str'=10,
	COMM_STOCK_PER_UNIT, line 93: commission on trades of stocks per stock
	COMM_STOCK_COST, line 93: commission on trades of stocks % of cost of trade
	COMM_STOCK_FLAT, line 93: commission on trades of stocks flat fee
	LEVERAGE_FACTOR, line 96: leverage factor used in calculating commission on trades of options
	COMM_PER_OPT, line 96: commission on trade of options per contract, rounding up.
	OPT_HOLDING_PARAMS, line 101: Option holding parameters, as dict of lists:
		{'L_VOL':[min. volatility, time to mature, holding period],
		'M_VOL':[min. volatility, time to mature, holding period],
		'H_VOL':[min. volatility, time to mature, holding period]}
	stocks, line 121: path to CSV containing stock prices
	irate, line 122: path to CSV containing interest rates
	corp_net_worth, line 123: path to CSV containing corporate net worth
	corp_market_val, line 124: path to CSV containing corporate market value
	market_filter, line 125: path to CSV containing additional filter

outputs:
	write_out_results(), lines 341-355, writes output to CSV

Python version 3.6.9, used: 
	calendar, # built-in, Python 3.6.9
	csv, # version 1.0
	datetime, # built-in, Python 3.6.9
	dateutil, # version 2.8.0
	functools, # built-in, Python 3.6.9 
	math, # built-in, Python 3.6.9 
	matplotlib, # version 3.1.1
	numpy, # version 1.16.4
	scipy, # version 1.3.1
	time # built-in, Python 3.6.9
'''

import calendar 
import csv
import datetime
from dateutil.relativedelta import relativedelta
from functools import reduce
import math
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm
import time
import pandas


# Functions to convert from string to datetime and vice-versa

def get_DT_obj(date_time_str:str) -> datetime.datetime:
	return datetime.datetime.strptime(date_time_str,'%Y-%m-%d')

def get_DT_str(date_time_obj:datetime.datetime) -> str:
	return datetime.datetime.strftime(date_time_obj,'%Y-%m-%d')

## Constants
OPTION_PR_ROUNDING=5 # round option prices to 1/10th of a pip

def main(SIM_START_DATE:'start date, YYYY-mm-dd, str',
	OUTPUT_CSV:str,
	STARTING_EQUITY:float,
	STRIKE_AT:'strike price, as fraction of underlying, float',
	EXIT_THRESHOLD:'profit threshold at which to exit option trade, as multipliers to purchase price, float',
	SIM_NAME:'simulation name for error analysis',
	OPT_FRACTION_K:'constant option fraction',
	OPT_FRACTION_M:'multiplier to increase option fraction based on volatility'=0,
	FAUSTMANN_R_MIN:'minimum Faustmann ratio (market cap/net worth) at which to buy options'=0,
	DEBUG:'set to true to print out full debug info'=False,
	TRADE_DAY_MIN:'make a trade on a first trading day after this day of the month, YYYY-mm-dd, str'=10,
	## Define commission on trades of stocks:
	# $2 per stock + 0% of the cost of the trade + $0 flat fee
	COMM_STOCK_PER_UNIT=2,COMM_STOCK_COST=0,COMM_STOCK_FLAT=0,
	## Define commission on trades of options:
	# $2 per 50 options (using S&P emini 50x), rounding up
	LEVERAGE_FACTOR=50,COMM_PER_OPT=2,
	# Option holding parameters, as dict of lists:
	# {'L_VOL':[min. volatility, time to mature, holding period],
	#  'M_VOL':[min. volatility, time to mature, holding period],
	#  'H_VOL':[min. volatility, time to mature, holding period]}
	OPT_HOLDING_PARAMS:"{'L_VOL':[min. volatility,time to mature,holding period],'M_VOL'://,'H_VOL'://}"={
			'L_VOL':[0,   12, 4],
			'M_VOL':[0.2,  6, 2],
			'H_VOL':[0.4,  3, 1]}
	):

	## INPUT DATA ##

	# Class to read data from CSV and store rows and headers
	class table():
		def __init__(self,filepath):
			try:
				with open(filepath) as _:
					reader=csv.reader(_)
					self.headers=next(reader)
					self.data=[_ for _ in reader]
			except:
				print('File %s not found'%filepath)

	# Collect data from CSVs
	stocks=table('data/^GSPC.csv')
	irate=table('data/risk_free_1yr_2yr_clean.csv')
	corp_net_worth=table('data/corp_net_worth.csv')
	corp_market_val=table('data/Corp_market_value.csv')
	volatility=table('data/volatility40.csv')
	market_filter=table('data/market_filter.csv') # only necessary when including additional filters
	datasets=[stocks,irate,corp_net_worth,corp_market_val,volatility]

	## DEFINE HELPER FUNCTIONS ##
	TRADING_COST_STOCK = lambda size, price: COMM_STOCK_PER_UNIT*size + COMM_STOCK_COST*size*price + COMM_STOCK_FLAT
	TRADING_COST_OPTION = lambda size: math.ceil(size/LEVERAGE_FACTOR)*COMM_PER_OPT

	# Purchase only put options
	##~ Note that we need to divide t by 252, the working days in the year
	## Note that we need to divide t by 356, the total days in the year

	# Function to compute price of put option
	def compute_put_opt_price(S:'Current underlying price',K:'strike price',
			r:'risk-free interest rate',t:'time to maturity(in days)',
			v:'volatility') -> 'price':
		#~ t/=252 # fraction of the year
		t/=365 # fraction of the year
		d1=(math.log(S/K)+t*(r+((v**2)/2)))/(v*math.sqrt(t))
		d2=d1-(v*math.sqrt(t))
		# calculate standard normal cumulative distribution function (mean=0, std=1)
		nd1=norm.cdf(-d1)
		nd2=norm.cdf(-d2)
		p=K*math.exp(-r*t)*nd2-S*nd1
		return p

	# Class to namespace functions that return a value given dates
	class getter_for_date():
		def __init__(self):
			pass
		def market_price(self,date:str) -> float:
			# Get market price for a matching date
			return float([_ for _ in stocks.data if _[0]==date][0][2])
		def irate(self,date:str) -> float:
			# Get interest rate for a matching date
			return float([_ for _ in irate.data if _[0]==date][0][1])/100
		def volatility(self,date:str) -> float:
			# Get real volatility for a matching date
			return float([_ for _ in volatility.data if _[0]==date][0][1])/100
		def net_worth(self,date:str) -> float:
			# Get net worth for a matching date
			times=[get_DT_obj(_[0]) for _ in corp_net_worth.data]
			return float(corp_net_worth.data[times.index([_ for _ in times if _<=get_DT_obj(date)][-1])][1])
		def market_val(self,date:str) -> float:
			# Get market value 
			times=[get_DT_obj(_[0]) for _ in corp_market_val.data]
			return float(corp_market_val.data[times.index([_ for _ in times if _<=get_DT_obj(date)][-1])][1])
		def faustmann_ratio(self,date:str) -> float:
			# Compute Faustmann ratio, which is market cap/net worth
			return (self.market_val(date)/1000)/get_for_date.net_worth(date)
		def put_opt_price(self,purchase_date:str, current_date:str, expire_date:str) -> dict:
			purchase_volatility=self.volatility(purchase_date)
			current_volatility=self.volatility(current_date)
			# Get strike and current price of a put option given purchase, current and expiry dates.
			# Calculate strike price at reference (purchase) date
			S_ref=self.market_price(purchase_date)
			r_ref=self.irate(purchase_date)
			t_ref=(get_DT_obj(expire_date)-get_DT_obj(purchase_date)).days
			v_ref=self.volatility(purchase_date)
			### Find K as proportional to reference strike
			K=S_ref*STRIKE_AT
			# Calculate today's option price
			S=self.market_price(current_date)
			r=self.irate(current_date)
			t=(get_DT_obj(expire_date)-get_DT_obj(current_date)).days
			v=self.volatility(current_date)
			opt_price=compute_put_opt_price(S, K, r, t, v)
			return {'K':K,'price':opt_price}
		def check_filter(self,date):
			return bool(int([_ for _ in market_filter.data if _[0]==date][0][1]))

	# Initialize this class
	get_for_date=getter_for_date()

	## Calculate valid time bounds - simulation should not extend beyound first and last days on the datasets.
	FIRST_VALID_DATE=max(map(get_DT_obj,map(lambda _:_[0][0],[_.data for _ in datasets])))
	LAST_VALID_DATE=min(map(get_DT_obj,map(lambda _:_[-1][0],[_.data for _ in datasets])))

	# Function to confirm that a particular date is present in all datasets
	def check_date(date: str, datasets: list):
		return reduce((lambda x, y: x * y), [date in [_[0] for _ in _] for _ in datasets] )

	# Get the next closest valid date
	def get_next_valid_date(date: str, datasets=[stocks.data,irate.data]):
		LAST_VALID_DT=min(map(get_DT_obj,map(lambda _:_[-1][0],datasets)))
		while True:
			# To the given date add one day at a time until a valid date is found
			# Return that date
			if check_date(date, datasets):
				return date
			if get_DT_obj(date)<LAST_VALID_DT:
				date=get_DT_str( get_DT_obj(date)+datetime.timedelta(days=1) )
			else:
				return False

	# U.S. equity stock option contracts expire on third friday of the month
	def get_third_friday(my_year: int, my_month: int) -> datetime.date:
		c = calendar.Calendar(firstweekday=calendar.SATURDAY)
		monthcal = c.monthdatescalendar(my_year, my_month)
		monthly_expire_date = monthcal[2][-1]
		return monthly_expire_date

	# Compute days to maturity from date of purchase
	def get_days_to_expire(tradeDate: datetime.datetime):
		newDate_far=tradeDate+datetime.timedelta(days=OPT_TIME_TO_MATURE*30)
		return (get_third_friday(newDate_far.year,newDate_far.month) - tradeDate.date()).days

	# Determine the next trade day first day after the 10th of the month after the holding period
	def make_nxt_trade_date(lastTradeDate):
		lastTradeDate=get_DT_obj(lastTradeDate)
		return get_next_valid_date(get_DT_str(datetime.datetime(lastTradeDate.year,lastTradeDate.month,10)+relativedelta(months=+OPT_HOLDING_PERIOD)))

	# Compute net worth (total equity)
	def get_net_worth(equity, this_trade_day):
		# add stocks and cash
		stocks_and_cash=equity['stocks'] * get_for_date.market_price(this_trade_day)+equity['cash']
		if equity['options']['bought']:
			# if holding any options add options
			return round(stocks_and_cash+equity['options']['count']*get_for_date.put_opt_price(equity['options']['bought'],this_trade_day,equity['options']['expire'])['price'],2)
		else:
			# otherwise return only stocks and cash
			return round(stocks_and_cash,2)

	## DEFINE TRADING FUNCTIONS ##

	def buy_stocks(cash:float,this_trade_day:str):
		# compute how many stocks we can buy with our cash, while accounting for transaction costs
		stocks_buy_vol=(cash-COMM_STOCK_FLAT)//(
			get_for_date.market_price(this_trade_day)+COMM_STOCK_PER_UNIT+
			COMM_STOCK_COST*get_for_date.market_price(this_trade_day))
		# add bought stocks to equity
		equity['stocks']+=stocks_buy_vol
		# find out how much cash was spent
		cashChange=(stocks_buy_vol*get_for_date.market_price(this_trade_day)+
				TRADING_COST_STOCK(stocks_buy_vol,get_for_date.market_price(this_trade_day)))
		# subtract spent cash from equity
		equity['cash']=round(equity['cash']-cashChange,2)

	def sell_stocks(cash:float,this_trade_day:str):
		# compute how many stocks to sell to get needed cash
		stocks_sell_vol=math.ceil(cash/get_for_date.market_price(this_trade_day))
		# subtract sold stocks from equity
		equity['stocks']-=stocks_sell_vol
		# add cash minus transaction fees
		equity['cash']=round(equity['cash']+stocks_sell_vol*get_for_date.market_price(this_trade_day)-
				TRADING_COST_STOCK(stocks_sell_vol,get_for_date.market_price(this_trade_day)),2)
			
	def buy_options():
		if DEBUG: print('Buying options right now')
		vol_current=get_for_date.volatility(this_trade_day)
		if DEBUG: print('current vol for ',this_trade_day,' : ',round(vol_current,3),' underlying: ',round(get_for_date.market_price(this_trade_day),2),' risk free rate ',round(get_for_date.irate(this_trade_day),4))
		# compute how much money to spend to fullfil the option fraction
		trade_value=get_net_worth(equity, this_trade_day)*(OPT_FRACTION)
		# compute number of days before desired expiry date
		days_to_expire=get_days_to_expire(get_DT_obj(this_trade_day))
		# compute expiry date
		expire_date=get_DT_str(get_DT_obj(this_trade_day)+datetime.timedelta(days_to_expire))
		# compute option price
		options_price=round(get_for_date.put_opt_price(this_trade_day,this_trade_day,expire_date)['price'],OPTION_PR_ROUNDING)
		option_strike=round(get_for_date.put_opt_price(this_trade_day,this_trade_day,expire_date)['K'],2)
		# compute how many options to buy accounting for the commission
		options_vol=trade_value//(options_price+COMM_PER_OPT/LEVERAGE_FACTOR)
		# compute option trade cost
		trade_cost=options_vol*options_price+TRADING_COST_OPTION(options_vol)
		if DEBUG: print("new options price is ",options_price,' expiration date: ',expire_date,' days to expire: ',days_to_expire,' Strike: ',option_strike,' number purchased: ',options_vol) # DEBUG
		if DEBUG: print('cost of options: ',round(trade_cost,2),' net worth ',round(get_net_worth(equity, this_trade_day),2))
		# find out how much cash needed
		missing_cash=trade_cost-equity['cash']
		# if we have more than enough cash
		if missing_cash<0:
			# buy stocks
			buy_stocks(-missing_cash,this_trade_day)
		else:
			# otherwise sell stocks
			sell_stocks(missing_cash,this_trade_day)
		# add options to equity
		equity['options']['count']=options_vol
		equity['options']['bought']=this_trade_day
		equity['options']['expire']=expire_date
		# calculate cash spent on options
		spent_cash=round(options_price*options_vol+TRADING_COST_OPTION(options_vol),2)
		# subtract spent cash from equity
		equity['cash']=round(equity['cash']-spent_cash,2)
		# return change in cash
		return -spent_cash

	def sell_options():
		if DEBUG: print('Selling options right now')
		vol_current=get_for_date.volatility(this_trade_day)
		if DEBUG: print('current vol for ',this_trade_day,' : ',round(vol_current,3),' underlying: ',round(get_for_date.market_price(this_trade_day),2),' risk free rate: ',round(get_for_date.irate(this_trade_day),4))
		# compute how much previous options cost today
		oldOptPrice=get_for_date.put_opt_price(equity['options']['bought'],this_trade_day,equity['options']['expire'])['price']
		old_option_strike=round(get_for_date.put_opt_price(equity['options']['bought'],this_trade_day,equity['options']['expire'])['K'],2)
		old_option_expire=equity['options']['expire']
		if DEBUG: print('current value of previous options: ',oldOptPrice,' strike: ',old_option_strike,' expiration: ',old_option_expire,' number of opts held: ',TRADING_COST_OPTION(equity['options']['count']))
		# compute returns from sale of options
		option_returns=equity['options']['count']*oldOptPrice-TRADING_COST_OPTION(equity['options']['count'])
		# add earned cash to equity
		equity['cash']=round(equity['cash']+option_returns,2)
		# writeout results
		write_out_results()
		# remove options from equity
		equity['options']['count']=0
		equity['options']['bought']=''
		equity['options']['expire']=''
		# return change in cash
		return option_returns


	## SET UP OUTPUT CSV AND DEFINE OUTPUT FUNCTION ##
	f=open(OUTPUT_CSV,'w')
	csv_writer=csv.writer(f)
	csv_writer.writerow(['purchase date','sale date', 'purchase underlying price',
				'sale underlying price','contracts number','equity after sale of options',
				'option price at purchase','option price at sale','profit/loss'])

	def write_out_results():
		# write row in csv, 
		# the header is defined below, at the start of the simulation
		opt_pr_purchase=round(get_for_date.put_opt_price(equity['options']['bought'],equity['options']['bought'],equity['options']['expire'])['price'],OPTION_PR_ROUNDING)
		opt_pr_sale=round(get_for_date.put_opt_price(equity['options']['bought'],this_trade_day,equity['options']['expire'])['price'],OPTION_PR_ROUNDING)
		opt_trade_profit=round((opt_pr_sale-opt_pr_purchase)*equity['options']['count']-TRADING_COST_OPTION(equity['options']['count']),2)
		csv_writer.writerow( [equity['options']['bought'],
			this_trade_day,
			get_for_date.market_price(equity['options']['bought']),
			get_for_date.market_price(this_trade_day),
			equity['options']['count'],
			get_net_worth(equity, this_trade_day),
			opt_pr_purchase,
			opt_pr_sale,
			opt_trade_profit])

	def updateConstants():
		global TRADE_DELTA
		global OPT_FRACTION
		global OPT_TIME_TO_MATURE
		global OPT_HOLDING_PERIOD
		current_volatility=get_for_date.volatility(this_trade_day)
		OPT_FRACTION=OPT_FRACTION_K+OPT_FRACTION_M*current_volatility
		OPT_FRACTION=0 if OPT_FRACTION<0 else OPT_FRACTION
		## Update option holding params based on volatility
		if current_volatility < OPT_HOLDING_PARAMS['M_VOL'][0]:
			OPT_TIME_TO_MATURE=OPT_HOLDING_PARAMS['L_VOL'][1]
			OPT_HOLDING_PERIOD=OPT_HOLDING_PARAMS['L_VOL'][2]
		elif current_volatility < OPT_HOLDING_PARAMS['H_VOL'][0]:
			OPT_TIME_TO_MATURE=OPT_HOLDING_PARAMS['M_VOL'][1]
			OPT_HOLDING_PERIOD=OPT_HOLDING_PARAMS['M_VOL'][2]
		else:
			OPT_TIME_TO_MATURE=OPT_HOLDING_PARAMS['H_VOL'][1]
			OPT_HOLDING_PERIOD=OPT_HOLDING_PARAMS['H_VOL'][2]

	## RUN SIMULATION ##
	# dict to store equity curve
	# format is [0:Date, 1:net_worth, 2:Faustmann_ratio, 3:option_returns, 4:number_of_S&P_index_held, 5:S&P_price_today, 6:num_options_held, 7:options_price]
	equity_curve=[]
	# set starting equity
	equity={'stocks':0,
		'options':{'count':0,'bought':None,'expire':None}, 
		'cash':STARTING_EQUITY}
	# determine the first trade day
	this_trade_day=get_next_valid_date(SIM_START_DATE)
	last_trade_day=this_trade_day
	# begin main simulation loop and continue until the last valid date in the dataset
	while get_DT_obj(this_trade_day)<LAST_VALID_DATE:
		if DEBUG: print()
		if DEBUG: print(SIM_NAME,' looping over date: ',this_trade_day)
		updateConstants()
		# set up variable to store returns from option sales
		option_returns=0
		# compute Faustmann ratio
		faustmann_ratio=get_for_date.faustmann_ratio(this_trade_day)
		# use Faustmann ratio to determine how to trade
		if faustmann_ratio>FAUSTMANN_R_MIN:
		# Replace above line with uncommented next to add another filter
		#~ if faustmann_ratio>FAUSTMANN_R_MIN and get_for_date.check_filter(this_trade_day):
			if equity['options']['count']:
				if DEBUG: print('ROLL OPTIONS')
				option_returns+=sell_options()
				option_returns+=buy_options()
			else:
				if DEBUG: print('\nSELL STOCKS AND BUY OPTIONS\n')
				option_returns+=buy_options()
		else:
			if equity['options']['count']:
				if DEBUG: print('SELL OPTIONS AND BUY STOCKS')
				option_returns+=sell_options()
				buy_stocks(equity['cash'],this_trade_day)
			else:
				if DEBUG: print('REMAIN AS IS')
				buy_stocks(equity['cash'],this_trade_day)
		opt_current_price_1 = get_for_date.put_opt_price(equity['options']['bought'], this_trade_day, equity['options']['expire'])['price']
		equity_curve.append([this_trade_day,get_net_worth(equity, this_trade_day),faustmann_ratio,option_returns,equity['stocks'],get_for_date.market_price(this_trade_day),equity['options']['count'],opt_current_price_1])
		# Move on to the next date
		last_trade_day=this_trade_day
		this_trade_day=make_nxt_trade_date(last_trade_day)
		## EXIT STRATEGY BEGINS HERE
		if DEBUG: print('TESTING EXIT NOW')
		# only run exit strategy if there are options in the portfolio
		if equity['options']['count']:
			# define local loop helper functions
			get_holding_opt_price = lambda _: get_for_date.put_opt_price(equity['options']['bought'], _, equity['options']['expire'])['price']
			iter_day_funct = lambda _: get_next_valid_date( get_DT_str( get_DT_obj(_)+datetime.timedelta(days=1) ) )
			# define local loop constants
			opt_start_price = get_holding_opt_price(last_trade_day)
			opt_exp_date = get_DT_obj(equity['options']['expire'])
			# keep track of the last trade day
			_ = last_trade_day
			# iterate over all days until the next trade day
			while _ != this_trade_day:
				# step to the next day
				_ = iter_day_funct(_)
				# check option price now
				opt_current_price = get_holding_opt_price(_)
				# count how many days to expire are left
				days_to_expire = (opt_exp_date-get_DT_obj(_)).days
				if DEBUG: print('now testing date ',_,
						' volatility: ',round(get_for_date.volatility(_),3),
						' opt price: ',round(opt_current_price,OPTION_PR_ROUNDING),
						' underlying: ',round(get_for_date.market_price(_),2),
						' days to expiry: ',days_to_expire,
						' risk free rate ',round(get_for_date.irate(_),4))
				# check if threshold is exceeded
				if opt_current_price > opt_start_price*EXIT_THRESHOLD:
					if DEBUG: print('    hit an exit threshold on date ',_)
					if DEBUG: print("    opt_current_price:",round(opt_current_price,2))
					# if so, then sell options on current day and re-run main loop now
					this_trade_day = _
					option_returns += sell_options()
					# Can use this next line to show dates where trades happen in equity curve. Otherwise comment out to not repeat days in equity curve
					# equity_curve.append([this_trade_day,get_net_worth(equity, this_trade_day),faustmann_ratio,option_returns,equity['stocks'],get_for_date.market_price(this_trade_day),equity['options']['count'],opt_current_price])
					break
				# 1/21/19 adding this line for full equity output
				else:
					equity_curve.append([_,get_net_worth(equity, _),faustmann_ratio,option_returns,equity['stocks'],get_for_date.market_price(_),equity['options']['count'],opt_current_price])
	## Close output file
	f.close()
	return equity_curve


# The following code is only executed if this is run as a stand-alone script,
# when this program is imported as a module the following will be ignored:
if __name__ == "__main__":
	
	print('Start time to run script:')
	print(datetime.datetime.now())
	
	start_time = time.time()
	# start_date='2008-06-10'
	start_date='1959-07-15'
	# ~ start_date='1988-06-10'
	start_equity=100000
	
	equity_curve1=main(SIM_START_DATE=start_date,
		OUTPUT_CSV='output_standalone1.csv',
		STARTING_EQUITY=start_equity,
		OPT_FRACTION_K=0.03,OPT_FRACTION_M=0,
		STRIKE_AT=0.8,
		# The Faustmann ratio is market cap/net worth
		FAUSTMANN_R_MIN=0,
		# Fraction at which to exit the option trade
		EXIT_THRESHOLD=10,
		SIM_NAME='Simulation 1',
		DEBUG=False,
		OPT_HOLDING_PARAMS={
			'L_VOL':[0,   12, 4],
			'M_VOL':[0.2,  6, 3],
			'H_VOL':[0.4,  3, 1]})
	
	# ~ equity_curve2=main(SIM_START_DATE=start_date,
		# ~ OUTPUT_CSV='out_data2.csv',
		# ~ STARTING_EQUITY=start_equity,
		# ~ OPT_FRACTION_K=0.005,OPT_FRACTION_M=0,
		# ~ STRIKE_AT=0.7,
		# ~ # The Faustmann ratio is market cap/net worth
		# ~ FAUSTMANN_R_MIN=0,
		# ~ # Fraction at which to exit the option trade
		# ~ EXIT_THRESHOLD=5,
		# ~ SIM_NAME='Simulation 2')
	
	
	# Save equity curve to .csv
	date_output1=[_[0] for _ in equity_curve1]
	equity_curve1_output=[_[1] for _ in equity_curve1]
	num_stocks1=[round(_[4],4) for _ in equity_curve1]
	price_stocks1=[round(_[5],4) for _ in equity_curve1]
	stocks_value1=[round(_[4]*_[5],4) for _ in equity_curve1]
	options_value1=[round(_[1]-(_[4]*_[5]),4) for _ in equity_curve1]
	num_options1=[_[6] for _ in equity_curve1]
	options_value1_2=[_[7] for _ in equity_curve1]
	
	# Use this line for debugging:
	# df1=pandas.DataFrame({'Date':date_output1, 'Equity1':equity_curve1_output, 'num_stocks':num_stocks1, 'price_stocks':price_stocks1, 'stocks_value':stocks_value1, 'options_value_calc':options_value1, 'num_options':num_options1, 'options_value_reported':options_value1_2})
	# Use this line for output for analytics:
	df1=pandas.DataFrame({'Date':date_output1, 'Equity1':equity_curve1_output})
	df1.to_csv('_equity1_output_01_29_20.csv', sep=',', index=False)
	
	print()
	print('%f seconds to run script' % (time.time() - start_time))
	print()
	
	## PLOT ##

	# Plot equity curve
	plt.plot([get_DT_obj(_[0]) for _ in equity_curve1],[_[1] for _ in equity_curve1],'r')
	# ~ plt.plot([get_DT_obj(_[0]) for _ in equity_curve2],[_[1] for _ in equity_curve2],'b')

	# ~ plt.plot([get_DT_obj(_[0]) for _ in equity_curve],[_[3]*10 for _ in equity_curve])
	# ~ plt.plot([get_DT_obj(_[0]) for _ in equity_curve],[_[3] for _ in equity_curve])
	# ~ plt.plot([get_DT_obj(_[0]) for _ in equity_curve],[get_for_date.market_price(_[0])*100 for _ in equity_curve])

	# To plot returns from option trades uncomment next two lines
	# ~ plt.plot([get_DT_obj(_[0]) for _ in equity_curve],[_[-1] for _ in equity_curve])
	# ~ plt.axhline(y=0, color='r', linestyle='-')

	plt.show()


#####
#
# Notes:
#
#####
'''
Time to run 10yrs: 

'''
