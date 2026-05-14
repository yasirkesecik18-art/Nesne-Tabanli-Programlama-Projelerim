"""
=============================================================================
GASTRO-ERP YÖNETİM SİSTEMİ v4.0 (ENTERPRISE EDITION)
Geliştirici: Yasir Karabacak (yasirsalvo)
Modüller: Kimlik Doğrulama, Veri Analizi, Loglama, CRUD, CSV Raporlama
Kullanılan Teknolojiler: Python 3, Tkinter, SQLite3, CSV, Datetime
=============================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import sys
import csv
import os
from datetime import datetime

# ==========================================
# GLOBAL DEĞİŞKENLER (OTURUM BİLGİLERİ)
# ==========================================
GIRIS_YAPAN_KULLANICI = ""
GIRIS_YAPAN_YETKI = ""
GIRIS_BASARILI = False

# ==========================================
# VERİTABANI MOTORU (ALTYAPI)
# ==========================================
def sistem_veritabanini_kur():
    """Sistemin ihtiyaç duyduğu 3 farklı tabloyu (Kullanıcı, Tarif, Log) kurar."""
    baglanti = sqlite3.connect("gastro_erp_v4.db")
    cursor = baglanti.cursor()
    
    # 1. KULLANICILAR TABLOSU
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kullanicilar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            k_adi TEXT UNIQUE,
            sifre TEXT,
            yetki TEXT
        )
    """)
    # Varsayılan Admin (SENSİN)
    cursor.execute("SELECT count(*) FROM kullanicilar")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO kullanicilar (k_adi, sifre, yetki) VALUES (?, ?, ?)", ("yasirsalvo", "213623640", "Admin"))
    
    # 2. TARİFLER TABLOSU (Detaylandırıldı)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tarifler (
            id TEXT PRIMARY KEY,
            ad TEXT,
            kategori TEXT,
            zorluk TEXT,
            sure TEXT,
            kalori TEXT,
            malzemeler TEXT,
            yapilisi TEXT
        )
    """)
    
    # 3. SİSTEM LOGLARI TABLOSU (İşlem Geçmişi)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS loglar (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarih TEXT,
            kullanici TEXT,
            islem_detayi TEXT
        )
    """)
    
    baglanti.commit()
    baglanti.close()

def log_kaydet(islem_metni):
    """Sistemde yapılan her hareketi saniyesi saniyesine veritabanına yazar."""
    zaman = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    kullanici = GIRIS_YAPAN_KULLANICI if GIRIS_YAPAN_KULLANICI else "SİSTEM"
    
    baglanti = sqlite3.connect("gastro_erp_v4.db")
    cursor = baglanti.cursor()
    cursor.execute("INSERT INTO loglar (tarih, kullanici, islem_detayi) VALUES (?, ?, ?)", (zaman, kullanici, islem_metni))
    baglanti.commit()
    baglanti.close()

