import streamlit as st
import pandas as pd
import os

# Możesz zmienić na 'produkty.xlsx', jeśli wyeksportujesz z Numbers do Excela
DB_FILE = 'produkty.csv' 

def load_data():
    if not os.path.exists(DB_FILE):
        # Tworzymy bazę startową, jeśli pliku nie ma
        df = pd.DataFrame({
            'nazwa': ['Ryż biały', 'Pierś z kurczaka', 'Oliwa z oliwek', 'Brokuły'],
            'kcal': [350, 120, 880, 34],
            'bialko': [7.0, 23.0, 0.0, 3.0],
            'tluszcz': [0.6, 2.0, 100.0, 0.4],
            'wegle': [77.0, 0.0, 0.0, 7.0]
        })
        df.to_csv(DB_FILE, index=False, sep=';') # Używamy średnika - bezpieczniejszy w PL
        return df
    
    # Próba wczytania (obsługa CSV ze średnikiem lub przecinkiem)
    try:
        if DB_FILE.endswith('.xlsx'):
            return pd.read_excel(DB_FILE)
        else:
            return pd.read_csv(DB_FILE, sep=None, engine='python')
    except Exception as e:
        st.error(f"Błąd wczytywania pliku: {e}")
        return pd.DataFrame()

st.title("🥗 Inteligentny Dietetyk")

df = load_data()

if not df.empty:
    # --- BOCZNY PANEL ---
    st.sidebar.header("Twoje Cele")
    total_kcal = st.sidebar.number_input("Dzienny limit kcal", value=2000)
    p_b = st.sidebar.slider("Białko %", 0, 100, 30)
    p_t = st.sidebar.slider("Tłuszcz %", 0, 100, 25)
    p_w = st.sidebar.slider("Węgle %", 0, 100, 45)
    ile_posilkow = st.sidebar.number_input("Liczba posiłków", value=4)

    # Cel na jeden posiłek
    target_b = ((total_kcal * (p_b/100)) / 4) / ile_posilkow
    target_t = ((total_kcal * (p_t/100)) / 9) / ile_posilkow
    target_w = ((total_kcal * (p_w/100)) / 4) / ile_posilkow

    # --- WYBÓR SKŁADNIKÓW ---
    st.subheader("Wybierz składniki posiłku")
    wybrane = st.multiselect("Wybierz produkty z bazy:", df['nazwa'].tolist(), default=df['nazwa'].tolist()[:3])

    if len(wybrane) >= 2:
        # --- ZAAWANSOWANY SOLVER (Uproszczona algebra liniowa) ---
        # Dla uproszczenia: program próbuje dopasować główne źródła
        
        subset = df[df['nazwa'].isin(wybrane)].copy()
        
        # Obliczamy wagi (w przybliżeniu), uwzględniając wzajemne przenikanie makro
        # Szukamy: Waga * (Makro/100) = Target
        
        # 1. Źródło białka (najwięcej białka w wybranej liście)
        main_b = subset.loc[subset['bialko'].idxmax()]
        # 2. Źródło węgli (najwięcej węgli)
        main_w = subset.loc[subset['wegle'].idxmax()]
        # 3. Źródło tłuszczu (najwięcej tłuszczu)
        main_t = subset.loc[subset['tluszcz'].idxmax()]

        # Obliczamy wagę białka (podstawa)
        waga_b = (target_b / main_b['bialko']) * 100
        
        # Odejmujemy białko z kurczaka od zapotrzebowania na węgle (bo np. ryż też ma białko)
        # Tutaj dzieje się magia balansu:
        pozostalo_w = target_w - (waga_b * main_b['wegle'] / 100)
        waga_w = (max(0, pozostalo_w) / main_w['wegle']) * 100
        
        pozostalo_t = target_t - (waga_b * main_b['tluszcz'] / 100) - (waga_w * main_w['tluszcz'] / 100)
        waga_t = (max(0, pozostalo_t) / main_t['tluszcz']) * 100

        st.info(f"Cel na ten posiłek: B: {target_b:.1f}g | T: {target_t:.1f}g | W: {target_w:.1f}g")
        
        c1, c2, c3 = st.columns(3)
        c1.metric(main_b['nazwa'], f"{waga_b:.0f} g")
        c2.metric(main_w['nazwa'], f"{waga_w:.0f} g")
        c3.metric(main_t['nazwa'], f"{waga_t:.0f} g")

        final_kcal = (waga_b*main_b['kcal'] + waga_w*main_w['kcal'] + waga_t*main_t['kcal'])/100
        st.success(f"Razem w posiłku: **{final_kcal:.0f} kcal**")
    else:
        st.warning("Wybierz przynajmniej 3 produkty (białko, węgle, tłuszcz), aby system mógł obliczyć proporcje.")

# Sekcja dodawania produktów
with st.expander("Dodaj produkt do bazy"):
    st.write("Uzupełnij dane (na 100g produktu):")
    # ... (tutaj formularz dodawania jak wcześniej)
