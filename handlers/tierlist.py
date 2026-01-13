from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from core.gemini import compose_with_gemini

router = Router()

# =========================================================
# LOGIKA UTAMA: MINTA TIER LIST KE AI
# =========================================================
async def process_tierlist_request(message_obj, role_or_lane: str):
    """
    Mengirim request Tier List ke AI.
    message_obj bisa berupa Message (dari command) atau CallbackQuery (dari tombol).
    """
    # Tentukan objek pesan untuk diedit/dibalas
    if isinstance(message_obj, CallbackQuery):
        msg = message_obj.message
        await message_obj.answer() # Hilangkan loading di tombol
    else:
        msg = message_obj

    # 1. Kirim Pesan Loading
    loading_msg = await msg.answer(f"📊 <b>Analis AI sedang menyusun Tier List Meta untuk {role_or_lane}...</b>")

    # 2. Siapkan Payload
    # Type 'tierlist' akan memicu prompt khusus di core/gemini.py
    payload = {
        "type": "tierlist",
        "input": role_or_lane  # Contoh: "Mage", "Exp Lane", "Roamer"
    }

    try:
        # 3. Minta Jawaban Gemini
        response_text = compose_with_gemini(payload)
        
        # 4. Tampilkan Hasil
        await loading_msg.edit_text(response_text, parse_mode="Markdown")
        
    except Exception as e:
        await loading_msg.edit_text(f"❌ Gagal mengambil data Meta.\nError: {str(e)}")

# =========================================================
# 1. HANDLER CALLBACK DARI MENU (Tombol)
# =========================================================

# Menangani tombol Role: "tier:role:fighter", "tier:role:mage", dll
@router.callback_query(F.data.startswith("tier:role:"))
async def on_tier_role_click(c: CallbackQuery):
    role_selected = c.data.split(":")[2].capitalize() # contoh: "Fighter"
    await process_tierlist_request(c, role_selected)

# Menangani tombol Lane: "tier:lane:gold", "tier:lane:exp", dll
@router.callback_query(F.data.startswith("tier:lane:"))
async def on_tier_lane_click(c: CallbackQuery):
    lane_selected = c.data.split(":")[2].capitalize() # contoh: "Gold"
    
    # Tambahkan kata "Lane" biar AI lebih paham konteksnya (kecuali Jungle/Roam)
    if lane_selected.lower() not in ["jungle", "roam"]:
        lane_input = f"{lane_selected} Lane"
    else:
        lane_input = lane_selected

    await process_tierlist_request(c, lane_input)

# =========================================================
# 2. HANDLER COMMAND MANUAL (/tierrole, /tierlane, /tierlist)
# =========================================================

@router.message(Command("tierlist"))
async def tier_general_cmd(m: Message):
    """Contoh: /tierlist"""
    await m.answer(
        "Gunakan format spesifik:\n"
        "👉 /tierrole <Role> (contoh: <code>/tierrole Mage</code>)\n"
        "👉 /tierlane <Lane> (contoh: <code>/tierlane Gold</code>)"
    )

@router.message(Command("tierrole"))
async def tier_role_cmd(m: Message):
    """Contoh: /tierrole Mage"""
    args = m.text.split(maxsplit=1)
    if len(args) < 2:
        await m.answer("Gunakan: <code>/tierrole NamaRole</code>\nContoh: <code>/tierrole Mage</code>")
        return
    await process_tierlist_request(m, args[1])

@router.message(Command("tierlane"))
async def tier_lane_cmd(m: Message):
    """Contoh: /tierlane Gold"""
    args = m.text.split(maxsplit=1)
    if len(args) < 2:
        await m.answer("Gunakan: <code>/tierlane NamaLane</code>\nContoh: <code>/tierlane Gold</code>")
        return
    await process_tierlist_request(m, args[1])