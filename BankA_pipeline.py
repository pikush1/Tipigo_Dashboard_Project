import pandas as pd
from bank_mapping import BankAMapping
import numpy as np

file_path = 'data/Stock_prices_and_benchmark.xlsx'
excel_data = pd.ExcelFile(file_path)

stock_prices_df = pd.read_excel(file_path, sheet_name='Stock Prices')
benchmark_df = pd.read_excel(file_path, sheet_name='Banchmark')

file_path = 'data/Raw_data.xlsx'
df = pd.read_excel(file_path)
bank_a_mapping = BankAMapping() # Here we will choose the strategy

uniform_raw_data = bank_a_mapping.map_to_uniform(df)

# Total assets final DF
Total_assets = pd.DataFrame()

# Fill Date column
first_date = uniform_raw_data['Date'].min()
last_date = pd.Timestamp("2025-04-01")
date_range = pd.date_range(start=first_date - pd.Timedelta(days=1), end=last_date)
Total_assets['Date'] = date_range

# Fill Month column
Total_assets["Month"] = Total_assets['Date'].dt.strftime('%Y-%m')

# Fill Buy_today column
filtered_buy = uniform_raw_data[uniform_raw_data["Action"] == "Buy"]
grouped_data = (
    filtered_buy
    .groupby("Date", as_index=False)
    .apply(lambda x: pd.Series({"Buy_today": (x["Quantity"] * x["Transaction_rate"]).sum()}))
)
Total_assets = (
    Total_assets.merge(grouped_data, on="Date", how="left")
)
Total_assets["Buy_today"] = Total_assets["Buy_today"].fillna(0)

# Fill Sell_today column
filtered_sell = uniform_raw_data[uniform_raw_data["Action"] == "Sell"]
grouped_data = (
    filtered_sell
    .groupby("Date", as_index=False)
    .apply(lambda x: pd.Series({"Sell_today": (x["Quantity"] * x["Transaction_rate"]).sum()}))
)
Total_assets = (
    Total_assets.merge(grouped_data, on="Date", how="left")
)
Total_assets["Sell_today"] = Total_assets["Sell_today"].fillna(0)

# Fill Dividend column
filtered_div = uniform_raw_data[uniform_raw_data["Action"] == "Dividend"]

grouped_data = (
    filtered_div
    .groupby("Date", as_index=False)["Net_transaction_amount"]
    .sum()
    .rename(columns={"Net_transaction_amount": "Dividend"})
)

Total_assets = Total_assets.merge(grouped_data, on="Date", how="left")
Total_assets["Dividend"] = Total_assets["Dividend"].fillna(0)


# Fill Fees column
grouped_fees = (
    uniform_raw_data
    .assign(Fees=uniform_raw_data["Transaction_fee_ILS"] / uniform_raw_data["Exchange_rate"])
    .groupby("Date", as_index=False)["Fees"]
    .sum()
)
Total_assets = (
    Total_assets.merge(grouped_fees, on="Date", how="left")
)
Total_assets["Fees"] = Total_assets["Fees"].fillna(0)

# Fill Tax column
grouped_fees = (
    uniform_raw_data
    .assign(Tax=uniform_raw_data["Tax_ILS_amount"])
    .groupby("Date", as_index=False)["Tax"]
    .sum()
)
Total_assets = (
    Total_assets.merge(grouped_fees, on="Date", how="left")
)
Total_assets["Tax"] = Total_assets["Tax"].fillna(0)

# Fill Cash column (vector calculation)
Initial_cash = 500000
Total_assets["Cash"] = None
Total_assets.loc[0, "Cash"] = Initial_cash

Total_assets["Net_change"] = (
    Total_assets["Sell_today"]  # Add Sell_today
    + Total_assets["Dividend"]  # Add Dividends
    - Total_assets["Buy_today"]  # Subtract Buy_today
    - Total_assets["Fees"]  # Subtract Fees
    - Total_assets["Tax"]  # Subtract Tax
)
Total_assets["Cash"] = Initial_cash + Total_assets["Net_change"].cumsum()
Total_assets.drop(columns=["Net_change"], inplace=True)

# Fill Quantity_after_split column

stock_prices_df = stock_prices_df.rename(columns={"Stock": "Stock_symbol"})
# Join on Date and Symbol
merged_raw_df = pd.merge(uniform_raw_data, stock_prices_df, on=["Date", "Stock_symbol"], how="left")
merged_raw_df["Round_div"] = np.floor(merged_raw_df["Transaction_rate"] / merged_raw_df["Value"])

merged_raw_df["Quantity_after_split"] = np.where(
    merged_raw_df["Round_div"] <= 1,
    merged_raw_df["Quantity"],
    merged_raw_df["Quantity"] * merged_raw_df["Round_div"]
)

unrealized_daily_df = pd.DataFrame()


#print(merged_raw_df)
#print(Total_assets)
# with pd.option_context('display.max_rows', None):
#     print(merged_raw_df)





