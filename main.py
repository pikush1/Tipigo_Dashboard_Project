import os
import pandas as pd
from strategy_selector import get_strategy
from hapoalim_benchmark import run
from create_pdf import create_pdf

MERGED_FILE = "data/merged_output.xlsx"

def main(file_path):
    # for testing :
    if os.path.exists(MERGED_FILE):
        print(f"Loading cached merged data from: {MERGED_FILE}")
        return pd.read_excel(MERGED_FILE)

    strategy = get_strategy(file_path)
    if not strategy:
        raise ValueError(f"No strategy found for file: {file_path}")
    
    final_data = strategy.run(file_path)
    benchmark_data = run("data/benchmarks/Stock_prices_and_benchmark_hapoalim.xlsx")

    merged = final_data.merge(benchmark_data, on="Date", how="inner")
    merged.to_excel(MERGED_FILE, index=False)
    print(f"Merged data saved to: {MERGED_FILE}")

    return merged

if __name__ == "__main__":
    file_path = 'data/raw_data/HistoricalStocksReports (68).xlsx' # "data/raw_data/Raw_data_hapoalim.xlsx" for testing
    merged_data = main(file_path)
    print(merged_data)
    # df = merged_data
    # create_pdf(df)







