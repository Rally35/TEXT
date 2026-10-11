import streamlit as st
import pandas as pd
from utils.data import get_quarterly_metrics
from utils.scraper import fetch_biznesradar_metrics
from utils.sidebar import render_sidebar

st.set_page_config(page_title="Metrics", layout="wide")

exchange, base_ticker, yf_ticker = render_sidebar()

st.header(f"Fundamental Metrics: {base_ticker}")

# Logika wyboru źródła
if exchange == "GPW":
    source = st.radio(
        "Wybierz źródło danych:",
        ["BiznesRadar (Zalecane dla GPW)", "Yahoo Finance (Wersja uproszczona)"],
        horizontal=True
    )
else:
    # Ukryj BiznesRadar dla giełd zagranicznych
    st.info("Dane z BiznesRadar są dostępne tylko dla GPW. Używam Yahoo Finance.")
    source = "Yahoo Finance"

st.markdown("---")

if "BiznesRadar" in source:
    st.subheader(f"Dane z BiznesRadar dla {base_ticker}")
    with st.spinner("Pobieranie..."):
        # Scraper używa podstawowego tickera (np. TEXT)
        df = fetch_biznesradar_metrics(base_ticker)
        
    if df.empty:
        st.error("Brak danych na BiznesRadar. Sprawdź poprawność tickera.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

else:
    st.subheader(f"Dane z Yahoo Finance dla {yf_ticker}")
    with st.spinner("Pobieranie..."):
        # YF używa tickera z sufiksem (np. TXT.WA)
        df_yf = get_quarterly_metrics(yf_ticker)
    
    if df_yf.empty:
        st.error("Brak danych sprawozdawczych w Yahoo Finance dla tej spółki.")
    else:
        def format_metric(row):
            formatted_row = []
            indicator = row['Wskaźnik']
            for val in row.drop('Wskaźnik'):
                if pd.isna(val):
                    formatted_row.append("-")
                elif indicator in ["ROA", "ROE"]:
                    formatted_row.append(f"{val * 100:.2f}%")
                else:
                    formatted_row.append(f"{val:.2f}")
            return [indicator] + formatted_row

        formatted_df = df_yf.apply(format_metric, axis=1, result_type='expand')
        formatted_df.columns = df_yf.columns
        st.dataframe(formatted_df, use_container_width=True, hide_index=True)