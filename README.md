# Tipigo_Dashboard_Project

The main function gets raw_data and finds the strategy that's right due to the file's name
mapped data returns the raw_data after mapping, each raw_data has a different strategy for mapping

Then, we take the stock prices from the Tipigo's system file
and the risk free rate from FRED

In the pipeline function we get mapped_data, stock_prices, initial_cash, risk_free
we create total_assets (unrealized is calculated there)
and final data which leaves us with - Date  Daily_yield  Cumulative_yield  daily_risk_free_rate_per_month  Excess_daily_yield

Then we take the benchmark data, and merge it with the final data to get the merged data

We use merged_data to create total_monthly, PDF, CSV