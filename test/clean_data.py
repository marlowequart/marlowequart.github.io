'''
remove dates from one file that are not found in the other file


Input: .csv file

Output: .csv file



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

'''
import pandas as pd
import datetime



input_file='data/^GSPC.csv'
risk_free_input='data/DTB1YR_clean.csv'

data_df = pd.read_csv(input_file,header=0)
date=data_df['Date'].tolist()
# equity=data_df['Equity1'].tolist()

rf_df = pd.read_csv(risk_free_input,header=0)
rf_date=rf_df['Date'].tolist()
rf_rate=rf_df['DTB1YR'].tolist()

start_date='1959-07-15'
start_idx=date.index(start_date)

# Convert dates to same format
# rf_date_mod=[]
# for i in range(len(rf_date)):
	# today=datetime.datetime.strptime(rf_date[i],'%m/%d/%y')
	# if today.year > 2020:
		# today = today.replace(year=today.year-100)
	# rf_date_mod.append(datetime.datetime.strftime(today,'%Y-%m-%d'))
rf_date_mod=rf_date


print('len gspc: ',len(date),', len rf: ',len(rf_date),', len rf data: ',len(rf_rate))
y=start_idx
z=0
mismatch=0
for i in range(len(rf_date_mod)):
	gspc_date=date[y]
	date_rf=rf_date_mod[z]
	# print()
	# print('gspc date: ',gspc_date,', rf_date: ',date_rf,' i: ',i,' y: ',y,' z: ',z)
	if date_rf != gspc_date:
		# print('found mismatch')
		rf_date_mod.pop(z)
		rf_rate.pop(z)
		y-=1
		z-=1
		mismatch+=1
		
	# if i > 4500:
		# break
	# if i > 4500:
		# break
	y+=1
	z+=1


# print()
print('number mismatches: ',mismatch)
print('len gspc: ',len(date[start_idx:]),', len rf: ',len(rf_date),', len rf data: ',len(rf_rate))

df1=pd.DataFrame({'Date':rf_date, 'Rate':rf_rate})
df1.to_csv('risk_free_1yr_clean.csv', sep=',', index=False)

'''


'''
change the date format in one file


Input: .csv file

Output: .csv file



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

import pandas as pd
import datetime


input_file='data/risk_free_1yr_clean.csv'
data_df = pd.read_csv(input_file,header=0)

date=data_df['Date'].tolist()
rate=data_df['Rate'].tolist()

date_mod=[]
for i in range(len(date)):
	today=datetime.datetime.strptime(date[i],'%m/%d/%Y')
	if today.year > 2020:
		today = today.replace(year=today.year-100)
	date_mod.append(datetime.datetime.strftime(today,'%Y-%m-%d'))
	
print(date[0:20])
print(date_mod[0:20])
print(len(date),len(date_mod))
# df1=pd.DataFrame({'Date':date_mod, 'Rate':rate})
# df1.to_csv('risk_free_1yr_clean_dates.csv', sep=',', index=False)