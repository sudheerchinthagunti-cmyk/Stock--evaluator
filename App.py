import streamlit as st
import yfinance as yf
import pandas as pd

# --- Website Configuration ---
st.set_page_config(page_title="Ultimate Stock Evaluator", layout="centered")

st.title("📈 The Ultimate Stock Evaluator")
st.markdown("Enter a stock ticker below. The system will pull live financial data from Yahoo Finance and grade it against the 6-point checklist.")

# --- User Input ---
ticker_symbol = st.text_input("Enter Stock Ticker (e.g., AAPL, MSFT, TSLA):", "AAPL").upper()

if ticker_symbol:
    with st.spinner(f"Fetching live accurate data for {ticker_symbol}..."):
        try:
            # Fetch data using yfinance
            stock = yf.Ticker(ticker_symbol)
            info = stock.info
            
            company_name = info.get('shortName', ticker_symbol)
            st.subheader(f"Live Evaluation: {company_name} ({ticker_symbol})")
            
            score = 0
            results = []

            # --- 1. Valuation (P/E Ratio) ---
            pe_ratio = info.get('trailingPE')
            # Using 25 as a standard market benchmark if industry average isn't available
            if pe_ratio is None:
                results.append(("Valuation (P/E)", "N/A", "N/A", "Data not available."))
            elif pe_ratio < 25: 
                score += 1
                results.append(("Valuation (P/E)", pe_ratio, "Pass", "P/E is under the 25x benchmark, suggesting reasonable valuation."))
            else:
                results.append(("Valuation (P/E)", pe_ratio, "Fail", "Stock is expensive relative to current profits (P/E > 25)."))

            # --- 2. Growth (PEG Ratio) ---
            peg_ratio = info.get('pegRatio')
            if peg_ratio is None:
                results.append(("Growth (PEG)", "N/A", "N/A", "Data not available."))
            elif peg_ratio < 1.0 and peg_ratio > 0:
                score += 1
                results.append(("Growth (PEG)", peg_ratio, "Pass", "Growth justifies the price (PEG < 1.0)."))
            else:
                results.append(("Growth (PEG)", peg_ratio, "Fail", "Overpaying for future growth (PEG > 1.0)."))

            # --- 3. Profit Quality (Operating Cash Flow / Net Profit) ---
            ocf = info.get('operatingCashflow')
            net_profit = info.get('netIncomeToCommon')
            
            if ocf and net_profit and net_profit > 0:
                profit_quality = round(ocf / net_profit, 2)
                if profit_quality >= 1.0:
                    score += 1
                    results.append(("Profit Quality", profit_quality, "Pass", "Paper profits are backed by actual hard cash."))
                else:
                    results.append(("Profit Quality", profit_quality, "Fail", "Profits are not translating fully into cash."))
            else:
                results.append(("Profit Quality", "N/A", "Fail", "Negative net profit or missing cash flow data."))

            # --- 4. Cash Generation (Free Cash Flow) ---
            fcf = info.get('freeCashflow')
            if fcf is None:
                results.append(("Cash Generation", "N/A", "N/A", "Data not available."))
            elif fcf > 0:
                # Basic check for positive FCF
                score += 1
                formatted_fcf = f"${fcf:,.0f}"
                results.append(("Cash Gen (FCF)", formatted_fcf, "Pass", "Company is generating positive free cash flow."))
            else:
                formatted_fcf = f"${fcf:,.0f}" if fcf else "N/A"
                results.append(("Cash Gen (FCF)", formatted_fcf, "Fail", "Negative free cash flow; burning cash."))

            # --- 5. Financial Safety (Debt-to-Equity Ratio) ---
            # Yahoo finance returns D/E as a percentage (e.g., 50 means 0.5)
            debt_equity_raw = info.get('debtToEquity')
            if debt_equity_raw is None:
                results.append(("Financial Safety", "N/A", "N/A", "Data not available."))
            else:
                debt_equity = round(debt_equity_raw / 100, 2)
                if debt_equity < 1.0:
                    score += 1
                    results.append(("Financial Safety (D/E)", debt_equity, "Pass", "Debt-to-Equity is below 1.0. Safe debt levels."))
                else:
                    results.append(("Financial Safety (D/E)", debt_equity, "Fail", "Drowning in debt (D/E > 1.0)."))

            # --- 6. Short-Term Health (Current Ratio) ---
            current_ratio = info.get('currentRatio')
            if current_ratio is None:
                results.append(("Short-Term Health", "N/A", "N/A", "Data not available."))
            elif current_ratio > 1.5:
                score += 1
                results.append(("Short-Term Health", current_ratio, "Pass", "Ample liquid assets to pay short-term bills."))
            else:
                results.append(("Short-Term Health", current_ratio, "Fail", "Current Ratio is 1.5 or lower. Potential liquidity risk."))

            # --- Display Final Score ---
            st.markdown(f"### Final Score: **{score} / 6**")
            st.progress(score / 6)

            # --- Display Results Table ---
            df = pd.DataFrame(results, columns=["Metric", "Live Value", "Status", "Why It Matters"])
            
            # Function to color code Pass/Fail
            def highlight_status(val):
                if val == 'Pass':
                    return 'color: green; font-weight: bold'
                elif val == 'Fail':
                    return 'color: red; font-weight: bold'
                return ''

            st.dataframe(df.style.map(highlight_status, subset=['Status']), use_container_width=True)
            
            st.caption("Note: P/E Ratio is compared against a standard benchmark of 25x. For the most accurate valuation, manually compare this P/E against direct industry competitors.")

        except Exception as e:
            st.error("Could not fetch accurate data for this ticker. Please ensure the symbol is correct and try again.")
          
