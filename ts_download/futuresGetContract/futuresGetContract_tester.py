import futuresGetContract
import sys
# ~ print( "\nUseage: python futuresGetContract.py <tracker> <date>")
# ~ print( "Example: python futuresGetContract.py BTC 2019-9-25")


# Usage: python futuresGetContract_tester.py todays_date
# ex: python futuresGetContract_tester.py 2019-9-25


# 4/30/20, update this script to go into update_data_ts.py to find the missing contracts between the last downloaded contracts and current contract


	# ~ indexes=['ESM20','NKM20','NQM20','RTYM20','BTCM20','VXM20']
	# ~ currencies=['ECM20','ADM20','BPM20','CDM20','SFM20','JYM20','MP1M20','NE1M20','DXM20','CNHM20']
	# ~ rates=['EDM20']
	# ~ non_ags=['YIJ20','LBH20']
	# ~ ags=['DAH20','CBH20','LHJ20','LCJ20','FCH20','KCH20','CTH20','OJH20','CCH20','SBH20']

currencies = [
	'AD',        # AUD/USD
	'BP',        # GBP/USD
	'CD',        # CAD/USD
	'EC',        # EUR/USD
	'DX',        # Dollar Index
	'JY',        # JPY/USD
	'NE1',        # NZD/USD
	'SF',        # CHF/USD
	'MP1',		# MXP/USD
	'CNH'		# chinese
]

agricultural = [
	# ~ 'BL',        # ? (not in pinnacle dataset)
	# ~ '_C',        # Corn
	'DA',		# Milk
	'CB',		# Butter
	'LH',		# Lean Hogs
	'LC',		# Live Cattle
	'FC',        # Feeder Cattle
	'KC',        # Coffee Arabica
	'CT',        # Cotton #2
	'OJ',		# Orange Juice
	'CC',		# Cocoa
	'SB',        # Sugar #11
	# ~ 'LR',        # Coffee Robusta (not in pinnacle)
	# ~ 'LS',        # Sugar #5 (not in pinnacle)
	# ~ '_O',        # Oats
	# ~ '_S',        # Soybeans
	# ~ 'SM',        # Soybean Meal
	# ~ '_W',        # Wheat
]
nonagricultural = [
	# ~ 'CL',        # Crude Oil
	# ~ 'GC',        # Gold
	# ~ 'HG',        # Copper
	# ~ 'HO',        # Heating Oil
	# ~ 'LG',        # Petroleum Gas
	# ~ 'NG',        # Natural Gas
	# ~ 'PA',        # Palladium
	# ~ 'PL',        # Platinum
	# ~ 'RB',        # RBOB Gas
	'YI',        # Silver
	'LB',		# Lumber
]
equities = [
	'ES',        # S&P Emini
	'NK',        # Nikkei 225
	'NQ',        # Nasdaq Emini
	'RTY',		# Russell
	'BTC',		# Bitcoin
	# ~ 'TW',        # MSCI Taiwan (not in pinnacle)
	'VX',        # VIX (not in pinnacle data)
	# ~ 'YM',        # DOW Emini
]
rates = [
	'ED',        # Eurodollar
	# ~ 'FV',        # US Treasury 5yr
	# ~ 'TU',        # US Treasury 2yr
	# ~ 'TY',        # US Treasury 10yr
	# ~ 'US',        # US Treasury 30yr
]

markets = currencies + agricultural + nonagricultural + equities + rates

print("\nCurrencies:")
for market in currencies:
	print( "Current contract name is %s"%futuresGetContract.getContractNameForDate(market,futuresGetContract.get_DT_obj(sys.argv[1])) )


print("\nAgs:")
for market in agricultural:
	print( "Current contract name is %s"%futuresGetContract.getContractNameForDate(market,futuresGetContract.get_DT_obj(sys.argv[1])) )


print("\nNon Ags:")
for market in nonagricultural:
	print( "Current contract name is %s"%futuresGetContract.getContractNameForDate(market,futuresGetContract.get_DT_obj(sys.argv[1])) )


print("\nEquities:")
for market in equities:
	print( "Current contract name is %s"%futuresGetContract.getContractNameForDate(market,futuresGetContract.get_DT_obj(sys.argv[1])) )


print("\nRates:")
for market in rates:
	print( "Current contract name is %s"%futuresGetContract.getContractNameForDate(market,futuresGetContract.get_DT_obj(sys.argv[1])) )

# ~ print( "\nGet list of rollover dates and contracts for this year\n" )
# ~ print( futuresGetContract.getDateReturn(sys.argv[1],futuresGetContract.get_DT_obj(sys.argv[2])) )


