import streamlit as st

def render_sidebar():
    st.sidebar.header("⚙️ Ustawienia Spółki")
    
    # Inicjalizacja domyślnych wartości w session_state
    if "exchange" not in st.session_state:
        st.session_state.exchange = "GPW"
    if "ticker" not in st.session_state:
        st.session_state.ticker = "TEXT"
        
    # Pola wyboru
    exchanges = ["GPW", "NASDAQ", "NYSE"]
    exchange = st.sidebar.selectbox(
        "Wybierz giełdę", 
        exchanges, 
        index=exchanges.index(st.session_state.exchange)
    )
    
    ticker = st.sidebar.text_input(
        "Podaj ticker", 
        value=st.session_state.ticker
    ).upper()
    
    # Przycisk zatwierdzający zmiany
    if st.sidebar.button("Zastosuj i pobierz dane"):
        st.session_state.exchange = exchange
        st.session_state.ticker = ticker
        st.rerun() # Odświeża stronę z nowymi danymi
        
    st.sidebar.markdown("---")
    
    # Formatowanie tickera pod Yahoo Finance
    if st.session_state.exchange == "GPW":
        yf_ticker = f"{st.session_state.ticker}.WA"
    else:
        yf_ticker = st.session_state.ticker
        
    return st.session_state.exchange, st.session_state.ticker, yf_ticker