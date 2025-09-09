# Tipigo_Dashboard_Project

The main function gets **raw_data** and finds the strategy with the **StrategySelector**, that's right due to the file's name
Each platform has its own strategy, and its own run method
All of the strategies have to implement a run method as they inherit from an ABC class.

For each platform, **strategy.run** method is implemented differently, according to the raw data of the platform
each strategy deals with all of the stages that need to be performed in order to get a csv & pdf which will be saved in
the results folder.
The method will return the processed data and will generate the necessary reports.

Notice that the risk free rate file is permanent for all platforms

To run **Hapoalim** -
Provide a dictionary like so :

    hapoalim_args = {
    "raw_data": "/Users/ofri.bracha/Desktop/tipigo_project/Tipigo_Dashboard_Project/data/raw_data/output_444558_hapoalim.xlsx",
    "system_file": "/Users/ofri.bracha/Desktop/tipigo_project/Tipigo_Dashboard_Project/data/system_files/444558.xlsx",
    "input_benchmarks": ['SPY'],
    "initial_cash": 500000,
    "risk_free_rate_file": risk_free_rate_file
    }
notes: benchmarks have to be in a list, can provide 2 benchmarks as well inside a list

To run **Interactive** -
Provide a dictionary like so :

     interactive_args = {
     "raw_data": "/Users/ofri.bracha/Desktop/tipigo_project/Tipigo_Dashboard_Project/data/raw_data/S&P500 SPY Hedged Interactive Brokers (2024) students.xlsx",
     "input_benchmarks": 'SPY',
     "initial_cash": 250000,
     "risk_free_rate_file": risk_free_rate_file
     }
notes: can handle only one benchmark, not inside a list

The main function can handle the fact that the input is different for every platform due to **kwargs.