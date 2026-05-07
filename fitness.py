import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# --- 1. VERİ TABANI ---
def fitness_db_baslat():
    baglanti = sqlite3.connect("fitness.db") # Yemek projesinden tamamen farklı bir dosya!
    cursor = baglanti.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS antrenman_gunlugu (
            kayit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            ad TEXT,
            kilo TEXT,
            boy TEXT,
            tur TEXT,
            sure TEXT,
            tarih TEXT,
            kalori TEXT
        )
    """)
    baglanti.commit()
    baglanti.close()

# --- 2. SINIFLAR (Hocanın İstediği 3 Sınıf) ---
class Antrenman:
    def __init__(self, antrenman_id, tur, sure):
        self.antrenman_id = antrenman_id
        self.tur = tur
        self.sure = sure

class Takip:
    def __init__(self, tarih, kalori):
        self.tarih = tarih
        self.kalori = kalori

class Sporcu:
    def __init__(self, sporcu_id, ad, kilo, boy):
        self.sporcu_id = sporcu_id
        self.ad = ad
        self.kilo = kilo
        self.boy = boy

    # Hocanın özellikle istediği metod. Veritabanına kaydetme işini bu sınıfa yaptırıyoruz!
    def ilerleme_kaydet(self, antrenman_nesnesi, takip_nesnesi):
        try:
            baglanti = sqlite3.connect("fitness.db")
            cursor = baglanti.cursor()
            cursor.execute("""
                INSERT INTO antrenman_gunlugu (ad, kilo, boy, tur, sure, tarih, kalori)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (self.ad, self.kilo, self.boy, antrenman_nesnesi.tur, antrenman_nesnesi.sure, takip_nesnesi.tarih, takip_nesnesi.kalori))
            baglanti.commit()
            baglanti.close()
            return True
        except Exception as e:
            return False

# --- 3. ARAYÜZ FONKSİYONLARI ---
def listeyi_yenile():
    liste.delete(0, tk.END)
    baglanti = sqlite3.connect("fitness.db")
    cursor = baglanti.cursor()
    cursor.execute("SELECT * FROM antrenman_gunlugu")
    for k in cursor.fetchall():
        # k[0] id, k[1] ad, k[2] kilo, vs..
        yazi = f"{k[6]} | {k[1]} ({k[2]}kg) - {k[4]} - {k[5]}dk - Yakılan: {k[7]} kcal"
        liste.insert(tk.END, yazi)
    baglanti.close()

def sisteme_kaydet():
    # Kutulardaki verileri al
    ad = entry_ad.get()
    kilo = entry_kilo.get()
    boy = entry_boy.get()
    tur = combo_tur.get()
    sure = entry_sure.get()
    tarih = entry_tarih.get()
    kalori = entry_kalori.get()

    if not (ad and kilo and tur and sure and tarih):
        messagebox.showwarning("Eksik Bilgi", "Lütfen tüm kutucukları doldurun!")
        return

    # Sınıflardan nesneleri (object) üretiyoruz
    yeni_sporcu = Sporcu("S1", ad, kilo, boy)
    yeni_antrenman = Antrenman("A1", tur, sure)
    yeni_takip = Takip(tarih, kalori)

    # Sporcu sınıfındaki "ilerleme_kaydet" metodunu çalıştırıp diğer nesneleri içine yolluyoruz
    basarili_mi = yeni_sporcu.ilerleme_kaydet(yeni_antrenman, yeni_takip)

    if basarili_mi:
        listeyi_yenile()
        messagebox.showinfo("Helal!", "Antrenman başarıyla kaydedildi, gelişime devam!")
    else:
        messagebox.showerror("Hata", "Kaydedilirken bir sorun oluştu.")

# --- 4. ARAYÜZ TASARIMI (Fitness Temalı) ---
fitness_db_baslat()

pencere = tk.Tk()
pencere.title("Fitness & Antrenman Takip Sistemi")
pencere.geometry("550x650")
pencere.config(bg="#1e272e") # Koyu tema, spor uygulaması hissiyatı

baslik_font = ("Arial", 12, "bold")
yazi_font = ("Arial", 10)
yazi_renk = "white"
arkaplan = "#1e272e"

# Başlık
tk.Label(pencere, text="FITNESS TAKİP SİSTEMİ", font=("Arial", 16, "bold"), bg=arkaplan, fg="#0fb9b1").pack(pady=15)

# Çerçeve
frame = tk.Frame(pencere, bg=arkaplan)
frame.pack(pady=10)

# Sporcu Bilgileri
tk.Label(frame, text="Sporcu Adı:", bg=arkaplan, fg=yazi_renk, font=yazi_font).grid(row=0, column=0, pady=5, sticky="e")
entry_ad = tk.Entry(frame, width=15)
entry_ad.grid(row=0, column=1, padx=5)

tk.Label(frame, text="Kilo (kg):", bg=arkaplan, fg=yazi_renk, font=yazi_font).grid(row=0, column=2, sticky="e")
entry_kilo = tk.Entry(frame, width=10)
entry_kilo.grid(row=0, column=3, padx=5)

tk.Label(frame, text="Boy (cm):", bg=arkaplan, fg=yazi_renk, font=yazi_font).grid(row=0, column=4, sticky="e")
entry_boy = tk.Entry(frame, width=10)
entry_boy.grid(row=0, column=5, padx=5)

# Antrenman & Takip Bilgileri
tk.Label(frame, text="Antrenman Türü:", bg=arkaplan, fg=yazi_renk, font=yazi_font).grid(row=1, column=0, pady=15, sticky="e")
combo_tur = ttk.Combobox(frame, values=["Ağırlık", "Kardiyo", "Crossfit", "Esneme"], width=12, state="readonly")
combo_tur.set("Seçiniz")
combo_tur.grid(row=1, column=1, padx=5)

tk.Label(frame, text="Süre (dk):", bg=arkaplan, fg=yazi_renk, font=yazi_font).grid(row=1, column=2, sticky="e")
entry_sure = tk.Entry(frame, width=10)
entry_sure.grid(row=1, column=3, padx=5)

tk.Label(frame, text="Yakılan Kalori:", bg=arkaplan, fg=yazi_renk, font=yazi_font).grid(row=2, column=0, pady=5, sticky="e")
entry_kalori = tk.Entry(frame, width=15)
entry_kalori.grid(row=2, column=1, padx=5)

tk.Label(frame, text="Tarih:", bg=arkaplan, fg=yazi_renk, font=yazi_font).grid(row=2, column=2, sticky="e")
entry_tarih = tk.Entry(frame, width=15)
entry_tarih.insert(0, "07.05.2026") # Bugünün tarihini otomatik yazsın
entry_tarih.grid(row=2, column=3, columnspan=3, sticky="w", padx=5)

# Kaydet Butonu
btn_kaydet = tk.Button(pencere, text="💪 İLERLEMEYİ KAYDET", command=sisteme_kaydet, bg="#0fb9b1", fg="white", font=baslik_font, width=25)
btn_kaydet.pack(pady=15)

# Liste
tk.Label(pencere, text="📋 Geçmiş Antrenman Kayıtları", font=baslik_font, bg=arkaplan, fg="#feca57").pack(pady=5)
liste = tk.Listbox(pencere, width=70, height=12, bg="#d2dae2", font=("Consolas", 10))
liste.pack(pady=5)

listeyi_yenile()
pencere.mainloop()
