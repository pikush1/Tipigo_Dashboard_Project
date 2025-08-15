import pandas as pd
import numpy as np

def pipeline(mapped_data: pd.DataFrame, stock_prices: pd.DataFrame, initial_cash, risk_free) -> pd.DataFrame:
    stock_prices_df = stock_prices

    # Total assets final DF
    Total_assets = pd.DataFrame()

    # Fill Date column
    mapped_data['Date'] = pd.to_datetime(mapped_data['Date'])
    first_date = mapped_data['Date'].min()
    last_date = pd.Timestamp("2025-04-01")
    date_range = pd.date_range(start=first_date - pd.Timedelta(days=1), end=last_date)
    Total_assets['Date'] = date_range

    # Fill Month column
    #Total_assets["Month"] = Total_assets['Date'].dt.strftime('%Y-%m')


    # Fill Buy_today column
    filtered_buy = mapped_data[mapped_data["Action"] == "Buy"]
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
    filtered_sell = mapped_data[mapped_data["Action"] == "Sell"]
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
    filtered_div = mapped_data[mapped_data["Action"] == "Dividend"]

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
        mapped_data
        .assign(Fees=mapped_data["Transaction_fee_ILS"] / mapped_data["Exchange_rate"])
        .groupby("Date", as_index=False)["Fees"]
        .sum()
    )
    Total_assets = (
        Total_assets.merge(grouped_fees, on="Date", how="left")
    )
    Total_assets["Fees"] = Total_assets["Fees"].fillna(0)

    # Fill Tax column
    grouped_fees = (
        mapped_data
        .assign(Tax=mapped_data["Tax_ILS_amount"])
        .groupby("Date", as_index=False)["Tax"]
        .sum()
    )
    Total_assets = (
        Total_assets.merge(grouped_fees, on="Date", how="left")
    )
    Total_assets["Tax"] = Total_assets["Tax"].fillna(0)


    # Fill Cash column (vector calculation)
    Total_assets["Cash"] = None
    Total_assets.loc[0, "Cash"] = initial_cash

    Total_assets["Net_change"] = (
        Total_assets["Sell_today"]  # Add Sell_today
        + Total_assets["Dividend"]  # Add Dividends
        - Total_assets["Buy_today"]  # Subtract Buy_today
        - Total_assets["Fees"]  # Subtract Fees
        - Total_assets["Tax"]  # Subtract Tax
    )
    Total_assets["Cash"] = initial_cash + Total_assets["Net_change"].cumsum()
    Total_assets.drop(columns=["Net_change"], inplace=True)


    # Fill Quantity_after_split column
    # Join on Date and Symbol
    merged_raw_df = pd.merge(mapped_data, stock_prices_df, on=["Date", "Symbol"], how="left")
    merged_raw_df["Round_div"] = np.floor(merged_raw_df["Transaction_rate"] / merged_raw_df["Closing Price"])

    merged_raw_df["Quantity_after_split"] = np.where(
        merged_raw_df["Round_div"] <= 1,
        merged_raw_df["Quantity"],
        merged_raw_df["Quantity"] * merged_raw_df["Round_div"]
    )


    # Sort both dataframes by date for consistent processing
    stock_prices_df = stock_prices_df.sort_values(by=['Date', 'Symbol'])
    merged_raw_df = merged_raw_df.sort_values(by='Date')

    # Initialize a dict to keep the running quantity per stock
    running_quantity = {}

    # Iterate through stock_prices_df row by row
    for idx, row in stock_prices_df.iterrows():
        stock = row['Symbol']
        date = row['Date']
        price = row['Closing Price']
        
        # Filter only transactions for the current date and stock
        day_transactions = merged_raw_df[
            (merged_raw_df['Symbol'] == stock) &
            (merged_raw_df['Date'] == date)
        ]
        
        # Initialize stock if not seen before
        if stock not in running_quantity:
            running_quantity[stock] = 0

        # Sum today's buys and sells
        buys = day_transactions[day_transactions['Action'] == "Buy"]['Quantity_after_split'].sum()
        sells = day_transactions[day_transactions['Action'] == "Sell"]['Quantity_after_split'].sum()
        
        # Update running quantity
        running_quantity[stock] += buys - sells
    
        # Compute cum_quantity = quantity * current price
        cum_quantity = running_quantity[stock] * price
        stock_prices_df.loc[idx, 'Unrealized_daily_per_stock'] = cum_quantity

    # Add unrealized to Total_assets
    daily_unrealized = (
        stock_prices_df
        .groupby("Date", as_index=False)["Unrealized_daily_per_stock"]
        .sum()
        .rename(columns={"Unrealized_daily_per_stock": "Unrealized"})
    )

    Total_assets = Total_assets.merge(daily_unrealized, on="Date", how="left")
    Total_assets["Unrealized"] = Total_assets["Unrealized"].fillna(0)

    Total_assets["Total"] = Total_assets["Unrealized"] + Total_assets["Cash"]
    Total_assets["Cumulative_yield"] = Total_assets["Total"] / Total_assets["Total"][0] - 1

    Total_assets["Daily_yield"] = (
    Total_assets["Cumulative_yield"].diff() / (Total_assets["Cumulative_yield"].shift(1) + 1)
    ).fillna(0.000)
    
    final_data = Total_assets[["Date", "Daily_yield", "Cumulative_yield"]].copy()

    
    risk_free["YearMonth"] = risk_free["observation_date"].dt.to_period("M")
    final_data["YearMonth"] = final_data["Date"].dt.to_period("M")

    final_data = final_data.merge(
        risk_free[["YearMonth", "daily_risk_free_rate_per_month"]],
        on="YearMonth",
        how="left"
    )

    final_data.drop(columns=["YearMonth"], inplace=True)
    final_data["Excess_daily_yield"] = final_data["Daily_yield"] - final_data["daily_risk_free_rate_per_month"]

    return final_data, Total_assets

