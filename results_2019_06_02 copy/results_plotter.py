# 6/2/19
# load data from csv
# Plot


#!ls data
import pprint
import copy

import csv
from matplotlib import pyplot as plt
from datetime import datetime


####
# Open results datafile
####







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

