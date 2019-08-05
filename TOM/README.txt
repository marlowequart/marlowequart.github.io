Summary of scripts:


stop_analysis.py
used to help determine optimum stop location for trades
Find largest % decline for winning trade and likelihood of that decline
Use that % decline to set stop


bet_size.py
use to calculate optimum bet size using Kelly Criterion
function returns max ammount to risk on trade. This relates to stop loss
and number of contracts is adjusted to meet that ammount of risk based on
stop location


plot_daily_returns_over_years.py
This script plots the average daily returns around a point of interest
over the course of many years. This script uses the mean of the mean method
so it is better as a rough calculation but does not represent actual returns.
This is useful to see if the TOM effect is stronger or weaker over time
This can be used as a quick baseline to see if a certain TOM strategy is better than others


hist_rtn_plotter.py
this script plots the actual returns over a given period using a given strategy
and plots returns over several durations in order to help see if a given
strategy is possibly becoming less effective.


tom_returns.py
This script is used to test a given trading strategy, with the ability to 
include stop losses and position sizing in order to determine the EV of the
strategy, CAGR and probability of catastrophic loss.


strategy_compare.py
I want to use this script to do a rough compare of different strategies
including start and end dates, buy/sell at open or close etc.

bear_markets.py
script used to assess strategy performance during bear markets or times of
high VIX. Study to consider turning strategy off in certain periods.






plot_daily_returns.py
this script plots the average daily returns (mean of each days return)
in a bar plot format over a given period. This is not useful for much
other than seeing what days have the best returns. See notes at end of script
for analysis and observations


russ_sp_compare.py
this script is a starting point to look at small cap vs large cap delta
during year rollover and also for TOM effect
