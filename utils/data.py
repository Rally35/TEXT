import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

@st.cache_data(ttl=3600)
def get_company_info(yf_ticker: str) -> dict:
    """
    Pobiera podstawowe informacje o spółce z zabezpieczeniem 
    przed błędami parsowania i blokadami Yahoo Finance.
    """
    try:
        ticker = yf.Ticker(yf_ticker)
        info = ticker.info
        if not info or len(info) <= 1:
            return {}
        return info
    except Exception:
        return {}


@st.cache_data(ttl=3600)
def get_historical_data(yf_ticker: str, period: str = "1y") -> pd.DataFrame:
    """
    Pobiera dane historyczne (OHLCV) dla wybranego okresu.
    """
    try:
        ticker = yf.Ticker(yf_ticker)
        df = ticker.history(period=period)
        return df if not df.empty else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def get_quarterly_metrics(yf_ticker: str) -> pd.DataFrame:
    """
    Pobiera kwartalne sprawozdania finansowe (rachunek zysków i strat,
    bilans oraz przepływy pieniężne) i wylicza podstawowe wskaźniki giełdowe.
    """
    try:
        ticker = yf.Ticker(yf_ticker)
        q_fin = ticker.quarterly_financials
        q_bs = ticker.quarterly_balance_sheet
        q_cf = ticker.quarterly_cashflow
        info = ticker.info

        # Sprawdzenie obecności kluczowych danych
        shares = info.get("sharesOutstanding") if info else None
        if not shares or q_fin is None or q_fin.empty or q_bs is None or q_bs.empty:
            return pd.DataFrame()

        # Pobieramy historię cen do wyznaczenia kapitalizacji na koniec kwartałów
        hist_prices = ticker.history(period="2y")
        if hist_prices.empty or "Close" not in hist_prices.columns:
            return pd.DataFrame()

        hist_close = hist_prices["Close"]

        # Ujednolicenie strefy czasowej w indeksie cen
        if hist_close.index.tz is not None:
            prices_index = hist_close.index.tz_localize(None)
        else:
            prices_index = hist_close.index

        # Ograniczamy analizę do maksymalnie 4 ostatnich zaraportowanych kwartałów
        dates = q_fin.columns[:4]
        results = {}

        for date in dates:
            date_clean = pd.to_datetime(date).tz_localize(None) if pd.to_datetime(date).tzinfo is not None else pd.to_datetime(date)
            date_str = date_clean.strftime("%Y-%m-%d")

            # Znajdź najbliższą historyczną cenę zamknięcia z/przed dniem bilansowym
            valid_dates = prices_index[prices_index <= date_clean]
            if valid_dates.empty:
                continue

            closest_date = valid_dates.max()
            price_loc = prices_index.get_loc(closest_date)
            price = hist_close.iloc[price_loc] if isinstance(price_loc, int) else hist_close.iloc[price_loc.tolist()[0]]

            # Pomocnicza funkcja bezpiecznego wyciągania pozycji ze sprawozdania
            def get_val(report_df, row_name):
                if report_df is not None and not report_df.empty and row_name in report_df.index and date in report_df.columns:
                    val = report_df.loc[row_name, date]
                    return val if pd.notna(val) else np.nan
                return np.nan

            # Pozycje z rachunku zysków i strat
            net_income = get_val(q_fin, "Net Income")
            revenue = get_val(q_fin, "Total Revenue")
            ebit = get_val(q_fin, "EBIT")
            ebitda = get_val(q_fin, "EBITDA")
            op_income = get_val(q_fin, "Operating Income")

            # Pozycje z bilansu
            total_assets = get_val(q_bs, "Total Assets")
            total_equity = get_val(q_bs, "Stockholders Equity")
            total_debt = get_val(q_bs, "Total Debt")
            cash = get_val(q_bs, "Cash And Cash Equivalents")

            # Przepływy pieniężne
            operating_cf = get_val(q_cf, "Operating Cash Flow")

            # Kapitalizacja i Enterprise Value (EV)
            market_cap = price * shares
            ev = market_cap + total_debt - cash if pd.notna(total_debt) and pd.notna(cash) else np.nan

            # Annualizacja zysków i przychodów (kwartał x 4)
            ann_net_income = net_income * 4 if pd.notna(net_income) else np.nan
            ann_revenue = revenue * 4 if pd.notna(revenue) else np.nan
            ann_ebit = ebit * 4 if pd.notna(ebit) else np.nan
            ann_ebitda = ebitda * 4 if pd.notna(ebitda) else np.nan
            ann_op_income = op_income * 4 if pd.notna(op_income) else np.nan
            ann_cf = operating_cf * 4 if pd.notna(operating_cf) else np.nan

            # Kalkulacja wskaźników
            cz = market_cap / ann_net_income if pd.notna(ann_net_income) and ann_net_income != 0 else np.nan
            cwk = market_cap / total_equity if pd.notna(total_equity) and total_equity != 0 else np.nan
            cs = market_cap / ann_revenue if pd.notna(ann_revenue) and ann_revenue != 0 else np.nan
            c_zo = market_cap / ann_op_income if pd.notna(ann_op_income) and ann_op_income != 0 else np.nan
            cp = market_cap / ann_cf if pd.notna(ann_cf) and ann_cf != 0 else np.nan

            ev_p = ev / ann_cf if pd.notna(ev) and pd.notna(ann_cf) and ann_cf != 0 else np.nan
            ev_ebit = ev / ann_ebit if pd.notna(ev) and pd.notna(ann_ebit) and ann_ebit != 0 else np.nan
            ev_ebitda = ev / ann_ebitda if pd.notna(ev) and pd.notna(ann_ebitda) and ann_ebitda != 0 else np.nan

            roa = ann_net_income / total_assets if pd.notna(ann_net_income) and pd.notna(total_assets) and total_assets != 0 else np.nan
            roe = ann_net_income / total_equity if pd.notna(ann_net_income) and pd.notna(total_equity) and total_equity != 0 else np.nan

            results[date_str] = {
                "C/Z": cz,
                "C/WK": cwk,
                "C/WK Grahama": np.nan,  # yfinance nie podaje aktywów bieżących netto w standardowym formacie
                "C/P": cp,
                "C/S": cs,
                "C/ZO": c_zo,
                "EV/P": ev_p,
                "EV/EBIT": ev_ebit,
                "EV/EBITDA": ev_ebitda,
                "ROA": roa,
                "ROE": roe,
            }

        df_metrics = pd.DataFrame(results)
        if df_metrics.empty:
            return pd.DataFrame()

        df_metrics.index.name = "Wskaźnik"
        return df_metrics.reset_index()

    except Exception:
        return pd.DataFrame()