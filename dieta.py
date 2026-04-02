import streamlit as st
import pandas as pd
import os

DB_FILE = 'produkty.csv'

# Funkcja wczytująca dane (dodajemy przykładowe dane, jeśli plik jest pusty)
def load_data():
    if not os.path.exists(DB_FILE) or os.stat(DB_FILE).st_size == 0:
        df = pd.DataFrame({
            'nazwa': ['Ryż biały', 'Pierś z kurczaka', 'Oliwa z oliwek', 'Brokuły'],
            'kcal': [350, 120, 880, 34],
            'bialko': [7.0, 23.0, 0.0, 3.0],
            'tluszcz': [0.6, 2.0, 100.0, 0.4],
            'wegle': [77.0, 0.0, 0.0, 7.0]
        })
        df.to_csv(DB_FILE, index=False)
        return df
    return pd.read_csv(DB_FILE)

st.title("🍎 Inteligentny Planer Diety")

# 1. USTAWIENIA CELÓW
st.sidebar.header("Twoje zapotrzebowanie")
total_kcal = st.sidebar.number_input("Kalorie na cały dzień (kcal)", value=2000)
p_bialko = st.sidebar.slider("Białko %", 0, 100, 30)
p_tluszcz = st.sidebar.slider("Tłuszcz %", 0, 100, 25)
p_wegle = st.sidebar.slider("Węglowodany %", 0, 100, 45)

# Obliczenia gramatury docelowej
g_b_total = (total_kcal * (p_bialko/100)) / 4
g_t_total = (total_kcal * (p_tluszcz/100)) / 9
g_w_total = (total_kcal * (p_wegle/100)) / 4

# 2. WYBÓR PRODUKTÓW DO POSIŁKU
st.header("🥗 Skonfiguruj swój posiłek")
st.info("Program wyliczy ilości dla JEDNEGO posiłku (zakładając podział na 4 posiłki dziennie).")

df = load_data()
ile_posilkow = st.number_input("Na ile posiłków dzielimy dietę?", value=4)

# Cele na jeden posiłek
target_b = g_b_total / ile_posilkow
target_t = g_t_total / ile_posilkow
target_w = g_w_total / ile_posilkow

col1, col2, col3 = st.columns(3)
with col1:
    produkt_b = st.selectbox("Źródło białka (np. Kurczak)", df['nazwa'].tolist(), index=1)
with col2:
    produkt_w = st.selectbox("Źródło węglowodanów (np. Ryż)", df['nazwa'].tolist(), index=0)
with col3:
    produkt_t = st.selectbox("Źródło tłuszczu (np. Oliwa)", df['nazwa'].tolist(), index=2)

if st.button("Oblicz gramaturę składników"):
    # Pobieranie danych wybranych produktów
    data_b = df[df['nazwa'] == produkt_b].iloc[0]
    data_w = df[df['nazwa'] == produkt_w].iloc[0]
    data_t = df[df['nazwa'] == produkt_t].iloc[0]

    # Uproszczony algorytm wyliczania wag:
    # 1. Ile produktu białkowego, by pokryć target_b
    waga_b = (target_b / data_b['bialko']) * 100
    # 2. Ile produktu węglowego, by pokryć pozostałe target_w (uwzględniając wegle z kurczaka/tłuszczu jeśli są)
    waga_w = (target_w / data_w['wegle']) * 100
    # 3. Ile produktu tłuszczowego, by dobić do target_t
    waga_t = (target_t / data_t['tluszcz']) * 100

    st.success(f"### Propozycja posiłku:")
    st.write(f"✅ **{waga_b:.0f}g** - {produkt_b}")
    st.write(f"✅ **{waga_w:.0f}g** - {produkt_w}")
    st.write(f"✅ **{waga_t:.0f}g** - {produkt_t}")
    
    # Podsumowanie tego posiłku
    posilek_kcal = (waga_b * data_b['kcal'] + waga_w * data_w['kcal'] + waga_t * data_t['kcal']) / 100
    st.caption(f"Suma kalorii w tym posiłku: {posilek_kcal:.0f} kcal")

# 3. ZARZĄDZANIE BAZĄ
with st.expander("Zarządzaj bazą produktów (CSV)"):
    st.dataframe(df)
    new_name = st.text_input("Nazwa nowego produktu")
    c1, c2, c3, c4 = st.columns(4)
    n_k = c1.number_input("kcal", 0.0)
    n_b = c2.number_input("B", 0.0)
    n_t = c3.number_input("T", 0.0)
    n_w = c4.number_input("W", 0.0)
    
    if st.button("Dodaj produkt"):
        new_row = pd.DataFrame([[new_name, n_k, n_b, n_t, n_w]], columns=df.columns)
        new_row.to_csv(DB_FILE, mode='a', header=False, index=False)
        st.rerun()
