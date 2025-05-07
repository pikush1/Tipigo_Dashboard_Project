import pandas as pd
from bank_mapping import BankAMapping

file_path = 'Stock_prices_and_benchmark.xlsx'
excel_data = pd.ExcelFile(file_path)

stock_prices_df = pd.read_excel(file_path, sheet_name='Stock Prices')
benchmark_df = pd.read_excel(file_path, sheet_name='Banchmark')

file_path = 'Raw_data.xlsx'
df = pd.read_excel(file_path)
bank_a_mapping = BankAMapping() # Here we will choose the strategy

uniform_raw_data = bank_a_mapping.map_to_uniform(df)

# Total assets final DF
Total_assets = pd.DataFrame()

# Fill Date column
first_date = uniform_raw_data['Date'].min()
last_date = uniform_raw_data['Date'].max()
date_range = pd.date_range(start=first_date - pd.Timedelta(days=1), end=last_date) # fix last day to 04-01-2025
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

# Fill 


print(Total_assets)


