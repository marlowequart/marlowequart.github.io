import delta_hedge as dhedge
import matplotlib.pyplot as plt
import time
import datetime
import pandas

start_time = time.time()
print('Start time to run script:')
print(datetime.datetime.now())


file_name_suffix='_1959to2019_02_05_20.csv'
# start_date='2008-06-10'
# start_date='1988-06-10'
start_date='1959-07-15'

# Set end date to 'None' to run to last valid date
# end_date='1969-08-18'
end_date='None'
# end_date='1988-06-10'
start_equity=100000


print('Sim 1')
print(datetime.datetime.now())

equity_curve1=dhedge.main(SIM_START_DATE=start_date,
	SIM_END_DATE=end_date,
	OUTPUT_CSV='sim1_out'+file_name_suffix,
	STARTING_EQUITY=start_equity,
	OPT_FRACTION_K=0.01,OPT_FRACTION_M=0,
	STRIKE_AT=0.8,
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
	SIM_END_DATE=end_date,
	OUTPUT_CSV='sim2_out'+file_name_suffix,
	STARTING_EQUITY=start_equity,
	OPT_FRACTION_K=0.02,OPT_FRACTION_M=0,
	STRIKE_AT=0.8,
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
	SIM_END_DATE=end_date,
	OUTPUT_CSV='sim3_out'+file_name_suffix,
	STARTING_EQUITY=start_equity,
	OPT_FRACTION_K=0.03,OPT_FRACTION_M=0,
	STRIKE_AT=0.8,
	# Fraction at which to exit the option trade
	EXIT_THRESHOLD=10,
	SIM_NAME='Simulation 3',
	DEBUG=False,
	OPT_HOLDING_PARAMS={
		'L_VOL':[0,   12, 4],
		'M_VOL':[0.2,  6, 3],
		'H_VOL':[0.4,  3, 1]})

print('Sim 4')
print(datetime.datetime.now())

equity_curve4=dhedge.main(SIM_START_DATE=start_date,
	SIM_END_DATE=end_date,
	OUTPUT_CSV='sim4_out'+file_name_suffix,
	STARTING_EQUITY=start_equity,
	OPT_FRACTION_K=0.04,OPT_FRACTION_M=0,
	STRIKE_AT=0.8,
	# Fraction at which to exit the option trade
	EXIT_THRESHOLD=10,
	SIM_NAME='Simulation 4',
	DEBUG=False,
	OPT_HOLDING_PARAMS={
		'L_VOL':[0,   12, 4],
		'M_VOL':[0.2,  6, 3],
		'H_VOL':[0.4,  3, 1]})

print('Sim 5')
print(datetime.datetime.now())

equity_curve5=dhedge.main(SIM_START_DATE=start_date,
	SIM_END_DATE=end_date,
	OUTPUT_CSV='sim5_out'+file_name_suffix,
	STARTING_EQUITY=start_equity,
	OPT_FRACTION_K=0.05,OPT_FRACTION_M=0,
	STRIKE_AT=0.8,
	# Fraction at which to exit the option trade
	EXIT_THRESHOLD=10,
	SIM_NAME='Simulation 5',
	DEBUG=False,
	OPT_HOLDING_PARAMS={
		'L_VOL':[0,   12, 4],
		'M_VOL':[0.2,  6, 3],
		'H_VOL':[0.4,  3, 1]})

print('Sim 6')
print(datetime.datetime.now())

equity_curve6=dhedge.main(SIM_START_DATE=start_date,
	SIM_END_DATE=end_date,
	OUTPUT_CSV='sim6_out'+file_name_suffix,
	STARTING_EQUITY=start_equity,
	OPT_FRACTION_K=0.06,OPT_FRACTION_M=0,
	STRIKE_AT=0.8,
	# Fraction at which to exit the option trade
	EXIT_THRESHOLD=10,
	SIM_NAME='Simulation 6',
	DEBUG=False,
	OPT_HOLDING_PARAMS={
		'L_VOL':[0,   12, 4],
		'M_VOL':[0.2,  6, 3],
		'H_VOL':[0.4,  3, 1]})


