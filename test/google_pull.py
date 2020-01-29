from googlefinance import getQuotes
import json


def get_quote(symbol):
	
	print (json.dumps(getQuotes(symbol),indent=2))
	
def main():
	symbol='AAPL'
	get_quote(symbol)
	
main()