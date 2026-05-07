import tkinter as tk
from tkinter import ttk, messagebox # ttk: Açılır menü ve modern tasarımlar için

# --- 1. KISIM: SINIFLAR (OOP Mantığımız Aynı) ---
class Malzeme:
    def __init__(self, malzeme_adi, miktar):
        self.malzeme_adi = malzeme_adi
        self.miktar = miktar

class Kullanici:
    def __init__(self, kullanici_id, ad):
        self.kullanici_id = kullanici_id
        self.ad = ad
    
    def tarif_degerlendir(self, tarif_nesnesi, verilen_puan):
        tarif_nesnesi.puan = verilen_puan

class Tarif:
    def __init__(self, tarif_id, tarif_adi, kategori, hazirlama_suresi):
        self.tarif_id = tarif_id
        self.tarif_adi = tarif_adi
        self.kategori = kategori
        self.hazirlama_suresi = hazirlama_suresi
        self.puan = "Yok"
    
    def tarif_guncelle(self, yeni_sure):
        self.hazirlama_suresi = yeni_sure

    def __str__(self):
        return f"ID: {self.tarif_id} | {self.tarif_adi} | Kat: {self.kategori} | Süre: {self.hazirlama_suresi} dk | Puan: {self.puan}"


# --- 2. KISIM: VERİLER VE FONKSİYONLAR ---
tarif_kutusu = []
aktif_kullanici = Kullanici("1", "Yasin")

tarif_kutusu.append(Tarif("101", "Menemen", "Kahvaltılık", "15"))
tarif_kutusu.append(Tarif("102", "Makarna", "Ana Yemek", "20"))
tarif_kutusu.append(Tarif("103", "Sütlaç", "Tatlı", "40")) # Ekran dolu dursun diye 3'e çıkardık

def listeyi_guncelle():
    liste_kutusu.delete(0, tk.END)
    for tarif in tarif_kutusu:
        liste_kutusu.insert(tk.END, str(tarif))

def tarif_ekle():
    t_id = entry_id.get()
    t_ad = entry_ad.get()
    t_kat = combo_kat.get() # Artık entry değil, combobox'tan alıyoruz
    t_sure = entry_sure.get()

    if t_id == "" or t_ad == "" or t_sure == "":
        messagebox.showwarning("Eksik Bilgi", "Lütfen tüm alanları doldurun!")
        return

    yeni_tarif = Tarif(t_id, t_ad, t_kat, t_sure)
    tarif_kutusu.append(yeni_tarif)
    listeyi_guncelle()
    
    # Kutuları temizle
    entry_id.delete(0, tk.END)
    entry_ad.delete(0, tk.END)
    entry_sure.delete(0, tk.END)
    combo_kat.set("Seçiniz...") # Açılır menüyü sıfırla
    messagebox.showinfo("Başarılı", "Tarif sisteme eklendi!")

# YENİ EKLENEN SİLME FONKSİYONU
def tarif_sil():
    secilen = liste_kutusu.curselection() # Listeden neyin seçildiğini bul
    if not secilen:
        messagebox.showwarning("Uyarı", "Lütfen listeden silmek istediğiniz tarifi seçin!")
        return
    
    index = secilen[0] # Seçilenin sırasını al
    del tarif_kutusu[index] # Kutudan sil
    listeyi_guncelle() # Ekranı yenile
    messagebox.showinfo("Başarılı", "Tarif başarıyla silindi!")

def sureyi_guncelle():
    hedef_id = entry_islem_id.get()
    yeni_sure = entry_islem_deger.get()
    
    for t in tarif_kutusu:
        if t.tarif_id == hedef_id:
            t.tarif_guncelle(yeni_sure)
            listeyi_guncelle()
            messagebox.showinfo("Başarılı", "Süre güncellendi!")
            return
    messagebox.showwarning("Hata", "Tarif bulunamadı.")

def puan_ver():
    hedef_id = entry_islem_id.get()
    verilen_puan = entry_islem_deger.get()
    
    for t in tarif_kutusu:
        if t.tarif_id == hedef_id:
            aktif_kullanici.tarif_degerlendir(t, verilen_puan)
            listeyi_guncelle()
            messagebox.showinfo("Başarılı", "Puan verildi!")
            return
    messagebox.showwarning("Hata", "Tarif bulunamadı.")