print('Sim 7')
print(datetime.datetime.now())

equity_curve7=dhedge.main(SIM_START_DATE=start_date,
	SIM_END_DATE=end_date,
	OUTPUT_CSV='sim7_out'+file_name_suffix,
	STARTING_EQUITY=start_equity,
	OPT_FRACTION_K=0.03,OPT_FRACTION_M=0,
	STRIKE_AT=0.7,
	# Fraction at which to exit the option trade
	EXIT_THRESHOLD=10,
	SIM_NAME='Simulation 7',
	DEBUG=False,
	OPT_HOLDING_PARAMS={
		'L_VOL':[0,   12, 4],
		'M_VOL':[0.2,  6, 3],
		'H_VOL':[0.4,  3, 1]})

print('Sim 8')
print(datetime.datetime.now())

equity_curve8=dhedge.main(SIM_START_DATE=start_date,
	SIM_END_DATE=end_date,
	OUTPUT_CSV='sim8_out'+file_name_suffix,
	STARTING_EQUITY=start_equity,
	OPT_FRACTION_K=0.03,OPT_FRACTION_M=0,
	STRIKE_AT=0.9,
	# Fraction at which to exit the option trade
	EXIT_THRESHOLD=10,
	SIM_NAME='Simulation 8',
	DEBUG=False,
	OPT_HOLDING_PARAMS={
		'L_VOL':[0,   12, 4],
		'M_VOL':[0.2,  6, 3],
		'H_VOL':[0.4,  3, 1]})

print('Sim 9')
print(datetime.datetime.now())

equity_curve9=dhedge.main(SIM_START_DATE=start_date,
	SIM_END_DATE=end_date,
	OUTPUT_CSV='sim9_out'+file_name_suffix,
	STARTING_EQUITY=start_equity,
	OPT_FRACTION_K=0.03,OPT_FRACTION_M=0,
	STRIKE_AT=0.8,
	# Fraction at which to exit the option trade
	EXIT_THRESHOLD=10,
	SIM_NAME='Simulation 9',
	DEBUG=False,
	OPT_HOLDING_PARAMS={
		'L_VOL':[0,   12, 4],
		'M_VOL':[0.3,  6, 3],
		'H_VOL':[0.4,  3, 1]})

print('Sim 10')
print(datetime.datetime.now())

equity_curve10=dhedge.main(SIM_START_DATE=start_date,
	SIM_END_DATE=end_date,
	OUTPUT_CSV='sim10_out'+file_name_suffix,
	STARTING_EQUITY=start_equity,
	OPT_FRACTION_K=0.03,OPT_FRACTION_M=0,
	STRIKE_AT=0.8,
	# Fraction at which to exit the option trade
	EXIT_THRESHOLD=10,
	SIM_NAME='Simulation 10',
	DEBUG=False,
	OPT_HOLDING_PARAMS={
		'L_VOL':[0,   12, 4],
		'M_VOL':[0.4,  3, 1],
		'H_VOL':[0.4,  3, 1]})

print('Sim 11')
print(datetime.datetime.now())

equity_curve11=dhedge.main(SIM_START_DATE=start_date,
	SIM_END_DATE=end_date,
	OUTPUT_CSV='sim11_out'+file_name_suffix,
	STARTING_EQUITY=start_equity,
	OPT_FRACTION_K=0.03,OPT_FRACTION_M=0,
	STRIKE_AT=0.8,
	# Fraction at which to exit the option trade
	EXIT_THRESHOLD=10,
	SIM_NAME='Simulation 11',
	DEBUG=False,
	OPT_HOLDING_PARAMS={
		'L_VOL':[0,   15, 4],
		'M_VOL':[0.2,  6, 3],
		'H_VOL':[0.4,  3, 1]})

print('Sim 12')
print(datetime.datetime.now())

