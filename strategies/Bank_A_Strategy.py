import pandas as pd
from strategies.base import MappingStrategy
import numpy as np

class BankAStrategy(MappingStrategy):
    def run(self, file_path: str) -> pd.DataFrame:
        raw = self.load(file_path)
        mapped = self.map_to_uniform(raw)
        return self.pipeline(mapped)

    def load(self, file_path: str) -> pd.DataFrame:
        return pd.read_excel(file_path)
    
    def map_to_uniform(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        column_mapping = {
            4: "Stock_symbol",        
            6: "Stock_full_name", 
            8: "Action",      
            9: "Date",       
            11: "Quantity",
            12: "Transaction_rate",
            13: "Gross_transaction_amount",
            16: "Net_transaction_amount",
            18: "Nominal_profit_ILS",
            25: "Real_profit_ILS",
            19: "Tax_ILS_amount",
            20: "Tax_used_amount",
            21: "Transaction_fee_ILS",
            22: "Exchange_rate",
            26: "Tax_ILS_percentage",
            27: "Tax_USD_percentage",
            28: "Percentage_transaction_fee",
            29: "Stock_exchange"
        }
        mapped_data = raw_data.rename(
            columns={raw_data.columns[i]: column_mapping[i] for i in column_mapping}
        )
        mapped_data = mapped_data[list(column_mapping.values())]
        action_mapping = {
            "קניה": "Buy",
            "מכירה": "Sell",
            "העברה לזכות הפקדון": "Transfer to deposit",
            "הטבה חלוקת מניות": "Stock distribution benefit",
            "דבידנד תשלום": "Dividend"
        }
        mapped_data["Action"] = mapped_data["Action"].map(action_mapping)
        return mapped_data

    def pipeline(self, mapped_data: pd.DataFrame) -> pd.DataFrame:
        
        file_path = 'data/Stock_prices_and_benchmark.xlsx'

        stock_prices_df = pd.read_excel(file_path, sheet_name='Stock Prices')
        #benchmark_df = pd.read_excel(file_path, sheet_name='Banchmark')

        # Total assets final DF
        Total_assets = pd.DataFrame()

        # Fill Date column
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
        merged_raw_df = pd.merge(mapped_data, stock_prices_df, on=["Date", "Stock_symbol"], how="left")
        merged_raw_df["Round_div"] = np.floor(merged_raw_df["Transaction_rate"] / merged_raw_df["Value"])

        merged_raw_df["Quantity_after_split"] = np.where(
            merged_raw_df["Round_div"] <= 1,
            merged_raw_df["Quantity"],
            merged_raw_df["Quantity"] * merged_raw_df["Round_div"]
        )


        # Sort both dataframes by date for consistent processing
        stock_prices_df = stock_prices_df.sort_values(by=['Date', 'Stock_symbol'])
        merged_raw_df = merged_raw_df.sort_values(by='Date')

        # Initialize a dict to keep the running quantity per stock
        running_quantity = {}

        # Initialize list to hold cum_quantity values
        cum_quantity_values = []

        # Iterate through stock_prices_df row by row
        for _, row in stock_prices_df.iterrows():
            stock = row['Stock_symbol']
            date = row['Date']
            price = row['Value']
            
            # Filter only transactions for the current date and stock
            day_transactions = merged_raw_df[
                (merged_raw_df['Stock_symbol'] == stock) &
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
            cum_quantity_values.append(cum_quantity)

        # Add unrealized to Total_assets
        stock_prices_df['Unrealized_daily_per_stock'] = cum_quantity_values
        #print(stock_prices_df)

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

        Final_data = Total_assets[["Date", "Daily_yield", "Cumulative_yield"]].copy()

        return Final_data