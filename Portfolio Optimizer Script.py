import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import yfinance as yf
from scipy.optimize import minimize
from fredapi import Fred
import logging

# Configure logging for debugging and tracking script execution
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define tickers and date range for historical data
logging.info("Defining tickers and date range.")
tickers = ["URA", "VOO", "QQQ", "BMO", "RSP", "NLR"]
end_date = datetime.today()
start_date = end_date - timedelta(days=3 * 365)

# Fetch adjusted close prices for the defined tickers
logging.info("Fetching adjusted close prices for tickers.")
adj_close_df = pd.DataFrame()
for ticker in tickers:
    logging.debug(f"Downloading data for {ticker}.")
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    adj_close_df[ticker] = stock_data['Close']

# Calculate log returns for the assets
logging.info("Calculating log returns.")
log_returns = np.log(adj_close_df / adj_close_df.shift(1)).dropna()

# Calculate annualized covariance matrix for portfolio risk analysis
logging.info("Calculating covariance matrix.")
cov_matrix = log_returns.cov() * 252

# Define portfolio metrics functions for optimization
logging.info("Defining portfolio metrics.")

def standard_deviation(weights, cov_matrix):
    """Calculate portfolio standard deviation (risk)."""
    variance = weights.T @ cov_matrix @ weights
    return np.sqrt(variance)

def portfolio_return(weights, log_returns):
    """Calculate expected portfolio return."""
    return np.sum(log_returns.mean() * weights) * 252

def sharpe_ratio(weights, log_returns, cov_matrix, risk_free_rate):
    """Calculate Sharpe Ratio."""
    return (portfolio_return(weights, log_returns) - risk_free_rate) / standard_deviation(weights, cov_matrix)

# Fetch risk-free rate from the Federal Reserve API
logging.info("Fetching risk-free rate from the Federal Reserve API.")
fred = Fred(api_key='051d5809ddca97caac87dd597a0ddc35')
ten_year_treasury = fred.get_series('GS10') / 100
risk_free_rate = ten_year_treasury.iloc[-1]
logging.debug(f"Risk-free rate: {risk_free_rate:.4f}")

# Optimization setup to maximize Sharpe Ratio
logging.info("Setting up optimization to maximize Sharpe Ratio.")

def neg_sharpe_ratio(weights, log_returns, cov_matrix, risk_free_rate):
    """Objective function to minimize negative Sharpe Ratio."""
    return -sharpe_ratio(weights, log_returns, cov_matrix, risk_free_rate)

# Constraints: weights must sum to 1; bounds: no shorting, max 40% allocation per asset
constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
bounds = [(0, 0.4) for _ in range(len(tickers))]
initial_weights = np.array([1 / len(tickers)] * len(tickers))  # Equal initial weights

# Run optimization to find optimal portfolio weights
logging.info("Running optimization.")
optimized_results = minimize(
    neg_sharpe_ratio,
    initial_weights,
    args=(log_returns, cov_matrix, risk_free_rate),
    method='SLSQP',
    constraints=constraints,
    bounds=bounds
)

# Extract optimal weights from optimization results
optimal_weights = optimized_results.x
logging.info("Optimization complete. Extracting results.")

# Display optimal portfolio metrics and weights
logging.info("Displaying optimal portfolio metrics.")
print("Optimal_weights")
for ticker, weight in zip(tickers, optimal_weights):
    print(f'{ticker}: {weight * 100:.4f}%')

optimal_portfolio_return = portfolio_return(optimal_weights, log_returns)
optimal_portfolio_volatility = standard_deviation(optimal_weights, cov_matrix)
optimal_sharpe_ratio = sharpe_ratio(optimal_weights, log_returns, cov_matrix, risk_free_rate)

print(f'Expected annual return: {optimal_portfolio_return:.4f}')
print(f'Expected annual volatility: {optimal_portfolio_volatility:.4f}')
print(f'Sharpe ratio: {optimal_sharpe_ratio:.4f}')

# Plot optimal portfolio weights for visualization
logging.info("Plotting optimal portfolio weights.")
plt.figure(figsize=(10, 6))
plt.bar(tickers, optimal_weights)
plt.xlabel('Assets')
plt.ylabel('Optimal Weights')
plt.title('Optimal Portfolio Weights')
plt.show()