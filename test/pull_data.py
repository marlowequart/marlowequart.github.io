import pandas as pd
import quandl
import datetime

import matplotlib.pyplot as plt

start = datetime.datetime(2018,1,1)
end = datetime.date.today()

# Let's get Apple stock data; Apple's ticker symbol is AAPL
# First argument is the series we want, second is the source
# ("yahoo" for Yahoo! Finance), third is the start date, fourth is the end date
symbol="AAPL"
data=quandl.get("WIKI/" + symbol, start_date=start, end_date=end)
type(data)

pd.core.frame.DataFrame

#data.head is the first 5 rows
print(data.head())