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


import csv
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np


input_file='data/^GSPC.csv'
risk_free_input='data/risk_free_1plus2yr.csv'

data_df = pd.read_csv(input_file,header=0)


rf_df = pd.read_csv(risk_free_input,header=0)


# input conditional argument
# ~ cond=data_df['Date'].isin(rf_df['Date']) == True

# ~ df2=rf_df.drop(rf_df[cond].index, inplace=True)

# ~ print(df2)

col='Date'
df1=data_df.set_index(col)
df2=rf_df.set_index(col)

# ~ print(df1.head())

# ~ df3=rf_df[~df2.index.isin(df1.index)]
df3=df2.index.isin(df1.index)
print(df3[0:300])

# drop rows in one df that dont match conditional argument
# ~ df2=rf_df.drop(rf_df[cond].index, inplace=True)

# ~ print(df2.head())