# --- 3. KISIM: ARAYÜZ (Gelişmiş Tasarım) ---
pencere = tk.Tk()
pencere.title("Profesyonel Yemek Tarif Platformu")
pencere.geometry("550x700") # Pencereyi biraz daha büyüttük
pencere.config(bg="#f4f4f9") # Daha modern kırık beyaz arka plan

font_baslik = ("Helvetica", 14, "bold")
font_normal = ("Helvetica", 10)

# ÜST BÖLÜM: Ekleme Çerçevesi
frame_ust = tk.LabelFrame(pencere, text="Yeni Tarif Ekleme Paneli", font=font_baslik, bg="#f4f4f9", padx=15, pady=15)
frame_ust.pack(padx=20, pady=10, fill="x")

tk.Label(frame_ust, text="Tarif ID:", bg="#f4f4f9", font=font_normal).grid(row=0, column=0, sticky="w", pady=5)
entry_id = tk.Entry(frame_ust, width=15)
entry_id.grid(row=0, column=1, padx=10)

tk.Label(frame_ust, text="Tarif Adı:", bg="#f4f4f9", font=font_normal).grid(row=0, column=2, sticky="w")
entry_ad = tk.Entry(frame_ust, width=20)
entry_ad.grid(row=0, column=3, padx=10)

tk.Label(frame_ust, text="Kategori:", bg="#f4f4f9", font=font_normal).grid(row=1, column=0, sticky="w", pady=5)
# YENİ: Açılır Menü (Combobox)
kategoriler = ["Kahvaltılık", "Ana Yemek", "Ara Sıcak", "Çorba", "Tatlı", "İçecek"]
combo_kat = ttk.Combobox(frame_ust, values=kategoriler, width=12, state="readonly")
combo_kat.set("Seçiniz...")
combo_kat.grid(row=1, column=1, padx=10)

tk.Label(frame_ust, text="Süre (dk):", bg="#f4f4f9", font=font_normal).grid(row=1, column=2, sticky="w")
entry_sure = tk.Entry(frame_ust, width=20)
entry_sure.grid(row=1, column=3, padx=10)

tk.Button(frame_ust, text="➜ Tarifi Sisteme Ekle", command=tarif_ekle, bg="#4CAF50", fg="white", font=("Helvetica", 10, "bold"), width=20).grid(row=2, column=0, columnspan=4, pady=15)


# ORTA BÖLÜM: Listeleme Çerçevesi
frame_orta = tk.LabelFrame(pencere, text="Sistemdeki Tarifler (Veritabanı)", font=font_baslik, bg="#f4f4f9", padx=15, pady=10)
frame_orta.pack(padx=20, pady=5, fill="both", expand=True)

# YENİ: Kaydırma Çubuğu (Scrollbar)
scrollbar = tk.Scrollbar(frame_orta)
scrollbar.pack(side="right", fill="y")

liste_kutusu = tk.Listbox(frame_orta, width=70, height=10, font=("Consolas", 10), yscrollcommand=scrollbar.set)
liste_kutusu.pack(side="left", fill="both")
scrollbar.config(command=liste_kutusu.yview)

# Seçili olanı silme butonu
tk.Button(pencere, text="🗑️ Seçili Tarifi Sil", command=tarif_sil, bg="#f44336", fg="white", font=font_normal).pack(pady=5)


# ALT BÖLÜM: Güncelleme Çerçevesi
frame_alt = tk.LabelFrame(pencere, text="Hızlı İşlem Menüsü (Güncelle & Oyla)", font=font_baslik, bg="#f4f4f9", padx=15, pady=15)
frame_alt.pack(padx=20, pady=10, fill="x")

tk.Label(frame_alt, text="Hedef ID:", bg="#f4f4f9", font=font_normal).grid(row=0, column=0, padx=5)
entry_islem_id = tk.Entry(frame_alt, width=10)
entry_islem_id.grid(row=0, column=1, padx=5)

tk.Label(frame_alt, text="Yeni Değer:", bg="#f4f4f9", font=font_normal).grid(row=0, column=2, padx=5)
entry_islem_deger = tk.Entry(frame_alt, width=10)
entry_islem_deger.grid(row=0, column=3, padx=5)

tk.Button(frame_alt, text="Süreyi Güncelle", command=sureyi_guncelle, bg="#FF9800", fg="white", font=font_normal).grid(row=0, column=4, padx=10)
tk.Button(frame_alt, text="Puan Ver (1-10)", command=puan_ver, bg="#2196F3", fg="white", font=font_normal).grid(row=0, column=5, padx=5)

listeyi_guncelle()
pencere.mainloop()