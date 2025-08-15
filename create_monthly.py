import pandas as pd

def create_monthly(data, benchmarks):
    data['Date'] = pd.to_datetime(data['Date'])
    data['Year-Month'] = data['Date'].dt.to_period('M')

    # Prepare aggregation dictionary
    agg_dict = {'Cumulative_yield': 'last'}
    rename_dict = {'Cumulative_yield': 'portfolio_return'}
    for benchmark in benchmarks:
        col = f'Cumulative_return_{benchmark}'
        agg_dict[col] = 'last'
        rename_dict[col] = f'benchmark_return_{benchmark}'

    monthly_data = data.groupby('Year-Month').agg(agg_dict).reset_index()
    monthly_data.rename(columns=rename_dict, inplace=True)

    # Calculate excess return for each benchmark
    for benchmark in benchmarks:
        monthly_data[f'excess_return_{benchmark}'] = (
            monthly_data['portfolio_return'] - monthly_data[f'benchmark_return_{benchmark}']
        )

    monthly_data['Year-Month'] = monthly_data['Year-Month'].astype(str)
    return monthly_data