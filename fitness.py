"""
=============================================================================
GYMLAND FITNESS & NUTRITION ERP v1.0 (ENTERPRISE)
Geliştirici: Yasir Karabacak (yasirsalvo)
Modüller: Üye Takibi, Vücut Analizi, Antrenman & Beslenme, Kasa/Raporlama
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
# GLOBAL DEĞİŞKENLER
# ==========================================
GIRIS_YAPAN_KULLANICI = ""
GIRIS_BASARILI = False

# ==========================================
# VERİTABANI MOTORU (GYMLAND ALTYAPISI)
# ==========================================
def gymland_veritabanini_kur():
    baglanti = sqlite3.connect("gymland_sistem.db")
    cursor = baglanti.cursor()
    
    # 1. PERSONEL/YÖNETİCİ TABLOSU
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS yoneticiler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            k_adi TEXT UNIQUE,
            sifre TEXT
        )
    """)
    cursor.execute("SELECT count(*) FROM yoneticiler")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO yoneticiler (k_adi, sifre) VALUES (?, ?)", ("yasirsalvo", "213623640"))
    
    # 2. ÜYELER VE VÜCUT ANALİZİ TABLOSU
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS uyeler (
            uye_id TEXT PRIMARY KEY,
            ad_soyad TEXT,
            hedef TEXT,
            kilo TEXT,
            yag_orani TEXT,
            uyelik_tipi TEXT,
            beslenme_kuru TEXT,
            antrenman_prog TEXT
        )
    """)
    
    # Default Fitness Verileri 
    cursor.execute("SELECT count(*) FROM uyeler")
    if cursor.fetchone()[0] == 0:
        ornekler = [
            ("1001", "Demirkan Yılmaz", "Düşük Yağ (Definasyon)", "78", "12", "VIP", "Yüksek Protein (Tavuk Göğsü, Yumurta), Omega 3, Multivitamin", "Push-Pull-Legs (Ağır)"),
            ("1002", "Burak Kaya", "Kas Kazanımı (Bulking)", "85", "16", "Standart", "Yüksek Karbonhidrat, Kreatin, Whey Protein", "Full Body (Hacim)")
        ]
        cursor.executemany("INSERT INTO uyeler VALUES (?, ?, ?, ?, ?, ?, ?, ?)", ornekler)

    # 3. SİSTEM LOGLARI
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS loglar (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarih TEXT,
            islem TEXT
        )
    """)
    
    baglanti.commit()
    baglanti.close()

def log_kaydet(islem_metni):
    zaman = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    baglanti = sqlite3.connect("gymland_sistem.db")
    cursor = baglanti.cursor()
    cursor.execute("INSERT INTO loglar (tarih, islem) VALUES (?, ?)", (zaman, islem_metni))
    baglanti.commit()
    baglanti.close()

