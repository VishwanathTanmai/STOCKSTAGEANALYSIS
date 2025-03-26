import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import modules.data_fetcher as data_fetcher
import modules.visualizations as visualizations
import modules.predictions as predictions

# Set page configuration
st.set_page_config(
    page_title="Stock Analysis Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# App title and description
st.title("📈 Stock Analysis")
st.markdown("Analyze real-time stock data with interactive charts and predictive capabilities by Vishwanath tanmai")

# Sidebar for stock selection and timeframe
with st.sidebar:
    st.header("Settings")
    
    # Stock search box
    stock_symbol = st.text_input("Enter Stock Symbol (e.g., AAPL, MSFT, GOOGL)", value="AAPL").upper()
    
    # Timeframe selection
    timeframe_options = {
        "1 Day": "1d",
        "5 Days": "5d",
        "1 Month": "1mo",
        "3 Months": "3mo", 
        "6 Months": "6mo",
        "1 Year": "1y",
        "2 Years": "2y",
        "5 Years": "5y",
        "10 Years": "10y",
        "Year to Date": "ytd",
        "Max": "max"
    }
    
    selected_timeframe = st.selectbox(
        "Select Timeframe",
        list(timeframe_options.keys()),
        index=4
    )
    
    timeframe = timeframe_options[selected_timeframe]
    
    # Interval selection based on timeframe
    interval_options = {
        "1 Day": "5m",
        "5 Days": "15m",
        "1 Month": "1h",
        "3 Months": "1d",
        "6 Months": "1d",
        "1 Year": "1d",
        "2 Years": "1d",
        "5 Years": "1wk",
        "10 Years": "1mo",
        "Year to Date": "1d",
        "Max": "1mo"
    }
    
    interval = interval_options[selected_timeframe]
    
    st.caption("Data provided by Yahoo Finance")

# Main content
try:
    # Loading spinner while fetching data
    with st.spinner(f"Fetching data for {stock_symbol}..."):
        # Fetch historical data
        hist_data = data_fetcher.get_historical_data(stock_symbol, timeframe, interval)
        
        # Fetch company info - with fallback for invalid symbols
        if hist_data is None or hist_data.empty:
            st.error(f"No data available for {stock_symbol}. Please check the symbol and try again.")
            st.info("Please try a different stock symbol or timeframe.")
            st.stop()  # Stop execution if no data
            
        company_info = data_fetcher.get_company_info(stock_symbol)
        
        # If we have data, display it
        if hist_data is not None and not hist_data.empty:
            # Display company name and basic info
            st.header(f"{company_info.get('shortName', stock_symbol)}")
            st.subheader(f"{company_info.get('exchange', '')} : {stock_symbol}")
            
            # Create tabs for different sections
            tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Financial Data", "Prediction", "About"])
            
            with tab1:
                # Top metrics row
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    current_price = data_fetcher.get_current_price(stock_symbol)
                    st.metric(
                        "Current Price", 
                        f"${current_price:.2f}", 
                        f"{company_info.get('regularMarketChangePercent', 0):.2f}%"
                    )
                
                with col2:
                    st.metric(
                        "Previous Close", 
                        f"${company_info.get('regularMarketPreviousClose', 0):.2f}"
                    )
                
                with col3:
                    st.metric(
                        "Day Range", 
                        f"${company_info.get('regularMarketDayLow', 0):.2f} - ${company_info.get('regularMarketDayHigh', 0):.2f}"
                    )
                
                with col4:
                    st.metric(
                        "52 Week Range", 
                        f"${company_info.get('fiftyTwoWeekLow', 0):.2f} - ${company_info.get('fiftyTwoWeekHigh', 0):.2f}"
                    )
                
                # Stock price chart
                st.subheader(f"{stock_symbol} Stock Price Chart")
                price_chart = visualizations.create_price_chart(hist_data, stock_symbol, timeframe)
                st.plotly_chart(price_chart, use_container_width=True)
                
                # Volume Chart
                st.subheader("Trading Volume")
                volume_chart = visualizations.create_volume_chart(hist_data, stock_symbol)
                st.plotly_chart(volume_chart, use_container_width=True)
                
                # Download data button
                csv = hist_data.to_csv(index=True)
                st.download_button(
                    label="Download Data as CSV",
                    data=csv,
                    file_name=f"{stock_symbol}_{timeframe}_data.csv",
                    mime="text/csv",
                )
            
            with tab2:
                # Financial Data Section
                st.header("Key Financial Metrics")
                
                # Key Metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Market Cap", f"${company_info.get('marketCap', 0) / 1_000_000_000:.2f}B")
                    st.metric("P/E Ratio", f"{company_info.get('trailingPE', 0):.2f}")
                    st.metric("EPS (TTM)", f"${company_info.get('trailingEps', 0):.2f}")
                
                with col2:
                    st.metric("Forward P/E", f"{company_info.get('forwardPE', 0):.2f}")
                    st.metric("Dividend Yield", f"{company_info.get('dividendYield', 0) * 100:.2f}%")
                    st.metric("Beta", f"{company_info.get('beta', 0):.2f}")
                
                with col3:
                    st.metric("52W High", f"${company_info.get('fiftyTwoWeekHigh', 0):.2f}")
                    st.metric("52W Low", f"${company_info.get('fiftyTwoWeekLow', 0):.2f}")
                    st.metric("Avg Volume", f"{company_info.get('averageVolume', 0) / 1_000_000:.2f}M")
                
                # Financial ratios
                st.subheader("Financial Ratios")
                
                try:
                    # Get financial data
                    financial_data = data_fetcher.get_financial_data(stock_symbol)
                    
                    if financial_data is not None and not financial_data.empty:
                        st.dataframe(financial_data, use_container_width=True)
                    else:
                        st.warning("Financial data not available for this stock")
                except Exception as e:
                    st.error(f"Error retrieving financial data: {e}")
                
                # Technical Indicators
                st.subheader("Technical Indicators")
                
                indicators_chart = visualizations.create_technical_indicators(hist_data, stock_symbol)
                st.plotly_chart(indicators_chart, use_container_width=True)
            
            with tab3:
                st.header("Stock Price Prediction")
                st.info("This prediction model uses historical stock data to forecast potential future price movements. Please note that these predictions are for educational purposes only and should not be used as financial advice.")
                
                # Training the prediction model
                with st.spinner("Training prediction model..."):
                    prediction_data = predictions.predict_next_day(hist_data, stock_symbol)
                
                if prediction_data is not None:
                    # Display predictions
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Predicted price for next day
                        predicted_price = prediction_data['predicted_price']
                        current_price = hist_data['Close'].iloc[-1]
                        price_diff = predicted_price - current_price
                        price_change_pct = (price_diff / current_price) * 100
                        
                        # Color coding based on prediction direction
                        if predicted_price > current_price:
                            st.markdown(f"<h3 style='color: #2E7D32'>Predicted Next Day Price: ${predicted_price:.2f}</h3>", unsafe_allow_html=True)
                            st.markdown(f"<h4 style='color: #2E7D32'>Change: +${price_diff:.2f} (+{price_change_pct:.2f}%)</h4>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<h3 style='color: #C62828'>Predicted Next Day Price: ${predicted_price:.2f}</h3>", unsafe_allow_html=True)
                            st.markdown(f"<h4 style='color: #C62828'>Change: ${price_diff:.2f} ({price_change_pct:.2f}%)</h4>", unsafe_allow_html=True)
                        
                        # Model metrics
                        st.subheader("Model Performance Metrics")
                        st.metric("Mean Absolute Error", f"${prediction_data['mae']:.4f}")
                        st.metric("Root Mean Squared Error", f"${prediction_data['rmse']:.4f}")
                        st.metric("R-squared", f"{prediction_data['r2']:.4f}")
                    
                    with col2:
                        # Show prediction chart
                        prediction_chart = visualizations.create_prediction_chart(
                            hist_data, prediction_data, stock_symbol
                        )
                        st.plotly_chart(prediction_chart, use_container_width=True)
                    
                    st.caption("⚠️ Disclaimer: This is a simplified prediction model for educational purposes. Stock market predictions are inherently uncertain.")
                else:
                    st.error("Unable to generate predictions. Insufficient data or error in the prediction model.")
            
            with tab4:
                # About the company section
                st.header("About the Company")
                
                # Company profile
                if 'longBusinessSummary' in company_info:
                    st.markdown(company_info['longBusinessSummary'])
                else:
                    st.warning("No company description available")
                
                # Key company data
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Company Information")
                    company_data = {
                        "Sector": company_info.get('sector', 'N/A'),
                        "Industry": company_info.get('industry', 'N/A'),
                        "Full Time Employees": company_info.get('fullTimeEmployees', 'N/A'),
                        "Country": company_info.get('country', 'N/A'),
                        "Website": company_info.get('website', 'N/A'),
                    }
                    
                    for key, value in company_data.items():
                        st.markdown(f"**{key}:** {value}")
                
                with col2:
                    st.subheader("Key Executives")
                    try:
                        if 'companyOfficers' in company_info and company_info['companyOfficers']:
                            executives_data = []
                            for officer in company_info['companyOfficers'][:5]:  # Limit to top 5
                                executive = {
                                    "Name": officer.get('name', 'N/A'),
                                    "Title": officer.get('title', 'N/A'),
                                    "Pay": f"${officer.get('totalPay', 0)/1000000:.2f}M" if 'totalPay' in officer else 'N/A'
                                }
                                executives_data.append(executive)
                            
                            df_executives = pd.DataFrame(executives_data)
                            st.dataframe(df_executives, use_container_width=True)
                        else:
                            st.info("No executive data available")
                    except Exception as e:
                        st.error(f"Error displaying executive data: {str(e)}")
        else:
            st.error(f"No data available for {stock_symbol}. Please check the symbol and try again.")

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.info("Please try a different stock symbol or timeframe.")
