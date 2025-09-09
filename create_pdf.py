import os
import matplotlib.pyplot as plt
from fpdf import FPDF
import numpy as np


def create_pdf_hapoalim(df, benchmarks, file_path="results/hapoalim_pdf_report.pdf"):
    TRADING_DAYS = 252
    # Portfolio stats (not a benchmark)
    correlation_dict = {}
    std_dict = {}
    beta_dict = {}
    final_return_dict = {}

    # Portfolio
    std_portfolio = df['Daily_yield'].std(ddof=0) * np.sqrt(TRADING_DAYS)
    final_portfolio = df['Cumulative_yield'].iloc[-1]

    # Benchmark loop
    for bm in benchmarks:
        # Expecting names like "QQQ", "QQEW" etc. and columns as 'Cumulative_return_{bm}' and 'Daily_Return_{bm}'
        corr = df['Daily_yield'].corr(df[f'Daily_return_{bm}'])
        std_bm = df[f'Daily_return_{bm}'].std(ddof=0) * np.sqrt(TRADING_DAYS)
        beta = df['Daily_yield'].cov(df[f'Daily_return_{bm}']) / df[f'Daily_return_{bm}'].var()        
        final_bm = df[f'Cumulative_return_{bm}'].iloc[-1]
        correlation_dict[bm] = corr
        std_dict[bm] = std_bm
        beta_dict[bm] = beta
        final_return_dict[bm] = final_bm

    # Max drawdown
    portfolio = df['Cumulative_yield']
    running_max = portfolio.expanding().max()
    drawdown = portfolio - running_max
    max_drawdown = drawdown.min()
    max_dd_date = df.loc[drawdown.idxmin(), 'Date']

    # Graph
    plt.plot(df['Date'], df['Cumulative_yield'], label='Portfolio', linewidth=1, color='#07b96d')
    for i, bm in enumerate(benchmarks):
        color = '#ACABAC' if i == 0 else '#5897D4'
        plt.plot(df['Date'], df[f'Cumulative_return_{bm}'], label=bm, linewidth=1, color=color)
    plt.title('Cumulative Return Comparison')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Return')
    plt.grid(True)
    plt.legend()
    plt.xticks(fontsize=8)
    plt.tight_layout()
    plt.savefig("data/cumulative_chart.png")
    plt.close()

    # Create PDF
    pdf = FPDF()
    pdf.add_page()

    # add logo
    pdf.image("design/logo/tipigo_logo_01.png", x=10, y=8, w=30)

    # add fonts
    pdf.add_font('Assistant', '', 'design/fonts/Assistant-Regular.ttf', uni=True)
    pdf.add_font('Assistant', 'B', 'design/fonts/Assistant-Bold.ttf', uni=True)
    
    # Title
    pdf.set_text_color(7, 185, 109)
    pdf.set_font('Assistant', 'B', 20)
    pdf.cell(200, 15, txt="Portfolio Performance Report", ln=True, align='C')
    pdf.ln(5)
    
    # Add the chart
    pdf.image("data/cumulative_chart.png", x=10, y=30, w=190)
    pdf.set_y(170)
    
    # Performance Statistics Section
    pdf.set_font('Assistant', 'B', 14)
    pdf.set_text_color(7, 185, 109)
    pdf.cell(200, 10, txt="Performance Statistics", ln=True, align='L')
    pdf.ln(5)
    
    # Table headers
    pdf.set_font("Arial", 'B', size=11)
    pdf.set_text_color(7, 185, 109)
    pdf.cell(50, 8, txt="Metric", border=1, align='C')
    pdf.cell(45, 8, txt="Portfolio", border=1, align='C')
    for bm in benchmarks:
        pdf.cell(45, 8, txt=bm, border=1, align='C')
    pdf.ln()

    # Table body in black
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=10)
    # Standard Deviation row
    pdf.cell(50, 8, txt="Std Dev (Annualized)", border=1, align='C')
    pdf.cell(45, 8, txt=f"{std_portfolio:.2%}", border=1, align='C')
    for bm in benchmarks:
        pdf.cell(45, 8, txt=f"{std_dict[bm]:.2%}", border=1, align='C')
    pdf.ln()
    
    # Correlation row
    pdf.cell(50, 8, txt="Correlation vs Portfolio", border=1, align='C')
    pdf.cell(45, 8, txt="1.00", border=1, align='C')  # Portfolio vs itself
    for bm in benchmarks:
        pdf.cell(45, 8, txt=f"{correlation_dict[bm]:.3f}", border=1, align='C')
    pdf.ln()
    
    # Beta row
    pdf.cell(50, 8, txt="Beta vs Portfolio", border=1, align='C')
    pdf.cell(45, 8, txt="1.00", border=1, align='C')  # Portfolio vs itself
    for bm in benchmarks:
        pdf.cell(45, 8, txt=f"{beta_dict[bm]:.3f}", border=1, align='C')
    pdf.ln(10)

    # Calculate sharpe ratio
    mean_excess_return = df["Excess_daily_yield"].mean()
    sharp_ratio = mean_excess_return / std_portfolio * np.sqrt(TRADING_DAYS)

    # Add Sharpe Ratio Header
    pdf.ln(5)
    pdf.set_font("Arial", 'B', size=12)
    pdf.set_text_color(7, 185, 109)
    pdf.cell(200, 8, txt="Sharpe Ratio", ln=True, align='L')
    pdf.ln(2)
    
    # Add Sharpe Ratio Value in black
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=10)
    pdf.cell(50, 6, txt=f"Sharpe ratio: {sharp_ratio:.2%}", ln=True)
        
    # Add final returns header
    pdf.ln(5)
    pdf.set_font("Arial", 'B', size=12)
    pdf.set_text_color(7, 185, 109)
    pdf.cell(200, 8, txt="Final Cumulative Returns", ln=True, align='L')
    pdf.ln(2)
    
    # Add final returns values in black
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=10)
    pdf.cell(50, 6, txt=f"Portfolio: {final_portfolio:.2%}", ln=True)
    for bm in benchmarks:
        pdf.cell(50, 6, txt=f"{bm}: {final_return_dict[bm]:.2%}", ln=True)
    
    # Add interpretation notes header
    pdf.ln(5)
    pdf.set_font("Arial", 'B', size=12)
    pdf.set_text_color(7, 185, 109)
    pdf.cell(200, 8, txt="Key Insights", ln=True, align='L')
    pdf.ln(2)
    
    # Key insights body in black
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=10)
    
    # Risk comparison (vs the first benchmark)
    bm0 = benchmarks[0]
    if std_portfolio > std_dict[bm0]:
        risk_text = f"Portfolio is riskier than {bm0} ({std_portfolio:.1%} vs {std_dict[bm0]:.1%} volatility)"
    else:
        risk_text = f"Portfolio is less risky than {bm0} ({std_portfolio:.1%} vs {std_dict[bm0]:.1%} volatility)"
    pdf.cell(200, 5, txt=f"- {risk_text}", ln=True)
    
    # Beta interpretation (vs the first benchmark)
    beta_val = beta_dict[bm0]
    if beta_val > 1:
        beta_text = f"Portfolio is more volatile than {bm0} (Beta: {beta_val:.2f})"
    elif beta_val < 1:
        beta_text = f"Portfolio is less volatile than {bm0} (Beta: {beta_val:.2f})"
    else:
        beta_text = f"Portfolio moves similarly to {bm0} (Beta: {beta_val:.2f})"
    pdf.cell(200, 5, txt=f"- {beta_text}", ln=True)
    
    # Correlation interpretation (vs the first benchmark)
    corr_val = correlation_dict[bm0]
    if corr_val > 0.8:
        corr_text = f"High correlation with {bm0} ({corr_val:.2f}) - similar market exposure"
    elif corr_val > 0.5:
        corr_text = f"Moderate correlation with {bm0} ({corr_val:.2f})"
    else:
        corr_text = f"Low correlation with {bm0} ({corr_val:.2f}) - potential diversification"
    pdf.cell(200, 5, txt=f"- {corr_text}", ln=True)
    
    # Adding the drawdown header
    pdf.ln(10)
    pdf.set_font("Arial", 'B', size=12)
    pdf.set_text_color(7, 185, 109)
    pdf.cell(200, 8, txt="Maximum Drawdown Analysis", ln=True, align='L')
    pdf.ln(2)
    
    # Drawdown values in black
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=10)
    pdf.cell(50, 6, txt=f"Max Drawdown: {max_drawdown:.2%}", ln=True)
    pdf.cell(50, 6, txt=f"Drawdown Date: {max_dd_date}", ln=True)
    pdf.cell(50, 6, txt=f"Peak Value: {running_max.max():.2%}", ln=True)

    pdf.output(file_path)

    print(f"PDF report generated at {file_path}")



