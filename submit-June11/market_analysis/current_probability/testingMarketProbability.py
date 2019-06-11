# run this script as:
# python testingMarketProbability.py InputDataset.csv

# e.g.
# python testingMarketProbability.py data/GSPC.csv

# use python 3.
# market_analysis module must be in local directory 
# or otherwise in python path

# Get command line parameter:
import sys




import pprint
import copy

import csv
from matplotlib import pyplot as plt
from datetime import datetime
#import datetime as datetimeroot

# One-liners used in this module:
addNyears=lambda d,n: d.replace(year=d.year+n)
parseDate=lambda _: datetime.strptime(_,'%Y-%m-%d') # convert date as string to a datetime object
lTranspose=lambda _: list(map(list, zip(*_))) # transpose a list (pivot table)
flattenList=lambda _: [_1 for _2 in _ for _1 in _2] # collapse a list of lists to a 1d-list.

from market_analysis.market_historical_stats import output_historical_data

sample_dataset=output_historical_data.get_data(sys.argv[1])
# compute intervals
mrkt_intervals=output_historical_data.compute_mrkt_intervals(sample_dataset)

currentMarketType=['bull', 'bear'][mrkt_intervals['bull_markets'][-1][1][0]<
                                 mrkt_intervals['bear_markets'][-1][1][0]]
#print(currentMarketType)


latest_mrkt_change=[mrkt_intervals['bull_markets'][-1][1],mrkt_intervals['bear_markets'][-1][1]][mrkt_intervals['bull_markets'][-1][1][0]>
                                 mrkt_intervals['bear_markets'][-1][1][0]]
#print(latest_mrkt_change)

# mrkt_intervals.keys()

is_in_correction= flattenList(mrkt_intervals[currentMarketType+'_mrkt_corrections'])[-1][1][0] == sample_dataset[-1][0]
print(flattenList(mrkt_intervals[currentMarketType+'_mrkt_corrections'])[-1][1][0])
#print(is_in_correction)
is_in_pullback= flattenList(mrkt_intervals[currentMarketType+'_mrkt_pullbacks'])[-1][1][0] == sample_dataset[-1][0]
print(flattenList(mrkt_intervals[currentMarketType+'_mrkt_pullbacks'])[-1][1][0])
#print(is_in_pullback)


if not is_in_pullback and not is_in_correction:
    marketModifier="market"
elif is_in_pullback:
    marketModifier="pullback"
elif is_in_correction:
    marketModifier="correction"

latest_corr_ival=flattenList(mrkt_intervals[currentMarketType+'_mrkt_corrections'])[-1]
latest_pullback_ival=flattenList(mrkt_intervals[currentMarketType+'_mrkt_pullbacks'])[-1]


#1. Determine the current market direction. 
# (bull market, bear market, bull pullback, bear pullback, bull correction, bear correction)
print ("Current market direction is: %s %s" %(currentMarketType,marketModifier))
marketDirection="%s %s" %(currentMarketType,marketModifier)

#2. Determine how long we have been going in this current direction (number of days)? By how much (% change)?

if marketModifier=="market": #TODO: check that this is correct - we must use the first point of the last interval
    direction_days=sample_dataset[-1][0]-latest_mrkt_change[0]
    direction_change=(sample_dataset[-1][1]-latest_mrkt_change[1])/latest_mrkt_change[1]
if marketModifier=="correction":
    direction_days=sample_dataset[-1][0]-latest_corr_ival[0][0]
    direction_change=(sample_dataset[-1][1]-latest_corr_ival[0][1])/latest_corr_ival[0][1]
if marketModifier=="pullback":
    direction_days=sample_dataset[-1][0]-latest_pullback_ival[0][0]
    direction_change=(sample_dataset[-1][1]-latest_pullback_ival[0][1])/latest_pullback_ival[0][1]
print("The market has been going in this direction for %s days" %direction_days.days)
print("The market changed by %d%%" %(float(direction_change)*100))

#3. Look up data in historical .csv files the extent and duration of the current type of move.
#marketModifier = "pullback"
print("Extents and directions of previous %s %ss" %(currentMarketType,marketModifier))
if marketModifier == "market":
	query='%s_%ss'%(currentMarketType,marketModifier)
