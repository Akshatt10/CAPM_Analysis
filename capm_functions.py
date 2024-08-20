import plotly.express as px
import numpy as np
import pandas as pd

def interactive_plot(df):
    fig = px.line()
    for i in df.columns[1:]:  # Exclude 'Date' column
        fig.add_scatter(x=df['Date'], y=df[i], name=i)
    fig.update_layout(
        width=450,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    return fig

def normalize(df_2):
    df = df_2.copy()
    for i in df.columns[1:]:  # Exclude 'Date' column
        df[i] = df[i] / df[i].iloc[0]  # Normalize prices to the first value
    return df

def daily_returns(df):
    df_daily_returns = df.copy()
    for i in df.columns[1:]:  # Exclude 'Date' column
        df_daily_returns[i] = df[i].pct_change() * 100  # Calculate daily returns as percentage
        df_daily_returns[i].fillna(0, inplace=True)  # Set NaN values to 0
    return df_daily_returns

def calc(stocks_daily_return, stock, benchmark):
    # Use the selected benchmark instead of 'Nifty 50'
    rm = stocks_daily_return[benchmark].mean() * 252  # Annualized market return
    
    # Perform linear regression to calculate beta (slope) and alpha (intercept)
    b, a = np.polyfit(stocks_daily_return[benchmark], stocks_daily_return[stock], 1)
    
    return b, a
