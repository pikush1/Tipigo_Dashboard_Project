import re
import pandas as pd

def InteractivePipeline(raw_data, input_benchmarks, initial_cash, risk_free_rate_file):
    raw_data_df = pd.read_excel(raw_data, sheet_name="Portfolio Raw Data")
    
    #long
    # Filter relevant rows for total and unrealized long
    filtered = raw_data_df[
        (raw_data_df.iloc[:, 1] == "Open Positions") &
        (raw_data_df.iloc[:, 2] == "Total") &
        (raw_data_df.iloc[:, 4] == "Stocks")
    ]
    # Extract needed columns
    result_df = filtered.iloc[:, [0, 12, 13]]
    # Rename columns
    result_df.columns = ["Date", "Total_Long", "Unrealized_Long"]

    # realized
    filtered = raw_data_df[
        (raw_data_df.iloc[:, 1] == "Realized & Unrealized Performance Summary") &
        (raw_data_df.iloc[:, 3] == "Total")
    ]

    realized_long_per_month = (
    filtered
    .groupby(raw_data_df.iloc[:, 0])
    .first()
    .iloc[:, 10]
    .reset_index()
)
    realized_long_per_month.columns = ["Date", "Realized_Long"]
    result_df = result_df.merge(realized_long_per_month, on="Date", how="left")

    filtered = raw_data_df[
    (raw_data_df.iloc[:, 1] == "Change in Dividend Accruals") &
    (raw_data_df.iloc[:, 3] == "Ending Dividend Accruals in USD")
]
    dividends = filtered.iloc[:, [0, 14]]
    dividends.columns = ["Date", "Dividends"]

    result_df = result_df.merge(dividends, on="Date", how="left")

    result_df["Total_Change_Long"] = result_df["Unrealized_Long"] + result_df["Realized_Long"] + result_df["Dividends"]

    # short
    # before row should have Futures or Totals, making sure we take the total associated with short
    # Filter relevant rows for total and unrealized long
    filtered = raw_data_df[
        (raw_data_df.iloc[:, 1] == "Open Positions") &
        (raw_data_df.iloc[:, 2] == "Total") &
        (raw_data_df.iloc[:, 4] == "Futures")
    ]
    # Extract needed columns
    short_df = filtered.iloc[:, [0, 12, 13]]
    # Rename columns
    short_df.columns = ["Date", "Total_Short", "Unrealized_Short"]
    result_df = result_df.merge(short_df, on="Date", how="left")

    # realized
    filtered = raw_data_df[
        (raw_data_df.iloc[:, 1] == "Realized & Unrealized Performance Summary") &
        (raw_data_df.iloc[:, 3] == "Total")
    ]

    realized_short_per_month = (
    filtered
    .groupby(raw_data_df.iloc[:, 0])
    .nth(1)
    .iloc[:, 10]
    .reset_index()
)
    print(realized_short_per_month.to_string())
    realized_short_per_month.columns = ["Date", "Realized_Short"]
    result_df = result_df.merge(realized_short_per_month, on="Date", how="left")

    result_df["Total_Change_Short"] = result_df["Unrealized_Short"] + result_df["Realized_Short"]
    
    # Total
    # unrealized total
    result_df["Unrealized_Total"] = result_df["Unrealized_Long"] + result_df["Unrealized_Short"]
    # realized total
    result_df["Realized_Total"] = result_df["Realized_Long"] + result_df["Realized_Short"]
    # total total
    result_df["Total_Change"] = result_df["Total_Change_Long"] + result_df["Total_Change_Short"]

    print(result_df.to_string())
    # print(result_df)

    return result_df