# ==========================================
# 1. MODÜL: GÜVENLİK (GYMLAND LOGIN)
# ==========================================
def giris_ekrani_baslat():
    def kimlik_dogrula():
        k_adi = entry_k_adi.get()
        sifre = entry_sifre.get()
        
        baglanti = sqlite3.connect("gymland_sistem.db")
        cursor = baglanti.cursor()
        cursor.execute("SELECT * FROM yoneticiler WHERE k_adi=? AND sifre=?", (k_adi, sifre))
        sonuc = cursor.fetchone()
        baglanti.close()
        
        if sonuc:
            global GIRIS_YAPAN_KULLANICI
            GIRIS_YAPAN_KULLANICI = k_adi
            
            btn_giris.config(state="disabled", text="GYMLAND SUNUCULARINA BAĞLANILIYOR...")
            def progress_artir(deger=0):
                if deger <= 100:
                    progress['value'] = deger
                    login.update_idletasks()
                    login.after(10, progress_artir, deger + 2)
                else:
                    global GIRIS_BASARILI
                    GIRIS_BASARILI = True
                    log_kaydet(f"Yönetici Girişi Yapıldı: {k_adi}")
                    login.destroy()
            progress_artir()
        else:
            log_kaydet(f"İzinsiz Erişim Denemesi: {k_adi}")
            messagebox.showerror("Güvenlik İhlali", "Hatalı Giriş! Sadece yetkili personeller girebilir.")

    login = tk.Tk()
    login.title("GymLand Protokolü")
    login.geometry("400x500")
    login.config(bg="#111111")
    login.resizable(False, False)

    tk.Label(login, text="GYMLAND YÖNETİM", font=("Consolas", 20, "bold"), bg="#111111", fg="#39ff14").pack(pady=(50, 10))
    tk.Label(login, text="PERSONEL GİRİŞİ", font=("Consolas", 12), bg="#111111", fg="#888888").pack(pady=(0, 30))

    tk.Label(login, text="YÖNETİCİ KİMLİĞİ", font=("Consolas", 10), bg="#111111", fg="#888888").pack(anchor="w", padx=55)
    entry_k_adi = tk.Entry(login, font=("Consolas", 12), bg="#222222", fg="#ffffff", insertbackground="#39ff14", relief="flat")
    entry_k_adi.pack(fill="x", padx=55, pady=(5, 15), ipady=8)

    tk.Label(login, text="GİZLİ ŞİFRE", font=("Consolas", 10), bg="#111111", fg="#888888").pack(anchor="w", padx=55)
    entry_sifre = tk.Entry(login, show="*", font=("Consolas", 12), bg="#222222", fg="#ffffff", insertbackground="#39ff14", relief="flat")
    entry_sifre.pack(fill="x", padx=55, pady=(5, 25), ipady=8)

    btn_giris = tk.Button(login, text="SİSTEMİ BAŞLAT", command=kimlik_dogrula, font=("Consolas", 12, "bold"), bg="#39ff14", fg="#000000", relief="flat", cursor="hand2")
    btn_giris.pack(fill="x", padx=55, ipady=10)

    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Horizontal.TProgressbar", background="#39ff14", troughcolor="#222222", bordercolor="#111111")
    progress = ttk.Progressbar(login, orient="horizontal", length=290, mode="determinate", style="Horizontal.TProgressbar")
    progress.pack(pady=30)

    login.mainloop()

