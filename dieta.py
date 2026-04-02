import tkinter as tk
from tkinter import messagebox

# Przykładowa baza produktów (można ją rozszerzać)
# Wartości na 100g produktu
food_db = [
    {"nazwa": "Ryż biały", "kcal": 350, "bialko": 7, "tluszcz": 0.6, "wegle": 77},
    {"nazwa": "Pierś z kurczaka", "kcal": 120, "bialko": 23, "tluszcz": 2, "wegle": 0},
    {"nazwa": "Oliwa z oliwek", "kcal": 880, "bialko": 0, "tluszcz": 100, "wegle": 0},
    {"nazwa": "Twaróg chudy", "kcal": 90, "bialko": 18, "tluszcz": 0.5, "wegle": 3.5}
]

def oblicz_makro():
    try:
        total_kcal = float(entry_kcal.get())
        p_bialko = float(entry_p_bialko.get()) / 100
        p_tluszcz = float(entry_p_tluszcz.get()) / 100
        p_wegle = float(entry_p_wegle.get()) / 100

        if round(p_bialko + p_tluszcz + p_wegle, 2) != 1.0:
            messagebox.showerror("Błąd", "Suma procentów musi wynosić 100%!")
            return

        # Obliczanie gramatury: Białko/Węgle = 4 kcal/g, Tłuszcz = 9 kcal/g
        g_bialko = (total_kcal * p_bialko) / 4
        g_tluszcz = (total_kcal * p_tluszcz) / 9
        g_wegle = (total_kcal * p_wegle) / 4

        label_result.config(text=f"Cel: B: {g_bialko:.1f}g | T: {g_tluszcz:.1f}g | W: {g_wegle:.1f}g")
        
        generuj_prosta_diete(g_bialko, g_tluszcz, g_wegle)

    except ValueError:
        messagebox.showerror("Błąd", "Wprowadź poprawne liczby!")

def generuj_prosta_diete(target_b, target_t, target_w):
    # Prosty algorytm wyświetlający dostępne produkty
    # W pełnej wersji tutaj znajdzie się logika dobierania wag produktów
    tekst_diety = "Sugerowane produkty z bazy:\n"
    for produkt in food_db:
        tekst_diety += f"- {produkt['nazwa']} ({produkt['kcal']} kcal/100g)\n"
    
    label_diet.config(text=tekst_diety)

# --- Konfiguracja Okna ---
root = tk.Tk()
root.title("Planer Diety v1.0")
root.geometry("400x500")

tk.Label(root, text="Zapotrzebowanie kcal:").pack(pady=5)
entry_kcal = tk.Entry(root)
entry_kcal.insert(0, "2000")
entry_kcal.pack()

tk.Label(root, text="Podział % (Białko / Tłuszcz / Węgle):").pack(pady=5)
frame_procenty = tk.Frame(root)
frame_procenty.pack()

entry_p_bialko = tk.Entry(frame_procenty, width=5)
entry_p_bialko.insert(0, "30")
entry_p_bialko.pack(side=tk.LEFT)

entry_p_tluszcz = tk.Entry(frame_procenty, width=5)
entry_p_tluszcz.insert(0, "25")
entry_p_tluszcz.pack(side=tk.LEFT)

entry_p_wegle = tk.Entry(frame_procenty, width=5)
entry_p_wegle.insert(0, "45")
entry_p_wegle.pack(side=tk.LEFT)

btn_oblicz = tk.Button(root, text="Oblicz i dobierz produkty", command=oblicz_makro)
btn_oblicz.pack(pady=20)

label_result = tk.Label(root, text="Cel: --", font=("Arial", 10, "bold"))
label_result.pack()

label_diet = tk.Label(root, text="", justify=tk.LEFT)
label_diet.pack(pady=10)

root.mainloop()
