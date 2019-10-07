# bayesian-networks
Here we implement a bayesian network. It runs rejection sampling and likelihood weighting.

We chose to do option A.

Project Report: https://docs.google.com/document/d/1eRo916UaDDCmXksviulb9tiaRkocYmbHNLMrP3mf7M8/edit?usp=sharing

Project Data: https://docs.google.com/spreadsheets/d/1YVu2UEQJbT9Y_PHwk5wVNlY4YRZ9XecYhPfiZl_p7Tw/edit?usp=sharing

## To run
`python3 bn.py inputs/network_option_a.txt inputs/queryNum.txt numSamples`

- `numSamples` is an integer representing the number of samples to run on
- `inputs/queryNum.txt` is the query file to run on, likely `inputs/query1.txt` or `inputs/query2.txt`

## Libraries used
We chose to use networkx to store our network. We found it straightforward to work with. We also used pandas to store the cpt as a dataframe, which was nicer to work with than an array or dictionary.