equity_curve12=dhedge.main(SIM_START_DATE=start_date,
	SIM_END_DATE=end_date,
	OUTPUT_CSV='sim12_out'+file_name_suffix,
	STARTING_EQUITY=start_equity,
	OPT_FRACTION_K=0.03,OPT_FRACTION_M=0,
	STRIKE_AT=0.8,
	# Fraction at which to exit the option trade
	EXIT_THRESHOLD=20,
	SIM_NAME='Simulation 12',
	DEBUG=False,
	OPT_HOLDING_PARAMS={
		'L_VOL':[0,   12, 4],
		'M_VOL':[0.2,  6, 3],
		'H_VOL':[0.4,  3, 1]})

print('Sim 13')
print(datetime.datetime.now())

equity_curve13=dhedge.main(SIM_START_DATE=start_date,
	SIM_END_DATE=end_date,
	OUTPUT_CSV='sim13_out'+file_name_suffix,
	STARTING_EQUITY=start_equity,
	OPT_FRACTION_K=0.03,OPT_FRACTION_M=0,
	STRIKE_AT=0.8,
	# Fraction at which to exit the option trade
	EXIT_THRESHOLD=30,
	SIM_NAME='Simulation 13',
	DEBUG=False,
	OPT_HOLDING_PARAMS={
		'L_VOL':[0,   12, 4],
		'M_VOL':[0.2,  6, 3],
		'H_VOL':[0.4,  3, 1]})

print('Sim 14')
print(datetime.datetime.now())

equity_curve14=dhedge.main(SIM_START_DATE=start_date,
	SIM_END_DATE=end_date,
	OUTPUT_CSV='sim14_out'+file_name_suffix,
	STARTING_EQUITY=start_equity,
	OPT_FRACTION_K=0.03,OPT_FRACTION_M=0,
	STRIKE_AT=0.8,
	# Fraction at which to exit the option trade
	EXIT_THRESHOLD=40,
	SIM_NAME='Simulation 14',
	DEBUG=False,
	OPT_HOLDING_PARAMS={
		'L_VOL':[0,   12, 4],
		'M_VOL':[0.2,  6, 3],
		'H_VOL':[0.4,  3, 1]})

print('Sim 15')
print(datetime.datetime.now())

