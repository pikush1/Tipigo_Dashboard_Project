import pandas as pd


def read_benchmark(file_path):
    benchmark1 = pd.read_excel(file_path, sheet_name="SPY")
    benchmark1["Tdate"] = pd.to_datetime(benchmark1["Tdate"])
    benchmark1 = benchmark1.rename(columns={'Tdate': 'Date'})  # This replaces Tdate with Date

    benchmark2 = pd.read_excel(file_path, sheet_name="RSP")
    benchmark2["Tdate"] = pd.to_datetime(benchmark2["Tdate"])
    benchmark2 = benchmark2.rename(columns={'Tdate': 'Date'})  # This replaces Tdate with Date

    merged_benchmarks = pd.merge(benchmark1, benchmark2, on='Date', how='inner', suffixes=('_SPY', '_RSP'))
    return merged_benchmarks


def process_benchmark_data(df):
    df = df.sort_values("Date")
    final_benchmark = pd.DataFrame()
    final_benchmark["Date"] = df["Date"].copy()
    final_benchmark["Daily_return_SPY"] = df["Tvalue_SPY"].pct_change().fillna(0)
    final_benchmark["Daily_Return_RSP"] = df["Tvalue_RSP"].pct_change().fillna(0)

    first_spy = df["Tvalue_SPY"].iloc[0] # first should come from starting date of protfolio !!!!!!!!!!!!!!!!!!!
    first_rsp = df["Tvalue_RSP"].iloc[0] # first should come from starting date of protfolio !!!!!!!!!!!!!!!!!!!

    final_benchmark["Cumulative_Return_SPY"] = (df["Tvalue_SPY"] / first_spy) - 1
    final_benchmark["Cumulative_Return_RSP"] = (df["Tvalue_RSP"] / first_rsp) - 1

    return final_benchmark

def run(file_path):
    benchmark_df = read_benchmark(file_path)
    result_df = process_benchmark_data(benchmark_df)
    return result_df

#print(run("data/tipigo_benchmarks.xlsx"))
