from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parent.parent / "dataset"

_HEROES = None
_ITEMS = None

def load_datasets():
    global _HEROES, _ITEMS
    if _HEROES is None:
        _HEROES = pd.read_csv(BASE / "mobile_legends_lane_roles.csv")
        _HEROES["Hero_norm"] = _HEROES["Hero"].str.lower()
    if _ITEMS is None:
        _ITEMS = pd.read_csv(BASE / "mlbb_items_dataset_enriched.csv")
        _ITEMS["Item_norm"] = _ITEMS["Item"].str.lower()
    return _HEROES, _ITEMS

def get_all_hero_names() -> list[str]:
    h, _ = load_datasets()
    return h["Hero"].tolist()

def get_hero_by_name(name: str) -> dict | None:
    if not name: return None
    h, _ = load_datasets()
    row = h[h["Hero_norm"] == name.lower()]
    if row.empty:
        alt = h[h["Hero"].str.lower().str.contains(name.lower())]
        if alt.empty: return None
        row = alt.iloc[[0]]
    return row.iloc[0].to_dict()

def list_heroes_by_role(role: str) -> list[str]:
    h, _ = load_datasets()
    role = (role or "").lower()
    mask = h.apply(lambda r: any(role in str(r[c]).lower() for c in ["Role_Lane_1","Role_Lane_2","Role_Lane_3"]), axis=1)
    return h.loc[mask, "Hero"].tolist()

def list_heroes_by_lane(lane: str) -> list[str]:
    return list_heroes_by_role(lane)
