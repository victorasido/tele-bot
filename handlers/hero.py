# handlers/hero.py
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from core.states import BotStates

from data.dal import get_hero_by_name
from core.rules import make_default_build, adjust_by_enemy_mix, lane_warning
from core.gemini import compose_with_gemini

router = Router()

# ---------------------------------------------------------
# 1. CARA LAMA (Manual Command)
# ---------------------------------------------------------
@router.message(Command("build"))
async def build_cmd(m: Message):
    """
    /build Harith lane=mid enemy=campur
    """
    try:
        parts = (m.text or "").split()
        if len(parts) < 2:
            return await m.answer("Contoh: /build Harith lane=mid enemy=campur")

        hero_name = parts[1]
        lane = None
        enemy = "campur"
        for p in parts[2:]:
            if p.startswith("lane="):
                lane = p.split("=", 1)[1]
            if p.startswith("enemy="):
                enemy = p.split("=", 1)[1]

        await process_build_logic(m, hero_name, lane, enemy)

    except Exception as e:
        await m.answer(f"Error: {e}")

# ---------------------------------------------------------
# 2. CARA BARU (Interaktif via Menu)
# ---------------------------------------------------------
@router.message(BotStates.waiting_for_hero_build)
async def process_build_input(m: Message, state: FSMContext):
    hero_name = m.text.strip()
    
    # Cek batal
    if hero_name.lower() in ["batal", "cancel", "exit"]:
        await state.clear()
        await m.answer("Aksi dibatalkan.")
        return

    # Jalankan logic build
    success = await process_build_logic(m, hero_name, lane=None, enemy="campur")
    
    if success:
        await state.clear() 

# ---------------------------------------------------------
# LOGIC INTI (FIXED)
# ---------------------------------------------------------
async def process_build_logic(m: Message, hero_name: str, lane: str | None, enemy: str):
    hero = get_hero_by_name(hero_name)
    
    if not hero:
        await m.answer(f"❌ Hero '{hero_name}' tidak ditemukan di dataset.\nSilakan coba ketik nama lain.")
        return False

    base_build = make_default_build(hero, lane)
    build = adjust_by_enemy_mix(base_build, enemy)
    warn = lane_warning(hero, lane)

    # --- PERBAIKAN DI SINI ---
    # Sebelumnya: "hero": hero["Hero"] (Salah, ini cuma kirim string nama)
    # Sekarang:   "hero": hero         (Benar, kirim full data hero biar AI bisa baca)
    payload = {
        "type": "build",
        "hero": hero, 
        "input": {"lane": lane if lane else "Auto-detect", "enemy_mix": enemy},
        "build": build,
        "warning": warn,
    }
    # --------------------------

    # Tampilkan nama hero yang terdeteksi (misal user ketik "nana", bot tahu itu "Nana")
    detected_name = hero.get('Hero', hero_name)
    loading_msg = await m.answer(f"⏳ Sedang meracik build untuk **{detected_name}**...")
    
    try:
        response = compose_with_gemini(payload)
        await loading_msg.edit_text(response)
        return True
    except Exception as e:
        # Tampilkan error detail untuk debugging
        import traceback
        traceback.print_exc() 
        await loading_msg.edit_text(f"Error AI: {e}")
        return True