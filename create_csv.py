import pandas as pd
import numpy as np
from scipy.stats.mstats import gmean

def create_csv(merged_data, total_assets, total_monthly, input_benchmarks, file_path="results/report.xlsx"):
    TRADING_DAYS = 252

    # --- Portfolio metrics ---
    std_portfolio = merged_data['Daily_yield'].std(ddof=0) * np.sqrt(TRADING_DAYS)
    portfolio = merged_data['Cumulative_yield']
    running_max = portfolio.expanding().max()
    drawdown = portfolio - running_max
    max_drawdown = drawdown.min()
    max_dd_date = merged_data.loc[drawdown.idxmin(), 'Date']
    final_portfolio = portfolio.iloc[-1]
    
    # --- Portfolio Sharpe Ratio calculation ---
    # Assuming 'Excess_daily_yield' column exists for portfolio
    if 'Excess_daily_yield' in merged_data.columns:
        mean_excess_return = merged_data["Excess_daily_yield"].mean()
        sharpe_ratio_portfolio = mean_excess_return / std_portfolio * np.sqrt(TRADING_DAYS)
    else:
        sharpe_ratio_portfolio = np.nan

    # --- Build metrics summary table ---
    # Start with Portfolio metrics
    metrics_rows = [
        ("Portfolio Std Dev (Annualized)", round(std_portfolio, 4)),
        ("Max Drawdown", round(max_drawdown, 4)),
        ("Max Drawdown Date", str(max_dd_date.date())),
        ("Final Cumulative Return", round(final_portfolio, 4)),
        ("Sharpe Ratio", round(sharpe_ratio_portfolio, 4) if not np.isnan(sharpe_ratio_portfolio) else np.nan)
    ]
    metrics_dict = {"Metric": [r[0] for r in metrics_rows], "Portfolio": [r[1] for r in metrics_rows]}

    # For each benchmark, add dynamic columns
    for bm in input_benchmarks:
        cumret_col = f'Cumulative_return_{bm}'
        dailyret_col = f'Daily_return_{bm}'
        excess_ret_col = f'Excess_daily_return_{bm}'  # Assuming this column exists for benchmarks
        
        # Default values
        bm_metrics = [np.nan, np.nan, '', np.nan, np.nan]
        
        if cumret_col in merged_data.columns and dailyret_col in merged_data.columns:
            std_bm = merged_data[dailyret_col].std(ddof=0) * np.sqrt(TRADING_DAYS)
            bm_cumret = merged_data[cumret_col].iloc[-1]
            
            # For max drawdown, calculate for benchmark as well
            bm_series = merged_data[cumret_col].fillna(method="ffill")
            bm_running_max = bm_series.expanding().max()
            bm_drawdown = bm_series - bm_running_max
            bm_max_drawdown = bm_drawdown.min()
            bm_max_dd_date = merged_data.loc[bm_drawdown.idxmin(), 'Date']
            
            # Calculate Sharpe ratio for benchmark
            sharpe_ratio_bm = np.nan
            if excess_ret_col in merged_data.columns:
                std_excess_bm = merged_data[excess_ret_col].std()
                if std_excess_bm != 0:
                    geomean_excess_bm = gmean(1 + merged_data[excess_ret_col]) - 1
                    sharpe_ratio_bm = geomean_excess_bm / std_excess_bm * np.sqrt(TRADING_DAYS)
            
            bm_metrics = [
                round(std_bm, 4),
                round(bm_max_drawdown, 4),
                str(bm_max_dd_date.date()),
                round(bm_cumret, 4),
                round(sharpe_ratio_bm, 4) if not np.isnan(sharpe_ratio_bm) else np.nan
            ]
        
        metrics_dict[bm] = bm_metrics

    metrics_summary = pd.DataFrame(metrics_dict)

    # --- Performance Chart Data ---
    chart_cols = ['Date', 'Cumulative_yield'] + [
        f'Cumulative_return_{bm}' for bm in input_benchmarks if f'Cumulative_return_{bm}' in merged_data.columns
    ]
    chart_data = merged_data[chart_cols].copy()

    # --- Write to Excel ---
    with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
        # Data sheets
        merged_data.to_excel(writer, sheet_name='Merged Data', index=False)
        total_assets.to_excel(writer, sheet_name='Total Assets', index=False)
        total_monthly.to_excel(writer, sheet_name='Monthly Summary', index=False)
        metrics_summary.to_excel(writer, sheet_name='Metrics Summary', index=False)
        chart_data.to_excel(writer, sheet_name='Performance Chart', startrow=1, index=False)

        # Chart
        workbook = writer.book
        worksheet = writer.sheets['Performance Chart']
        chart = workbook.add_chart({'type': 'line'})
        for i, col in enumerate(chart_data.columns[1:], start=1):  # skip Date
            chart.add_series({
                'name':       ['Performance Chart', 1, i],
                'categories': ['Performance Chart', 2, 0, len(chart_data)+1, 0],
                'values':     ['Performance Chart', 2, i, len(chart_data)+1, i],
            })
        chart.set_title({'name': 'Cumulative Returns Comparison'})
        chart.set_x_axis({'name': 'Date'})
        chart.set_y_axis({'name': 'Cumulative Return'})
        chart.set_legend({'position': 'bottom'})
        worksheet.insert_chart('F2', chart)