# ==========================================
# 2. MODÜL: GYMLAND ANA ERP YAZILIMI
# ==========================================
def ana_programi_baslat():
    BG_MAIN = "#121212"
    BG_PANEL = "#1e1e1e"
    TEXT_FG = "#e0e0e0"
    TEXT_MUTED = "#888888"
    ACCENT = "#39ff14" # Neon Yeşil
    ACCENT_ALT = "#ffaa00" # Turuncu (Uyarılar için)
    
    app = tk.Tk()
    app.title(f"GYMLAND ENTERPRISE v1.0 | Admin: {GIRIS_YAPAN_KULLANICI}")
    app.geometry("1250x780")
    app.config(bg=BG_MAIN)
    
    style = ttk.Style()
    style.theme_create("gym_theme", parent="alt", settings={
        "TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0], "background": BG_MAIN}},
        "TNotebook.Tab": {
            "configure": {"padding": [15, 10], "background": BG_PANEL, "foreground": TEXT_FG, "font": ("Consolas", 11, "bold")},
            "map": {"background": [("selected", ACCENT)], "foreground": [("selected", "#000000")]}
        }
    })
    style.theme_use("gym_theme")

    ust_frame = tk.Frame(app, bg=BG_MAIN)
    ust_frame.pack(fill="x", padx=20, pady=10)
    tk.Label(ust_frame, text="GYMLAND MERKEZİ VERİTABANI", font=("Consolas", 22, "bold"), bg=BG_MAIN, fg=ACCENT).pack(side="left")
    
    def rapor_al():
        try:
            baglanti = sqlite3.connect("gymland_sistem.db")
            cursor = baglanti.cursor()
            cursor.execute("SELECT * FROM uyeler")
            veriler = cursor.fetchall()
            
            dosya_adi = f"GymLand_Uyeler_{datetime.now().strftime('%Y%m%d')}.csv"
            masaustu = os.path.join(os.path.expanduser("~"), "Desktop", dosya_adi)
            
            with open(masaustu, mode='w', newline='', encoding='utf-8-sig') as dosya:
                yazici = csv.writer(dosya)
                yazici.writerow(["Üye ID", "Ad Soyad", "Hedef", "Kilo (KG)", "Yağ Oranı (%)", "Üyelik Tipi", "Beslenme & Supplement", "Antrenman"])
                yazici.writerows(veriler)
            
            log_kaydet("GymLand Üye Veritabanı Excel'e Aktarıldı.")
            messagebox.showinfo("Rapor Başarılı", f"Rapor masaüstüne kaydedildi!\n{dosya_adi}")
        except Exception as e:
            messagebox.showerror("Hata", f"Rapor alınamadı: {str(e)}")
            
    tk.Button(ust_frame, text="⚡ EXCEL ÜYE RAPORU AL", command=rapor_al, font=("Consolas", 10, "bold"), bg=ACCENT_ALT, fg="#000000", relief="flat", cursor="hand2").pack(side="right", ipady=5, ipadx=10)

    notebook = ttk.Notebook(app)
    notebook.pack(fill="both", expand=True, padx=20, pady=10)

    tab_dashboard = tk.Frame(notebook, bg=BG_MAIN)
    tab_uyeler = tk.Frame(notebook, bg=BG_MAIN)
    tab_kayit = tk.Frame(notebook, bg=BG_MAIN)
    tab_loglar = tk.Frame(notebook, bg=BG_MAIN)

    notebook.add(tab_dashboard, text="📊 VÜCUT ANALİZ MERKEZİ")
    notebook.add(tab_uyeler, text="🏋️ AKTİF ÜYELER")
    notebook.add(tab_kayit, text="📝 YENİ ÜYE & KÜR KAYDI")
    notebook.add(tab_loglar, text="🛡️ GÜVENLİK LOGLARI")

    # ---------------------------------------------------------
    # SEKME 1: DASHBOARD (GYM İSTATİSTİKLERİ)
    # ---------------------------------------------------------
    def grafik_ciz():
        for widget in tab_dashboard.winfo_children(): widget.destroy()
        baglanti = sqlite3.connect("gymland_sistem.db")
        cursor = baglanti.cursor()
        
        cursor.execute("SELECT count(*) FROM uyeler")
        toplam_uye = cursor.fetchone()[0]
        
        cursor.execute("SELECT hedef, COUNT(*) FROM uyeler GROUP BY hedef")
        hedefler = cursor.fetchall()
        baglanti.close()

        stat_frame = tk.Frame(tab_dashboard, bg=BG_MAIN)
        stat_frame.pack(fill="x", pady=20)
        
        tk.Label(stat_frame, text=f"TOPLAM AKTİF ÜYE: {toplam_uye}", font=("Consolas", 16, "bold"), bg=BG_PANEL, fg=ACCENT, padx=20, pady=10).pack(side="left", padx=20)
        tk.Label(stat_frame, text="SİSTEM: HARDCORE MODU AKTİF", font=("Consolas", 16, "bold"), bg=BG_PANEL, fg=ACCENT_ALT, padx=20, pady=10).pack(side="left", padx=20)

        tk.Label(tab_dashboard, text="ÜYE HEDEFLERİ DAĞILIMI", font=("Consolas", 14, "bold"), bg=BG_MAIN, fg=TEXT_MUTED).pack(pady=(30, 10))
        
        canvas_w, canvas_h = 800, 400
        canvas = tk.Canvas(tab_dashboard, width=canvas_w, height=canvas_h, bg=BG_PANEL, highlightthickness=0)
        canvas.pack(pady=10)
        
        if not hedefler:
            canvas.create_text(canvas_w/2, canvas_h/2, text="VERİ TABANINDA ÜYE YOK", fill=TEXT_MUTED, font=("Consolas", 14))
            return

        max_deger = max(v[1] for v in hedefler) if hedefler else 1
        bar_genislik = 120
        bosluk = 80
        baslangic_x = (canvas_w - (len(hedefler) * bar_genislik + (len(hedefler) - 1) * bosluk)) / 2

        for i, (hedef, sayi) in enumerate(hedefler):
            bar_h = (sayi / max_deger) * (canvas_h - 120)
            x0 = baslangic_x + i * (bar_genislik + bosluk)
            y0 = canvas_h - 50
            x1 = x0 + bar_genislik
            y1 = y0 - bar_h
            
            canvas.create_rectangle(x0, y0, x1, y1, fill=ACCENT, outline="")
            canvas.create_text(x0 + bar_genislik/2, y1 - 20, text=str(sayi), fill=TEXT_FG, font=("Consolas", 14, "bold"))
            hedef_kisa = hedef.split("(")[0] if "(" in hedef else hedef
            canvas.create_text(x0 + bar_genislik/2, y0 + 20, text=hedef_kisa, fill=TEXT_MUTED, font=("Consolas", 10, "bold"))

    grafik_ciz()

    # ---------------------------------------------------------
    # SEKME 2: ÜYE YÖNETİMİ (TREEVIEW)
    # ---------------------------------------------------------
    arama_frame = tk.Frame(tab_uyeler, bg=BG_MAIN)
    arama_frame.pack(fill="x", pady=10)
    tk.Label(arama_frame, text="🔎 Üye Ara:", font=("Consolas", 12, "bold"), bg=BG_MAIN, fg=ACCENT).pack(side="left")
    entry_arama = tk.Entry(arama_frame, font=("Consolas", 12), bg=BG_PANEL, fg=TEXT_FG, relief="flat", width=35)
    entry_arama.pack(side="left", padx=10, ipady=5)
    
    style.configure("Treeview", background=BG_PANEL, foreground=TEXT_FG, fieldbackground=BG_PANEL, rowheight=35, borderwidth=0)
    style.configure("Treeview.Heading", background="#2a2a2a", foreground=ACCENT, font=("Consolas", 11, "bold"), relief="flat")
    
    tablo_frame = tk.Frame(tab_uyeler, bg=BG_MAIN)
    tablo_frame.pack(fill="both", expand=True)
    
    scroll_y = tk.Scrollbar(tablo_frame)
    scroll_y.pack(side="right", fill="y")
    
    sutunlar = ("ID", "Ad", "Hedef", "Kilo", "Yag", "Uyelik")
    tablo = ttk.Treeview(tablo_frame, columns=sutunlar, show="headings", yscrollcommand=scroll_y.set)
    
    tablo.heading("ID", text="ÜYE NO"); tablo.column("ID", width=80, anchor="center")
    tablo.heading("Ad", text="AD SOYAD"); tablo.column("Ad", width=200)
    tablo.heading("Hedef", text="HEDEF PROGRAMI"); tablo.column("Hedef", width=200)
    tablo.heading("Kilo", text="KİLO (KG)"); tablo.column("Kilo", width=100, anchor="center")
    tablo.heading("Yag", text="YAĞ ORANI (%)"); tablo.column("Yag", width=120, anchor="center")
    tablo.heading("Uyelik", text="ÜYELİK TİPİ"); tablo.column("Uyelik", width=150, anchor="center")
    tablo.pack(fill="both", expand=True)
    scroll_y.config(command=tablo.yview)

    def tablo_doldur(kelime=""):
        for row in tablo.get_children(): tablo.delete(row)
        baglanti = sqlite3.connect("gymland_sistem.db")
        cursor = baglanti.cursor()
        if kelime == "":
            cursor.execute("SELECT uye_id, ad_soyad, hedef, kilo, yag_orani, uyelik_tipi FROM uyeler")
        else:
            cursor.execute("SELECT uye_id, ad_soyad, hedef, kilo, yag_orani, uyelik_tipi FROM uyeler WHERE ad_soyad LIKE ?", ('%' + kelime + '%',))
        for k in cursor.fetchall():
            k_formatli = list(k)
            k_formatli[4] = f"%{k[4]}" # Yağ oranına % işareti ekle
            tablo.insert("", tk.END, values=k_formatli)
        baglanti.close()

    entry_arama.bind("<KeyRelease>", lambda e: tablo_doldur(entry_arama.get()))
    
    def uye_sil():
        secili = tablo.focus()
        if not secili: return
        t_id = tablo.item(secili, 'values')[0]
        t_ad = tablo.item(secili, 'values')[1]
        
        cevap = messagebox.askyesno("Kritik İşlem", f"{t_id} ID'li {t_ad} isimli üyenin kaydı SİLİNECEK. Onaylıyor musunuz?")
        if cevap:
            baglanti = sqlite3.connect("gymland_sistem.db")
            cursor = baglanti.cursor()
            cursor.execute("DELETE FROM uyeler WHERE uye_id=?", (t_id,))
            baglanti.commit()
            baglanti.close()
            log_kaydet(f"ÜYE SİLİNDİ: {t_ad} (ID: {t_id})")
            tablo_doldur()

    tk.Button(tab_uyeler, text="❌ SEÇİLİ ÜYEYİ SALONDAN SİL", command=uye_sil, font=("Consolas", 11, "bold"), bg="#ff3333", fg="#ffffff", relief="flat", cursor="hand2").pack(pady=10, ipady=6, ipadx=10)

    # ---------------------------------------------------------
    # SEKME 3: YENİ ÜYE & KÜR KAYDI (DETAYLI FORM)
    # ---------------------------------------------------------
    form_frame = tk.Frame(tab_kayit, bg=BG_MAIN)
    form_frame.pack(fill="both", expand=True, pady=10)
    
    sol_f = tk.Frame(form_frame, bg=BG_MAIN, width=400)
    sol_f.pack(side="left", fill="y", padx=20)
    
    alanlar = [("ÜYE KİMLİK NO", "e_id"), ("AD SOYAD", "e_ad"), ("FİTNESS HEDEFİ", "c_hedef"), 
               ("KİLO (KG)", "e_kilo"), ("VÜCUT YAĞ ORANI (%)", "e_yag"), ("ÜYELİK TİPİ", "c_uyelik")]
    
    e_id = tk.Entry(sol_f, font=("Consolas", 12), bg=BG_PANEL, fg=TEXT_FG, relief="flat")
    e_ad = tk.Entry(sol_f, font=("Consolas", 12), bg=BG_PANEL, fg=TEXT_FG, relief="flat")
    c_hedef = ttk.Combobox(sol_f, values=["Düşük Yağ (Definasyon)", "Kas Kazanımı (Bulking)", "Kilo Koruma (Maintenance)"], state="readonly")
    e_kilo = tk.Entry(sol_f, font=("Consolas", 12), bg=BG_PANEL, fg=TEXT_FG, relief="flat")
    e_yag = tk.Entry(sol_f, font=("Consolas", 12), bg=BG_PANEL, fg=TEXT_FG, relief="flat")
    c_uyelik = ttk.Combobox(sol_f, values=["Aylık Standart", "3 Aylık Gold", "6 Aylık VIP", "Yıllık Platinum"], state="readonly")
    
    for lbl, widget in alanlar:
        tk.Label(sol_f, text=lbl, font=("Consolas", 10, "bold"), bg=BG_MAIN, fg=TEXT_MUTED).pack(anchor="w", pady=(12, 3))
        w = eval(widget)
        if isinstance(w, ttk.Combobox): w.set("Seçiniz...")
        w.pack(fill="x", ipady=6)

    sag_f = tk.Frame(form_frame, bg=BG_MAIN)
    sag_f.pack(side="right", fill="both", expand=True, padx=20)
    
    tk.Label(sag_f, text="DİYET & SUPPLEMENT KÜRÜ (Detaylı):", font=("Consolas", 11, "bold"), bg=BG_MAIN, fg=ACCENT).pack(anchor="w", pady=(12,3))
    text_beslenme = tk.Text(sag_f, height=6, font=("Consolas", 11), bg=BG_PANEL, fg=TEXT_FG, relief="flat", insertbackground=ACCENT)
    text_beslenme.pack(fill="x")
    
    tk.Label(sag_f, text="ANTRENMAN DÖNGÜSÜ (Bölge & Setler):", font=("Consolas", 11, "bold"), bg=BG_MAIN, fg=ACCENT).pack(anchor="w", pady=(15,3))
    text_antrenman = tk.Text(sag_f, height=7, font=("Consolas", 11), bg=BG_PANEL, fg=TEXT_FG, relief="flat", insertbackground=ACCENT)
    text_antrenman.pack(fill="both", expand=True)

    def kayit_yap():
        t_id, t_ad, t_hedef = e_id.get(), e_ad.get(), c_hedef.get()
        t_kilo, t_yag, t_uyelik = e_kilo.get(), e_yag.get(), c_uyelik.get()
        t_beslenme = text_beslenme.get("1.0", tk.END).strip()
        t_antrenman = text_antrenman.get("1.0", tk.END).strip()
        
        if not (t_id and t_ad and t_kilo and t_yag and t_beslenme and t_antrenman) or t_hedef == "Seçiniz..." or t_uyelik == "Seçiniz...":
            messagebox.showwarning("Eksik Veri", "Sisteme eksik veri girilemez! Tüm alanları doldurun.")
            return
        if not (t_id.isdigit() and t_kilo.isdigit() and t_yag.isdigit()):
            messagebox.showerror("Tip Hatası", "ID, Kilo ve Yağ Oranı alanlarına SADECE RAKAM girilmelidir.")
            return
            
        try:
            baglanti = sqlite3.connect("gymland_sistem.db")
            cursor = baglanti.cursor()
            cursor.execute("INSERT INTO uyeler VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                           (t_id, t_ad, t_hedef, t_kilo, t_yag, t_uyelik, t_beslenme, t_antrenman))
            baglanti.commit()
            baglanti.close()
            
            log_kaydet(f"YENİ ÜYE KAYDI: {t_ad} ({t_hedef} Programı)")
            messagebox.showinfo("Başarılı", "Üye bilgileri GymLand veritabanına eklendi.")
            
            for e in [e_id, e_ad, e_kilo, e_yag]: e.delete(0, tk.END)
            text_beslenme.delete("1.0", tk.END); text_antrenman.delete("1.0", tk.END)
            c_hedef.set("Seçiniz..."); c_uyelik.set("Seçiniz...")
            
            tablo_doldur()
            notebook.select(tab_uyeler)
        except sqlite3.IntegrityError:
            messagebox.showerror("Kritik Hata", "Bu Üye Numarası (ID) sistemde zaten kullanımda!")

    tk.Button(tab_kayit, text="💾 ÜYEYİ VERİTABANINA ŞİFRELE VE KAYDET", command=kayit_yap, font=("Consolas", 14, "bold"), bg=ACCENT, fg="#000000", relief="flat", cursor="hand2").pack(fill="x", padx=20, pady=15, ipady=12)

    # ---------------------------------------------------------
    # SEKME 4: GÜVENLİK LOGLARI
    # ---------------------------------------------------------
    log_scroll = tk.Scrollbar(tab_loglar)
    log_scroll.pack(side="right", fill="y")
    
    tablo_log = ttk.Treeview(tab_loglar, columns=("ID", "Tarih", "İslem"), show="headings", yscrollcommand=log_scroll.set)
    tablo_log.heading("ID", text="SIRA"); tablo_log.column("ID", width=60, anchor="center")
    tablo_log.heading("Tarih", text="SİSTEM SAATİ"); tablo_log.column("Tarih", width=180, anchor="center")
    tablo_log.heading("İslem", text="YAPILAN İŞLEM DETAYI"); tablo_log.column("İslem", width=700)
    tablo_log.pack(fill="both", expand=True, padx=10, pady=10)
    log_scroll.config(command=tablo_log.yview)
    
    def loglari_getir():
        for row in tablo_log.get_children(): tablo_log.delete(row)
        baglanti = sqlite3.connect("gymland_sistem.db")
        cursor = baglanti.cursor()
        cursor.execute("SELECT * FROM loglar ORDER BY log_id DESC")
        for k in cursor.fetchall(): tablo_log.insert("", tk.END, values=k)
        baglanti.close()

    # ---------------------------------------------------------
    # GÜNCELLEME TETİKLEYİCİLERİ
    # ---------------------------------------------------------
    def sekme_degisti(event):
        secili_sekme = notebook.index(notebook.select())
        if secili_sekme == 0: grafik_ciz()
        elif secili_sekme == 3: loglari_getir()

    notebook.bind("<<NotebookTabChanged>>", sekme_degisti)
    
    durum_cubugu = tk.Frame(app, bg="#0a0a0a")
    durum_cubugu.pack(fill="x", side="bottom")
    tk.Label(durum_cubugu, text=f"GymLand Core v1.0 | Bağlantı: Şifreli", font=("Consolas", 9), bg="#0a0a0a", fg=TEXT_MUTED).pack(side="left", padx=20, pady=5)
    tk.Label(durum_cubugu, text=f"Son Senkronizasyon: {datetime.now().strftime('%d.%m.%Y %H:%M')}", font=("Consolas", 9), bg="#0a0a0a", fg=TEXT_MUTED).pack(side="right", padx=20, pady=5)

    tablo_doldur()
    loglari_getir()
    app.mainloop()

# ==========================================
# MOTORU ÇALIŞTIRMA (BOOT SEQUENCE)
# ==========================================
if __name__ == "__main__":
    gymland_veritabanini_kur()
    giris_ekrani_baslat()
    if GIRIS_BASARILI:
        ana_programi_baslat()