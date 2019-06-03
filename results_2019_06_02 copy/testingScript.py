# load data from csv
# Plot
# Loop through data identifying bull markets
# Make a function so that the looping can be done to identify other market conditions

#!ls data
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

data=[]
with open('data/GSPC_80_10.csv','r') as _:
    _=csv.reader(_)
    for _ in _:
        data.append(_)
# date, closing price
closingData=[[parseDate(_[data[0].index('Date')]),float(_[data[0].index('Close')])] for _ in data[1:]]

from testingModule.identify_markets import identify_markets

#sampleDataset=[_ for _ in closingData if _[0]> addNyears(closingData[0][0],30) and _[0]< addNyears(closingData[0][0],60)]
sampleDataset=closingData
allMarkets = identify_markets(sampleDataset,0.8,1.2)
#pprint.pprint(allMarkets)

#cleanup
allBulls=[_ for _ in allMarkets['bull_markets'] if _[1] is not None]
allBears=[_ for _ in allMarkets['bear_markets'] if _[1] is not None]
#print("Bear markets")
#pprint.pprint(allBulls)
#print("Bull markets")
#pprint.pprint(allBears)

#import importlib

from testingModule import market_adjustment
#importlib.reload(market_adjustment)

allBullCorrs,allBullBwCorrs=[],[]
for _ in allBulls:
    results=market_adjustment.market_adjustment('bull',0.10,sampleDataset,_)
    allBullCorrs.append(results['adjustments'])
    allBullBwCorrs.append(results['between_adjustments'])

allBullPullbacks,allBullBwPullbacks=[],[]
for _ in flattenList(allBullBwCorrs):
    results=market_adjustment.market_adjustment('bull',0.05,sampleDataset,_)
    allBullPullbacks.append(results['adjustments'])
    allBullBwPullbacks.append(results['between_adjustments'])

allBearCorrs,allBearBwCorrs=[],[]
for _ in allBears:
    results=market_adjustment.market_adjustment('bear',0.10,sampleDataset,_)
    allBearCorrs.append(results['adjustments'])
    allBearBwCorrs.append(results['between_adjustments'])

allBearPullbacks,allBearBwPullbacks=[],[]
for _ in flattenList(allBearBwCorrs):
    results=market_adjustment.market_adjustment('bear',0.05,sampleDataset,_)
    allBearPullbacks.append(results['adjustments'])
    allBearBwPullbacks.append(results['between_adjustments'])

####
# PLOT Data
####
#plot with line overlays

plt.figure()
plt.title("Markets, bull corrections and bull pullbacks on ^GSPC")
plt.yscale('log')

plt.plot(*lTranspose(sampleDataset))

def plotMarket(market, color, label):
    for i,_ in enumerate(market): # PLOT BULL MARKETS
        if i==0: 
            plt.plot(*lTranspose(_), color=color, label=label)
        else: 
            plt.plot(*lTranspose(_), color=color)

plotMarket(allBulls, 'green', 'bull market')
plotMarket(allBears, 'red', 'bear market')
plotMarket(flattenList(allBullCorrs), 'orange', 'bull correction')
plotMarket(flattenList(allBullPullbacks), 'yellow', 'bull pullback')
plotMarket(flattenList(allBearCorrs), 'orange', 'bull correction')
plotMarket(flattenList(allBearPullbacks), 'yellow', 'bull pullback')
   
plt.legend()
plt.show()



