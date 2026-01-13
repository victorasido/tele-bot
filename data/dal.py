from pathlib import Path
import pandas as pd

# Lokasi folder dataset
BASE = Path(__file__).resolve().parent.parent / "dataset"

_HEROES = None

def load_datasets():
    global _HEROES
    
    # --- UPDATE: BACA FULL_HERO_DATA.CSV ---
    if _HEROES is None:
        # Target file: dataset/FULL_HERO_DATA.csv
        hero_path = BASE / "FULL_HERO_DATA.csv" 
        
        if hero_path.exists():
            try:
                _HEROES = pd.read_csv(hero_path)
                
                # Normalisasi nama hero
                if "Hero" in _HEROES.columns:
                    _HEROES["Hero_norm"] = _HEROES["Hero"].astype(str).str.lower().str.strip()
                    print(f"[INFO] Berhasil memuat {_HEROES.shape[0]} hero dari FULL_HERO_DATA.csv")
                else:
                    print("[ERROR] Kolom 'Hero' tidak ditemukan di CSV!")
                    _HEROES = pd.DataFrame()
            except Exception as e:
                print(f"[ERROR] Gagal membaca CSV: {e}")
                _HEROES = pd.DataFrame()
        else:
            print(f"[WARNING] File tidak ditemukan: {hero_path}")
            # Fallback cek folder datamine (jaga-jaga)
            alt_path = BASE.parent / "datamine" / "FULL_HERO_DATA.csv"
            if alt_path.exists():
                print(f"[INFO] Mencoba baca dari folder datamine...")
                try:
                    _HEROES = pd.read_csv(alt_path)
                    _HEROES["Hero_norm"] = _HEROES["Hero"].astype(str).str.lower().str.strip()
                    print(f"[INFO] Berhasil memuat dari datamine.")
                except:
                    _HEROES = pd.DataFrame()
            else:
                _HEROES = pd.DataFrame()

    return _HEROES, None

# --- FUNGSI GETTER ---
def get_all_hero_names() -> list[str]:
    h, _ = load_datasets()
    if h is None or h.empty or "Hero" not in h.columns:
        return []
    return h["Hero"].dropna().tolist()

def get_hero_by_name(name: str) -> dict | None:
    if not name: return None
    h, _ = load_datasets()
    if h is None or h.empty: return None
    
    name_lower = name.lower().strip()
    row = h[h["Hero_norm"] == name_lower]
    
    if row.empty:
        mask = h["Hero_norm"].str.contains(name_lower, na=False)
        row = h[mask]
    
    if row.empty: return None
    return row.iloc[0].fillna("").to_dict()

def list_heroes_by_role(role: str) -> list[str]:
    h, _ = load_datasets()
    if h is None or h.empty or "Role" not in h.columns: return []
    mask = h["Role"].astype(str).str.lower().str.contains(role.lower().strip(), na=False)
    return h.loc[mask, "Hero"].tolist()

def list_heroes_by_lane(lane: str) -> list[str]:
    h, _ = load_datasets()
    if h is None or h.empty: return []
    l_low = lane.lower().strip()
    mask = pd.Series([False]*len(h))
    if "PrimaryLane" in h.columns: mask |= h["PrimaryLane"].astype(str).str.lower().str.contains(l_low, na=False)
    if "SecondaryLane" in h.columns: mask |= h["SecondaryLane"].astype(str).str.lower().str.contains(l_low, na=False)
    return h.loc[mask, "Hero"].tolist()