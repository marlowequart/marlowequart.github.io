'''
This study is used to help determine the optimal stop loss for the TOM trade.

Kelly formula is edge/odds

(payoff*win_prob-loss_prob)/payoff

Input: 

Output: 


	



pandas version: 0.18.1
matplotlib version: 3.0.3
mpl_finance version: 0.10.0
numpy version: 1.10.1
scipy version: 0.16.0

python version: 3.5.4

'''

import pandas as pd
import os
import numpy as np
import re
import datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import time



def main():

	bankroll=10000.
	num_wins=245
	num_loss=135
	
	# avg daily % return
	avg_daily=100
	
	# payoff is what you walk away with when you bet $1, which is just adding the percent gain
	payoff=1+(avg_daily/100)
	
	
	win_prob=num_wins/(num_wins+num_loss)
	loss_prob=1.-win_prob
	
	kelly=bankroll*(payoff*win_prob-loss_prob)/payoff
	kelly_pct=(payoff*win_prob-loss_prob)/payoff
	
	print('Kelly says to bet '+str(round(kelly_pct,2))+'% of bankroll which is '+str(round(kelly,2)))
	
	# The bet size is telling you the most you should risk or the total ammount you should buy?




main()