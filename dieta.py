import streamlit as st
import pandas as pd
import io
import os

# --- KONFIGURACJA PLIKU ---
DB_FILE = 'produkty.csv'

def load_data():
    if not os.path.exists(DB_FILE):
        return pd.DataFrame()
    try:
        with open(DB_FILE, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
        start_index = -1
        for i, line in enumerate(lines):
            if 'nazwa' in line.lower():
                start_index = i
                break
        if start_index == -1: return pd.DataFrame()
        clean_csv = "".join(lines[start_index:])
        df = pd.read_csv(io.StringIO(clean_csv), sep=None, engine='python')
        df = df.dropna(axis=1, how='all')
        df.columns = df.columns.str.strip().str.lower()
        df = df.dropna(subset=['nazwa'])
        for col in ['kcal', 'bialko', 'tluszcz', 'wegle']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
        return df.fillna(0)
    except:
        return pd.DataFrame()

# --- INTERFEJS ---
st.set_page_config(page_title="Planer 5 Posiłków", layout="wide")
st.title("🍽️ Planer Diety: 5 Posiłków Dziennie")

df = load_data()

if not df.empty:
    # --- BOCZNY PANEL: CELE ---
    st.sidebar.header("🎯 Twoje Cele Dziennie")
    total_kcal = st.sidebar.number_input("Limit kcal", value=2000, step=50)
    p_b = st.sidebar.slider("Białko %", 0, 100, 30)
    p_t = st.sidebar.slider("Tłuszcz %", 0, 100, 25)
    p_w = st.sidebar.slider("Węgle %", 0, 100, 45)

    # Cele w gramach
    target_b = (total_kcal * (p_b/100)) / 4
    target_t = (total_kcal * (p_t/100)) / 9
    target_w = (total_kcal * (p_w/100)) / 4

    # --- DASHBOARD (PODSUMOWANIE) ---
    st.write("### Pozostało do spożycia dzisiaj:")
    # Te zmienne będą aktualizowane przez pętlę posiłków
    current_b, current_t, current_w, current_kcal = 0, 0, 0, 0

    # --- KREATOR 5 POSIŁKÓW ---
    st.divider()
    
    for i in range(1, 6):
        with st.expander(f"🍴 POSIŁEK NR {i}", expanded=True):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                wybor = st.multiselect(f"Wybierz produkty (Posiłek {i})", df['nazwa'].tolist(), key=f"prod_{i}")
            
            for p_name in wybor:
                p_data = df[df['nazwa'] == p_name].iloc[0]
                col_gram, col_info = st.columns([1, 3])
                
                with col_gram:
                    gramy = st.number_input(f"Gramy: {p_name}", min_value=0, value=100, step=10, key=f"g_{i}_{p_name}")
                
                # Obliczenia dla konkretnego produktu w posiłku
                p_b = (gramy * p_data['bialko']) / 100
                p_t = (gramy * p_data['tluszcz']) / 100
                p_w = (gramy * p_data['wegle']) / 100
                p_k = (gramy * p_data['kcal']) / 100
                
                with col_info:
                    st.caption(f"➔ {p_k:.0f} kcal | B: {p_b:.1f}g | T: {p_t:.1f}g | W: {p_w:.1f}g")
                
                current_b += p_b
                current_t += p_t
                current_w += p_w
                current_kcal += p_k

    # --- WYŚWIETLENIE WYNIKÓW NA GÓRZE (DZIĘKI ST.EMPTY LUB METRICS) ---
    st.sidebar.divider()
    st.sidebar.write("### 📊 Statystyki Dnia")
    st.sidebar.metric("Kalorie", f"{current_kcal:.0f} / {total_kcal}")
    
    # Wyświetlanie brakujących wartości
    diff_b = target_b - current_b
    diff_w = target_w - current_w
    diff_t = target_t - current_t

    st.divider()
    res_col1, res_col2, res_col3 = st.columns(3)
    res_col1.metric("Białko (Pozostało)", f"{diff_b:.1f} g", delta=f"{current_b:.1f} g zjedzone", delta_color="off")
    res_col2.metric("Węgle (Pozostało)", f"{diff_w:.1f} g", delta=f"{current_w:.1f} g zjedzone", delta_color="off")
    res_col3.metric("Tłuszcz (Suma)", f"{current_t:.1f} g", delta=f"Cel: {target_t:.1f} g")

    if current_kcal > total_kcal:
        st.warning("⚠️ Przekroczyłeś dzienny limit kalorii!")
    elif diff_b < 5 and diff_w < 5:
        st.balloons()
        st.success("🎯 Gratulacje! Idealnie dopasowałeś makroskładniki.")

else:
    st.error("Błąd wczytywania bazy. Sprawdź plik produkty.csv")
