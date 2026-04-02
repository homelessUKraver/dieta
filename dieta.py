import streamlit as st
import pandas as pd
import io
import os

# --- KONFIGURACJA ---
DB_FILE = 'produkty.csv'

def load_data():
    """Wczytuje i czyści plik CSV wyeksportowany z Numbers/Excela."""
    if not os.path.exists(DB_FILE):
        st.error(f"Nie znaleziono pliku {DB_FILE} w folderze programu!")
        return pd.DataFrame()

    try:
        # Próbujemy odczytać plik z kodowaniem obsługującym polskie znaki
        with open(DB_FILE, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()

        # 1. Znajdujemy linię, w której zaczynają się nagłówki (szukamy 'nazwa')
        start_index = -1
        for i, line in enumerate(lines):
            if 'nazwa' in line.lower():
                start_index = i
                break
        
        if start_index == -1:
            st.error("W pliku CSV nie znaleziono nagłówka 'nazwa'!")
            return pd.DataFrame()

        # 2. Czyścimy tekst - bierzemy dane od nagłówka w dół
        clean_lines = lines[start_index:]
        clean_csv = "".join(clean_lines)

        # 3. Wczytujemy do Pandas (sep=None automatycznie wykryje średnik lub przecinek)
        df = pd.read_csv(io.StringIO(clean_csv), sep=None, engine='python')

        # 4. Usuwamy puste kolumny (powstałe przez średniki na końcach linii w Numbers)
        df = df.dropna(axis=1, how='all')
        
        # 5. Standaryzacja nazw kolumn (usuwamy spacje, małe litery)
        df.columns = df.columns.str.strip().str.lower()
        
        # 6. Usuwamy puste wiersze i konwertujemy liczby (na wypadek przecinków zamiast kropek)
        df = df.dropna(subset=['nazwa'])
        for col in ['kcal', 'bialko', 'tluszcz', 'wegle']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
        
        return df.fillna(0)

    except Exception as e:
        st.error(f"Błąd podczas przetwarzania pliku: {e}")
        return pd.DataFrame()

# --- INTERFEJS UŻYTKOWNIKA ---
st.set_page_config(page_title="Inteligentny Dietetyk", layout="wide")
st.title("🍎 Inteligentny Planer Diety")

df = load_data()

if not df.empty:
    # --- PANEL BOCZNY (USTAWIENIA) ---
    st.sidebar.header("⚙️ Twoje Cele")
    total_kcal = st.sidebar.number_input("Dzienny limit kcal", value=2000, step=50)
    
    st.sidebar.subheader("Podział Makroskładników (%)")
    p_b = st.sidebar.slider("Białko (%)", 0, 100, 30)
    p_t = st.sidebar.slider("Tłuszcz (%)", 0, 100, 25)
    p_w = st.sidebar.slider("Węglowodany (%)", 0, 100, 45)
    
    if p_b + p_t + p_w != 100:
        st.sidebar.error("Suma procentów musi wynosić 100%!")
    
    n_posilkow = st.sidebar.number_input("Liczba posiłków dziennie", value=4, min_value=1)

    # --- OBLICZENIA CELU NA POSIŁEK ---
    target_b_meal = ((total_kcal * (p_b/100)) / 4) / n_posilkow
    target_t_meal = ((total_kcal * (p_t/100)) / 9) / n_posilkow
    target_w_meal = ((total_kcal * (p_w/100)) / 4) / n_posilkow

    st.subheader(f"🎯 Cel na jeden posiłek ({total_kcal // n_posilkow} kcal)")
    c1, c2, c3 = st.columns(3)
    c1.metric("Białko", f"{target_b_meal:.1f} g")
    c2.metric("Tłuszcz", f"{target_t_meal:.1f} g")
    c3.metric("Węglowodany", f"{target_w_meal:.1f} g")

    # --- KREATOR POSIŁKU ---
    st.divider()
    st.subheader("🥣 Skonfiguruj skład posiłku")
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        produkt_b = st.selectbox("Wybierz źródło białka:", df['nazwa'].tolist())
    with col_b:
        # Filtrujemy bazę, żeby zasugerować coś z węglami (opcjonalne, tutaj cała lista)
        produkt_w = st.selectbox("Wybierz źródło węglowodanów:", df['nazwa'].tolist())
    with col_c:
        produkt_t = st.selectbox("Wybierz źródło tłuszczu:", df['nazwa'].tolist())

    if st.button("✨ Oblicz gramaturę składników", type="primary"):
        # Pobieranie danych wybranych produktów
        b_data = df[df['nazwa'] == produkt_b].iloc[0]
        w_data = df[df['nazwa'] == produkt_w].iloc[0]
        t_data = df[df['nazwa'] == produkt_t].iloc[0]

        # --- ALGORYTM SOLVERA (Uproszczony) ---
        # 1. Ile produktu białkowego, by dobić do białka?
        waga_b = (target_b_meal / b_data['bialko']) * 100 if b_data['bialko'] > 0 else 0
        
        # 2. Ile produktu węglowego, by dobić do węgli (odejmujemy to, co już jest w kurczaku)?
        wegle_w_bialku = (waga_b * b_data['wegle']) / 100
        pozostalo_w = target_w_meal - wegle_w_bialku
        waga_w = (max(0, pozostalo_w) / w_data['wegle']) * 100 if w_data['wegle'] > 0 else 0
        
        # 3. Ile produktu tłuszczowego, by dobić do tłuszczu (odejmujemy tłuszcz z kurczaka i ryżu)?
        tluszcz_w_reszcie = ((waga_b * b_data['tluszcz']) / 100) + ((waga_w * w_data['tluszcz']) / 100)
        pozostalo_t = target_t_meal - tluszcz_w_reszcie
        waga_t = (max(0, pozostalo_t) / t_data['tluszcz']) * 100 if t_data['tluszcz'] > 0 else 0

        # Wyświetlanie wyniku
        st.success("### Twoja porcja:")
        res1, res2, res3 = st.columns(3)
        res1.info(f"**{waga_b:.0f}g**\n\n{produkt_b}")
        res2.info(f"**{waga_w:.0f}g**\n\n{produkt_w}")
        res3.info(f"**{waga_t:.0f}g**\n\n{produkt_t}")

        # Podsumowanie kcal
        suma_kcal = (waga_b*b_data['kcal'] + waga_w*w_data['kcal'] + waga_t*t_data['kcal'])/100
        st.write(f"Suma kalorii w tym posiłku: **{suma_kcal:.0f} kcal**")

    # --- PODGLĄD BAZY ---
    with st.expander("📂 Zobacz całą bazę produktów"):
        st.dataframe(df, use_container_width=True)

else:
    st.warning("Dodaj plik produkty.csv do folderu z programem, aby zacząć.")
