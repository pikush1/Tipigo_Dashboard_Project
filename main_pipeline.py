import pandas as pd

# Tipigo mapping

data = pd.read_excel("data/tipigo_system_data.xlsx", sheet_name="Insert Daily Performance")

# Relevant rows and columns
start_col = data.columns.get_loc("2023-01-03")
selected_df = data.iloc[[67, 68, 69, 70], start_col:]
final_data = selected_df.transpose().reset_index()
final_data.columns = ["Date", "Assets", "Cash", "Units", "Unit Price"]

final_data["Date"] = pd.to_datetime(final_data["Date"])
final_data["Cumulative_yield"] = final_data["Unit Price"] - 1


final_data["Daily_yield"] = (final_data["Cumulative_yield"] - final_data["Cumulative_yield"].shift(1)) / (1 + final_data["Cumulative_yield"].shift(1)) * 100
final_data["Daily_yield"][0] = 0

benchmark_data = pd.read_excel("data/tipigo_system_data.xlsx", sheet_name="insert banchmark")
benchmark_data = benchmark_data.rename(columns={"Tdate": "Date"})
benchmark_data["Date"] = pd.to_datetime(benchmark_data["Date"])
final_data = pd.merge(final_data, benchmark_data[["Date", "Tvalue"]], on="Date", how="left")
final_data = final_data.rename(columns={"Tvalue": "SPY"})



print(final_data)

