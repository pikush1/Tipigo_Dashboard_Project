import pandas as pd
from strategies.base import MappingStrategy


# Tipigo mapping
class BankBStrategy(MappingStrategy):
    def run(self, file_path: str) -> pd.DataFrame:
        raw = self.load(file_path)
        return self.pipeline(raw)
    
    def load(self, file_path: str) -> pd.DataFrame:
        return pd.read_excel(file_path, sheet_name="Insert Daily Performance")
    
    def pipeline(self, data: pd.DataFrame) -> pd.DataFrame:

        # Relevant rows and columns
        start_col = data.columns.get_loc("2023-01-03")
        selected_df = data.iloc[[67, 68, 69, 70], start_col:]
        tipigo_data = selected_df.transpose().reset_index()
        tipigo_data.columns = ["Date", "Assets", "Cash", "Units", "Unit Price"]

        tipigo_data["Date"] = pd.to_datetime(tipigo_data["Date"])
        tipigo_data["Cumulative_yield"] = tipigo_data["Unit Price"] - 1


        tipigo_data["Daily_yield"] = (tipigo_data["Cumulative_yield"] - tipigo_data["Cumulative_yield"].shift(1)) / (1 + tipigo_data["Cumulative_yield"].shift(1)) * 100
        tipigo_data["Daily_yield"][0] = 0

        benchmark_data = pd.read_excel("data/tipigo_system_data.xlsx", sheet_name="insert banchmark")
        benchmark_data = benchmark_data.rename(columns={"Tdate": "Date"})
        benchmark_data["Date"] = pd.to_datetime(benchmark_data["Date"])
        tipigo_data = pd.merge(tipigo_data, benchmark_data[["Date", "Tvalue"]], on="Date", how="left")
        tipigo_data = tipigo_data.rename(columns={"Tvalue": "SPY"})

        Final_data = tipigo_data[["Date", "Daily_yield", "Cumulative_yield"]].copy()

        return Final_data