def create_pdf_interactive(result_df, input_benchmarks, file_path="results/interactive_pdf_report.pdf"):
    MONTHS_PER_YEAR = 12

    # --- Portfolio stats ---
    # Use Portfolio_Monthly_Yield for standard deviation and Beta
    std_portfolio = result_df['Portfolio_Monthly_Yield'].std(ddof=0) * np.sqrt(MONTHS_PER_YEAR)
    portfolio_cumulative = result_df['Total_Cumulative_Return']
    final_portfolio_return = portfolio_cumulative.iloc[-1]

    # --- Benchmark stats ---
    monthly_ret_col = f"{input_benchmarks}_Monthly_Return"
    cum_ret_col = f"{input_benchmarks}_Cumulative_Return"

    if monthly_ret_col in result_df.columns:
        # Correlation
        correlation_with_portfolio = result_df['Portfolio_Monthly_Yield'].corr(result_df[monthly_ret_col])

        # Std Dev
        std_bm = result_df[monthly_ret_col].std(ddof=0) * np.sqrt(MONTHS_PER_YEAR)

        # Beta
        beta_vs_portfolio = result_df['Portfolio_Monthly_Yield'].cov(result_df[monthly_ret_col]) / result_df[
            monthly_ret_col].var()

        # Final Return
        final_bm_return = result_df[cum_ret_col].iloc[-1]
    else:
        correlation_with_portfolio = np.nan
        std_bm = np.nan
        beta_vs_portfolio = np.nan
        final_bm_return = np.nan

    # --- Max drawdown ---
    running_max = portfolio_cumulative.expanding().max()
    drawdown = portfolio_cumulative - running_max
    max_drawdown = drawdown.min()
    max_dd_date = result_df.loc[drawdown.idxmin(), 'Date']

    # --- Graph ---
    plt.style.use('fivethirtyeight')
    plt.figure(figsize=(10, 6))
    plt.plot(result_df['Date'], result_df['Total_Cumulative_Return'], label='Portfolio', linewidth=2, color='#07b96d')
    plt.plot(result_df['Date'], result_df[f'{input_benchmarks}_Cumulative_Return'], label=input_benchmarks, linewidth=2,
             color='#ACABAC')
    plt.title('Cumulative Return Comparison')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Return')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.xticks(fontsize=8, rotation=45)
    plt.tight_layout()
    chart_path = "results/cumulative_chart.png"
    if not os.path.exists('results'):
        os.makedirs('results')
    plt.savefig(chart_path)
    plt.close()

    # --- Create PDF ---
    pdf = FPDF()
    pdf.add_page()

    # NOTE: Placeholder for logo and fonts. You will need to replace these
    # with your actual file paths for the code to run correctly.
    # pdf.image("design/logo/tipigo_logo_01.png", x=10, y=8, w=30)
    # pdf.add_font('Assistant', '', 'design/fonts/Assistant-Regular.ttf', uni=True)
    # pdf.add_font('Assistant', 'B', 'design/fonts/Assistant-Bold.ttf', uni=True)

    # Title
    pdf.set_text_color(7, 185, 109)
    pdf.set_font('helvetica', 'B', 20)
    pdf.cell(200, 15, txt="Portfolio Performance Report", ln=True, align='C')
    pdf.ln(5)

    # Add the chart
    pdf.image(chart_path, x=10, y=30, w=190)
    pdf.set_y(170)

    # Performance Statistics Section
    pdf.set_font('helvetica', 'B', 14)
    pdf.set_text_color(7, 185, 109)
    pdf.cell(200, 10, txt="Performance Statistics", ln=True, align='L')
    pdf.ln(5)

    # Table headers
    pdf.set_font("helvetica", 'B', size=11)
    pdf.set_text_color(7, 185, 109)
    pdf.cell(50, 8, txt="Metric", border=1, align='C')
    pdf.cell(45, 8, txt="Portfolio", border=1, align='C')
    pdf.cell(45, 8, txt=input_benchmarks, border=1, align='C')
    pdf.ln()

    # Table body in black
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("helvetica", size=10)

    # Standard Deviation row
    pdf.cell(50, 8, txt="Std Dev (Annualized)", border=1, align='C')
    pdf.cell(45, 8, txt=f"{std_portfolio:.2%}", border=1, align='C')
    pdf.cell(45, 8, txt=f"{std_bm:.2%}" if not np.isnan(std_bm) else "N/A", border=1, align='C')
    pdf.ln()

    # Correlation row
    pdf.cell(50, 8, txt="Correlation vs Portfolio", border=1, align='C')
    pdf.cell(45, 8, txt="1.00", border=1, align='C')  # Portfolio vs itself
    pdf.cell(45, 8, txt=f"{correlation_with_portfolio:.3f}" if not np.isnan(correlation_with_portfolio) else "N/A",
             border=1, align='C')
    pdf.ln()

    # Beta row
    pdf.cell(50, 8, txt="Beta vs Portfolio", border=1, align='C')
    pdf.cell(45, 8, txt="1.00", border=1, align='C')  # Portfolio vs itself
    pdf.cell(45, 8, txt=f"{beta_vs_portfolio:.3f}" if not np.isnan(beta_vs_portfolio) else "N/A", border=1, align='C')
    pdf.ln(10)

    # Sharpe Ratio
    mean_excess_return = result_df["Risk_Free_Excess_Return"].mean()
    std_excess_return = result_df["Risk_Free_Excess_Return"].std(ddof=0)
    sharpe_ratio_portfolio = (mean_excess_return / std_excess_return) * np.sqrt(
        MONTHS_PER_YEAR) if std_excess_return != 0 else np.nan

    pdf.ln(5)
    pdf.set_font("helvetica", 'B', size=12)
    pdf.set_text_color(7, 185, 109)
    pdf.cell(200, 8, txt="Sharpe Ratio", ln=True, align='L')
    pdf.ln(2)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("helvetica", size=10)
    pdf.cell(50, 6, txt=f"Sharpe ratio: {sharpe_ratio_portfolio:.2%}" if not np.isnan(
        sharpe_ratio_portfolio) else "Sharpe ratio: N/A", ln=True)

    # Final returns
    pdf.ln(5)
    pdf.set_font("helvetica", 'B', size=12)
    pdf.set_text_color(7, 185, 109)
    pdf.cell(200, 8, txt="Final Cumulative Returns", ln=True, align='L')
    pdf.ln(2)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("helvetica", size=10)
    pdf.cell(50, 6, txt=f"Portfolio: {final_portfolio_return:.2%}", ln=True)
    pdf.cell(50, 6, txt=f"{input_benchmarks}: {final_bm_return:.2%}" if not np.isnan(
        final_bm_return) else f"{input_benchmarks}: N/A", ln=True)

    # Key insights
    pdf.ln(5)
    pdf.set_font("helvetica", 'B', size=12)
    pdf.set_text_color(7, 185, 109)
    pdf.cell(200, 8, txt="Key Insights", ln=True, align='L')
    pdf.ln(2)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("helvetica", size=10)

    # Risk comparison
    if std_portfolio > std_bm:
        risk_text = f"Portfolio is riskier than {input_benchmarks} ({std_portfolio:.1%} vs {std_bm:.1%} volatility)"
    else:
        risk_text = f"Portfolio is less risky than {input_benchmarks} ({std_portfolio:.1%} vs {std_bm:.1%} volatility)"
    pdf.cell(200, 5, txt=f"- {risk_text}", ln=True)

    # Beta interpretation
    if beta_vs_portfolio > 1:
        beta_text = f"Portfolio is more volatile than {input_benchmarks} (Beta: {beta_vs_portfolio:.2f})"
    elif beta_vs_portfolio < 1:
        beta_text = f"Portfolio is less volatile than {input_benchmarks} (Beta: {beta_vs_portfolio:.2f})"
    else:
        beta_text = f"Portfolio moves similarly to {input_benchmarks} (Beta: {beta_vs_portfolio:.2f})"
    pdf.cell(200, 5, txt=f"- {beta_text}", ln=True)

    # Correlation interpretation
    if correlation_with_portfolio > 0.8:
        corr_text = f"High correlation with {input_benchmarks} ({correlation_with_portfolio:.2f}) - similar market exposure"
    elif correlation_with_portfolio > 0.5:
        corr_text = f"Moderate correlation with {input_benchmarks} ({correlation_with_portfolio:.2f})"
    else:
        corr_text = f"Low correlation with {input_benchmarks} ({correlation_with_portfolio:.2f}) - potential diversification"
    pdf.cell(200, 5, txt=f"- {corr_text}", ln=True)

    # Max Drawdown Analysis
    pdf.ln(10)
    pdf.set_font("helvetica", 'B', size=12)
    pdf.set_text_color(7, 185, 109)
    pdf.cell(200, 8, txt="Maximum Drawdown Analysis", ln=True, align='L')
    pdf.ln(2)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("helvetica", size=10)
    pdf.cell(50, 6, txt=f"Max Drawdown: {max_drawdown:.2%}", ln=True)
    pdf.cell(50, 6, txt=f"Drawdown Date: {max_dd_date}", ln=True)

    pdf.output(file_path)

    print(f"PDF report generated at {file_path}")