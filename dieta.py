import tkinter as tk
from tkinter import messagebox
import csv
import os

# Nazwa pliku z bazą danych
DB_FILE = 'produkty.csv'

def wczytaj_aze_danych():
    produkty = []
    if not os.path.exists(DB_FILE):
        # Tworzy pusty plik z nagłówkami, jeśli nie istnieje
        with open(DB_FILE, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['nazwa', 'kcal', 'bialko', 'tluszcz', 'wegle'])
        return produkty

    with open(DB_FILE, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Konwersja wartości tekstowych z CSV na liczby
            produkty.append({
                "nazwa": row['nazwa'],
                "kcal": float(row['kcal']),
                "bialko": float(row['bialko']),
                "tluszcz": float(row['tluszcz']),
                "wegle": float(row['wegle'])
            })
    return produkty

def oblicz_makro():
    try:
        total_kcal = float(entry_kcal.get())
        p_bialko = float(entry_p_bialko.get()) / 100
        p_tluszcz = float(entry_p_tluszcz.get()) / 100
        p_wegle = float(entry_p_wegle.get()) / 100

        if round(p_bialko + p_tluszcz + p_wegle, 2) != 1.0:
            messagebox.showerror("Błąd", "Suma procentów musi wynosić 100%!")
            return

        # Obliczanie zapotrzebowania w gramach
        g_bialko = (total_kcal * p_bialko) / 4
        g_tluszcz = (total_kcal * p_tluszcz) / 9
        g_wegle = (total_kcal * p_wegle) / 4

        label_result.config(text=f"Cel: B: {g_bialko:.1f}g | T: {g_tluszcz:.1f}g | W: {g_wegle:.1f}g")
        
        wyswietl_dostepne_produkty()

    except ValueError:
        messagebox.showerror("Błąd", "Wprowadź poprawne liczby!")

def wyswietl_dostepne_produkty():
    baza = wczytaj_aze_danych()
    tekst_diety = "Produkty w bazie (na 100g):\n"
    for p in baza:
        tekst_diety += f"• {p['nazwa']}: B:{p['bialko']} T:{p['tluszcz']} W:{p['wegle']} ({p['kcal']} kcal)\n"
    
    label_diet.config(text=tekst_diety)

# --- GUI ---
root = tk.Tk()
root.title("Dietetyk CSV v1.1")
root.geometry("500x600")

tk.Label(root, text="Zapotrzebowanie kaloryczne (kcal):", font=("Arial", 10, "bold")).pack(pady=5)
entry_kcal = tk.Entry(root)
entry_kcal.insert(0, "2000")
entry_kcal.pack()

tk.Label(root, text="Podział % (Białko / Tłuszcz / Węgle):").pack(pady=5)
frame_procenty = tk.Frame(root)
frame_procenty.pack()

entry_p_bialko = tk.Entry(frame_procenty, width=5)
entry_p_bialko.insert(0, "30")
entry_p_bialko.pack(side=tk.LEFT, padx=5)

entry_p_tluszcz = tk.Entry(frame_procenty, width=5)
entry_p_tluszcz.insert(0, "25")
entry_p_tluszcz.pack(side=tk.LEFT, padx=5)

entry_p_wegle = tk.Entry(frame_procenty, width=5)
entry_p_wegle.insert(0, "45")
entry_p_wegle.pack(side=tk.LEFT, padx=5)

btn_oblicz = tk.Button(root, text="Wczytaj bazę i oblicz makro", command=oblicz_makro, bg="#4CAF50", fg="white")
btn_oblicz.pack(pady=20)

label_result = tk.Label(root, text="Cel: --", font=("Arial", 11, "bold"), fg="blue")
label_result.pack()

# Scrollbar dla listy produktów, jeśli baza będzie duża
frame_list = tk.Frame(root)
frame_list.pack(pady=10, fill=tk.BOTH, expand=True)

label_diet = tk.Label(frame_list, text="Kliknij przycisk, aby wczytać dane z CSV", justify=tk.LEFT, anchor="nw")
label_diet.pack(padx=10)

root.mainloop()
