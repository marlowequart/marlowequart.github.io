import pandas as pd

input_file='_trade_results_02_05_20_3.csv'

data_df = pd.read_csv(input_file,header=0)


data_df.to_csv('_trade_results_02_05_20_3_noblk.csv', sep=',', index=False)

