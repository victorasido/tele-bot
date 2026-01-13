from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from core.states import BotStates
from data.dal import get_hero_by_name
from core.gemini import compose_with_gemini

router = Router()

# =========================================================
# LOGIKA UTAMA (Dipakai oleh Command & Menu)
# =========================================================
async def process_comp_request(m: Message, hero_name: str):
    """
    Memproses permintaan komposisi tim menggunakan AI.
    """
    # 1. Validasi Hero di Database
    hero_data = get_hero_by_name(hero_name)
    
    if not hero_data:
        await m.answer(
            f"❌ Hero <b>{hero_name}</b> tidak ditemukan.\n"
            "Pastikan ejaan benar (contoh: Tigreal, Atlas, Estes)."
        )
        return False

    real_name = hero_data.get('Hero', hero_name)
    role = hero_data.get('Role', 'Unknown')

    # 2. Kirim Pesan Loading
    loading_msg = await m.answer(f"🤖 <b>Coach AI sedang meracik tim untuk {real_name} ({role})...</b>")

    # 3. Siapkan Payload ke AI
    payload = {
        "type": "comp", # Memicu prompt 'comp' di gemini.py
        "hero": hero_data
    }

    try:
        # 4. Minta Jawaban Gemini
        response_text = compose_with_gemini(payload)
        
        # 5. Tampilkan Hasil
        await loading_msg.edit_text(response_text, parse_mode="Markdown")
        return True
        
    except Exception as e:
        await loading_msg.edit_text(f"❌ Terjadi kesalahan saat menghubungi AI.\nError: {str(e)}")
        return False

# =========================================================
# 1. HANDLER COMMAND (/comp <hero>)
# =========================================================
@router.message(Command("comp"))
async def comp_cmd(m: Message):
    """
    Contoh: /comp Tigreal
    """
    args = m.text.split(maxsplit=1)
    if len(args) < 2:
        await m.answer("⚠️ Gunakan format: <code>/comp NamaHero</code>")
        return

    hero_input = args[1]
    await process_comp_request(m, hero_input)

# =========================================================
# 2. HANDLER INPUT DARI MENU (State FSM) - BARU!
# =========================================================
@router.message(BotStates.waiting_for_hero_comp)
async def comp_state_handler(m: Message, state: FSMContext):
    """
    Menangani input teks setelah user klik tombol 'Komposisi Team'.
    """
    text = m.text.strip()
    
    # Cek command batal
    if text.lower() in ['batal', 'cancel', 'exit', '/cancel']:
        await state.clear()
        await m.answer("✅ Aksi dibatalkan.")
        return

    # Proses request
    success = await process_comp_request(m, text)
    
    # Jika sukses, reset state. Jika gagal (typo), biarkan user coba lagi.
    if success:
        await state.clear()