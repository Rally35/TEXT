import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st

@st.cache_data(ttl=3600)  # Odświeżaj co godzinę, aby nie obciążać serwerów BiznesRadar
def fetch_biznesradar_metrics(ticker="TEXT"):
    # Nagłówki udające przeglądarkę zapobiegają blokowaniu żądań przez serwer
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # URL do wskaźników rynkowych i rentowności
    urls = {
        "rynkowe": f"https://www.biznesradar.pl/wskazniki-wartosci-rynkowej/{ticker}",
        "rentownosc": f"https://www.biznesradar.pl/wskazniki-rentownosci/{ticker}"
    }
    
    all_metrics = {}
    quarters = []
    
    # Definiujemy wskaźniki, które nas interesują
    target_metrics = [
        "C/Z", "C/WK", "C/WK Grahama", "C/P", "C/S", 
        "C/ZO", "EV/P", "EV/EBIT", "EV/EBITDA", "ROA", "ROE"
    ]

    for category, url in urls.items():
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            table = soup.find('table', class_='report-table')
            if not table:
                continue
            
            # Pobieranie nagłówków (kwartałów) - robimy to tylko raz
            if not quarters:
                for th in table.find('tr').find_all('th'):
                    # Szukamy nagłówków zawierających 'Q' (np. 2023/Q1)
                    header_text = th.text.strip()
                    if 'Q' in header_text:
                        # Często tekst zawiera dodatkowe białe znaki, bierzemy tylko pierwszą część
                        quarters.append(header_text.split('\n')[0].strip())
            
            # Przeszukiwanie wierszy tabeli w poszukiwaniu wskaźników
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                if not cells:
                    continue
                
                metric_name_raw = cells[0].text.strip().split('\n')[0]
                
                # Sprawdzenie czy wiersz odpowiada jednemu z poszukiwanych wskaźników
                matched_metric = None
                for tm in target_metrics:
                    if metric_name_raw == tm or metric_name_raw.startswith(tm + " "):
                        matched_metric = tm
                        break
                        
                if matched_metric and matched_metric not in all_metrics:
                    values = []
                    # Zbieranie wartości dla poszczególnych kwartałów
                    for td in cells[1:]:
                        val_span = td.find('span', class_='value')
                        if val_span:
                            values.append(val_span.text.strip())
                        else:
                            # Czasami wartość jest oznaczona tyldą (brak danych)
                            text = td.text.strip()
                            values.append(text if text else "-")
                            
                    # Przycięcie do liczby znalezionych kwartałów
                    all_metrics[matched_metric] = values[:len(quarters)]
                    
        except Exception as e:
            print(f"Błąd podczas scrapowania {url}: {e}")

    if not all_metrics or not quarters:
        return pd.DataFrame()
        
    # Wybieramy tylko 4 ostatnie kwartały
    last_4_quarters = quarters[-4:]
    
    # Zbudowanie DataFrame
    df = pd.DataFrame(all_metrics).T
    df.columns = quarters
    
    # Ograniczenie do ostatnich 4 kwartałów i uporządkowanie
    df = df[last_4_quarters]
    df.index.name = 'Wskaźnik'
    df = df.reset_index()
    
    # Sortowanie wierszy zgodnie z kolejnością zdefiniowaną przez użytkownika
    df['sort_cat'] = pd.Categorical(df['Wskaźnik'], categories=target_metrics, ordered=True)
    df = df.sort_values('sort_cat').drop('sort_cat', axis=1)
    
    return df