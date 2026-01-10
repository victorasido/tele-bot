from pathlib import Path
import pandas as pd

# Menentukan lokasi folder dataset
BASE = Path(__file__).resolve().parent.parent / "dataset"

_HEROES = None
_ITEMS = None

def load_datasets():
    global _HEROES, _ITEMS
    
    if _HEROES is None:
        # --- UPDATE BARU: BACA MULTIPLE CSV ---
        # Kita meload semua file build_meta2025_*.csv
        csv_files = [
            "build_meta2025_fighter.csv",
            "build_meta2025_mage.csv",
            "build_meta2025_marksman.csv",
            "build_meta2025_support.csv",
            "build_meta2025_tank.csv"
        ]
        
        dfs = []
        for file_name in csv_files:
            file_path = BASE / file_name
            # Cek apakah file ada biar gak error kalau ada satu yg kurang
            if file_path.exists():
                try:
                    df = pd.read_csv(file_path)
                    dfs.append(df)
                except Exception as e:
                    print(f"[WARNING] Gagal baca {file_name}: {e}")
            else:
                print(f"[WARNING] File tidak ditemukan: {file_name}")
        
        if dfs:
            # Gabungkan semua csv menjadi satu tabel besar
            _HEROES = pd.concat(dfs, ignore_index=True)
            
            # Normalisasi nama hero untuk pencarian
            # Pastikan kolom 'Hero' ada. Kalau di csv baru namanya beda, sesuaikan.
            if "Hero" in _HEROES.columns:
                _HEROES["Hero_norm"] = _HEROES["Hero"].str.lower()
            else:
                print("[ERROR] Kolom 'Hero' tidak ditemukan di CSV!")
        else:
            print("[ERROR] Tidak ada dataset hero yang berhasil di-load!")
            _HEROES = pd.DataFrame() # Return empty df biar gak crash
            
    if _ITEMS is None:
        # Load item dataset (pastikan file ini ada atau sesuaikan namanya)
        item_path = BASE / "mlbb_items_dataset_enriched.csv"
        if item_path.exists():
            _ITEMS = pd.read_csv(item_path)
            _ITEMS["Item_norm"] = _ITEMS["Item"].str.lower()
        else:
            # Fallback biar gak error kalau file item belum ada
            print("[WARNING] File item tidak ditemukan.")
            _ITEMS = pd.DataFrame(columns=["Item", "Item_norm"])

    return _HEROES, _ITEMS

def get_all_hero_names() -> list[str]:
    h, _ = load_datasets()
    if h.empty: return []
    return h["Hero"].tolist()

def get_hero_by_name(name: str) -> dict | None:
    if not name: return None
    h, _ = load_datasets()
    
    if h.empty: return None
    
    # Cari exact match
    row = h[h["Hero_norm"] == name.lower()]
    if row.empty:
        # Cari partial match (misal: "nana" ketemu di "Nana")
        alt = h[h["Hero"].str.lower().str.contains(name.lower())]
        if alt.empty: return None
        row = alt.iloc[[0]]
    
    return row.iloc[0].to_dict()

def list_heroes_by_role(role: str) -> list[str]:
    h, _ = load_datasets()
    if h.empty: return []
    
    role = (role or "").lower()
    # Sesuaikan kolom role di CSV baru kamu.
    # Di file lama kolomnya: Role_Lane_1, dll. 
    # Di file baru (build_meta2025) kolom utamanya adalah "Role"
    
    # Kita cek kolom 'Role' dulu
    if "Role" in h.columns:
        mask = h["Role"].str.lower().str.contains(role)
        return h.loc[mask, "Hero"].tolist()
    
    return []

def list_heroes_by_lane(lane: str) -> list[str]:
    h, _ = load_datasets()
    if h.empty: return []
    
    lane = (lane or "").lower()
    # Di file build_meta2025, kolom lane adalah "PrimaryLane" atau "SecondaryLane"
    mask = h.apply(lambda r: lane in str(r.get("PrimaryLane", "")).lower() or lane in str(r.get("SecondaryLane", "")).lower(), axis=1)
    return h.loc[mask, "Hero"].tolist()