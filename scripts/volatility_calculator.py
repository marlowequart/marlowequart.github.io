# To calculate volatility, get the moving standard deviation of 1 month interval

import csv
import datetime
import numpy as np

get_DT_obj=lambda _: datetime.datetime.strptime(_,'%Y-%m-%d')
get_DT_str=lambda _: datetime.datetime.strftime(_,'%Y-%m-%d')

with open('data/^GSPC.csv') as f:
	r=csv.DictReader(f)
	data=[_ for _ in r]

with open('data/volatility.csv','w') as f:
	w=csv.DictWriter(f, ['Date','Volatility'])
	w.writeheader()
	for i in range(1,len(data)-30-1):
		start=i
		stop=i+30
		out_date=data[stop+1]['Date']
		out_v = np.std(np.asarray(
			[(float(data[_]['Close'])-float(data[_-1]['Close']))/float(data[_-1]['Close']) 
					  for _ in range(i,i+30)]))*np.sqrt(252)*100
		w.writerow({'Date':out_date,'Volatility':out_v})
