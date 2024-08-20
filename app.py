import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import capm_functions

# Streamlit app configuration
st.set_page_config(page_title="CAPM Analysis", page_icon="📈", layout='wide')

# Custom CSS for styling
st.markdown(
    """
    <style>
    .main-header {
        font-size: 32px;
        font-weight: bold;
        color: #4B6CB7;
        text-align: center;
        margin-bottom: 30px;
    }
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
    }
    .metric-header {
        font-size: 20px;
        font-weight: bold;
        color: #4B6CB7;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Main Header
st.markdown('<h1 class="main-header">Capital Asset Pricing Model (CAPM)</h1>', unsafe_allow_html=True)

# Benchmarks and stock lists
benchmarks = {
    'Nifty 50': '^NSEI',
    'NASDAQ 100': '^NDX'
}

nifty50_stocks = [
     'ADANIPORTS.NS', 'ASIANPAINT.NS', 'AXISBANK.NS', 'BAJAJ-AUTO.NS', 'BAJAJFINSV.NS',
    'BAJFINANCE.NS', 'BHARTIARTL.NS', 'BPCL.NS', 'BRITANNIA.NS', 'CIPLA.NS',
    'COALINDIA.NS', 'DIVISLAB.NS', 'DRREDDY.NS', 'EICHERMOT.NS', 'GRASIM.NS',
    'HCLTECH.NS', 'HDFC.NS', 'HDFC.NS', 'HDFCBANK.NS', 'HDFCLIFE.NS', 'HEROMOTOCO.NS',
    'HINDALCO.NS', 'HINDUNILVR.NS', 'ICICIBANK.NS', 'INDUSINDBK.NS', 'INFY.NS',
    'ITC.NS', 'JSWSTEEL.NS', 'KOTAKBANK.NS', 'LT.NS', 'M&M.NS',
    'MARUTI.NS', 'NESTLEIND.NS', 'NTPC.NS', 'ONGC.NS', 'POWERGRID.NS',
    'RELIANCE.NS', 'SBILIFE.NS', 'SBIN.NS', 'SUNPHARMA.NS', 'TATAMOTORS.NS',
    'TATASTEEL.NS', 'TCS.NS', 'TECHM.NS', 'TITAN.NS', 'ULTRACEMCO.NS',
    'UPL.NS', 'WIPRO.NS'
]

nasdaq100_stocks = [
      'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B', 'UNH', 'V',
    'MA', 'HD', 'DIS', 'ADBE', 'CMCSA', 'NFLX', 'INTC', 'CSCO', 'PFE', 'MRK',
    'PEP', 'AVGO', 'TXN', 'QCOM', 'ABT', 'TMO', 'CRM', 'ORCL', 'COST', 'NKE',
    'MCD', 'AMGN', 'MDT', 'HON', 'BMY', 'C', 'BAX', 'BA', 'GILD', 'MS',
    'CVX', 'WMT', 'WBA', 'MCO', 'CAT', 'DHR', 'LMT', 'IBM', 'UPS', 'COP',
    'AMT', 'LRCX', 'LLY', 'CL', 'SBUX', 'T', 'MDLZ', 'EOG', 'MCK', 'SNY',
    'WFC', 'FIS', 'MO', 'CME', 'GS', 'ADP', 'IACI', 'BMY', 'AON', 'KMB',
    'PSA', 'ISRG', 'MCHP', 'HPE', 'MU', 'LUV', 'MSCI', 'CSX', 'XOM', 'TRV'
]

# Sidebar for page navigation
page = st.sidebar.selectbox("Select Page", ["CAPM Analysis", "Stock Comparison"])

if page == "CAPM Analysis":
    col1, col2 = st.columns([1, 1])
    with col1:
        benchmark = st.selectbox("Select Benchmark", options=list(benchmarks.keys()))
    with col2:
        stocks_list = st.multiselect("Choose stocks", nifty50_stocks if benchmark == 'Nifty 50' else nasdaq100_stocks)

    year = st.slider("Number of Years", 1, 15, 5)

    if not stocks_list or year == 0:
        st.warning("Please select at least one stock and a valid number of years.")
    else:
        try:
            end = datetime.date.today()
            start = datetime.date(end.year - year, end.month, end.day)

            with st.spinner("Fetching data..."):
                benchmark_symbol = benchmarks[benchmark]
                benchmark_data = yf.download(benchmark_symbol, start=start, end=end)
                benchmark_data = benchmark_data[['Close']].rename(columns={'Close': benchmark})

                stocks_df = pd.DataFrame()
                for stock in stocks_list:
                    data = yf.download(stock, start=start, end=end)
                    stocks_df[stock] = data['Close']

            stocks_df.reset_index(inplace=True)
            benchmark_data.reset_index(inplace=True)
            stocks_df = pd.merge(stocks_df, benchmark_data[['Date', benchmark]], on='Date', how='inner')

            st.markdown("### Stock Prices Overview")
            col1, col2 = st.columns([1, 1])
            with col1:
                st.dataframe(stocks_df.head(), use_container_width=True)
            with col2:
                st.dataframe(stocks_df.tail(), use_container_width=True)

            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown("### Stock Price Movements")
                st.plotly_chart(capm_functions.interactive_plot(stocks_df), use_container_width=True)
            with col2:
                normalized_df = capm_functions.normalize(stocks_df)
                st.markdown("### Normalized Stock Prices")
                st.plotly_chart(capm_functions.interactive_plot(normalized_df), use_container_width=True)

            # CAPM Calculations
            stock_daily_return = capm_functions.daily_returns(stocks_df)
            beta = {}
            alpha = {}

            for stock in stocks_list:
                b, a = capm_functions.calc(stock_daily_return, stock, benchmark)
                beta[stock] = b
                alpha[stock] = a

            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown("### Beta Values")
                beta_df = pd.DataFrame({'Stock': beta.keys(), 'Beta Value': [round(b, 2) for b in beta.values()]})
                st.dataframe(beta_df, use_container_width=True)

            with col2:
                st.markdown("### Expected Return using CAPM")
                rf = 0  # Risk-free rate
                rm = stock_daily_return[benchmark].mean() * 252  # Market return

                return_values = [round(rf + beta[stock] * (rm - rf), 2) for stock in stocks_list]
                return_df = pd.DataFrame({'Stock': stocks_list, 'Expected Return (CAPM)': return_values})
                st.dataframe(return_df, use_container_width=True)

        except Exception as e:
            st.error(f"An error occurred: {e}")

elif page == "Stock Comparison":
    col1, col2 = st.columns([1, 1])
    with col1:
        stock1 = st.selectbox("Select First Stock", options=nifty50_stocks + nasdaq100_stocks)
    with col2:
        stock2 = st.selectbox("Select Second Stock", options=nifty50_stocks + nasdaq100_stocks)

    year = st.slider("Number of Years for Comparison", 1, 15, 5)

    if stock1 and stock2 and year > 0:
        try:
            end = datetime.date.today()
            start = datetime.date(end.year - year, end.month, end.day)

            with st.spinner("Fetching stock data..."):
                data1 = yf.download(stock1, start=start, end=end)
                data2 = yf.download(stock2, start=start, end=end)

            df1 = data1[['Close']].rename(columns={'Close': stock1})
            df2 = data2[['Close']].rename(columns={'Close': stock2})

            df1.reset_index(inplace=True)
            df2.reset_index(inplace=True)

            comparison_df = pd.merge(df1, df2, on='Date', how='inner')

            comparison_df[f'{stock1} Return (%)'] = (comparison_df[stock1] / comparison_df[stock1].iloc[0] - 1) * 100
            comparison_df[f'{stock2} Return (%)'] = (comparison_df[stock2] / comparison_df[stock2].iloc[0] - 1) * 100

            st.markdown("### Cumulative Return Comparison (%)")
            st.line_chart(comparison_df[['Date', f'{stock1} Return (%)', f'{stock2} Return (%)']].set_index('Date'))

            final_returns = comparison_df[['Date', f'{stock1} Return (%)', f'{stock2} Return (%)']].iloc[-1]
            st.markdown(f"### Final Cumulative Returns Over {year} Years")
            st.write(f"{stock1} Return: {final_returns[f'{stock1} Return (%)']:.2f}%")
            st.write(f"{stock2} Return: {final_returns[f'{stock2} Return (%)']:.2f}%")

        except Exception as e:
            st.error(f"An error occurred: {e}")
