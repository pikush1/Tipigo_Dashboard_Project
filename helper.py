import pandas as pd

df = pd.read_excel(
    'data/raw_data/HistoricalStocksReports_hapoalim (68).xlsb',
    engine='pyxlsb',
    skiprows=3
)

df.columns = df.columns.str.strip()

df['תאריך נכונות'] = pd.to_datetime('1899-12-30') + pd.to_timedelta(df['תאריך נכונות'], unit='D')


# Get the name of the second column (account name)
second_col = df.columns[2]  # This should be 'שם חשבון'

# Show the detected column name for debug
print(f"Splitting by column: '{second_col}'")

# Split by account name and save each group as Excel files
for value, group in df.groupby(second_col):
    # Create a safe filename
    safe_value = str(value).replace('/', '_').replace('\\', '_')
    group.to_excel(f'data/raw_data/output_{safe_value}_hapoalim.xlsx', index=False)
