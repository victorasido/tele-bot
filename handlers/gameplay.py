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
async def process_gameplay_request(m: Message, hero_name: str):
    """
    Fungsi sentral untuk memproses permintaan gameplay ke AI.
    """
    # 1. Validasi Hero di Database
    # Kita butuh data Role dari CSV agar saran AI akurat (misal: Chou Tank vs Chou Fighter)
    hero_data = get_hero_by_name(hero_name)
    
    if not hero_data:
        await m.answer(
            f"❌ Hero <b>{hero_name}</b> tidak ditemukan.\n"
            "Pastikan ejaan benar (contoh: Ling, Fanny, Gusion)."
        )
        return False

    real_name = hero_data.get('Hero', hero_name)
    role = hero_data.get('Role', 'Unknown')

    # 2. Kirim Pesan Loading
    loading_msg = await m.answer(f"🎮 <b>Coach AI sedang menyusun panduan untuk {real_name} ({role})...</b>")

    # 3. Siapkan Payload ke AI
    payload = {
        "type": "gameplay",  # Ini akan memicu prompt 'gameplay' di core/gemini.py
        "hero": hero_data,
        "input": f"Berikan guide lengkap untuk hero {real_name}"
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
# 1. HANDLER COMMAND (/gameplay <hero>)
# =========================================================
@router.message(Command("gameplay"))
async def gameplay_cmd(m: Message):
    """
    Contoh: /gameplay Fanny
    """
    args = m.text.split(maxsplit=1)
    if len(args) < 2:
        await m.answer("⚠️ Gunakan format: <code>/gameplay NamaHero</code>")
        return

    hero_input = args[1]
    await process_gameplay_request(m, hero_input)

# =========================================================
# 2. HANDLER INPUT DARI MENU (State FSM) - BARU!
# =========================================================
@router.message(BotStates.waiting_for_hero_gameplay)
async def gameplay_state_handler(m: Message, state: FSMContext):
    """
    Menangani input teks setelah user klik tombol 'Gameplay Guide' di menu.
    """
    text = m.text.strip()
    
    # Cek command batal
    if text.lower() in ['batal', 'cancel', 'exit', '/cancel']:
        await state.clear()
        await m.answer("✅ Aksi dibatalkan.")
        return

    # Proses request
    success = await process_gameplay_request(m, text)
    
    # Jika sukses (hero ketemu & AI jawab), reset state.
    # Jika gagal (typo), biarkan state aktif biar user bisa coba lagi.
    if success:
        await state.clear()