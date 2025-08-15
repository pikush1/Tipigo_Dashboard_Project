import os
import pandas as pd
from strategy_selector import MappingStrategy
#from strategies.tipigo_strategy import run_tipigo
from create_pdf import create_pdf
from create_csv import create_csv
from create_monthly import create_monthly
from total_assets_calc import pipeline
from split_system_data import take_stock_prices, take_benchmark
from risk_free import compute_risk_free_rate
from interactive_pipeline import InteractivePipeline

#MERGED_FILE = "data/merged_output.xlsx"

def main(raw_data, input_benchmarks, initial_cash, risk_free_rate_file, system_file=None):
    # for testing :
    # if os.path.exists(MERGED_FILE):
    #     print(f"Loading cached merged data from: {MERGED_FILE}")
    #     return pd.read_excel(MERGED_FILE)

    strategy = MappingStrategy(raw_data)
    # if not strategy and "tipigo" in raw_data.lower():
    #     final_data = run_tipigo(raw_data)
    if not strategy :
        raise ValueError(f"No strategy found for file: {raw_data}")
    # interactive
    if strategy == "interactive":
        total_assets_monthly = InteractivePipeline(raw_data, input_benchmarks, initial_cash, risk_free_rate_file)
        return total_assets_monthly
    # hapoalim
    mapped_data = strategy.run(raw_data)
    stock_prices = take_stock_prices(system_file) # per account
    risk_free = compute_risk_free_rate(risk_free_rate_file)
    final_data, total_assets = pipeline(mapped_data, stock_prices, initial_cash, risk_free)

    benchmark_data = take_benchmark(stock_prices, input_benchmarks)

    merged = final_data.merge(benchmark_data, on="Date", how="left")
    # merged.to_excel(MERGED_FILE, index=False)
    # print(f"Merged data saved to: {MERGED_FILE}")

    return merged, total_assets

if __name__ == "__main__":        
    # permanent risk free rate file
    risk_free_rate_file = "data/risk_free_rate.xlsx"

    # hapoalim
    # raw_data = "data/raw_data/output_444558_hapoalim.xlsx"
    # system_file = "data/system_files/444558.xlsx"
    # input_benchmarks = ['SPY'] # manually insert benchmarks, maybe write as a dictionary to match file number to benchmark
    # initial_cash = 500000

    # merged_data, total_assets = main(raw_data, input_benchmarks, initial_cash, risk_free_rate_file, system_file)
    # risk_free_rate_file = "data/risk_free_rate.xlsx"

    # total_monthly = create_monthly(merged_data, input_benchmarks)
    # create_pdf(merged_data, input_benchmarks)
    # create_csv(merged_data, total_assets, total_monthly, input_benchmarks)


    # # interactive

    raw_data = "data/raw_data/S&P500 SPY Hedged Interactive Brokers (2024) students.xlsx"
    input_benchmarks = ['SPY']
    initial_cash = 250000
    total_assets_monthly = main(raw_data, input_benchmarks, initial_cash, risk_free_rate_file)

    # create_pdf(total_assets_monthly, input_benchmarks)
    # create_csv(total_assets_monthly, input_benchmarks)









