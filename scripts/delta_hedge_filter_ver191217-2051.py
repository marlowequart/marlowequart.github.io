'''
file name: delta_hedge_ver191028-1149.py
date: October 28, 2019
description: Script runs a simulation for applying a delta hedge strategy over historical data.
	Delta hedge strategy attempts to minimize risks with stock market crashes.
	Stock equity is hedged with put options during times when Faustmann ratio 
	(market cap / net worth) is above a threshold.
	The following parameters can be adjust

inputs:
	SIM_START_DATE, line 55, type string YYYY-MM-DD: date on which to start the simulation
	OUTPUT_CSV, line 57, type string: path to output csv file
	STARTING_EQUITY, line 60, type float: starting equity, in $
	OPT_FRACTION, line 61, type float: fraction of equity to spend on options
	OPT_HOLDING_PERIOD, line 64, type int: holding time in months
	OPT_TIME_TO_MATURE, line 65, type int: time to maturity in months at option purchase
	TRADE_DAY_MIN, line 68, type int: day of the month at or after which the trade should be executed
	FAUSTMANN_R_MIN, line 71, type float: Faustmann ratio threshold
	TRADE_DELTA, line 74, type float: trade delta
	IMPLIED_VOLATILITY, line 75, type float: implied volatility
	COMM_STOCK_PER_UNIT, line 79, type float: stock broker commission per unit
	COMM_STOCK_COST, line 80, type float: stock broker commission on precent of sale
	COMM_STOCK_FLAT, line 81, type float: stock broker flat commission on trade
	LEVERAGE_FACTOR, line 86, type float: option broker leverage factor
	COMM_PER_OPT, line 87, type float: option broker commission per contract
	stocks, line 107: path to CSV containing stock prices
	irate, line 108: path to CSV containing interest rates
	corp_net_worth, line 109: path to CSV containing corporate net worth
	corp_market_val, line 110: path to CSV containing corporate market value
	market_filter, line 111: path to CSV containing additional filter

outputs:
	write_out_results(), lines 312-328, writes output to CSV

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


## INPUT CONSTANTS ##

SIM_START_DATE='1988-06-10'
#SIM_START_DATE='2015-06-10'

OUTPUT_CSV='out_data.csv'

# Define the basic portfolio parameters
STARTING_EQUITY = 100000 # $100,000
#OPT_FRACTION_K = -0.5/100#0.5/100 # 0.5%
OPT_FRACTION_K = 0.005#0.01 #0.005
OPT_FRACTION_M = 0
#OPT_FRACTION = 5/100 # 0.5%

# Define option time parameters
OPT_HOLDING_PERIOD = 1 # months
OPT_TIME_TO_MATURE = 3 # months
#OPT_TIME_TO_MATURE = 6 # months

# Make a trade on first trading day in this range:
TRADE_DAY_MIN = 10 # 10th of the month

# The Faustmann ratio is market cap/net worth
FAUSTMANN_R_MIN = 0#1.0 #1.1#0.6 # If below this value, make equity 100%

# Option settings
#TRADE_DELTA = -0.01
#TRADE_DELTA = -0.005
#TRADE_DELTA = -0.02
#TRADE_DELTA = -0.1
TRADE_DELTA_K = 0#-0.01
#TRADE_DELTA_K = -0.01
#TRADE_DELTA=TRADE_DELTA_K
TRADE_DELTA_M = -0.1
#TRADE_DELTA_M = 0
#IMPLIED_VOLATILITY = 30/100 # 30%

# Fraction at which to exit the option trade
EXIT_THRESHOLD=5


## Define commission on trades of stocks:
# $2 per stock + 0% of the cost of the trade + $0 flat fee
COMM_STOCK_PER_UNIT=2
COMM_STOCK_COST=0
COMM_STOCK_FLAT=0
TRADING_COST_STOCK = lambda size, price: COMM_STOCK_PER_UNIT*size + COMM_STOCK_COST*size*price + COMM_STOCK_FLAT

## Define commission on trades of options:
# $2 per 50 options (using S&P emini 50x), rounding up
LEVERAGE_FACTOR = 50
COMM_PER_OPT=2
TRADING_COST_OPTION = lambda size: math.ceil(size/LEVERAGE_FACTOR)*COMM_PER_OPT


## INPUT DATA ##

# Class to read data from CSV and store rows and headers
class table():
	def __init__(self,filepath):
		with open(filepath) as _:
			reader=csv.reader(_)
			self.headers=next(reader)
			self.data=[_ for _ in reader]

# Collect data from CSVs
stocks=table('data/^GSPC.csv')
irate=table('data/DGS2clean.csv')
corp_net_worth=table('data/corp_net_worth.csv')
corp_market_val=table('data/Corp_market_value.csv')
volatility=table('data/volatility40.csv')
market_filter=table('data/market_filter.csv')
datasets=[stocks,irate,corp_net_worth,corp_market_val,volatility]


## DEFINE HELPER FUNCTIONS ##

# Purchase only put options
## Note that we need to divide t by 252, the working days in the year
## To find K we use a fraction of the year for t.

# Function to compute strike of put option
def put_greeks_k(S:'Current underlying price',
		delta,r:'risk-free interest rate',
		t:'time to maturity(in days)',v:'volatility') -> 'strike price':
	t/=252
	# calculate standard normal cumulative distribution
	nd1=delta/math.exp(-r*t) + 1
	delta=math.exp(-r*t)*(nd1-1)
	# compute inverse of the standard normal cumulative distribution function (mean=0, std=1)
	d1=norm.ppf(nd1)
	K=S/(math.e**(v*math.sqrt(t)*d1 - t*(r+(v**2/2))))
	return K

# Function to compute price of put option
def put_opt_price(S:'Current underlying price',K:'strike price',
		r:'risk-free interest rate',t:'time to maturity(in days)',
		v:'volatility') -> 'price':
	t/=252 # fraction of the year
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
		#print(current_date)
		purchase_volatility=self.volatility(purchase_date)
		current_volatility=self.volatility(current_date)
		#print(IMPLIED_VOLATILITY)
		# Get strike and current price of a put option given purchase, current and expiry dates.
		# Calculate strike price at reference (purchase) date
		S_ref=self.market_price(purchase_date)
		r_ref=self.irate(purchase_date)
		t_ref=(get_DT_obj(expire_date)-get_DT_obj(purchase_date)).days
		v_ref=self.volatility(purchase_date)
		#print("IMPLIED_VOLATILITY",IMPLIED_VOLATILITY)#debug
		delta_ref=TRADE_DELTA_K+TRADE_DELTA_M*v_ref
		K=put_greeks_k(S_ref,delta_ref,r_ref,t_ref,v_ref)
		# ~ print('Strike price of option: ',K)
		# Calculate today's option price
		S=self.market_price(current_date)
		r=self.irate(current_date)
		t=(get_DT_obj(expire_date)-get_DT_obj(current_date)).days
		v=self.volatility(current_date)
		opt_price=put_opt_price(S, K, r, t, v)
		#print(purchase_date,current_date,expire_date,opt_price,"\n")
		#print('put_opt_price params:',S, K, r, t, v)
		return {'K':K,'price':opt_price}
	def check_filter(self,date):
		return bool(int([_ for _ in market_filter.data if _[0]==date][0][1]))


# Initialize this class
get_for_date=getter_for_date()

# Functions to convert from string to datetime and vice-versa
get_DT_obj=lambda _: datetime.datetime.strptime(_,'%Y-%m-%d')
get_DT_str=lambda _: datetime.datetime.strftime(_,'%Y-%m-%d')

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

def buy_stocks(cash,this_trade_day):
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

def sell_stocks(cash,this_trade_day):
	# compute how many stocks to sell to get needed cash
	stocks_sell_vol=math.ceil(cash/get_for_date.market_price(this_trade_day))
	# subtract sold stocks from equity
	equity['stocks']-=stocks_sell_vol
	# add cash minus transaction fees
	equity['cash']=round(equity['cash']+stocks_sell_vol*get_for_date.market_price(this_trade_day)-
			TRADING_COST_STOCK(stocks_sell_vol,get_for_date.market_price(this_trade_day)),2)
		
def buy_options():
	print('Buying options right now')
	vol_current=get_for_date.volatility(this_trade_day)
	print('current vol for ',this_trade_day,' : ',round(vol_current,3),' underlying: ',round(get_for_date.market_price(this_trade_day),2))
	# compute how much money to spend to fullfil the option fraction
	trade_value=get_net_worth(equity, this_trade_day)*(OPT_FRACTION)
	# compute number of days before desired expiry date
	days_to_expire=get_days_to_expire(get_DT_obj(this_trade_day))
	# compute expiry date
	expire_date=get_DT_str(get_DT_obj(this_trade_day)+datetime.timedelta(days_to_expire))
	# compute option price
	options_price=round(get_for_date.put_opt_price(this_trade_day,this_trade_day,expire_date)['price'],2)
	option_strike=round(get_for_date.put_opt_price(this_trade_day,this_trade_day,expire_date)['K'],2)
	# compute how many options to buy accounting for the commission
	options_vol=trade_value//(options_price+COMM_PER_OPT/LEVERAGE_FACTOR)
	# compute option trade cost
	trade_cost=options_vol*options_price+TRADING_COST_OPTION(options_vol)
	print("new options price is ",options_price,' expiration date: ',expire_date,' Strike: ',option_strike,' number purchased: ',options_vol) # DEBUG
	print('cost of options: ',round(trade_cost,2),' net worth ',round(get_net_worth(equity, this_trade_day),2))
	# find out how much cash needed
	missing_cash=trade_cost-equity['cash']
#	#print("Current stock price is", get_for_date.market_price(this_trade_day)) # DEBUG
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
#	#print('we bought options ',options_price*options_vol) # DEBUG
	# calculate cash spent on options
	spent_cash=round(options_price*options_vol+TRADING_COST_OPTION(options_vol),2)
	# subtract spent cash from equity
	equity['cash']=round(equity['cash']-spent_cash,2)
	# return change in cash
	#print(options_price*options_vol/get_net_worth(equity, this_trade_day))
	#print(round(get_for_date.put_opt_price(equity['options']['bought'],equity['options']['bought'], equity['options']['expire'])['price'],2))
	#print("buyopt dates:",equity['options']['bought'],equity['options']['bought'],equity['options']['expire'])
	#print("buyopt options_price:",round(get_for_date.put_opt_price(equity['options']['bought'],equity['options']['bought'], equity['options']['expire'])['price'],2))
	return -spent_cash

def sell_options():
	print('Selling options right now')
	vol_current=get_for_date.volatility(this_trade_day)
	print('current vol for ',this_trade_day,' : ',round(vol_current,3),' underlying: ',round(get_for_date.market_price(this_trade_day),2))
	# compute how much previous options cost today
	oldOptPrice=get_for_date.put_opt_price(equity['options']['bought'],this_trade_day,equity['options']['expire'])['price']
	old_option_strike=round(get_for_date.put_opt_price(equity['options']['bought'],this_trade_day,equity['options']['expire'])['K'],2)
	old_option_expire=equity['options']['expire']
	print('current value of previous options: ',oldOptPrice,' strike: ',old_option_strike,' expiration: ',old_option_expire,' number of opts held: ',TRADING_COST_OPTION(equity['options']['count']))
	# compute returns from sale of options
	option_returns=equity['options']['count']*oldOptPrice-TRADING_COST_OPTION(equity['options']['count'])
	print('total return on sale: ',option_returns)
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
			'option price at purchase','option price at sale'])

def write_out_results():
	# write row in csv, 
	# the header is defined below, at the start of the simulation
	csv_writer.writerow( [equity['options']['bought'],
		this_trade_day,
		get_for_date.market_price(equity['options']['bought']),
		get_for_date.market_price(this_trade_day),
		equity['options']['count'],
		get_net_worth(equity, this_trade_day),
		round(get_for_date.put_opt_price(equity['options']['bought'],equity['options']['bought'],equity['options']['expire'])['price'],2),
		round(get_for_date.put_opt_price(equity['options']['bought'],this_trade_day,equity['options']['expire'])['price'],2) ])
	#print("writeout dates:",equity['options']['bought'],equity['options']['bought'],equity['options']['expire'])
	#print("writeout opt price:",round(get_for_date.put_opt_price(equity['options']['bought'],equity['options']['bought'],equity['options']['expire'])['price'],2))
	#print("writeout dates:",equity['options']['bought'],equity['options']['bought'],equity['options']['expire'])
	#print(get_for_date.put_opt_price(equity['options']['bought'],equity['options']['bought'],equity['options']['expire']))
	#print("\nATTENTION")
	#print(get_for_date.put_opt_price("2000-06-12","2000-06-12","2000-12-15"))
	#print("OK\n")
	#print()


def updateConstants():
	global TRADE_DELTA
	global OPT_FRACTION
	global OPT_TIME_TO_MATURE
	global OPT_HOLDING_PERIOD
	current_volatility=get_for_date.volatility(this_trade_day)
	#TRADE_DELTA=TRADE_DELTA_K+TRADE_DELTA_M*current_volatility
	OPT_FRACTION=OPT_FRACTION_K+OPT_FRACTION_M*current_volatility
	OPT_FRACTION=0 if OPT_FRACTION<0 else OPT_FRACTION
	## Update 
	# OPT_HOLDING_PERIOD = 1 # months
	# OPT_TIME_TO_MATURE = 3 # months
	if current_volatility < 0.2:
		OPT_TIME_TO_MATURE=12
		OPT_HOLDING_PERIOD=4
	elif current_volatility < 0.4:
		OPT_TIME_TO_MATURE=6
		OPT_HOLDING_PERIOD=2
	else:
		OPT_TIME_TO_MATURE=3
		OPT_HOLDING_PERIOD=1

## RUN SIMULATION ##
# dict to store equity curve
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
	#IMPLIED_VOLATILITY=get_for_date.volatility(this_trade_day)/100.0
	print()
	print('loop restarting here, todays date: ',this_trade_day)
	updateConstants()
	#print(TRADE_DELTA)
	#print(OPT_FRACTION)
	# set up variable to store returns from option sales
	option_returns=0
	# compute Faustmann ratio
	faustmann_ratio=get_for_date.faustmann_ratio(this_trade_day)
	
	# use Faustmann ratio to determine how to trade
	# FAUSTMANN_R_MIN set to 0, 2019-12-17
	if faustmann_ratio>FAUSTMANN_R_MIN: #and get_for_date.check_filter(this_trade_day):
		# if you have options, roll options
		if equity['options']['count']:
			print('ROLL OPTIONS')
			option_returns+=sell_options()
			option_returns+=buy_options()
		# otherwise buy options
		else:
			print('\nSELL STOCKS AND BUY OPTIONS\n')
			option_returns+=buy_options()
	
	# FAUSTMANN_R_MIN set to 0, 2019-12-17, else statement never executes
	else:
		print('this never executes')
		if equity['options']['count']:
			print('SELL OPTIONS AND BUY STOCKS')
			option_returns+=sell_options()
			buy_stocks(equity['cash'],this_trade_day)
		else:
			print('REMAIN AS IS')
			buy_stocks(equity['cash'],this_trade_day)
	print('Date:',this_trade_day,'; Faustmann ratio:',faustmann_ratio, '; Net worth:',get_net_worth(equity, this_trade_day))
	equity_curve.append([this_trade_day,get_net_worth(equity, this_trade_day),faustmann_ratio,option_returns])
	print('current equity: ',equity)
	# Move on to the next date
	last_trade_day=this_trade_day
	this_trade_day=make_nxt_trade_date(last_trade_day)
	## EXIT STRATEGY BEGINS HERE
	print('TESTING EXIT NOW')
	if equity['options']['count']:
		get_holding_opt_price=lambda _: get_for_date.put_opt_price(equity['options']['bought'], _, equity['options']['expire'])['price']
		# ~ print(equity)
		opt_start_price=get_holding_opt_price(last_trade_day)
		print("option_start_price:",round(opt_start_price,2),', option strike: ',)
		# ~ print(last_trade_day, this_trade_day)
		idayf=lambda _: get_next_valid_date( get_DT_str( get_DT_obj(_)+datetime.timedelta(days=1) ) )
		q=last_trade_day
		while q != this_trade_day:
			q=idayf(q)
			opt_current_price=get_holding_opt_price(q)
			print('now testing date ',q,' volatility: ',round(get_for_date.volatility(q),3),' opt price: ',round(opt_current_price,2),' underlying: ',round(get_for_date.market_price(q),2))
			if opt_current_price>opt_start_price*EXIT_THRESHOLD:
				print('hit an exit threshold on date ',q)
				print("opt_current_price:",round(opt_current_price,2))
				this_trade_day=q
				option_returns+=sell_options()
				equity_curve.append([this_trade_day,get_net_worth(equity, this_trade_day),faustmann_ratio,option_returns])
				print('Net Worth: ',get_net_worth(equity, this_trade_day))
				break
		#break

## Close output file
f.close()

## PLOT ##

# Plot equity curve
plt.plot([get_DT_obj(_[0]) for _ in equity_curve],[_[1] for _ in equity_curve])

#plt.plot([get_DT_obj(_[0]) for _ in equity_curve],[_[3]*10 for _ in equity_curve])
plt.plot([get_DT_obj(_[0]) for _ in equity_curve],[_[3] for _ in equity_curve])
plt.plot([get_DT_obj(_[0]) for _ in equity_curve],[get_for_date.market_price(_[0])*100 for _ in equity_curve])

#get_for_date.market_price(this_trade_day)
# To plot returns from option trades uncomment next two lines
#plt.plot([get_DT_obj(_[0]) for _ in equity_curve],[_[-1] for _ in equity_curve])
#plt.axhline(y=0, color='r', linestyle='-')

plt.show()




