# ==========================================
# 1. MODÜL: SİBER GÜVENLİK (LOGİN)
# ==========================================
def giris_ekrani_baslat():
    def kimlik_dogrula():
        k_adi = entry_k_adi.get()
        sifre = entry_sifre.get()
        
        baglanti = sqlite3.connect("gastro_erp_v4.db")
        cursor = baglanti.cursor()
        cursor.execute("SELECT yetki FROM kullanicilar WHERE k_adi=? AND sifre=?", (k_adi, sifre))
        sonuc = cursor.fetchone()
        baglanti.close()
        
        if sonuc:
            global GIRIS_YAPAN_KULLANICI, GIRIS_YAPAN_YETKI
            GIRIS_YAPAN_KULLANICI = k_adi
            GIRIS_YAPAN_YETKI = sonuc[0]
            
            # Şov Kısmı: Yükleme Barı
            btn_giris.config(state="disabled", text="KİMLİK ONAYLANDI. SİSTEM YÜKLENİYOR...")
            def progress_artir(deger=0):
                if deger <= 100:
                    progress['value'] = deger
                    login.update_idletasks()
                    login.after(10, progress_artir, deger + 2)
                else:
                    global GIRIS_BASARILI
                    GIRIS_BASARILI = True
                    log_kaydet(f"Sisteme {GIRIS_YAPAN_YETKI} yetkisiyle giriş yapıldı.")
                    login.destroy()
            progress_artir()
        else:
            log_kaydet(f"BAŞARISIZ GİRİŞ DENEMESİ! Denenen Kullanıcı: {k_adi}")
            messagebox.showerror("Güvenlik İhlali", "Geçersiz kimlik bilgileri! Erişim reddedildi.")

    login = tk.Tk()
    login.title("Gastro-ERP Güvenlik Duvarı")
    login.geometry("400x500")
    login.config(bg="#0a0c12")
    login.resizable(False, False)

    tk.Label(login, text="ERP SİSTEMİNE GİRİŞ", font=("Consolas", 18, "bold"), bg="#0a0c12", fg="#00ffcc").pack(pady=(50, 30))

    tk.Label(login, text="KULLANICI ADI", font=("Consolas", 10), bg="#0a0c12", fg="#8a8d9e").pack(anchor="w", padx=55)
    entry_k_adi = tk.Entry(login, font=("Consolas", 12), bg="#1c1f2e", fg="#ffffff", insertbackground="#00ffcc", relief="flat")
    entry_k_adi.pack(fill="x", padx=55, pady=(5, 15), ipady=8)

    tk.Label(login, text="GÜVENLİK ŞİFRESİ", font=("Consolas", 10), bg="#0a0c12", fg="#8a8d9e").pack(anchor="w", padx=55)
    entry_sifre = tk.Entry(login, show="*", font=("Consolas", 12), bg="#1c1f2e", fg="#ffffff", insertbackground="#00ffcc", relief="flat")
    entry_sifre.pack(fill="x", padx=55, pady=(5, 25), ipady=8)

    btn_giris = tk.Button(login, text="ŞİFRELİ BAĞLANTIYI BAŞLAT", command=kimlik_dogrula, font=("Consolas", 11, "bold"), bg="#00ffcc", fg="#000000", relief="flat", cursor="hand2")
    btn_giris.pack(fill="x", padx=55, ipady=10)

    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Horizontal.TProgressbar", background="#00ffcc", troughcolor="#1c1f2e", bordercolor="#0a0c12")
    progress = ttk.Progressbar(login, orient="horizontal", length=290, mode="determinate", style="Horizontal.TProgressbar")
    progress.pack(pady=30)

    login.mainloop()

