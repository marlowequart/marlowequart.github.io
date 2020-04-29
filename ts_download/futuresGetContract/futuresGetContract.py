import csv
import numpy as np
import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta, FR
import re
# Functions to convert from string to datetime and vice-versa

def get_DT_obj(date_time_str:str) -> datetime.datetime:
    return datetime.datetime.strptime(date_time_str,'%Y-%m-%d')

def get_DT_str(date_time_obj:datetime.datetime) -> str:
    return datetime.datetime.strftime(date_time_obj,'%Y-%m-%d')

# Futures contract naming convertion is CCMYY (Contract-month-year)
MonthCodes=['F','G','H','J','K','M','N','Q','U','V','X','Z']
# DM = Delivery Month
# MPDM = Month Prior to Delivery Month

d=[]
with open('futuresGetContractAux/ts_download_list.txt') as f:
    r=csv.DictReader(f)
    d=[_ for _ in r]
    
getTrackerDescr=lambda t: [_ for _ in d if _['symbol']==t][0]
getThursPr2Fri=lambda dt: dt.replace(day=1)+relativedelta(weekday=FR(+2))-timedelta(days=1)


def getDateReturn(tracker, currentDate):
    #print(tracker)
    #print(currentDate)
    RollDateDef=getTrackerDescr(tracker)['Roll Date']
    #print(RollDateDef)
    if not ' of ' in RollDateDef:
        print('Can not run\n')
        return
    else:
        # DM = Delivery Month
        # MPDM = Month Prior to Delivery Month
        instr_date, instr_month = RollDateDef.split(' of ')
        month_delta=-1 if instr_month=='MPDM' else (0 if instr_month=='DM' else month)
        DMs=getTrackerDescr(tracker)['contract months'].split(',')
        #ContractNames=[tracker+DMs[-1]+str(currentDate.year-1)] + [
        #    tracker+_+str(currentDate.year) for _ in DMs]
        ContractNames=[tracker+_+str(currentDate.year) for _ in DMs] + [tracker+DMs[0]+str(currentDate.year+1)]
        #print(DMs)
        RollMonthsNum=np.asarray([MonthCodes.index(_) for _ in DMs])+month_delta
        #print (RollMonthsNum)
        ThisYrRollMFirstDates=[currentDate.replace(month=1,day=1)+relativedelta(months=_) 
                               for _ in RollMonthsNum]
        # Compute days
        if 'prior' not in instr_date:
            #print('simple day')
            dayOfMonth=re.search(r'\d+', instr_date).group()
            #print(dayOfMonth)
            rolloverDates=[_.replace(day=int(dayOfMonth)) for _ in ThisYrRollMFirstDates]
        elif "Thur prior 2nd Fri" in instr_date:
            #print("check for 2nd fr")
            rolloverDates=[_.replace(day=int(getThursPr2Fri(_).day)) 
                     for _ in ThisYrRollMFirstDates]
            #print(getThursPr2Fri(currentDate))
        else:
            #print('complicated day, cannot procede')
            raise ValueError('unexpected date description in the lookup file!')
        return [rolloverDates,ContractNames]
    print()

def getContractNameForDate(tracker,date):
    rolloverDates,contractNames=getDateReturn(tracker,date)
    datesPrior=[_ for _ in rolloverDates if _ < date]
    return contractNames[len(datesPrior)]
