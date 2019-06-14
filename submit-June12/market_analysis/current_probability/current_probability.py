
'''
file name: current_probability.py
date: June 12, 2019
description: The main() function computes the number of days and the price change for the current market conditions,
	and uses past occurences to estimate probability of whether the current conditions will persist.
	In case that the present conditions are neither correction or pullback, it will calculate the probability
	of a new pullback or correction taking place.

inputs:
	input_file_path, line 35, type str: path to the input file
	output_file_path, line 35, type str: path to the output file

outputs:
	c.save(), line 230, outputs PDF.

Python version 3.6.7, modules used:
	This module, copy, csv, sys, pprint.
'''
import copy # built-in, Python 3.6.7
import csv # version 1.0
import pprint # built-in, Python 3.6.7
import sys # built-in, Python 3.6.7

from reportlab.pdfgen import canvas # version 3.5.23
from reportlab.lib.pagesizes import letter, A4 # version 3.5.23

# import modules from this package
from market_analysis.market_historical_stats import output_historical_data

# One-liners used in this module:
flatten_list=lambda _: [_1 for _2 in _ for _1 in _2] # collapse a list of lists to a 1d-list.


def main(input_file_path: str,output_file_path:str) -> None:
	# Read dataset from a file, call functions from market_analysis.market_historical_stats to 
	# determine market intervals, then compare current market conditions to historical intervals to
	# find out the probability that market conditions will persist.
	# If the market is not in correction or pullback, compute the probability that a 
	# correction or a pullback will occur.
	# Inputs:
	#	input_file_path is the path to the input CSV file
	#	output_file_path is the path to the output PDF file
	# Outputs:
	#	Nothing, creates a PDF file.

	# Get data from input CSV
	sample_dataset=output_historical_data.get_data(input_file_path)
	# Compute intervals
	mrkt_intervals=output_historical_data.compute_mrkt_intervals(sample_dataset)
	# Find out if the current market is bull or bear
	current_market_type=['bull', 'bear'][mrkt_intervals['bull_markets'][-1][1][0]<
								 mrkt_intervals['bear_markets'][-1][1][0]]
	# Find out the time and price of the last change in the market (bull to bear, or bear to bull)
	latest_mrkt_change=[mrkt_intervals['bull_markets'][-1][1],mrkt_intervals['bear_markets'][-1][1]][mrkt_intervals['bull_markets'][-1][1][0]>
								 mrkt_intervals['bear_markets'][-1][1][0]]
	print('Current date is %s, price is %s' %(sample_dataset[-1][0],sample_dataset[-1][1]))
	# Find out if current conditions are in correction or in pullback
	is_in_correction= flatten_list(mrkt_intervals[current_market_type+'_mrkt_corrections'])[-1][1][0] == sample_dataset[-1][0]
	is_in_pullback= flatten_list(mrkt_intervals[current_market_type+'_mrkt_pullbacks'])[-1][1][0] == sample_dataset[-1][0]

	# Record the subtype of the market in a variable market_modifier
	if not is_in_pullback and not is_in_correction:
		market_modifier="market"
	elif is_in_pullback:
		market_modifier="pullback"
	elif is_in_correction:
		market_modifier="correction"

	# Get the latest correction and the latest pullback intervals.
	latest_corr_ival=flatten_list(mrkt_intervals[current_market_type+'_mrkt_corrections'])[-1]
	latest_pullback_ival=flatten_list(mrkt_intervals[current_market_type+'_mrkt_pullbacks'])[-1]


	#1. Determine the current market direction. 
	# (bull market, bear market, bull pullback, bear pullback, bull correction, bear correction)
	marketDirection="%s %s" %(current_market_type,market_modifier)
	print("Current market direction is %s."%marketDirection)

	#2. Determine how long we have been going in this current direction (number of days)? By how much (% change)?

	# Declare a small function to compute minimum and maximum over the market interval between present and given date
	last_ival_price_extrema = lambda dset, sep, f: f([_[1] for _ in dset if _[0]>=sep])

	# find out how long did the present conditions (market, correction or pullback) presisted for, 
	# and find the price range across this interval
	if market_modifier=="market":
		direction_days=sample_dataset[-1][0]-latest_mrkt_change[0]
		direction_diff=last_ival_price_extrema(sample_dataset,latest_mrkt_change[0],max)-last_ival_price_extrema(sample_dataset,latest_mrkt_change[0],min)
		direction_change=direction_diff/latest_mrkt_change[1]
	if market_modifier=="correction":
		direction_days=sample_dataset[-1][0]-latest_corr_ival[0][0]
		direction_diff=last_ival_price_extrema(sample_dataset,latest_corr_ival[0][0],max)-last_ival_price_extrema(sample_dataset,latest_corr_ival[0][0],min)
		direction_change=direction_diff/latest_corr_ival[0][1]
	if market_modifier=="pullback":
		direction_days=sample_dataset[-1][0]-latest_pullback_ival[0][0]
		direction_diff=last_ival_price_extrema(sample_dataset,latest_pullback_ival[0][0],max)-last_ival_price_extrema(sample_dataset,latest_pullback_ival[0][0],min)
		direction_change=direction_diff/latest_pullback_ival[0][1]
	print("The market has been going in this direction for %s days" %direction_days.days)
	print("The market changed by %d%%" %(float(direction_change)*100))

	#3. Look up data in historical .csv files the extent and duration of the current type of move.
	print("Extents and directions of previous %s %ss" %(current_market_type,market_modifier))
	if market_modifier == "market":
		query='%s_%ss'%(current_market_type,market_modifier)
		# remove the first and last at the probability computation step	
		past_moves=[[(_[1][0]-_[0][0]).days,(_[1][1]-_[0][1])/_[0][1]] for _ in mrkt_intervals[query][1:-1]]
	else:
		query='%s_mrkt_%ss'%(current_market_type,market_modifier)
		# for pullbacks only the last should be removed, but not the first
		past_moves=[[(_[1][0]-_[0][0]).days,(_[1][1]-_[0][1])/_[0][1]] for _ in flatten_list(mrkt_intervals[query])[:-1]]

	# pprint.pprint(past_moves)

	# 4. Calculate odds comparing current extent and duration to historical data. 
	# For example if there are 75 samples of bull market corrections in the database, 
	# and the current correction is larger than 60 of these samples, the probability 
	# that the correction will continue is:
	# (75-60)/75 = 0.2 (percent) 4 to 1 against correction continuing (odds ratio)

	lenghtProbability=(len(past_moves)-len([_ for _ in past_moves if _[0]<direction_days.days]))/len(past_moves)
	priceProbability=(len(past_moves)-len([_ for _ in past_moves if abs(_[1])<abs(direction_change)]))/len(past_moves)
	print("The probability that %s will continue based on market length is %.5f, or %d%%; the odds are  1:%.5f"%(
		marketDirection,lenghtProbability,(100*float(lenghtProbability)), (1/(1.0000001-lenghtProbability))))#avoid devision by zero
	print("The probability that %s will continue based on price change is %.5f, or %d%%; the odds are  1:%.5f"%(
		marketDirection,priceProbability,(100*float(priceProbability)), (1/(1.0000001-priceProbability))))#avoid devision by zero


	# 5. Calculate the "Probability of a pullback (using time between pullbacks), 
	# a correction (using time between corrections) 
	# and change in direction (becoming bull vs bear market) based on historical data"

	# Only if the current conditions are neither correction nor pullback
	if market_modifier == "market":
		# Compute probability of correction
		bwCorr_past_moves=[[(_[1][0]-_[0][0]).days,(_[1][1]-_[0][1])/_[0][1]] for _ in flatten_list(mrkt_intervals[current_market_type+'_mrkt_bw_corrections'])]
		latest_bw_corr_ival=flatten_list(mrkt_intervals[current_market_type+'_mrkt_bw_corrections'])[-1]
		corr_direction_days=sample_dataset[-1][0]-latest_bw_corr_ival[0][0]
		corr_direction_diff=last_ival_price_extrema(sample_dataset,latest_bw_corr_ival[0][0],max)-last_ival_price_extrema(sample_dataset,latest_bw_corr_ival[0][0],min)
		corr_direction_change=corr_direction_diff/latest_bw_corr_ival[0][1]
		corr_lenghtProbability=1-(len(bwCorr_past_moves[:-1])-len([_ for _ in bwCorr_past_moves[:-1] if _[0]<corr_direction_days.days]))/len(bwCorr_past_moves[:-1])
		corr_priceProbability=1-(len(bwCorr_past_moves)-len([_ for _ in bwCorr_past_moves if abs(_[1])<abs(corr_direction_change)]))/len(bwCorr_past_moves)

		print("The probability that correction will occur based on market length is %.5f, or %d%%; the odds are  1:%.5f"%(
			corr_lenghtProbability,(100*float(corr_lenghtProbability)), (1/(1.0000001-corr_lenghtProbability)))) # avoid devision by zero
		print("The probability that correction will occur based on price change is %.5f, or %d%%; the odds are  1:%.5f"%(
			corr_priceProbability,(100*float(corr_priceProbability)), (1/(1.0000001-corr_priceProbability)))) # avoid devision by zero

		# Compute probability of a pullback
		bwPullback_past_moves=[[(_[1][0]-_[0][0]).days,(_[1][1]-_[0][1])/_[0][1]] for _ in flatten_list(mrkt_intervals[current_market_type+'_mrkt_bw_pullbacks'])]
		latest_bw_pullback_ival=flatten_list(mrkt_intervals[current_market_type+'_mrkt_bw_pullbacks'])[-1]
		pullback_direction_days=sample_dataset[-1][0]-latest_bw_pullback_ival[0][0]
		pullback_direction_diff=last_ival_price_extrema(sample_dataset,latest_bw_pullback_ival[0][0],max)-last_ival_price_extrema(sample_dataset,latest_bw_pullback_ival[0][0],min)
		pullback_direction_change=pullback_direction_diff/latest_bw_pullback_ival[0][1]
		pullback_lenghtProbability=1-(len(bwPullback_past_moves[:-1])-len([_ for _ in bwPullback_past_moves[:-1] if _[0]<pullback_direction_days.days]))/len(bwPullback_past_moves[:-1])
		pullback_priceProbability=1-(len(bwPullback_past_moves)-len([_ for _ in bwPullback_past_moves if abs(_[1])<abs(pullback_direction_change)]))/len(bwPullback_past_moves)

		print("The probability that pullback will occur based on market length is %.5f, or %d%%; the odds are  1:%.5f"%(
			pullback_lenghtProbability,(100*float(pullback_lenghtProbability)), (1/(1.0000001-pullback_lenghtProbability))))#avoid devision by zero
		print("The probability that pullback will occur based on price change is %.5f, or %d%%; the odds are  1:%.5f"%(
			pullback_priceProbability,(100*float(pullback_priceProbability)), (1/(1.0000001-pullback_priceProbability))))#avoid devision by zero
	else:
		print("Currently in adjustment! No need to calculate probability of pullback or correction.")

	# Write to PDF

	# Output:
	# A .pdf file with the following statistics summarized:
	#	1. % change (extent), direction, type and duration of current move.
	#	2. Odds that the market will continue in its current trend (both extent and duration), 
	# print odds in both % out of 100 and 3 to 1 terms (odds ratio).
	#	3. Probability of a pullback (using time between pullbacks), a correction (using time 
	# between corrections) and change in direction (becoming bull vs bear market) based on historical data.

	c = canvas.Canvas(output_file_path, pagesize=letter)
	fontSize=12
	c.setFont("Helvetica", 12)
	c.setTitle("Current probability for %s"%sys.argv[1])
	
	# Set margins to 0.25 in using paper dimentions
	marginLeft=int(0.25*letter[0]/8.5)
	marginTop=int(0.25*letter[1]/11)
	
	# Set line spacing to single, which is 115%
	lineCoords=range(int(letter[1]-marginTop-12),100,-int(fontSize*1.15))
	
	# Write to PDF
	to_write="The current date is %s." %sample_dataset[-1][0].strftime('%Y-%m-%d')
	c.drawString(marginLeft, lineCoords[0], to_write)
	to_write="The current market direction is %s %s." %(current_market_type,market_modifier)
	c.drawString(marginLeft, lineCoords[1], to_write)
	
	to_write="These conditions persisted for %s days." %direction_days.days
	c.drawString(marginLeft, lineCoords[3], to_write)
	to_write="The market changed by %.2f%%." %(float(direction_change)*100)
	c.drawString(marginLeft, lineCoords[4], to_write)
	
	to_write="The probability that %s will continue based on market length is %.5f, or %.2f%%;\n the odds are 1:%.5f"%(
		marketDirection,lenghtProbability,(100*float(lenghtProbability)), (1/(1.0000001-lenghtProbability)))#avoid devision by zero
	to_write=to_write.split('\n')
	c.drawString(marginLeft, lineCoords[6], to_write[0])
	c.drawString(marginLeft, lineCoords[7], to_write[1])
	
	to_write="The probability that %s will continue based on price change is %.5f, or %.2f%%;\n the odds are 1:%.5f"%(
		marketDirection,priceProbability,(100*float(priceProbability)), (1/(1.0000001-priceProbability)))#avoid devision by zero
	to_write=to_write.split('\n')
	c.drawString(marginLeft, lineCoords[9], to_write[0])
	c.drawString(marginLeft, lineCoords[10], to_write[1])
	
	# Only if the current conditions are neither correction nor pullback
	if market_modifier == "market":
		to_write="The probability that correction will occur based on market length is %.5f, or %.2f%%;\n the odds are  1:%.5f"%(corr_lenghtProbability,(100*float(corr_lenghtProbability)), (1/(1.0000001-corr_lenghtProbability)))#avoid devision by zero
		to_write=to_write.split('\n')
		c.drawString(marginLeft, lineCoords[13], to_write[0])
		c.drawString(marginLeft, lineCoords[14], to_write[1])
		to_write="The probability that correction will occur based on price change is %.5f, or %.2f%%;\n the odds are  1:%.5f"%(corr_priceProbability,(100*float(corr_priceProbability)), (1/(1.0000001-corr_priceProbability)))#avoid devision by zero
		to_write=to_write.split('\n')
		c.drawString(marginLeft, lineCoords[16], to_write[0])
		c.drawString(marginLeft, lineCoords[17], to_write[1])
		to_write="The probability that pullback will occur based on market length is %.5f, or %d%%;\n the odds are  1:%.5f"%(pullback_lenghtProbability,(100*float(pullback_lenghtProbability)), (1/(1.0000001-pullback_lenghtProbability)))
		to_write=to_write.split('\n')
		c.drawString(marginLeft, lineCoords[20], to_write[0])
		c.drawString(marginLeft, lineCoords[21], to_write[1])
		to_write="The probability that pullback will occur based on price change is %.5f, or %d%%;\n the odds are  1:%.5f"%(pullback_priceProbability,(100*float(pullback_priceProbability)), (1/(1.0000001-pullback_priceProbability)))
		to_write=to_write.split('\n')
		c.drawString(marginLeft, lineCoords[23], to_write[0])
		c.drawString(marginLeft, lineCoords[24], to_write[1])

	# Save PDF
	c.save()



# Check whether the module runs as a main script or is imported into another module.
# If module is run as a main script, then command line arguments are captured and used as parameters for the main() function
# to provide paths to the input and output files. 
if __name__ == "__main__":
	input_file_path=sys.argv[1]
	output_file_path=sys.argv[2]
	main(input_file_path,output_file_path)







