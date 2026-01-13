from pathlib import Path
import pandas as pd

# Menentukan lokasi folder dataset
BASE = Path(__file__).resolve().parent.parent / "dataset"

_HEROES = None
_ITEMS = None

def load_datasets():
    global _HEROES, _ITEMS
    
    # --- LOAD DATA HERO (DIPERBAIKI) ---
    if _HEROES is None:
        hero_path = BASE / "HeroData.csv"
        
        if hero_path.exists():
            try:
                # Membaca HeroData.csv
                _HEROES = pd.read_csv(hero_path)
                
                # Normalisasi nama hero untuk pencarian (case-insensitive)
                if "Hero" in _HEROES.columns:
                    _HEROES["Hero_norm"] = _HEROES["Hero"].astype(str).str.lower().str.strip()
                    print(f"[INFO] Berhasil memuat {_HEROES.shape[0]} hero dari HeroData.csv")
                else:
                    print("[ERROR] Kolom 'Hero' tidak ditemukan di HeroData.csv!")
                    _HEROES = pd.DataFrame()
            except Exception as e:
                print(f"[ERROR] Gagal membaca HeroData.csv: {e}")
                _HEROES = pd.DataFrame()
        else:
            print(f"[WARNING] File dataset tidak ditemukan: {hero_path}")
            _HEROES = pd.DataFrame()

    # --- LOAD DATA ITEM (OPSIONAL / PELENGKAP) ---
    if _ITEMS is None:
        item_path = BASE / "mlbb_items_dataset_enriched.csv"
        if item_path.exists():
            try:
                _ITEMS = pd.read_csv(item_path)
                if "Item" in _ITEMS.columns:
                    _ITEMS["Item_norm"] = _ITEMS["Item"].astype(str).str.lower().str.strip()
                print("[INFO] Berhasil memuat dataset item.")
            except Exception as e:
                print(f"[WARNING] Gagal membaca dataset item: {e}")
                _ITEMS = pd.DataFrame()
        else:
            print("[WARNING] File mlbb_items_dataset_enriched.csv tidak ditemukan. (Fitur detail item mungkin terbatas)")
            _ITEMS = pd.DataFrame(columns=["Item", "Item_norm"])

    return _HEROES, _ITEMS

def get_all_hero_names() -> list[str]:
    """Mengembalikan list semua nama hero yang tersedia."""
    h, _ = load_datasets()
    if h.empty or "Hero" not in h.columns:
        return []
    return h["Hero"].dropna().tolist()

def get_hero_by_name(name: str) -> dict | None:
    """Mencari data hero berdasarkan nama (exact atau partial match)."""
    if not name: return None
    h, _ = load_datasets()
    
    if h.empty: return None
    
    name_lower = name.lower().strip()
    
    # 1. Cari Exact Match di kolom Hero_norm
    row = h[h["Hero_norm"] == name_lower]
    
    # 2. Jika tidak ada, cari Partial Match (misal: "leo" -> "Leomord")
    if row.empty:
        # Filter yang mengandung string input
        mask = h["Hero_norm"].str.contains(name_lower, na=False)
        row = h[mask]
    
    if row.empty:
        return None
    
    # Ambil hasil pertama dan ubah ke dictionary
    # fillna("") agar data kosong tidak jadi NaN (memudahkan pemrosesan string nanti)
    return row.iloc[0].fillna("").to_dict()

def list_heroes_by_role(role: str) -> list[str]:
    """Mengembalikan list nama hero berdasarkan Role."""
    h, _ = load_datasets()
    if h.empty or "Role" not in h.columns:
        return []
    
    role_lower = role.lower().strip()
    # Cari hero yang kolom Role-nya mengandung kata kunci input
    mask = h["Role"].astype(str).str.lower().str.contains(role_lower, na=False)
    return h.loc[mask, "Hero"].tolist()

def list_heroes_by_lane(lane: str) -> list[str]:
    """Mengembalikan list nama hero berdasarkan Primary atau Secondary Lane."""
    h, _ = load_datasets()
    if h.empty: return []
    
    lane_lower = lane.lower().strip()
    
    # Cek di PrimaryLane ATAU SecondaryLane
    # Pastikan kolom ada sebelum dicek
    mask1 = pd.Series([False] * len(h))
    mask2 = pd.Series([False] * len(h))

    if "PrimaryLane" in h.columns:
        mask1 = h["PrimaryLane"].astype(str).str.lower().str.contains(lane_lower, na=False)
    
    if "SecondaryLane" in h.columns:
        mask2 = h["SecondaryLane"].astype(str).str.lower().str.contains(lane_lower, na=False)
        
    return h.loc[mask1 | mask2, "Hero"].tolist()