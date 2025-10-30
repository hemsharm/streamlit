import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page configuration
st.set_page_config(
    page_title="Stock Information Dashboard",
    page_icon="📈",
    layout="wide"
)

# Title and description
st.title("📊 Stock Information Dashboard")
st.markdown("Enter a stock symbol to get analyst ratings, technical indicators, and interactive charts")

# Input section
col1, col2 = st.columns([3, 1])
with col1:
    stock_symbol = st.text_input("Enter Stock Symbol (e.g., AAPL, MSFT, GOOGL)", value="AAPL")
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    search_button = st.button("Get Stock Data", type="primary")

# Function to calculate moving averages
def calculate_ma(data, period):
    """Calculate Moving Average"""
    return data['Close'].rolling(window=period).mean().iloc[-1]

# Function to calculate moving average series
def calculate_ma_series(data, period):
    """Calculate Moving Average Series"""
    return data['Close'].rolling(window=period).mean()

# Function to get 200-day low
def get_200_day_low(data):
    """Get the lowest price in the last 200 days"""
    return data['Low'].tail(200).min()

# Function to get analyst rating
def get_analyst_rating(ticker):
    """Get analyst recommendations"""
    try:
        recommendations = ticker.recommendations
        if recommendations is not None and not recommendations.empty:
            latest = recommendations.tail(10)
            
            # Count recommendations
            buy_count = latest[latest['To Grade'].str.contains('Buy|Outperform|Overweight', case=False, na=False)].shape[0]
            hold_count = latest[latest['To Grade'].str.contains('Hold|Neutral', case=False, na=False)].shape[0]
            sell_count = latest[latest['To Grade'].str.contains('Sell|Underperform|Underweight', case=False, na=False)].shape[0]
            
            total = buy_count + hold_count + sell_count
            if total > 0:
                buy_pct = (buy_count / total) * 100
                hold_pct = (hold_count / total) * 100
                sell_pct = (sell_count / total) * 100
                
                # Determine overall rating
                if buy_pct >= 60:
                    overall = "Strong Buy"
                elif buy_pct >= 40:
                    overall = "Buy"
                elif hold_pct >= 50:
                    overall = "Hold"
                elif sell_pct >= 40:
                    overall = "Sell"
                else:
                    overall = "Hold"
                
                return {
                    'overall': overall,
                    'buy': buy_count,
                    'hold': hold_count,
                    'sell': sell_count,
                    'buy_pct': buy_pct,
                    'hold_pct': hold_pct,
                    'sell_pct': sell_pct
                }
        return None
    except:
        return None

# Function to create price chart with moving averages
def create_price_chart(hist_data, stock_symbol, ma_20, ma_50, low_200):
    """Create interactive price chart with moving averages"""
    
    # Calculate MA series
    hist_data['MA20'] = calculate_ma_series(hist_data, 20)
    hist_data['MA50'] = calculate_ma_series(hist_data, 50)
    
    fig = go.Figure()
    
    # Add candlestick chart
    fig.add_trace(go.Candlestick(
        x=hist_data.index,
        open=hist_data['Open'],
        high=hist_data['High'],
        low=hist_data['Low'],
        close=hist_data['Close'],
        name='Price',
        increasing_line_color='#26a69a',
        decreasing_line_color='#ef5350'
    ))
    
    # Add 20-day MA
    fig.add_trace(go.Scatter(
        x=hist_data.index,
        y=hist_data['MA20'],
        name='20-Day MA',
        line=dict(color='#ff9800', width=2)
    ))
    
    # Add 50-day MA
    fig.add_trace(go.Scatter(
        x=hist_data.index,
        y=hist_data['MA50'],
        name='50-Day MA',
        line=dict(color='#2196f3', width=2)
    ))
    
    # Add 200-day low line
    fig.add_hline(
        y=low_200,
        line_dash="dash",
        line_color="red",
        annotation_text=f"200-Day Low: ${low_200:.2f}",
        annotation_position="right"
    )
    
    fig.update_layout(
        title=f'{stock_symbol.upper()} Stock Price with Moving Averages',
        yaxis_title='Price ($)',
        xaxis_title='Date',
        template='plotly_white',
        height=600,
        hovermode='x unified',
        xaxis_rangeslider_visible=False
    )
    
    return fig