# ==========================================
# 2. MODÜL: ANA YAZILIM (DEV MİMARİ)
# ==========================================
def ana_programi_baslat():
    # --- TEMA VE RENKLER ---
    BG_MAIN = "#0f111a"
    BG_PANEL = "#1c1f2e"
    TEXT_FG = "#ffffff"
    TEXT_MUTED = "#8a8d9e"
    ACCENT = "#00ffcc"
    DANGER = "#ff3366"
    
    app = tk.Tk()
    app.title(f"GASTRO-ERP ENTERPRISE v4.0 | Oturum: {GIRIS_YAPAN_KULLANICI} ({GIRIS_YAPAN_YETKI})")
    app.geometry("1200x750")
    app.config(bg=BG_MAIN)
    
    # Sekme (Tab) Stilleri
    style = ttk.Style()
    style.theme_create("erp_theme", parent="alt", settings={
        "TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0], "background": BG_MAIN}},
        "TNotebook.Tab": {
            "configure": {"padding": [15, 10], "background": BG_PANEL, "foreground": TEXT_FG, "font": ("Consolas", 10, "bold")},
            "map": {"background": [("selected", ACCENT)], "foreground": [("selected", "#000000")]}
        }
    })
    style.theme_use("erp_theme")

    # Üst Menü / Kontrol Paneli
    ust_frame = tk.Frame(app, bg=BG_MAIN)
    ust_frame.pack(fill="x", padx=20, pady=10)
    tk.Label(ust_frame, text="KURUMSAL YÖNETİM PANELİ", font=("Consolas", 20, "bold"), bg=BG_MAIN, fg=ACCENT).pack(side="left")
    
    # Raporlama Butonu (CSV Çıktı)
    def rapor_al():
        try:
            baglanti = sqlite3.connect("gastro_erp_v4.db")
            cursor = baglanti.cursor()
            cursor.execute("SELECT * FROM tarifler")
            veriler = cursor.fetchall()
            
            dosya_adi = f"Sistem_Raporu_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
            masaustu = os.path.join(os.path.expanduser("~"), "Desktop", dosya_adi)
            
            with open(masaustu, mode='w', newline='', encoding='utf-8-sig') as dosya:
                yazici = csv.writer(dosya)
                yazici.writerow(["ID", "Tarif Adı", "Kategori", "Zorluk", "Süre (dk)", "Kalori", "Malzemeler", "Yapılışı"])
                yazici.writerows(veriler)
            
            log_kaydet("Sistem Veritabanı Excel/CSV formatında dışarı aktarıldı.")
            messagebox.showinfo("Rapor Başarılı", f"Veriler başarıyla masaüstüne kaydedildi!\nDosya: {dosya_adi}")
        except Exception as e:
            messagebox.showerror("Hata", f"Rapor alınamadı: {str(e)}")
            
    tk.Button(ust_frame, text="📊 EXCEL RAPORU AL", command=rapor_al, font=("Consolas", 10, "bold"), bg="#ffb86c", fg="#000000", relief="flat", cursor="hand2").pack(side="right", ipady=5, ipadx=10)

    notebook = ttk.Notebook(app)
    notebook.pack(fill="both", expand=True, padx=20, pady=10)

    # ================= SEKMELERİN OLUŞTURULMASI =================
    tab_dashboard = tk.Frame(notebook, bg=BG_MAIN)
    tab_tarifler = tk.Frame(notebook, bg=BG_MAIN)
    tab_detaylar = tk.Frame(notebook, bg=BG_MAIN)
    tab_kullanicilar = tk.Frame(notebook, bg=BG_MAIN)
    tab_loglar = tk.Frame(notebook, bg=BG_MAIN)

    notebook.add(tab_dashboard, text="🖥️ DASHBOARD (ANALİZ)")
    notebook.add(tab_tarifler, text="📋 TARİF YÖNETİMİ")
    notebook.add(tab_detaylar, text="📝 REÇETE EKLEME MERKEZİ")
    if GIRIS_YAPAN_YETKI == "Admin":
        notebook.add(tab_kullanicilar, text="👥 KULLANICI YÖNETİMİ")
    notebook.add(tab_loglar, text="🕵️ SİSTEM LOGLARI")

    # ---------------------------------------------------------
    # SEKME 1: DASHBOARD & MATEMATİKSEL GRAFİK (ŞOV KISMI)
    # ---------------------------------------------------------
    def grafik_ciz():
        # Verileri topla
        baglanti = sqlite3.connect("gastro_erp_v4.db")
        cursor = baglanti.cursor()
        cursor.execute("SELECT kategori, COUNT(*) FROM tarifler GROUP BY kategori")
        veriler = cursor.fetchall()
        
        cursor.execute("SELECT count(*) FROM tarifler")
        toplam_tarif = cursor.fetchone()[0]
        
        cursor.execute("SELECT count(*) FROM kullanicilar")
        toplam_kullanici = cursor.fetchone()[0]
        baglanti.close()

        # Üst İstatistikler
        stat_frame = tk.Frame(tab_dashboard, bg=BG_MAIN)
        stat_frame.pack(fill="x", pady=20)
        
        tk.Label(stat_frame, text=f"TOPLAM TARİF: {toplam_tarif}", font=("Consolas", 16, "bold"), bg=BG_PANEL, fg=ACCENT, padx=20, pady=10).pack(side="left", padx=20)
        tk.Label(stat_frame, text=f"AKTİF KULLANICI: {toplam_kullanici}", font=("Consolas", 16, "bold"), bg=BG_PANEL, fg="#ffb86c", padx=20, pady=10).pack(side="left", padx=20)
        tk.Label(stat_frame, text=f"SİSTEM DURUMU: OPTİMAL", font=("Consolas", 16, "bold"), bg=BG_PANEL, fg="#00ffcc", padx=20, pady=10).pack(side="left", padx=20)

        # Matematiksel Sütun Grafiği (Canvas ile Algoritma)
        tk.Label(tab_dashboard, text="KATEGORİ DAĞILIM GRAFİĞİ (CANVAS RENDER)", font=("Consolas", 12, "bold"), bg=BG_MAIN, fg=TEXT_MUTED).pack(pady=(20, 5))
        
        canvas_w, canvas_h = 800, 350
        canvas = tk.Canvas(tab_dashboard, width=canvas_w, height=canvas_h, bg=BG_PANEL, highlightthickness=0)
        canvas.pack(pady=10)
        
        if not veriler:
            canvas.create_text(canvas_w/2, canvas_h/2, text="HENÜZ YETERLİ VERİ YOK", fill=TEXT_MUTED, font=("Consolas", 14))
            return

        max_deger = max(v[1] for v in veriler) if veriler else 1
        bar_genislik = 80
        bosluk = 60
        baslangic_x = (canvas_w - (len(veriler) * bar_genislik + (len(veriler) - 1) * bosluk)) / 2

        for i, (kategori, sayi) in enumerate(veriler):
            bar_h = (sayi / max_deger) * (canvas_h - 100)
            x0 = baslangic_x + i * (bar_genislik + bosluk)
            y0 = canvas_h - 40
            x1 = x0 + bar_genislik
            y1 = y0 - bar_h
            
            # Sütunu Çiz
            canvas.create_rectangle(x0, y0, x1, y1, fill=ACCENT, outline="")
            # Sayıyı Yaz
            canvas.create_text(x0 + bar_genislik/2, y1 - 15, text=str(sayi), fill=TEXT_FG, font=("Consolas", 12, "bold"))
            # Kategoriyi Yaz
            canvas.create_text(x0 + bar_genislik/2, y0 + 15, text=kategori, fill=TEXT_MUTED, font=("Consolas", 10))

    grafik_ciz() # Dashboard'u renderla

    # ---------------------------------------------------------
    # SEKME 2: TARİF YÖNETİMİ (TREEVIEW VE ARAMA)
    # ---------------------------------------------------------
    # Arama Barı
    arama_frame = tk.Frame(tab_tarifler, bg=BG_MAIN)
    arama_frame.pack(fill="x", pady=10)
    tk.Label(arama_frame, text="Sistemde Ara (Canlı):", font=("Consolas", 11), bg=BG_MAIN, fg=TEXT_FG).pack(side="left")
    entry_arama = tk.Entry(arama_frame, font=("Consolas", 11), bg=BG_PANEL, fg=TEXT_FG, relief="flat", width=30)
    entry_arama.pack(side="left", padx=10, ipady=4)
    
    # Treeview (Excel Tablosu) Ayarları
    style.configure("Treeview", background=BG_PANEL, foreground=TEXT_FG, fieldbackground=BG_PANEL, rowheight=30, borderwidth=0)
    style.configure("Treeview.Heading", background="#151722", foreground=ACCENT, font=("Consolas", 10, "bold"), relief="flat")
    
    tablo_frame = tk.Frame(tab_tarifler, bg=BG_MAIN)
    tablo_frame.pack(fill="both", expand=True)
    
    scroll_y = tk.Scrollbar(tablo_frame)
    scroll_y.pack(side="right", fill="y")
    
    sutunlar = ("ID", "Ad", "Kategori", "Zorluk", "Süre", "Kalori")
    tablo = ttk.Treeview(tablo_frame, columns=sutunlar, show="headings", yscrollcommand=scroll_y.set)
    
    tablo.heading("ID", text="KOD"); tablo.column("ID", width=60, anchor="center")
    tablo.heading("Ad", text="YEMEK ADI"); tablo.column("Ad", width=250)
    tablo.heading("Kategori", text="KATEGORİ"); tablo.column("Kategori", width=150)
    tablo.heading("Zorluk", text="ZORLUK SEVİYESİ"); tablo.column("Zorluk", width=120, anchor="center")
    tablo.heading("Süre", text="SÜRE (Dk)"); tablo.column("Süre", width=100, anchor="center")
    tablo.heading("Kalori", text="KALORİ (Kcal)"); tablo.column("Kalori", width=100, anchor="center")
    tablo.pack(fill="both", expand=True)
    scroll_y.config(command=tablo.yview)

    def tablo_doldur(kelime=""):
        for row in tablo.get_children(): tablo.delete(row)
        baglanti = sqlite3.connect("gastro_erp_v4.db")
        cursor = baglanti.cursor()
        if kelime == "":
            cursor.execute("SELECT id, ad, kategori, zorluk, sure, kalori FROM tarifler")
        else:
            cursor.execute("SELECT id, ad, kategori, zorluk, sure, kalori FROM tarifler WHERE ad LIKE ?", ('%' + kelime + '%',))
        for k in cursor.fetchall():
            tablo.insert("", tk.END, values=k)
        baglanti.close()

    entry_arama.bind("<KeyRelease>", lambda e: tablo_doldur(entry_arama.get()))
    
    def tarif_sil():
        secili = tablo.focus()
        if not secili: return
        t_id = tablo.item(secili, 'values')[0]
        t_ad = tablo.item(secili, 'values')[1]
        
        cevap = messagebox.askyesno("Onay", f"{t_id} kodlu '{t_ad}' sistemden tamamen silinecek. Emin misiniz?")
        if cevap:
            baglanti = sqlite3.connect("gastro_erp_v4.db")
            cursor = baglanti.cursor()
            cursor.execute("DELETE FROM tarifler WHERE id=?", (t_id,))
            baglanti.commit()
            baglanti.close()
            log_kaydet(f"TARİF SİLİNDİ: {t_ad} (ID: {t_id})")
            tablo_doldur()
            dashboard_guncelle()

    tk.Button(tab_tarifler, text="🚫 SEÇİLİ KAYDI SİL", command=tarif_sil, font=("Consolas", 11, "bold"), bg=DANGER, fg=TEXT_FG, relief="flat", cursor="hand2").pack(pady=10, ipady=5, ipadx=10)

    # ---------------------------------------------------------
    # SEKME 3: REÇETE EKLEME (DETAYLI FORM)
    # ---------------------------------------------------------
    form_frame = tk.Frame(tab_detaylar, bg=BG_MAIN)
    form_frame.pack(fill="both", expand=True, pady=20)
    
    # Sol Form Alanı (Temel Bilgiler)
    sol_f = tk.Frame(form_frame, bg=BG_MAIN, width=400)
    sol_f.pack(side="left", fill="y", padx=20)
    
    alanlar = [("TARİF KODU (ID)", "e_id"), ("YEMEK ADI", "e_ad"), ("KATEGORİ", "c_kat"), 
               ("ZORLUK DERECESİ", "c_zorluk"), ("SÜRE (Dk)", "e_sure"), ("KALORİ (Kcal)", "e_kalori")]
    
    e_id = tk.Entry(sol_f, font=("Consolas", 11), bg=BG_PANEL, fg=TEXT_FG, relief="flat")
    e_ad = tk.Entry(sol_f, font=("Consolas", 11), bg=BG_PANEL, fg=TEXT_FG, relief="flat")
    c_kat = ttk.Combobox(sol_f, values=["Kahvaltılık", "Ana Yemek", "Tatlı", "Çorba", "İçecek"], state="readonly")
    c_zorluk = ttk.Combobox(sol_f, values=["Çok Kolay", "Kolay", "Orta", "Zor", "Profesyonel"], state="readonly")
    e_sure = tk.Entry(sol_f, font=("Consolas", 11), bg=BG_PANEL, fg=TEXT_FG, relief="flat")
    e_kalori = tk.Entry(sol_f, font=("Consolas", 11), bg=BG_PANEL, fg=TEXT_FG, relief="flat")
    
    for lbl, widget in alanlar:
        tk.Label(sol_f, text=lbl, font=("Consolas", 10, "bold"), bg=BG_MAIN, fg=TEXT_MUTED).pack(anchor="w", pady=(10, 2))
        w = eval(widget)
        if isinstance(w, ttk.Combobox): w.set("Seçiniz...")
        w.pack(fill="x", ipady=5)

    # Sağ Form Alanı (Uzun Metinler)
    sag_f = tk.Frame(form_frame, bg=BG_MAIN)
    sag_f.pack(side="right", fill="both", expand=True, padx=20)
    
    tk.Label(sag_f, text="MALZEMELER (Her satıra bir tane):", font=("Consolas", 10, "bold"), bg=BG_MAIN, fg=TEXT_MUTED).pack(anchor="w", pady=(10,2))
    text_malzeme = tk.Text(sag_f, height=6, font=("Consolas", 10), bg=BG_PANEL, fg=TEXT_FG, relief="flat")
    text_malzeme.pack(fill="x")
    
    tk.Label(sag_f, text="HAZIRLANIŞ ADIMLARI (Adım adım yazın):", font=("Consolas", 10, "bold"), bg=BG_MAIN, fg=TEXT_MUTED).pack(anchor="w", pady=(10,2))
    text_yapilis = tk.Text(sag_f, height=8, font=("Consolas", 10), bg=BG_PANEL, fg=TEXT_FG, relief="flat")
    text_yapilis.pack(fill="both", expand=True)

    def detayli_kayit_yap():
        t_id, t_ad, t_kat, t_zorluk = e_id.get(), e_ad.get(), c_kat.get(), c_zorluk.get()
        t_sure, t_kalori = e_sure.get(), e_kalori.get()
        t_malz = text_malzeme.get("1.0", tk.END).strip()
        t_yapilis = text_yapilis.get("1.0", tk.END).strip()
        
        # Validation (Kusursuz Hata Yakalama)
        if not (t_id and t_ad and t_sure and t_kalori and t_malz and t_yapilis) or t_kat == "Seçiniz...":
            messagebox.showwarning("Eksik Veri", "Lütfen tüm veri alanlarını doldurun!")
            return
        if not (t_id.isdigit() and t_sure.isdigit() and t_kalori.isdigit()):
            messagebox.showerror("Tip Hatası", "ID, Süre ve Kalori kısımlarına HARF YAZILAMAZ!")
            return
        if any(char.isdigit() for char in t_ad):
            messagebox.showerror("Tip Hatası", "Yemek adında rakam bulunamaz!")
            return
            
        try:
            baglanti = sqlite3.connect("gastro_erp_v4.db")
            cursor = baglanti.cursor()
            cursor.execute("INSERT INTO tarifler VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                           (t_id, t_ad, t_kat, t_zorluk, t_sure, t_kalori, t_malz, t_yapilis))
            baglanti.commit()
            baglanti.close()
            
            log_kaydet(f"YENİ TARİF EKLENDİ: {t_ad} (Kategori: {t_kat})")
            messagebox.showinfo("Sistem", "Kayıt Başarıyla Veritabanına İşlendi.")
            
            # Formu Temizle
            for e in [e_id, e_ad, e_sure, e_kalori]: e.delete(0, tk.END)
            text_malzeme.delete("1.0", tk.END); text_yapilis.delete("1.0", tk.END)
            c_kat.set("Seçiniz..."); c_zorluk.set("Seçiniz...")
            
            tablo_doldur()
            dashboard_guncelle()
            notebook.select(tab_tarifler) # Ekleme bitince listeye geri at
        except sqlite3.IntegrityError:
            messagebox.showerror("Kritik Hata", "Bu ID sistemde zaten mevcut!")

    tk.Button(tab_detaylar, text="💾 VERİTABANINA ŞİFRELEYEREK KAYDET", command=detayli_kayit_yap, font=("Consolas", 12, "bold"), bg=ACCENT, fg="#000000", relief="flat", cursor="hand2").pack(fill="x", padx=20, pady=15, ipady=10)

    # ---------------------------------------------------------
    # SEKME 4: SİSTEM LOGLARI (İZ SÜRME)
    # ---------------------------------------------------------
    log_scroll = tk.Scrollbar(tab_loglar)
    log_scroll.pack(side="right", fill="y")
    
    tablo_log = ttk.Treeview(tab_loglar, columns=("ID", "Tarih", "Kullanici", "İslem"), show="headings", yscrollcommand=log_scroll.set)
    tablo_log.heading("ID", text="LOG NO"); tablo_log.column("ID", width=50, anchor="center")
    tablo_log.heading("Tarih", text="ZAMAN DAMGASI"); tablo_log.column("Tarih", width=150, anchor="center")
    tablo_log.heading("Kullanici", text="KULLANICI"); tablo_log.column("Kullanici", width=100, anchor="center")
    tablo_log.heading("İslem", text="YAPILAN İŞLEM DETAYI"); tablo_log.column("İslem", width=600)
    tablo_log.pack(fill="both", expand=True, padx=10, pady=10)
    log_scroll.config(command=tablo_log.yview)
    
    def loglari_getir():
        for row in tablo_log.get_children(): tablo_log.delete(row)
        baglanti = sqlite3.connect("gastro_erp_v4.db")
        cursor = baglanti.cursor()
        cursor.execute("SELECT * FROM loglar ORDER BY log_id DESC")
        for k in cursor.fetchall():
            tablo_log.insert("", tk.END, values=k)
        baglanti.close()

    # ---------------------------------------------------------
    # GÜNCELLEME TETİKLEYİCİLERİ VE ALT ÇUBUK
    # ---------------------------------------------------------
    def dashboard_guncelle():
        # Sekme değiştiğinde her şeyi tazele
        for widget in tab_dashboard.winfo_children(): widget.destroy()
        grafik_ciz()
        loglari_getir()

    notebook.bind("<<NotebookTabChanged>>", lambda e: dashboard_guncelle())
    
    durum_cubugu = tk.Frame(app, bg="#0a0c12")
    durum_cubugu.pack(fill="x", side="bottom")
    tk.Label(durum_cubugu, text=f"Sistem Durumu: ÇEVRİMİÇİ  |  Aktif Modül: YKALEATHER Yazılım Altyapısı", font=("Consolas", 9), bg="#0a0c12", fg=TEXT_MUTED).pack(side="left", padx=20, pady=5)
    tk.Label(durum_cubugu, text=f"Tarih: {datetime.now().strftime('%d.%m.%Y')}", font=("Consolas", 9), bg="#0a0c12", fg=TEXT_MUTED).pack(side="right", padx=20, pady=5)

    tablo_doldur()
    loglari_getir()
    app.mainloop()

# ==========================================
# MOTORU ÇALIŞTIRMA (BOOT SEQUENCE)
# ==========================================
if __name__ == "__main__":
    sistem_veritabanini_kur() # Tabloları yarat
    giris_ekrani_baslat()     # Güvenlik duvarını aç
    
    if GIRIS_BASARILI:        # Kimlik doğrulandıysa ERP'yi aç
        ana_programi_baslat()