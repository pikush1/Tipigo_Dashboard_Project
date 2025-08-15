import pandas as pd
from typing import List

def take_stock_prices(filepath): # this function takes tipigo's system file, extract stock prices
    df = pd.read_excel(filepath, sheet_name="Daily Performance")
    
    # Get price columns (from column 7 onwards)
    price_columns = df.columns[7:]
    
    # Clean and prepare the data
    df_clean = df[["Symbol"] + list(price_columns)].copy()
    
    # Remove invalid/non-stock symbols
    df_clean = df_clean[~df_clean["Symbol"].isin(["Assets", "Cash", "Units", "Unit Price"])]
    df_clean = df_clean.dropna(subset=["Symbol"])
    df_clean = df_clean[df_clean["Symbol"].str.strip() != ""]
    
    # Convert price columns to numeric before any operations
    for col in price_columns:
        df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
    
    # Only keep rows that have at least some price data
    df_clean = df_clean[df_clean[price_columns].notna().any(axis=1)]
    

    if df_clean["Symbol"].duplicated().any():
        # Instead of picking the best row, combine all data for each symbol
        def combine_symbol_data(df, price_cols):
            result_rows = []
            for symbol in df["Symbol"].unique():
                symbol_data = df[df["Symbol"] == symbol]
                
                # Create a new row for this symbol
                combined_row = {"Symbol": symbol}
                
                # For each price column, take the first non-null value found
                for col in price_cols:
                    # Get all non-null values for this column across all rows of this symbol
                    non_null_values = symbol_data[col].dropna()
                    if len(non_null_values) > 0:
                        # Take the first non-null value (you could also use .iloc[0] or another logic)
                        combined_row[col] = non_null_values.iloc[0]
                    else:
                        combined_row[col] = None
                
                result_rows.append(combined_row)
            
            return pd.DataFrame(result_rows)
        
        df_grouped = combine_symbol_data(df_clean, price_columns)
    else:
        # No duplicates, use data as-is
        df_grouped = df_clean.reset_index(drop=True)
    
    # Melt to long format
    stock_prices = df_grouped.melt(
        id_vars=["Symbol"],
        value_vars=price_columns,
        var_name="Date",
        value_name="Closing Price"
    )
    
    # Convert data types
    stock_prices["Date"] = pd.to_datetime(stock_prices["Date"], errors='coerce')
    stock_prices["Closing Price"] = pd.to_numeric(stock_prices["Closing Price"], errors="coerce")
    
    # Clean up final data
    stock_prices.dropna(subset=["Closing Price", "Date"], inplace=True)
    stock_prices = stock_prices.sort_values(by=["Symbol", "Date"]).reset_index(drop=True)
    
    return stock_prices

#print(take_stock_prices("data/system_files/444517.xlsx"))

def take_benchmark(stock_prices, benchmarks):
    benchmark_mask = stock_prices["Symbol"].isin(benchmarks)
    benchmark_df = stock_prices[benchmark_mask].copy()
    benchmark_df = benchmark_df.sort_values(["Symbol", "Date"])

    final_benchmark = pd.DataFrame()
    final_benchmark["Date"] = benchmark_df["Date"].drop_duplicates().sort_values().values

    for benchmark in benchmarks:
        benchmark_data = benchmark_df[benchmark_df['Symbol'] == benchmark].copy()
        benchmark_data = benchmark_data.sort_values("Date")
        daily = benchmark_data["Closing Price"].pct_change().fillna(0).values
        cumulative = (benchmark_data["Closing Price"] / benchmark_data["Closing Price"].iloc[0] - 1).values
        temp_df = pd.DataFrame({
            "Date": benchmark_data["Date"].values,
            f"Daily_return_{benchmark}": daily,
            f"Cumulative_return_{benchmark}": cumulative
        })
        final_benchmark = final_benchmark.merge(temp_df, on="Date", how="left")

    return final_benchmark

#print(take_benchmark(take_stock_prices("data/system_files/444517.xlsx"), ['QQEW']))
