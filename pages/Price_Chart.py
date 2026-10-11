import streamlit as st
from utils.data import get_historical_data
from utils.charts import create_candlestick_chart
from utils.sidebar import render_sidebar

st.set_page_config(page_title="Price Chart", layout="wide")

exchange, base_ticker, yf_ticker = render_sidebar()

st.header(f"Interaktywny Wykres: {base_ticker} ({exchange})")

period = st.selectbox("Zakres czasu", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "10y"], index=3)
df = get_historical_data(yf_ticker, period)

if not df.empty:
    fig = create_candlestick_chart(df)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Brak danych cenowych do wyświetlenia. Sprawdź ticker.")