#	pastMoves=[[(_[1][0]-_[0][0]).days,(_[1][1]-_[0][1])/_[0][1]] for _ in mrkt_intervals[query]]
	pastMoves=[[(_[1][0]-_[0][0]).days,(_[1][1]-_[0][1])/_[0][1]] for _ in mrkt_intervals[query][1:-1]] #TODO: check this is correct
	# what I'm trying to do here is remove the first and last at the probability computation step	
else:
	query='%s_mrkt_%ss'%(currentMarketType,marketModifier)
#	pastMoves=[[(_[1][0]-_[0][0]).days,(_[1][1]-_[0][1])/_[0][1]] for _ in flattenList(mrkt_intervals[query])]
	pastMoves=[[(_[1][0]-_[0][0]).days,(_[1][1]-_[0][1])/_[0][1]] for _ in flattenList(mrkt_intervals[query])[:-1]] #TODO: check this is correct
	# for pullbacks only the last should be removed, but not the first

pprint.pprint(pastMoves)

# 4. Calculate odds comparing current extent and duration to historical data. 
#For example if there are 75 samples of bull market corrections in the database, 
#and the current correction is larger than 60 of these samples, the probability 
#that the correction will continue is:

# (75-60)/75 = 0.2 (percent) 4 to 1 against correction continuing (odds ratio)
lenghtProbability=(len(pastMoves)-len([_ for _ in pastMoves if _[0]<direction_days.days]))/len(pastMoves)
priceProbability=(len(pastMoves)-len([_ for _ in pastMoves if abs(_[1])<abs(direction_change)]))/len(pastMoves)
print("The probability that %s will continue based on market length is %.5f, or %d%%; the odds are  1:%.5f"%(
    marketDirection,lenghtProbability,(100*float(lenghtProbability)), (1/(1.0000001-lenghtProbability))))#avoid devision by zero
print("The probability that %s will continue based on price change is %.5f, or %d%%; the odds are  1:%.5f"%(
    marketDirection,priceProbability,(100*float(priceProbability)), (1/(1.0000001-priceProbability))))#avoid devision by zero



# Write to PDF

# Output:
# A .pdf file with the following statistics summarized:
#    1. % change (extent), direction, type and duration of current move.
#    2. Odds that the market will continue in its current trend (both extent and duration), 
# print odds in both % out of 100 and 3 to 1 terms (odds ratio).
#    3. Probability of a pullback (using time between pullbacks), a correction (using time 
# between corrections) and change in direction (becoming bull vs bear market) based on historical data.


#TODO: clean this up, move imports to the top
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, cm
from reportlab.lib.pagesizes import letter, A4
c = canvas.Canvas('market_probability_test.pdf', pagesize=letter) #TODO: use custom name

lineCoords=range(int(letter[1]-100),100,-20) # create list to store line locations to write things to

to_write="The current market direction is %s %s" %(currentMarketType,marketModifier)
c.drawString(100, lineCoords[0], to_write)
to_write="The market has been going in this direction for %s days" %direction_days.days
c.drawString(100, lineCoords[1], to_write)
to_write="The market changed by %.2f%%" %(float(direction_change)*100)
c.drawString(100, lineCoords[2], to_write)

to_write="The probability that %s will continue based on market length is %.5f, or %d%%; the odds are  1:%.5f"%(
    marketDirection,lenghtProbability,(100*float(lenghtProbability)), (1/(1.0000001-lenghtProbability)))#avoid devision by zero
c.drawString(100, lineCoords[4], to_write)

to_write="The probability that %s will continue based on price change is %.5f, or %d%%; the odds are  1:%.5f"%(
    marketDirection,priceProbability,(100*float(priceProbability)), (1/(1.0000001-priceProbability)))#avoid devision by zero
c.drawString(100, lineCoords[5], to_write)

#for i in lineCoords:
#    print(i)
#    c.drawString(100,i,'abracadabra')

#c.showPage()

#c.drawString(100,100,'ali a baba')

c.save()











