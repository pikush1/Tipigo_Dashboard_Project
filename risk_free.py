import pandas as pd

def compute_risk_free_rate(file_path):
    file = pd.read_excel(file_path, sheet_name="Monthly")
    file["observation_date"] = pd.to_datetime(file["observation_date"])
    file["daily_risk_free_rate_per_month"] = ((file["TB3MS"]/100) + 1) **(1/252) - 1
    return file

#print(compute_risk_free_rate("data/risk_free_rate.xlsx"))