import csv

with open('vix_days_dec08_to_nov2018_volsum.csv') as fr, open('vixmq_dec08_to_nov18.csv','w',newline='') as fw:
	cr=csv.reader(fr,delimiter=';')
	cw=csv.writer(fw,delimiter=';')
	cw.writerow(next(cr))
	cw.writerows(reversed(list(cr)))