# Function to create volume chart
def create_volume_chart(hist_data, stock_symbol):
    """Create volume chart"""
    
    colors = ['red' if close < open else 'green' 
              for close, open in zip(hist_data['Close'], hist_data['Open'])]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=hist_data.index,
        y=hist_data['Volume'],
        name='Volume',
        marker_color=colors,
        opacity=0.7
    ))
    
    fig.update_layout(
        title=f'{stock_symbol.upper()} Trading Volume',
        yaxis_title='Volume',
        xaxis_title='Date',
        template='plotly_white',
        height=300,
        showlegend=False
    )
    
    return fig

# Function to create analyst rating pie chart
def create_analyst_chart(analyst_data):
    """Create analyst rating distribution chart"""
    
    fig = go.Figure(data=[go.Pie(
        labels=['Buy', 'Hold', 'Sell'],
        values=[analyst_data['buy'], analyst_data['hold'], analyst_data['sell']],
        hole=.4,
        marker=dict(colors=['#26a69a', '#ffa726', '#ef5350']),
        textinfo='label+percent',
        textfont_size=14
    )])
    
    fig.update_layout(
        title='Analyst Recommendations Distribution',
        height=400,
        showlegend=True,
        template='plotly_white'
    )
    
    return fig

# Function to create price comparison chart
def create_comparison_chart(hist_data, stock_symbol, current_price, ma_20, ma_50, low_200):
    """Create bar chart comparing current price with indicators"""
    
    fig = go.Figure()
    
    categories = ['Current Price', '20-Day MA', '50-Day MA', '200-Day Low']
    values = [current_price, ma_20, ma_50, low_200]
    colors = ['#2196f3', '#ff9800', '#9c27b0', '#f44336']
    
    fig.add_trace(go.Bar(
        x=categories,
        y=values,
        marker_color=colors,
        text=[f'${v:.2f}' for v in values],
        textposition='outside'
    ))
    
    fig.update_layout(
        title=f'{stock_symbol.upper()} - Price vs Technical Indicators',
        yaxis_title='Price ($)',
        template='plotly_white',
        height=400,
        showlegend=False
    )
    
    return fig

