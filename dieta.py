import streamlit as st
import pandas as pd
import os

# Konfiguracja strony
st.set_page_config(page_title="Planer Diety", layout="centered")

DB_FILE = 'produkty.csv'

# Funkcja wczytująca dane
def load_data():
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=['nazwa', 'kcal', 'bialko', 'tluszcz', 'wegle'])
        df.to_csv(DB_FILE, index=False)
        return df
    return pd.read_csv(DB_FILE)

st.title("🍎 Inteligentny Planer Diety")

# Sidebar - Dane wejściowe
st.sidebar.header("Twoje zapotrzebowanie")
total_kcal = st.sidebar.number_input("Kalorie (kcal)", value=2000, step=50)
p_bialko = st.sidebar.slider("Białko %", 0, 100, 30)
p_tluszcz = st.sidebar.slider("Tłuszcz %", 0, 100, 25)
p_wegle = st.sidebar.slider("Węglowodany %", 0, 100, 45)

# Logika obliczeń
if p_bialko + p_tluszcz + p_wegle != 100:
    st.sidebar.error("Suma procentów musi wynosić 100%!")
else:
    g_b = (total_kcal * (p_bialko/100)) / 4
    g_t = (total_kcal * (p_tluszcz/100)) / 9
    g_w = (total_kcal * (p_wegle/100)) / 4

    st.subheader("Twoje cele dzienne:")
    col1, col2, col3 = st.columns(3)
    col1.metric("Białko", f"{g_b:.1f} g")
    col2.metric("Tłuszcz", f"{g_t:.1f} g")
    col3.metric("Węgle", f"{g_w:.1f} g")

# Baza produktów
st.divider()
st.subheader("Baza produktów (z pliku CSV)")
df_produkty = load_data()
st.dataframe(df_produkty, use_container_width=True)

# Dodawanie nowego produktu przez aplikację
with st.expander("Dodaj nowy produkt do bazy"):
    new_name = st.text_input("Nazwa produktu")
    c1, c2, c3, c4 = st.columns(4)
    n_k = c1.number_input("kcal", 0.0)
    n_b = c2.number_input("B", 0.0)
    n_t = c3.number_input("T", 0.0)
    n_w = c4.number_input("W", 0.0)
    
    if st.button("Zapisz do CSV"):
        new_row = pd.DataFrame([[new_name, n_k, n_b, n_t, n_w]], 
                               columns=['nazwa', 'kcal', 'bialko', 'tluszcz', 'wegle'])
        new_row.to_csv(DB_FILE, mode='a', header=False, index=False)
        st.success("Dodano produkt! Odśwież stronę.")
