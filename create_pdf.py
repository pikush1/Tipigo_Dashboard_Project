import matplotlib.pyplot as plt
from fpdf import FPDF
import numpy as np

def create_pdf(df):
    TRADING_DAYS = 252
    # Correlation
    correlation_QQQ = df['Cumulative_yield'].corr(df['Cumulative_Return_QQQ'])
    correlation_QQEW = df['Cumulative_yield'].corr(df['Cumulative_Return_QQEW'])

    # Standart deviation
    std_portfolio = df['Daily_yield'].std(ddof=0) * np.sqrt(TRADING_DAYS)
    std_QQQ = df['Daily_Return_QQQ'].std(ddof=0) * np.sqrt(TRADING_DAYS)
    std_QQEW = df['Daily_Return_QQEW'].std(ddof=0) * np.sqrt(TRADING_DAYS)

    # Beta
    beta_QQQ = correlation_QQQ * std_portfolio / std_QQQ
    beta_QQEW = correlation_QQEW * std_portfolio / std_QQEW

    # Max dropdown
    portfolio = df['Cumulative_yield']
    running_max = portfolio.expanding().max()
    drawdown = portfolio - running_max
    max_drawdown = drawdown.min()
    max_dd_date = df.loc[drawdown.idxmin(), 'Date']
    
    # Graph
    plt.figure(figsize=(10, 6))
    plt.plot(df['Date'], df['Cumulative_yield'], label='Portfolio', linewidth=2, color='green')
    plt.plot(df['Date'], df['Cumulative_Return_QQEW'], label='QQEW', linewidth=2, color='blue')
    plt.plot(df['Date'], df['Cumulative_Return_QQQ'], label='QQQ', linewidth=2, color='gray')

    plt.title('Cumulative Return Comparison')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Return')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("data/cumulative_chart.png")
    plt.close()

    # Create enhanced PDF with statistics
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", 'B', size=16)
    pdf.cell(200, 15, txt="Portfolio Performance Report", ln=True, align='C')
    pdf.ln(5)
    
    # Add the chart
    pdf.image("data/cumulative_chart.png", x=10, y=30, w=190)

    pdf.set_y(150)  # Adjust this value based on your image size
    
    # Performance Statistics Section
    pdf.set_font("Arial", 'B', size=14)
    pdf.cell(200, 10, txt="Performance Statistics", ln=True, align='L')
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', size=11)
    pdf.cell(50, 8, txt="Metric", border=1, align='C')
    pdf.cell(45, 8, txt="Portfolio", border=1, align='C')
    pdf.cell(45, 8, txt="QQEW", border=1, align='C')
    pdf.cell(45, 8, txt="QQQ", border=1, align='C')
    pdf.ln()
    
    # Standard Deviation row
    pdf.set_font("Arial", size=10)
    pdf.cell(50, 8, txt="Std Dev (Annualized)", border=1, align='C')
    pdf.cell(45, 8, txt=f"{std_portfolio:.2%}", border=1, align='C')
    pdf.cell(45, 8, txt=f"{std_QQEW:.2%}", border=1, align='C')
    pdf.cell(45, 8, txt=f"{std_QQQ:.2%}", border=1, align='C')
    pdf.ln()
    
    # Correlation row
    pdf.cell(50, 8, txt="Correlation vs Portfolio", border=1, align='C')
    pdf.cell(45, 8, txt="1.00", border=1, align='C')  # Portfolio vs itself
    pdf.cell(45, 8, txt=f"{correlation_QQEW:.3f}", border=1, align='C')
    pdf.cell(45, 8, txt=f"{correlation_QQQ:.3f}", border=1, align='C')
    pdf.ln()
    
    # Beta row
    pdf.cell(50, 8, txt="Beta vs Portfolio", border=1, align='C')
    pdf.cell(45, 8, txt="1.00", border=1, align='C')  # Portfolio vs itself
    pdf.cell(45, 8, txt=f"{beta_QQEW:.3f}", border=1, align='C')
    pdf.cell(45, 8, txt=f"{beta_QQQ:.3f}", border=1, align='C')
    pdf.ln(10)
    
    # Add final returns
    final_portfolio = df['Cumulative_yield'].iloc[-1]
    final_QQEW = df['Cumulative_Return_QQEW'].iloc[-1]
    final_QQQ = df['Cumulative_Return_QQQ'].iloc[-1]

    pdf.ln(5)
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(200, 8, txt="Final Cumulative Returns", ln=True, align='L')
    pdf.ln(2)
    
    pdf.set_font("Arial", size=10)
    pdf.cell(50, 6, txt=f"Portfolio: {final_portfolio:.2%}", ln=True)
    pdf.cell(50, 6, txt=f"QQEW: {final_QQEW:.2%}", ln=True)
    pdf.cell(50, 6, txt=f"QQQ: {final_QQQ:.2%}", ln=True)
    
    # Add interpretation notes
    pdf.ln(5)
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(200, 8, txt="Key Insights", ln=True, align='L')
    pdf.ln(2)
    
    pdf.set_font("Arial", size=9)
    
    # Risk comparison
    if std_portfolio > std_QQQ:
        risk_text = f"Portfolio is riskier than QQQ ({std_portfolio:.1%} vs {std_QQQ:.1%} volatility)"
    else:
        risk_text = f"Portfolio is less risky than QQQ ({std_portfolio:.1%} vs {std_QQQ:.1%} volatility)"
    
    pdf.cell(200, 5, txt=f"- {risk_text}", ln=True)
    
    # Beta interpretation
    if beta_QQQ > 1:
        beta_text = f"Portfolio is more volatile than QQQ (Beta: {beta_QQQ:.2f})"
    elif beta_QQQ < 1:
        beta_text = f"Portfolio is less volatile than QQQ (Beta: {beta_QQQ:.2f})"
    else:
        beta_text = f"Portfolio moves similarly to QQQ (Beta: {beta_QQQ:.2f})"
    
    pdf.cell(200, 5, txt=f"- {beta_text}", ln=True)
    
    # Correlation interpretation
    if correlation_QQQ > 0.8:
        corr_text = f"High correlation with QQQ ({correlation_QQQ:.2f}) - similar market exposure"
    elif correlation_QQQ > 0.5:
        corr_text = f"Moderate correlation with QQQ ({correlation_QQQ:.2f})"
    else:
        corr_text = f"Low correlation with QQQ ({correlation_QQQ:.2f}) - potential diversification"
    
    pdf.cell(200, 5, txt=f"- {corr_text}", ln=True)
    
    # Adding the drawdown
    pdf.ln(10)

    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(200, 8, txt="Maximum Drawdown Analysis", ln=True, align='L')
    pdf.ln(2)

    pdf.set_font("Arial", size=10)
    pdf.cell(50, 6, txt=f"Max Drawdown: {max_drawdown:.2%}", ln=True)
    pdf.cell(50, 6, txt=f"Drawdown Date: {max_dd_date}", ln=True)
    pdf.cell(50, 6, txt=f"Peak Value: {running_max.max():.2%}", ln=True)

    return pdf.output("results/portfolio_report.pdf")