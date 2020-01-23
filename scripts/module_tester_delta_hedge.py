import delta_hedge as dhedge
import matplotlib.pyplot as plt
import time
import datetime
import pandas

start_time = time.time()
print('Start time to run script:')
print(datetime.datetime.now())

start_date='1988-06-10'
start_equity=100000

equity_curve1=dhedge.main(SIM_START_DATE=start_date,
	OUTPUT_CSV='sim1_out.csv',
	STARTING_EQUITY=start_equity,
	OPT_FRACTION_K=0.005,OPT_FRACTION_M=0,
	STRIKE_AT=0.7,
	# The Faustmann ratio is market cap/net worth
	FAUSTMANN_R_MIN=0,
	# Fraction at which to exit the option trade
	EXIT_THRESHOLD=5,
	SIM_NAME='Simulation 1',
	DEBUG=False,
	OPT_HOLDING_PARAMS={
		'L_VOL':[0,   12, 4],
		'M_VOL':[0.2,  6, 3],
		'H_VOL':[0.4,  3, 1]})

equity_curve2=dhedge.main(SIM_START_DATE=start_date,
	OUTPUT_CSV='sim2_out.csv',
	STARTING_EQUITY=start_equity,
	OPT_FRACTION_K=0.005,OPT_FRACTION_M=0,
	STRIKE_AT=0.8,
	# The Faustmann ratio is market cap/net worth
	FAUSTMANN_R_MIN=0,
	# Fraction at which to exit the option trade
	EXIT_THRESHOLD=5,
	SIM_NAME='Simulation 2',
	DEBUG=False,
	OPT_HOLDING_PARAMS={
		'L_VOL':[0,   12, 4],
		'M_VOL':[0.2,  6, 3],
		'H_VOL':[0.4,  3, 1]})

equity_curve3=dhedge.main(SIM_START_DATE=start_date,
	OUTPUT_CSV='sim3_out.csv',
	STARTING_EQUITY=start_equity,
	OPT_FRACTION_K=0.005,OPT_FRACTION_M=0,
	STRIKE_AT=0.9,
	# The Faustmann ratio is market cap/net worth
	FAUSTMANN_R_MIN=0,
	# Fraction at which to exit the option trade
	EXIT_THRESHOLD=5,
	SIM_NAME='Simulation 3',
	DEBUG=False,
	OPT_HOLDING_PARAMS={
		'L_VOL':[0,   12, 4],
		'M_VOL':[0.2,  6, 3],
		'H_VOL':[0.4,  3, 1]})


# Save equity curves into .csv file
## SET UP OUTPUT CSV AND DEFINE OUTPUT FUNCTION ##
date_output1=[_[0] for _ in equity_curve1]
equity_curve1_output=[_[1] for _ in equity_curve1]
date_output2=[_[0] for _ in equity_curve2]
equity_curve2_output=[_[1] for _ in equity_curve2]
date_output3=[_[0] for _ in equity_curve3]
equity_curve3_output=[_[1] for _ in equity_curve3]

df1=pandas.DataFrame({'Date':date_output1, 'Equity1':equity_curve1_output})
df2=pandas.DataFrame({'Date':date_output2, 'Equity1':equity_curve2_output})
df3=pandas.DataFrame({'Date':date_output3, 'Equity1':equity_curve3_output})

# ~ df = pandas.DataFrame(data={'Date': equity_curve1[0], 'Equity1': equity_curve1_output, 'Equity2': equity_curve2_output, 'Equity3': equity_curve3_output})
df1.to_csv('equity1_output.csv', sep=',', index=False)
df2.to_csv('equity2_output.csv', sep=',', index=False)
df3.to_csv('equity3_output.csv', sep=',', index=False)


print()
print('%f seconds to run script' % (time.time() - start_time))
print()

## PLOT ##

# Plot equity curve
plt.plot([dhedge.get_DT_obj(_[0]) for _ in equity_curve1],[_[1] for _ in equity_curve1],'r')
plt.plot([dhedge.get_DT_obj(_[0]) for _ in equity_curve2],[_[1] for _ in equity_curve2],'b')
plt.plot([dhedge.get_DT_obj(_[0]) for _ in equity_curve3],[_[1] for _ in equity_curve3],'g')

# ~ plt.plot([get_DT_obj(_[0]) for _ in equity_curve],[_[3]*10 for _ in equity_curve])
# ~ plt.plot([get_DT_obj(_[0]) for _ in equity_curve],[_[3] for _ in equity_curve])
# ~ plt.plot([get_DT_obj(_[0]) for _ in equity_curve],[get_for_date.market_price(_[0])*100 for _ in equity_curve])

# To plot returns from option trades uncomment next two lines
# ~ plt.plot([get_DT_obj(_[0]) for _ in equity_curve],[_[-1] for _ in equity_curve])
# ~ plt.axhline(y=0, color='r', linestyle='-')

plt.show()
