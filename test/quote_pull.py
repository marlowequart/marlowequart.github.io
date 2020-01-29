import pandas as pd
import datetime
import quandl
quandl.ApiConfig.api_key = 'TYozsYkiZmn4AGLbqEsV'

from yahoofinancials import YahooFinancials as yf


# import urllib
# import re
# import time
# import requests
# from bs4 import BeautifulSoup

# def get_quote_g(symbol):
# 	url = 'http://google.com/finance?q='+ symbol
# 	page = requests.get(url)
# 	
# 	soup = BeautifulSoup(page.text, 'html.parser')
# 	div_price = soup.findALL('b')
# 	
# 	f_write=open("html_data",'w')
# 	f_write.write(soup.prettify())
# 	f_write.close()
# 	print(soup.prettify())
	
# 	print(div_price)
# 	span_price = div_price.find(attrs={"class": "pr"})
	
# 	print(float(span_price.text.strip()))





	
# 	content = http.request('GET', base_url)
# 	content = urllib.urlopen(base_url).read()

# 	print(page.text)
# 	m = re.search('id="ref_(.*?)">(.*?)<', page.text)
# 	print (m)
# 	if m:
# 		quote = m.group(2)
# 		print (quote)
# 	else:
# 		quote = 'no quote available for: ' + symbol
# 	return quote
	

def get_quote(symbol):
	quote = yf(symbol)
	data = quote.get_stock_price_data(reformat=True)	
	return data[symbol]['regularMarketPrice']
	
	
#Get earnings data
def get_earnings(symbol):
	quote = yf(symbol)
	data = quote.get_stock_earnings_data(reformat=True)
	trailing_12=0
	for i in range(4):
		trailing_12=trailing_12+data[symbol]['earningsData']['quarterly'][i]['actual']
	
	print(data[symbol]['earningsData']['quarterly'])
	return trailing_12
	

def get_quote_q(symbol):

	today=datetime.date.today()
# 	print(today)
# 	yday=datetime.date.today() - datetime.timedelta(10)
	yday=datetime.datetime(2018,1,5)


# qopts.columns: request data from specific columns by passing the qopts.columns parameter.
# for multiple columns, include column names separated by comma
# .gte returns values greater than or equal to
# .lte returns values less than or equal to
# 	data=quandl.get_table('WIKI/PRICES',ticker=[symbol],
# 							qopts = {'columns': ['date', 'adj_close']},
# 							date = {'gte': yday, 'lte': today},
# 							paginate=True)

# 	data=quandl.get('WIKI/'+symbol, start_date=yday, end_date=today)
	quote = YahooFinancials(symbol)

# Returns a dictionary with the stock price data
# regularMarketPrice has the current price data
	data = quote.get_stock_price_data(reformat=True)

	

	print(data[symbol]['regularMarketPrice'])
# 	print(type(data))
# 	pd.core.frame.DataFrame
# 	quote.head is the first 5 rows
# 	print(quote.head())
	
	
def main():
	symbol='BRK-B'
	quote=get_earnings(symbol)
	print(symbol+' earnings = '+str(quote))
	
main()
