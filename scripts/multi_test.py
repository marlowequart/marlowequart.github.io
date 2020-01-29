import delta_hedge as dhedge
import matplotlib.pyplot as plt
import time
import datetime
import pandas

start_time = time.time()
print('Start time to run script:')
print(datetime.datetime.now())

start_date='1959-07-15'
start_equity=100000

equity_curve1=dhedge.main(SIM_START_DATE=start_date,
	OUTPUT_CSV='sim1_out.csv',
	STARTING_EQUITY=start_equity,
	OPT_FRACTION_K=0.03,OPT_FRACTION_M=0,
	STRIKE_AT=0.7,
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

print('Sim 2')
print(datetime.datetime.now())

equity_curve2=dhedge.main(SIM_START_DATE=start_date,
	OUTPUT_CSV='sim2_out.csv',
	STARTING_EQUITY=start_equity,
	OPT_FRACTION_K=0.03,OPT_FRACTION_M=0,
	STRIKE_AT=0.9,
	# The Faustmann ratio is market cap/net worth
	FAUSTMANN_R_MIN=0,
	# Fraction at which to exit the option trade
	EXIT_THRESHOLD=10,
	SIM_NAME='Simulation 2',
	DEBUG=False,
	OPT_HOLDING_PARAMS={
		'L_VOL':[0,   12, 4],
		'M_VOL':[0.2,  6, 3],
		'H_VOL':[0.4,  3, 1]})

print('Sim 3')
print(datetime.datetime.now())

equity_curve3=dhedge.main(SIM_START_DATE=start_date,
	OUTPUT_CSV='sim3_out.csv',
	STARTING_EQUITY=start_equity,
	OPT_FRACTION_K=0.03,OPT_FRACTION_M=0,
	STRIKE_AT=0.8,
	# The Faustmann ratio is market cap/net worth
	FAUSTMANN_R_MIN=0,
	# Fraction at which to exit the option trade
	EXIT_THRESHOLD=20,
	SIM_NAME='Simulation 3',
	DEBUG=False,
	OPT_HOLDING_PARAMS={
		'L_VOL':[0,   12, 4],
		'M_VOL':[0.2,  6, 3],
		'H_VOL':[0.4,  3, 1]})

print('Sim 4')
print(datetime.datetime.now())

equity_curve4=dhedge.main(SIM_START_DATE=start_date,
	OUTPUT_CSV='sim4_out.csv',
	STARTING_EQUITY=start_equity,
	OPT_FRACTION_K=0.03,OPT_FRACTION_M=0,
	STRIKE_AT=0.8,
	# The Faustmann ratio is market cap/net worth
	FAUSTMANN_R_MIN=0,
	# Fraction at which to exit the option trade
	EXIT_THRESHOLD=30,
	SIM_NAME='Simulation 4',
	DEBUG=False,
	OPT_HOLDING_PARAMS={
		'L_VOL':[0,   12, 4],
		'M_VOL':[0.2,  6, 3],
		'H_VOL':[0.4,  3, 1]})

print('Sim 5')
print(datetime.datetime.now())

equity_curve5=dhedge.main(SIM_START_DATE=start_date,
	OUTPUT_CSV='sim5_out.csv',
	STARTING_EQUITY=start_equity,
	OPT_FRACTION_K=0.03,OPT_FRACTION_M=0,
	STRIKE_AT=0.8,
	# The Faustmann ratio is market cap/net worth
	FAUSTMANN_R_MIN=0,
	# Fraction at which to exit the option trade
	EXIT_THRESHOLD=40,
	SIM_NAME='Simulation 5',
	DEBUG=False,
	OPT_HOLDING_PARAMS={
		'L_VOL':[0,   12, 4],
		'M_VOL':[0.2,  6, 3],
		'H_VOL':[0.4,  3, 1]})

print('Sim 6')
print(datetime.datetime.now())

equity_curve6=dhedge.main(SIM_START_DATE=start_date,
	OUTPUT_CSV='sim6_out.csv',
	STARTING_EQUITY=start_equity,
	OPT_FRACTION_K=0.03,OPT_FRACTION_M=0,
	STRIKE_AT=0.8,
	# The Faustmann ratio is market cap/net worth
	FAUSTMANN_R_MIN=0,
	# Fraction at which to exit the option trade
	EXIT_THRESHOLD=50,
	SIM_NAME='Simulation 6',
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
date_output4=[_[0] for _ in equity_curve4]
equity_curve4_output=[_[1] for _ in equity_curve4]
date_output5=[_[0] for _ in equity_curve5]
equity_curve5_output=[_[1] for _ in equity_curve5]
date_output6=[_[0] for _ in equity_curve6]
equity_curve6_output=[_[1] for _ in equity_curve6]

df1=pandas.DataFrame({'Date':date_output1, 'Equity1':equity_curve1_output})
df2=pandas.DataFrame({'Date':date_output2, 'Equity1':equity_curve2_output})
df3=pandas.DataFrame({'Date':date_output3, 'Equity1':equity_curve3_output})
df4=pandas.DataFrame({'Date':date_output4, 'Equity1':equity_curve4_output})
df5=pandas.DataFrame({'Date':date_output5, 'Equity1':equity_curve5_output})
df6=pandas.DataFrame({'Date':date_output6, 'Equity1':equity_curve6_output})

# ~ df = pandas.DataFrame(data={'Date': equity_curve1[0], 'Equity1': equity_curve1_output, 'Equity2': equity_curve2_output, 'Equity3': equity_curve3_output})
df1.to_csv('equity1_output.csv', sep=',', index=False)
df2.to_csv('equity2_output.csv', sep=',', index=False)
df3.to_csv('equity3_output.csv', sep=',', index=False)
df4.to_csv('equity4_output.csv', sep=',', index=False)
df5.to_csv('equity5_output.csv', sep=',', index=False)
df6.to_csv('equity6_output.csv', sep=',', index=False)


print()
print('%f seconds to run script' % (time.time() - start_time))
print(datetime.datetime.now())
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

