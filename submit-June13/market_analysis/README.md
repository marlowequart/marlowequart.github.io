# Version

Date: June 12, 2019.

# Introduction

Make sure this package can be found on your PYTHONPATH. 
Either copy it to one of the python directories, or add this directory to the 
path, or run scripts from the same directory as where you place this package.

The package market_analysis consists of 3 subpackages.
Subpackage `market_historical_stats` computes historical probabilities and 
outputs market types and market intervals, `current_probability` computes 
current probabilities and outputs results to pdf. 
`overall_probability` contains the code to batch process multiple input file, 
a list of input and output pathsfiles must be provided as CSV.

# Examples

Assign market type, correction, pullback to each data point:
```
        python -m market_analysis.market_historical_stats.output_historical_data data-19-07-09/GSPC.csv GSPC-dps-1907-09.csv
```

Assign market type, correction, pullback, time between corrections and 
time between pullbacks to each data point:
```
        python -m market_analysis.market_historical_stats.output_historical_data data-19-07-09/GSPC.csv GSPC-dps-det-1907-09.csv detailed
```

Create a CSV of market intervals for markets, corrections, pullbacks and 
time between corrections and pullbacks:
```
        python -m market_analysis.market_historical_stats.output_market_intervals data-19-07-09/GSPC.csv GSPC-ivals-1907-09.csv
```

Generate a PDF for current market probabilities
```
        python -m market_analysis.current_probability.current_probability GSPC.csv GSPC.pdf
```

Process multiple files in a loop given a list of input and output files as CSV
(you need to list the paths to the input and outputs as two columns in the CSV,
then provide a path to this new file):
```
        python -m market_analysis.overall_probability.batch_pdf  sources.csv
```

# Bash tricks

The module `current_probability` outputs both to PDF and stdout. This is done 
intentionally, as in combination with a few lines of Bash scripting this 
can be used to examine how does the algorithm performs over time, a step 
that would be neccessary to validate the quality of predictions.

To generate a PDF for current market probabilities, while cropping off the 
last 1000 datapoints from the end of the dataset:
```
        head -n -1000 data/GSPC.csv > GSPC-1000.csv; python -m market_analysis.current_probability.current_probability  GSPC-1000.csv GSPC-1000.pdf
```

To examine "The probability that pullback will occur based on price change" 
for the period of the last 100 days sampled at 5 day intervals:
```
        for i in $(seq 100 -5 0); do head -n -$i data/GSPC.csv > GSPC-x.csv; python -m market_analysis.current_probability.current_probability GSPC-x.csv GSPC-x.pdf | grep 'The probability that pullback will occur based on price change is\|Current date is\|Current market direction is'; done
```