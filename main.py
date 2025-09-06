
from strategy_selector import MappingStrategy
from create_pdf import create_pdf_hapoalim, create_pdf_interactive
from create_csv import create_csv_hapoalim, create_csv_interactive
from total_assets_calc import pipeline
from split_system_data import take_stock_prices, take_benchmark
from risk_free import compute_risk_free_rate
from interactive_pipeline import InteractivePipeline


def main(raw_data, input_benchmarks, initial_cash, risk_free_rate_file, system_file=None):

    risk_free = compute_risk_free_rate(risk_free_rate_file)

    strategy = MappingStrategy(raw_data)

    if not strategy :
        raise ValueError(f"No strategy found for file: {raw_data}")

    # interactive
    if strategy.lower() == "interactive":
        total_assets_monthly = InteractivePipeline(raw_data, input_benchmarks, initial_cash, risk_free)
        return total_assets_monthly

    # hapoalim
    mapped_data = strategy.run(raw_data)
    stock_prices = take_stock_prices(system_file) # per account
    final_data, total_assets = pipeline(mapped_data, stock_prices, initial_cash, risk_free)

    benchmark_data = take_benchmark(stock_prices, input_benchmarks)

    merged = final_data.merge(benchmark_data, on="Date", how="left")


    return merged, total_assets

if __name__ == "__main__":        
    # permanent risk free rate file
    risk_free_rate_file = "/Users/ofri.bracha/Desktop/tipigo_project/Tipigo_Dashboard_Project/data/risk_free_rate.xlsx"

    # hapoalim
    # raw_data = "/Users/ofri.bracha/Desktop/tipigo_project/Tipigo_Dashboard_Project/data/raw_data/output_444558_hapoalim.xlsx"
    # system_file = "/Users/ofri.bracha/Desktop/tipigo_project/Tipigo_Dashboard_Project/data/system_files/444558.xlsx"
    # input_benchmarks = ['SPY']    # manually insert benchmarks, maybe write as a dictionary to match file number to benchmark
    # initial_cash = 500000
    #
    # merged_data, total_assets = main(raw_data, input_benchmarks, initial_cash, risk_free_rate_file, system_file)
    #
    # total_monthly = create_monthly(merged_data, input_benchmarks)
    # create_pdf_hapoalim(merged_data, input_benchmarks)
    # create_csv_hapoalim(merged_data, total_assets, total_monthly, input_benchmarks)


    # interactive

    raw_data = "/Users/ofri.bracha/Desktop/tipigo_project/Tipigo_Dashboard_Project/data/raw_data/S&P500 SPY Hedged Interactive Brokers (2024) students.xlsx"
    input_benchmarks = 'SPY'
    initial_cash = 250000
    total_assets_monthly = main(raw_data, input_benchmarks, initial_cash, risk_free_rate_file)

    create_pdf_interactive(total_assets_monthly, input_benchmarks)
    create_csv_interactive(total_assets_monthly, input_benchmarks)


# לעשות ממשק משתמש, לשאול את קרן על זה שזה סבבה להשתמש בזה
# לעבוד על דוח אמצע, דוח מסכם