'''
print("Latest price is %s" %sampleDataset[-1])
if allBulls[-1][1]<allBears[-1][1]: 
    print("Currently we are in a bull market, \nlast bear market was %s"  %allBears[-1])
    marketAge=sampleDataset[-1][0]-allBears[-1][1][0]
else:
    print("Currently we are in a bear market, \nlast bull market was %s"  %allBulls[-1])
    marketAge=sampleDataset[-1][0]-allBulls[-1][1][0]
print("Market age is %s" %marketAge)
'''
'''
#plot with markers
import copy
sampleDatasetEdit=copy.deepcopy(sampleDataset) # we wouldn't want to mess up our data

for dp in sampleDatasetEdit:
    dp.append('undefined')# add a third column to store market type
    dp.append('undefined')# add a forth column to store corrections
    dp.append('undefined')# add a fifth column to store pullbacks

# not a computationally efficient solution, but quick to implement
def updateColumnTo(dset,states,columnNum,value):
    for dpoint in dset:
        if dpoint[0]==states[0][0] or dpoint[0]==states[1][0]:
            dpoint[columnNum]='undefined'
        if dpoint[0]>states[0][0] and dpoint[0]<states[1][0]:
            dpoint[columnNum]=value


for bull in allBulls:
    updateColumnTo(sampleDatasetEdit,bull,2,'bull')
for bear in allBears:
    updateColumnTo(sampleDatasetEdit,bear,2,'bear')
    
for _ in flattenList(allBullCorrs):
    updateColumnTo(sampleDatasetEdit,_,3,'correction')
for _ in flattenList(allBullBwCorrs):
    updateColumnTo(sampleDatasetEdit,_,3,'between_corrections')
for _ in flattenList(allBearCorrs):
    updateColumnTo(sampleDatasetEdit,_,3,'correction')
for _ in flattenList(allBullBwCorrs):
    updateColumnTo(sampleDatasetEdit,_,3,'between_corrections')
        
for _ in flattenList(allBullPullbacks):
    updateColumnTo(sampleDatasetEdit,_,4,'pullback')
for _ in flattenList(allBullBwPullbacks):
    updateColumnTo(sampleDatasetEdit,_,4,'between_pullbacks')
for _ in flattenList(allBearPullbacks):
    updateColumnTo(sampleDatasetEdit,_,4,'pullback')
for _ in flattenList(allBullBwPullbacks):
    updateColumnTo(sampleDatasetEdit,_,4,'between_pullbacks')

#set plot start and finish
p_start=0
p_finish=7823
# ~ print(len(sampleDatasetEdit))

test_bull_bw_pullbacks=[_[0:2] for _ in sampleDatasetEdit[p_start:p_finish] if _[2]=='bull' and _[4]=='between_pullbacks']
test_bull_corrs=[_[0:2] for _ in sampleDatasetEdit[p_start:p_finish] if _[2]=='bull' and _[3]=='correction']
test_bull_pullbacks=[_[0:2] for _ in sampleDatasetEdit[p_start:p_finish] if _[2]=='bull' and _[4]=='pullback']
test_bear=[_[0:2] for _ in sampleDatasetEdit[p_start:p_finish] if _[2]=='bear']
test_bear_corrs=[_[0:2] for _ in sampleDatasetEdit[p_start:p_finish] if _[2]=='bear' and _[3]=='correction']
test_bear_pullbacks=[_[0:2] for _ in sampleDatasetEdit[p_start:p_finish] if _[2]=='bear' and _[4]=='pullback']

# ~ plt.figure(figsize=(20,8))
plt.figure()
plt.title("Markets, bull corrections and bull pullbacks on ^GSPC")
plt.yscale('log')
plt.plot(*lTranspose(test_bull_bw_pullbacks),'.', markersize=1, color='green')
plt.plot(*lTranspose(test_bear),'.', markersize=1, color='red')
plt.plot(*lTranspose(test_bull_corrs),'.', markersize=1, color='orange')
plt.plot(*lTranspose(test_bull_pullbacks),'.', markersize=1, color='yellow')
plt.plot(*lTranspose(test_bear_corrs),'.', markersize=1, color='orange')
plt.plot(*lTranspose(test_bear_pullbacks),'.', markersize=1, color='yellow')
plt.show()
'''
# LAST STEP IS TO EXPORT TO CSV
'''
import csv

with open ('output.csv', 'w') as f:
    w=csv.writer(f)
    w.writerows(sampleDatasetEdit)
    
'''
