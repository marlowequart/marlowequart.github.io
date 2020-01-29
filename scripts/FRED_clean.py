'''
Clean up the data from FRED to remove period data


'''
import csv
import pandas as pd
import datetime


risk_free_input='data/DTB1YR.csv'
save_file_name='DTB1YR_clean.csv'

rf_df = pd.read_csv(risk_free_input,header=0)
rf_date=rf_df['DATE'].tolist()
rf_rate=rf_df['DTB1YR'].tolist()

rf_start_date='1959-07-15'
rf_end_date='2001-08-24'

rf_start_idx=rf_date.index(rf_start_date)
rf_end_idx=rf_date.index(rf_end_date)



for i in range(rf_start_idx,rf_end_idx):
	# check for period
	# if period, print date and make same rate as previous date
	# then save result as .csv
	if rf_rate[i] == '.':
		rf_rate[i]=rf_rate[i-1]
		print('fixing date: '+rf_date[i])




df1=pd.DataFrame({'Date':rf_date[rf_start_idx:rf_end_idx], 'DTB1YR':rf_rate[rf_start_idx:rf_end_idx]})
df1.to_csv(save_file_name, sep=',', index=False)
