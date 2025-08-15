import matplotlib.pyplot as plt
from fpdf import FPDF
import numpy as np
from scipy.stats import gmean

def create_pdf(df, benchmarks): 
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

    return pdf.output("results/portfolio_report.pdf")