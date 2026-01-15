import pandas as pd
import os
from pathlib import Path

# Setup Path yang Dinamis (Biar gak error di beda folder)
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "dataset" / "FULL_HERO_DATA.csv"

def get_hero_data():
    """Membaca CSV dan mengembalikan DataFrame"""
    if not DATA_PATH.exists():
        print(f"❌ Error: File dataset tidak ditemukan di {DATA_PATH}")
        return None
    try:
        df = pd.read_csv(DATA_PATH)
        # Normalisasi nama kolom biar aman (strip spasi)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        print(f"❌ Error membaca CSV: {e}")
        return None

def get_hero_by_name(hero_name: str):
    """Mencari data hero spesifik berdasarkan nama"""
    df = get_hero_data()
    if df is None: return None

    # Bersihkan input user
    hero_name_clean = hero_name.strip().lower()
    
    # Cari yang namanya mirip (case insensitive)
    # Kita pakai str.contains biar 'Lance' bisa ketemu 'Lancelot'
    result = df[df['Hero'].str.lower() == hero_name_clean]
    
    # Kalau gak ketemu persis, coba contain
    if result.empty:
        result = df[df['Hero'].str.lower().str.contains(hero_name_clean, na=False)]

    if not result.empty:
        # Ambil baris pertama sebagai dictionary
        return result.iloc[0].to_dict()
    
    return None

# --- [BAGIAN BARU YANG KEMARIN KURANG] ---
def get_all_hero_names():
    """Mengembalikan list semua nama hero yang ada di CSV"""
    df = get_hero_data()
    if df is None: return []
    
    if 'Hero' in df.columns:
        return df['Hero'].tolist()
    return []