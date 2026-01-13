from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from data.dal import get_hero_by_name, list_heroes_by_role, list_heroes_by_lane
import random

router = Router()

@router.message(Command("comp"))
async def comp_cmd(m: Message):
    """
    Contoh: /comp Tigreal
    Memberikan rekomendasi hero yang cocok menemani hero tersebut.
    """
    args = m.text.split(maxsplit=1)
    if len(args) < 2:
        await m.answer("Gunakan: <code>/comp NamaHero</code>\nContoh: <code>/comp Tigreal</code>")
        return

    hero_name = args[1]
    hero = get_hero_by_name(hero_name)

    if not hero:
        await m.answer(f"❌ Hero <b>{hero_name}</b> tidak ditemukan.")
        return

    role = hero.get('Role', 'Unknown')
    lane = hero.get('PrimaryLane', 'Unknown')
    
    # Logika Sederhana: Cari partner yang MELENGKAPI role/lane
    # Misal: Jika hero adalah Tank (Roam), cari Marksman (Gold) dan Mage (Mid).
    
    recommendations = []
    
    if "Roam" in lane or "Tank" in role:
        # Cari Gold Laner & Jungler
        mm = list_heroes_by_lane("Gold")
        jg = list_heroes_by_lane("Jungle")
        if mm: recommendations.append(f"🔫 <b>Gold Laner:</b> {random.choice(mm)}")
        if jg: recommendations.append(f"⚔️ <b>Jungler:</b> {random.choice(jg)}")
        
    elif "Gold" in lane or "Marksman" in role:
        # Cari Roamer & Mid Laner
        roam = list_heroes_by_lane("Roam")
        mid = list_heroes_by_lane("Mid")
        if roam: recommendations.append(f"🛡 <b>Roamer:</b> {random.choice(roam)}")
        if mid: recommendations.append(f"🔮 <b>Mid Laner:</b> {random.choice(mid)}")
        
    elif "Jungle" in lane:
        # Cari Roamer & Exp Laner
        roam = list_heroes_by_lane("Roam")
        exp = list_heroes_by_lane("Exp")
        if roam: recommendations.append(f"🛡 <b>Roamer:</b> {random.choice(roam)}")
        if exp: recommendations.append(f"🥊 <b>Exp Laner:</b> {random.choice(exp)}")
        
    elif "Mid" in lane or "Mage" in role:
        # Cari Jungler & Roamer
        jg = list_heroes_by_lane("Jungle")
        roam = list_heroes_by_lane("Roam")
        if jg: recommendations.append(f"⚔️ <b>Jungler:</b> {random.choice(jg)}")
        if roam: recommendations.append(f"🛡 <b>Roamer:</b> {random.choice(roam)}")
        
    elif "Exp" in lane or "Fighter" in role:
        # Cari Mid Laner & Jungler
        mid = list_heroes_by_lane("Mid")
        jg = list_heroes_by_lane("Jungle")
        if mid: recommendations.append(f"🔮 <b>Mid Laner:</b> {random.choice(mid)}")
        if jg: recommendations.append(f"⚔️ <b>Jungler:</b> {random.choice(jg)}")

    # Fallback jika logika di atas tidak menangkap (misal data lane kosong)
    if not recommendations:
         recommendations.append("<i>Tips: Pastikan tim memiliki minimal 1 Tank/Support dan 1 Marksman.</i>")

    rec_text = "\n".join(recommendations)
    
    await m.answer(
        f"🤝 <b>Rekomendasi Tim untuk {hero.get('Hero')}</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"Hero ini bermain di <b>{lane}</b> sebagai <b>{role}</b>.\n"
        f"Pasangan yang cocok:\n\n"
        f"{rec_text}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<i>Catatan: Rekomendasi ini berdasarkan sinergi lane dasar.</i>"
    )