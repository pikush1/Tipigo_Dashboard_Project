
from strategy_selector import StrategySelector
from create_pdf import create_pdf_hapoalim
from create_csv import create_csv_hapoalim
from risk_free import compute_risk_free_rate
from create_monthly import create_monthly


def main(raw_data, input_benchmarks, initial_cash, risk_free_rate_file, system_file=None):

    kwargs = {
        "raw_data": raw_data,
        "input_benchmarks": input_benchmarks,
        "initial_cash": initial_cash,
        "risk_free_rate_file": risk_free_rate_file,
        "system_file": system_file
    }

    strategy = StrategySelector(raw_data)
    if not strategy :
        raise ValueError(f"No strategy found for file: {raw_data}")

    result_tuple = strategy.run(**kwargs)

    return result_tuple



if __name__ == "__main__":

    # permanent riskfree rate file
    risk_free_rate_file = "/Users/ofri.bracha/Desktop/tipigo_project/Tipigo_Dashboard_Project/data/risk_free_rate.xlsx"

    # run hapoalim :

    hapoalim_args = {
    "raw_data": "/Users/ofri.bracha/Desktop/tipigo_project/Tipigo_Dashboard_Project/data/raw_data/output_444558_hapoalim.xlsx",
    "system_file": "/Users/ofri.bracha/Desktop/tipigo_project/Tipigo_Dashboard_Project/data/system_files/444558.xlsx",
    "input_benchmarks": ['SPY'],  # manually insert benchmarks, maybe write as a dictionary to match file number to benchmark
    "initial_cash": 500000,
    "risk_free_rate_file": risk_free_rate_file
}
    main(**hapoalim_args)


#     # run interactive :

#     interactive_args = {
#     "raw_data": "/Users/ofri.bracha/Desktop/tipigo_project/Tipigo_Dashboard_Project/data/raw_data/S&P500 SPY Hedged Interactive Brokers (2024) students.xlsx",
#     "input_benchmarks": 'SPY', # supports only one benchmark here
#     "initial_cash": 250000,
#     "risk_free_rate_file": risk_free_rate_file
# }
#     main(**interactive_args)









