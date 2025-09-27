"""
Business rules sederhana untuk:
- Validasi lane (lane_warning)
- Build default (make_default_build)
- Penyesuaian build vs komposisi musuh (adjust_by_enemy_mix)
- Heuristik counter hero (infer_counters_for_hero)
"""

from typing import List, Dict, Optional


def lane_warning(hero_row: Dict, lane_input: Optional[str]) -> Optional[str]:
    """
    Beri peringatan jika lane input user tidak cocok dengan lane di dataset.
    """
    if not lane_input:
        return None

    lanes = [
        str(hero_row.get("Role_Lane_1") or ""),
        str(hero_row.get("Role_Lane_2") or ""),
        str(hero_row.get("Role_Lane_3") or ""),
    ]
    lanes = [l for l in lanes if l and l.lower() != "nan"]

    ok = any(lane_input.lower() in l.lower() for l in lanes)
    if not ok and lanes:
        return f'⚠️ Lane "{lane_input}" kurang cocok untuk {hero_row.get("Hero", "Hero")}. Disarankan: {", ".join(lanes)}.'
    return None


def make_default_build(hero_row: Dict, lane: Optional[str]) -> List[str]:
    """
    Build dasar berdasarkan role/lane dari dataset.
    Sederhana tapi cukup untuk fondasi (nanti bisa diperdalam).
    """
    role_text = (
        (hero_row.get("Role_Lane_1") or "")
        + " "
        + (hero_row.get("Role_Lane_2") or "")
        + " "
        + (hero_row.get("Role_Lane_3") or "")
    ).lower()

    lane = (lane or "").lower()
    build: List[str] = []

    # Sepatu + 2 core (sangat sederhana / baseline)
    if "mage" in role_text or "mid" in lane:
        build += ["Magic Shoes", "Calamity Reaper", "Genius Wand"]
    elif "marksman" in role_text or "gold" in lane:
        build += ["Swift Boots", "Windtalker", "Berserker's Fury"]
    elif "jungle" in lane:
        build += ["Tough Boots", "Hunter Strike", "Malefic Roar"]
    elif "tank" in role_text or "roam" in lane:
        build += ["Tough Boots", "Dominance Ice", "Antique Cuirass"]
    elif "fighter" in role_text or "exp" in lane:
        build += ["Tough Boots", "War Axe", "Bloodlust Axe"]
    else:
        build += ["Tough Boots", "War Axe", "Dominance Ice"]

    return build


def adjust_by_enemy_mix(build: List[str], enemy_mix: Optional[str]) -> List[str]:
    """
    Tambah item penyesuaian berdasarkan komposisi musuh:
    - magic: tambahkan anti-magic
    - physical: tambahkan anti-physical
    - campur (default): kombinasi keduanya
    """
    em = (enemy_mix or "campur").lower()
    adjusted = list(build)

    if em == "magic":
        adjusted += ["Athena's Shield", "Radiant Armor"]
    elif em == "physical":
        adjusted += ["Dominance Ice", "Blade Armor"]
    else:
        adjusted += ["Athena's Shield", "Dominance Ice"]

    # jaga maksimal 6 slot agar rapi
    return adjusted[:6]


# ===== Heuristik Counter (sederhana) =====

# Tag → list counter hero/item (placeholder; boleh kamu perkuat nantinya)
COUNTER_TAGS: Dict[str, List[str]] = {
    "marksman": ["Khufra", "Franco", "Hayabusa"],           # CC keras & assassin
    "mage": ["Natalia", "Lancelot", "Hayabusa"],            # gap-closer & burst ke squishy
    "fighter": ["Karrie", "Dyrroth", "Valir"],              # anti-tank / anti-melee
    "tank": ["Valir", "Karrie", "Esmeralda"],               # anti-cc pushback / %HP shred
    "assassin": ["Baxia", "Khufra", "Atlas"],               # anti-mobilitas + anti-regen
    "support": ["Natalia", "Hayabusa", "Franco"],           # pickoff support
    # tag khusus (item-level)
    "regen": ["Dominance Ice", "Necklace of Durance", "Sea Halberd"],
}


def _role_tag_text(hero_row: Dict) -> str:
    text = (
        (hero_row.get("Role_Lane_1") or "")
        + " "
        + (hero_row.get("Role_Lane_2") or "")
        + " "
        + (hero_row.get("Role_Lane_3") or "")
    ).lower()
    return text


def infer_role_tag(hero_row: Dict) -> str:
    """
    Ambil satu tag utama dari teks role/lane untuk heuristik.
    """
    t = _role_tag_text(hero_row)
    for key in [
        "marksman",
        "mage",
        "fighter",
        "tank",
        "assassin",
        "support",
        "roam",
        "exp",
        "mid",
        "gold",
        "jungle",
    ]:
        if key in t:
            return key
    return "fighter"  # default aman


def infer_counters_for_hero(hero_row: Dict) -> List[str]:
    """
    Kembalikan daftar counter hero/item untuk 1 hero target.
    (Heuristik ringan – bisa kamu ganti dengan mapping yang lebih akurat nanti.)
    """
    tag = infer_role_tag(hero_row)
    return COUNTER_TAGS.get(tag, ["Khufra", "Franco", "Valir"])
