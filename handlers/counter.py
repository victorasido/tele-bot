from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from data.dal import list_heroes_by_role, list_heroes_by_lane

router = Router()

# =========================================================
# 1. HANDLER CALLBACK DARI MENU (Tombol)
# =========================================================

# Menangani tombol Role: "tier:role:fighter", "tier:role:mage", dll
@router.callback_query(F.data.startswith("tier:role:"))
async def on_tier_role_click(c: CallbackQuery):
    # Ambil role dari data tombol (split string)
    role_selected = c.data.split(":")[2]  # contoh: "fighter"
    
    # Ambil data dari CSV via DAL
    heroes = list_heroes_by_role(role_selected)
    
    # Format output
    if heroes:
        hero_list = ", ".join(sorted(heroes))
        text = (
            f"📊 <b>Daftar Hero Role: {role_selected.capitalize()}</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"{hero_list}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"<i>Total: {len(heroes)} Hero</i>"
        )
    else:
        text = f"❌ Tidak ada hero ditemukan untuk role <b>{role_selected}</b>."

    # Edit pesan menu sebelumnya
    await c.message.edit_text(text)
    await c.answer()

# Menangani tombol Lane: "tier:lane:gold", "tier:lane:exp", dll
@router.callback_query(F.data.startswith("tier:lane:"))
async def on_tier_lane_click(c: CallbackQuery):
    lane_selected = c.data.split(":")[2]  # contoh: "gold"
    
    heroes = list_heroes_by_lane(lane_selected)
    
    if heroes:
        hero_list = ", ".join(sorted(heroes))
        text = (
            f"🗺 <b>Daftar Hero Lane: {lane_selected.capitalize()}</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"{hero_list}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"<i>Total: {len(heroes)} Hero</i>"
        )
    else:
        text = f"❌ Tidak ada hero ditemukan untuk lane <b>{lane_selected}</b>."

    await c.message.edit_text(text)
    await c.answer()

# =========================================================
# 2. HANDLER COMMAND MANUAL (/tierrole, /tierlane)
# =========================================================

@router.message(Command("tierrole"))
async def tier_role_cmd(m: Message):
    """Contoh: /tierrole Mage"""
    args = m.text.split(maxsplit=1)
    if len(args) < 2:
        await m.answer("Gunakan: <code>/tierrole NamaRole</code>\nContoh: <code>/tierrole Mage</code>")
        return
        
    role = args[1]
    heroes = list_heroes_by_role(role)
    
    if heroes:
        await m.answer(f"📊 <b>Role {role}:</b>\n" + ", ".join(sorted(heroes)))
    else:
        await m.answer(f"Tidak ada hero dengan role '{role}'.")

@router.message(Command("tierlane"))
async def tier_lane_cmd(m: Message):
    """Contoh: /tierlane Gold"""
    args = m.text.split(maxsplit=1)
    if len(args) < 2:
        await m.answer("Gunakan: <code>/tierlane NamaLane</code>\nContoh: <code>/tierlane Gold</code>")
        return
        
    lane = args[1]
    heroes = list_heroes_by_lane(lane)
    
    if heroes:
        await m.answer(f"🗺 <b>Lane {lane}:</b>\n" + ", ".join(sorted(heroes)))
    else:
        await m.answer(f"Tidak ada hero di lane '{lane}'.")