equity_curve15=dhedge.main(SIM_START_DATE=start_date,
	SIM_END_DATE=end_date,
	OUTPUT_CSV='sim15_out'+file_name_suffix,
	STARTING_EQUITY=start_equity,
	OPT_FRACTION_K=0.03,OPT_FRACTION_M=0,
	STRIKE_AT=0.8,
	# Fraction at which to exit the option trade
	EXIT_THRESHOLD=50,
	SIM_NAME='Simulation 15',
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
date_output7=[_[0] for _ in equity_curve7]
equity_curve7_output=[_[1] for _ in equity_curve7]
date_output8=[_[0] for _ in equity_curve8]
equity_curve8_output=[_[1] for _ in equity_curve8]
date_output9=[_[0] for _ in equity_curve9]
equity_curve9_output=[_[1] for _ in equity_curve9]
date_output10=[_[0] for _ in equity_curve10]
equity_curve10_output=[_[1] for _ in equity_curve10]
date_output11=[_[0] for _ in equity_curve11]
equity_curve11_output=[_[1] for _ in equity_curve11]
date_output12=[_[0] for _ in equity_curve12]
equity_curve12_output=[_[1] for _ in equity_curve12]
date_output13=[_[0] for _ in equity_curve13]
equity_curve13_output=[_[1] for _ in equity_curve13]
date_output14=[_[0] for _ in equity_curve14]
equity_curve14_output=[_[1] for _ in equity_curve14]
date_output15=[_[0] for _ in equity_curve15]
equity_curve15_output=[_[1] for _ in equity_curve15]


df1=pandas.DataFrame({'Date':date_output1, 'Equity':equity_curve1_output})
df2=pandas.DataFrame({'Date':date_output2, 'Equity':equity_curve2_output})
df3=pandas.DataFrame({'Date':date_output3, 'Equity':equity_curve3_output})
df4=pandas.DataFrame({'Date':date_output4, 'Equity':equity_curve4_output})
df5=pandas.DataFrame({'Date':date_output5, 'Equity':equity_curve5_output})
df6=pandas.DataFrame({'Date':date_output6, 'Equity':equity_curve6_output})
df7=pandas.DataFrame({'Date':date_output7, 'Equity':equity_curve7_output})
df8=pandas.DataFrame({'Date':date_output8, 'Equity':equity_curve8_output})
df9=pandas.DataFrame({'Date':date_output9, 'Equity':equity_curve9_output})
df10=pandas.DataFrame({'Date':date_output10, 'Equity':equity_curve10_output})
df11=pandas.DataFrame({'Date':date_output11, 'Equity':equity_curve11_output})
df12=pandas.DataFrame({'Date':date_output12, 'Equity':equity_curve12_output})
df13=pandas.DataFrame({'Date':date_output13, 'Equity':equity_curve13_output})
df14=pandas.DataFrame({'Date':date_output14, 'Equity':equity_curve14_output})
df15=pandas.DataFrame({'Date':date_output15, 'Equity':equity_curve15_output})

# ~ df = pandas.DataFrame(data={'Date': equity_curve1[0], 'Equity1': equity_curve1_output, 'Equity2': equity_curve2_output, 'Equity3': equity_curve3_output})
df1.to_csv('equity1_output'+file_name_suffix, sep=',', index=False)
df2.to_csv('equity2_output'+file_name_suffix, sep=',', index=False)
df3.to_csv('equity3_output'+file_name_suffix, sep=',', index=False)
df4.to_csv('equity4_output'+file_name_suffix, sep=',', index=False)
df5.to_csv('equity5_output'+file_name_suffix, sep=',', index=False)
df6.to_csv('equity6_output'+file_name_suffix, sep=',', index=False)
df7.to_csv('equity7_output'+file_name_suffix, sep=',', index=False)
df8.to_csv('equity8_output'+file_name_suffix, sep=',', index=False)
df9.to_csv('equity9_output'+file_name_suffix, sep=',', index=False)
df10.to_csv('equity10_output'+file_name_suffix, sep=',', index=False)
df11.to_csv('equity11_output'+file_name_suffix, sep=',', index=False)
df12.to_csv('equity12_output'+file_name_suffix, sep=',', index=False)
df13.to_csv('equity13_output'+file_name_suffix, sep=',', index=False)
df14.to_csv('equity14_output'+file_name_suffix, sep=',', index=False)
df15.to_csv('equity15_output'+file_name_suffix, sep=',', index=False)


print()
print('%f seconds to run script' % (time.time() - start_time))
print(datetime.datetime.now())
print()

## PLOT ##

# Plot equity curve
plt.plot([dhedge.get_DT_obj(_[0]) for _ in equity_curve1],[_[1] for _ in equity_curve1],'r')
# plt.plot([dhedge.get_DT_obj(_[0]) for _ in equity_curve2],[_[1] for _ in equity_curve2],'b')
# plt.plot([dhedge.get_DT_obj(_[0]) for _ in equity_curve3],[_[1] for _ in equity_curve3],'g')

# ~ plt.plot([get_DT_obj(_[0]) for _ in equity_curve],[_[3]*10 for _ in equity_curve])
# ~ plt.plot([get_DT_obj(_[0]) for _ in equity_curve],[_[3] for _ in equity_curve])
# ~ plt.plot([get_DT_obj(_[0]) for _ in equity_curve],[get_for_date.market_price(_[0])*100 for _ in equity_curve])

# To plot returns from option trades uncomment next two lines
# ~ plt.plot([get_DT_obj(_[0]) for _ in equity_curve],[_[-1] for _ in equity_curve])
# ~ plt.axhline(y=0, color='r', linestyle='-')

plt.show()

