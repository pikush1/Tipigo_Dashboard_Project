import pandas as pd


def read_benchmark(file_path):
    df = pd.read_excel(file_path, sheet_name="Banchmark")
    df = df[df["ETF"].isin(["QQEW", "QQQ"])]
    return df

def process_benchmark_data(df):
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")

    df_qqew = df[df["ETF"] == "QQEW"].copy()
    df_qqq = df[df["ETF"] == "QQQ"].copy()

    df_qqew["Daily_Return_QQEW"] = df_qqew["Value"].pct_change().fillna(0)
    df_qqq["Daily_Return_QQQ"] = df_qqq["Value"].pct_change().fillna(0)

    first_qqew = df_qqew["Value"].iloc[0]
    first_qqq = df_qqq["Value"].iloc[0]

    df_qqew["Cumulative_Return_QQEW"] = (df_qqew["Value"] / first_qqew) - 1
    df_qqq["Cumulative_Return_QQQ"] = (df_qqq["Value"] / first_qqq) - 1

    result = pd.merge(
        df_qqew[["Date", "Daily_Return_QQEW", "Cumulative_Return_QQEW"]],
        df_qqq[["Date", "Daily_Return_QQQ", "Cumulative_Return_QQQ"]],
        on="Date",
        how="inner"
    )

    return result

def run(file_path):
    benchmark_df = read_benchmark(file_path)
    result_df = process_benchmark_data(benchmark_df)
    return result_df

#print(run("data/Stock_prices_and_benchmark.xlsx"))

