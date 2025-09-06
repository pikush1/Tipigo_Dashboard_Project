import re
import pandas as pd

def InteractivePipeline(raw_data, input_benchmarks, initial_cash, risk_free):
    raw_data_df = pd.read_excel(raw_data, sheet_name="Portfolio Raw Data")
    benchmark = pd.read_excel(raw_data, sheet_name=f"{input_benchmarks} Raw Data")
    
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

    realized_short_per_month = filtered.iloc[1::2, [0, 10]]

    # Reset the index and rename the columns.
    realized_short_per_month = realized_short_per_month.reset_index(drop=True)
    realized_short_per_month.columns = ["Date", "Realized_Short"]

    # Convert the Date column to a proper datetime format for merging.
    realized_short_per_month['Date'] = pd.to_datetime(realized_short_per_month['Date']).dt.to_period('M')
    result_df['Date'] = pd.to_datetime(result_df['Date']).dt.to_period('M')

    result_df = result_df.merge(realized_short_per_month, on="Date", how="left")

    result_df["Total_Change_Short"] = result_df["Unrealized_Short"] + result_df["Realized_Short"]
    
    # Total
    # unrealized total
    result_df["Unrealized_Total"] = result_df["Unrealized_Long"] + result_df["Unrealized_Short"]
    # realized total
    result_df["Realized_Total"] = result_df["Realized_Long"] + result_df["Realized_Short"]
    # total
    result_df["Total_Change"] = result_df["Total_Change_Long"] + result_df["Total_Change_Short"]


    # Add cash deposits & withdraws from raw_data
    filtered_data = raw_data_df[raw_data_df.iloc[:, 3] == "Deposits"].iloc[:, [0,5]]
    filtered_data.columns = ['Date', 'Amount']
    filtered_data['Date'] = pd.to_datetime(filtered_data['Date'])
    filtered_data['Date'] = filtered_data['Date'].dt.strftime('%Y-%m')
    result_df['Date'] = result_df['Date'].astype(str)

    merged_df = pd.merge(result_df, filtered_data, on='Date', how='left')
    merged_df.rename(columns={'Amount': 'Deposits & Withdraws'}, inplace=True)
    merged_df.fillna(0, inplace=True)
    result_df = merged_df

    result_df["Monthly Opening Balance"] = initial_cash + (result_df['Total_Change'] + result_df['Deposits & Withdraws']).shift(1).cumsum().fillna(0)
    result_df["Portfolio_Monthly_Yield"] = (result_df["Monthly Opening Balance"] + result_df['Total_Change']) / (result_df["Monthly Opening Balance"]) - 1

    # Add 1 to each value in the 'Portfolio_Monthly_Yield' column to get return factors
    result_df['Return_Factor'] = 1 + result_df['Portfolio_Monthly_Yield']

    # Calculate the cumulative product of the return factors
    result_df['Cumulative_Return_Factor'] = result_df['Return_Factor'].cumprod()

    # Subtract 1 to get the 'Total Cumulative Return'
    result_df['Total_Cumulative_Return'] = result_df['Cumulative_Return_Factor'] - 1
    result_df = result_df.drop(columns=['Cumulative_Return_Factor', 'Return_Factor'])

#_____________________________________________________________

    benchmark.rename(columns={'Month Identifier': 'Date'}, inplace=True)

    merged_df = pd.merge(result_df, benchmark[['Date', benchmark.iloc[:, 4].name]], on='Date', how='left')
    merged_df.rename(columns={benchmark.iloc[:, 4].name: f"{input_benchmarks}_Monthly_Return"}, inplace=True)
    merged_df[f"{input_benchmarks}_Monthly_Return"] = merged_df[f"{input_benchmarks}_Monthly_Return"] / 100
    result_df = merged_df

    result_df['Return_Factor_Benchmark'] = 1 + result_df[f"{input_benchmarks}_Monthly_Return"]
    result_df['Cumulative_Return_Factor_Benchmark'] = result_df['Return_Factor_Benchmark'].cumprod()
    result_df[f"{input_benchmarks}_Cumulative_Return"] = result_df['Cumulative_Return_Factor_Benchmark'] - 1
    result_df = result_df.drop(columns=['Cumulative_Return_Factor_Benchmark', 'Return_Factor_Benchmark'])
    result_df["Excess_Return"] = result_df["Portfolio_Monthly_Yield"] - result_df[f"{input_benchmarks}_Monthly_Return"]


    # Add risk-free data
    risk_free["YearMonth"] = pd.to_datetime(risk_free["observation_date"]).dt.to_period("M")
    result_df["YearMonth"] = pd.to_datetime(result_df["Date"]).dt.to_period("M")

    result_df = result_df.merge(
        risk_free[["YearMonth", "daily_risk_free_rate_per_month"]],
        on="YearMonth",
        how="left"
    )

    result_df.drop(columns=["YearMonth"], inplace=True)
    result_df["Risk_Free_Excess_Return"] = result_df["Portfolio_Monthly_Yield"] - result_df["daily_risk_free_rate_per_month"]


    print(result_df.to_string())
    return result_df