# Main logic
if search_button or stock_symbol:
    try:
        with st.spinner(f'Fetching data for {stock_symbol.upper()}...'):
            # Create ticker object
            ticker = yf.Ticker(stock_symbol.upper())
            
            # Get historical data (1 year for 200-day calculations)
            hist_data = ticker.history(period="1y")
            
            if hist_data.empty:
                st.error("❌ Invalid stock symbol or no data available. Please try again.")
            else:
                # Get stock info
                info = ticker.info
                company_name = info.get('longName', stock_symbol.upper())
                current_price = info.get('currentPrice', hist_data['Close'].iloc[-1])
                
                # Display company header
                st.markdown(f"## {company_name} ({stock_symbol.upper()})")
                st.markdown(f"### Current Price: ${current_price:.2f}")
                st.markdown("---")
                
                # Calculate metrics
                ma_50 = calculate_ma(hist_data, 50)
                ma_20 = calculate_ma(hist_data, 20)
                low_200 = get_200_day_low(hist_data)
                analyst_data = get_analyst_rating(ticker)
                
                # Display metrics in columns
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        label="📊 200-Day Low Price",
                        value=f"${low_200:.2f}",
                        delta=f"{((current_price - low_200) / low_200 * 100):.2f}% from low"
                    )
                
                with col2:
                    st.metric(
                        label="📈 50-Day Moving Average",
                        value=f"${ma_50:.2f}",
                        delta=f"{((current_price - ma_50) / ma_50 * 100):.2f}%"
                    )
                
                with col3:
                    st.metric(
                        label="📉 20-Day Moving Average",
                        value=f"${ma_20:.2f}",
                        delta=f"{((current_price - ma_20) / ma_20 * 100):.2f}%"
                    )
                
                with col4:
                    if analyst_data:
                        rating_colors = {
                            "Strong Buy": "🟢",
                            "Buy": "🟢",
                            "Hold": "🟡",
                            "Sell": "🔴"
                        }
                        color = rating_colors.get(analyst_data['overall'], "⚪")
                        
                        st.metric(
                            label="⭐ Analyst Rating",
                            value=f"{color} {analyst_data['overall']}"
                        )
                    else:
                        st.metric(
                            label="⭐ Analyst Rating",
                            value="N/A"
                        )
                
                st.markdown("---")
                
                # CHARTS SECTION
                st.header("📈 Interactive Charts")
                
                # Price chart with moving averages
                st.subheader("Price Chart with Moving Averages")
                price_chart = create_price_chart(hist_data.copy(), stock_symbol, ma_20, ma_50, low_200)
                st.plotly_chart(price_chart, use_container_width=True)
                
                # Volume chart
                st.subheader("Trading Volume")
                volume_chart = create_volume_chart(hist_data.copy(), stock_symbol)
                st.plotly_chart(volume_chart, use_container_width=True)
                
                # Two column layout for additional charts
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Price Comparison")
                    comparison_chart = create_comparison_chart(hist_data, stock_symbol, current_price, ma_20, ma_50, low_200)
                    st.plotly_chart(comparison_chart, use_container_width=True)
                
                with col2:
                    if analyst_data:
                        st.subheader("Analyst Ratings")
                        analyst_chart = create_analyst_chart(analyst_data)
                        st.plotly_chart(analyst_chart, use_container_width=True)
                    else:
                        st.info("Analyst rating data not available for this stock")
                
                st.markdown("---")
                
                # Detailed Analyst Information
                if analyst_data:
                    st.subheader("📋 Detailed Analyst Recommendations (Last 10)")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"""
                        <div style='background-color: #d4edda; padding: 20px; border-radius: 10px; text-align: center;'>
                            <h3 style='color: #155724;'>🟢 Buy</h3>
                            <h2 style='color: #155724;'>{analyst_data['buy']}</h2>
                            <p style='color: #155724;'>{analyst_data['buy_pct']:.1f}%</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div style='background-color: #fff3cd; padding: 20px; border-radius: 10px; text-align: center;'>
                            <h3 style='color: #856404;'>🟡 Hold</h3>
                            <h2 style='color: #856404;'>{analyst_data['hold']}</h2>
                            <p style='color: #856404;'>{analyst_data['hold_pct']:.1f}%</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <div style='background-color: #f8d7da; padding: 20px; border-radius: 10px; text-align: center;'>
                            <h3 style='color: #721c24;'>🔴 Sell</h3>
                            <h2 style='color: #721c24;'>{analyst_data['sell']}</h2>
                            <p style='color: #721c24;'>{analyst_data['sell_pct']:.1f}%</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Technical Analysis Summary
                st.markdown("---")
                st.subheader("📊 Technical Analysis Summary")
                
                signals = []
                if current_price > ma_50:
                    signals.append("✅ Price is above 50-day MA (Bullish)")
                else:
                    signals.append("❌ Price is below 50-day MA (Bearish)")
                
                if current_price > ma_20:
                    signals.append("✅ Price is above 20-day MA (Short-term Bullish)")
                else:
                    signals.append("❌ Price is below 20-day MA (Short-term Bearish)")
                
                if ma_20 > ma_50:
                    signals.append("✅ 20-day MA is above 50-day MA (Uptrend)")
                else:
                    signals.append("❌ 20-day MA is below 50-day MA (Downtrend)")
                
                gain_from_low = ((current_price - low_200) / low_200 * 100)
                if gain_from_low > 50:
                    signals.append(f"✅ Price is {gain_from_low:.1f}% above 200-day low (Strong Recovery)")
                elif gain_from_low > 20:
                    signals.append(f"✅ Price is {gain_from_low:.1f}% above 200-day low (Recovering)")
                else:
                    signals.append(f"⚠️ Price is only {gain_from_low:.1f}% above 200-day low (Near Support)")
                
                for signal in signals:
                    st.markdown(f"- {signal}")
                
                # Additional Information
                st.markdown("---")
                st.subheader("ℹ️ Additional Information")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Market Cap:** {info.get('marketCap', 'N/A'):,}" if isinstance(info.get('marketCap'), (int, float)) else "**Market Cap:** N/A")
                with col2:
                    st.write(f"**Volume:** {info.get('volume', 'N/A'):,}" if isinstance(info.get('volume'), (int, float)) else "**Volume:** N/A")
                with col3:
                    st.write(f"**PE Ratio:** {info.get('trailingPE', 'N/A'):.2f}" if isinstance(info.get('trailingPE'), (int, float)) else "**PE Ratio:** N/A")
                
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        st.info("Please make sure you've entered a valid stock symbol (e.g., AAPL, MSFT, GOOGL)")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Data provided by Yahoo Finance | For informational purposes only</p>
    <p><strong>Disclaimer:</strong> This is not financial advice. Always consult with a qualified financial advisor before making investment decisions.</p>
</div>
""", unsafe_allow_html=True)