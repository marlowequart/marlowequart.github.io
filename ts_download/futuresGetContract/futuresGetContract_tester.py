import futuresGetContract
import sys
print( "\nUseage: python futuresGetContract.py <tracker> <date>")
print( "Example: python futuresGetContract.py BTC 2019-9-25")

print( "\nGet list of rollover dates and contracts for this year\n" )
print( futuresGetContract.getDateReturn(sys.argv[1],futuresGetContract.get_DT_obj(sys.argv[2])) )

print( "\nCurrent contract name is %s"%futuresGetContract.getContractNameForDate(sys.argv[1],futuresGetContract.get_DT_obj(sys.argv[2])) )
