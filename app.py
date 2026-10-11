import streamlit as st
from utils.sidebar import render_sidebar

st.set_page_config(page_title="Dashboard Giełdowy", layout="wide")

# Wywołanie paska bocznego
exchange, base_ticker, yf_ticker = render_sidebar()

st.title(f"📊 Command Center: {base_ticker} ({exchange})")
st.markdown(f"""
Witaj w analitycznym dashboardzie giełdowym. 
Aktualnie analizujesz spółkę **{base_ticker}** notowaną na **{exchange}**.

Użyj menu po lewej stronie, aby przełączać się między:
* **Metrics:** Analiza fundamentalna (Wskaźniki C/Z, ROE itp.)
* **Price Chart:** Zaawansowany wykres świecowy z wolumenem
* **Predictions:** Przyszłe prognozy ML
""")