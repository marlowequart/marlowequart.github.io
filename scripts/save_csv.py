import delta_hedge as dhedge
import matplotlib.pyplot as plt
import time
import pandas as pd

sp_input_file='data/^GSPC.csv'
vol_input_file='data/volatility40.csv'

sp_data_df = pd.read_csv(sp_input_file,header=0)
vol_data_df = pd.read_csv(vol_input_file,header=0)

sp_date=sp_data_df['Date'].tolist()
sp_price=sp_data_df['Close'].tolist()

vol_date=vol_data_df['Date'].tolist()
vol_price=vol_data_df['Volatility'].tolist()

# ~ print(vol_date)

# Save equity curves into .csv file
## SET UP OUTPUT CSV AND DEFINE OUTPUT FUNCTION ##
# ~ date_output=[_[0] for _ in equity_curve1]
# ~ equity_curve1_output=[_[1] for _ in equity_curve1]
# ~ equity_curve2_output=[_[1] for _ in equity_curve2]
# ~ equity_curve3_output=[_[1] for _ in equity_curve3]

# ~ df=pandas.DataFrame({'Date':date_output, 'Equity1':equity_curve1_output, 'Equity2':equity_curve2_output, 'Equity3':equity_curve3_output})
df=pd.DataFrame({'Date':vol_date, 'Equity1':vol_price})

# ~ df = pandas.DataFrame(data={'Date': equity_curve1[0], 'Equity1': equity_curve1_output, 'Equity2': equity_curve2_output, 'Equity3': equity_curve3_output})
df.to_csv('equity_output.csv', sep=',', index=False)

