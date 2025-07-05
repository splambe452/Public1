import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from scipy.stats import norm
import datetime as dt

##Set time froim a certain number of eyars 
years = 10
endDate = dt.datetime.now()
startDate = endDate - dt. timedelta(days=years*365)
#create a list of tivckers 
tickers = ['NLR', 'URA','RSP','VOO','QQQ','BMO']
####Downloading Adjusted Close Prices daily - ADJ counts for dividends and accoutn spplits i only have close tho 
adj_close_df = pd.DataFrame()
for ticker in tickers:
    data = yf.download(ticker, start = startDate, end = endDate)
    adj_close_df[ticker] = data['Close']
print(adj_close_df)
###Calculating Daily Log Returns and drop na 
log_returns_df = np.log(adj_close_df / adj_close_df.shift(1)).dropna()
print(log_returns_df)
###Defining Functions to Calculate Portfolio Expected Return and Standard Deviation
## Assuming future returns based on prevoius returns 
### Create a function that will be used to calculate portfolio expected return
#We are assuming that future returns are based on past returns, which is not a reliable assumption.
def expected_return(weights, log_returns):
    return np.sum(log_returns.mean()*weights)
### Create a function that will be used to calculate portfolio standard deviation
## Covariance matrix takes into account the correlation between the assets in the portfolio
def standard_deviation (weights, cov_matrix):
    variance = weights.T @ cov_matrix @ weights
    return np.sqrt(variance)
###Creating a Covariance Matrix
cov_matrix = log_returns_df.cov()
print(cov_matrix)
#Calculating Portfolio Expected Return and Standard Deviation
portfolio_value = 100000  # Initial portfolio value
weights = np.array([1/len(tickers)] * len(tickers))  # Equal weights for simplicity
portfolio_expected_return = expected_return(weights, log_returns_df)
portfolio_std_dev = standard_deviation(weights, cov_matrix)
###Defining Functions for Monte Carlo Simulation
def random_z_score():
    return np.random.normal(0, 1)
### Create a function to calculate scenarioGainLoss
days = 1 # Number of days for the simulation, can be adjusted
def scenario_gain_loss(portfolio_value, portfolio_std_dev, z_score, days):
    return portfolio_value * portfolio_expected_return * days + portfolio_value * portfolio_std_dev * z_score * np.sqrt(days)
##Running Monte Carlo Simulation
### Run 10000 simulations
simulations = 10000
scenarioReturn = []
for i in range(simulations):
    z_score = random_z_score()
    scenarioReturn.append(scenario_gain_loss(portfolio_value, portfolio_std_dev, z_score, days))
##Calculating Value at Risk (VaR)
### Specify a confidence interval and calculate the Value at Risk (VaR) typically is 99 or 95%
confidence_interval = 0.95
VaR = -np.percentile(scenarioReturn, 100 * (1 - confidence_interval))
print(VaR)
##Plotting the Results
### Plot the results of all 10000 scenarios
plt.hist(scenarioReturn, bins=50, density=True)
plt.xlabel('Scenario Gain/Loss ($)')
plt.ylabel('Frequency')
plt.title(f'Distribution of Portfolio Gain/Loss Over {days} Days')
plt.axvline(-VaR, color='r', linestyle='dashed', linewidth=2, label=f'VaR at {confidence_interval:.0%} confidence level')
plt.legend()
plt.show()

