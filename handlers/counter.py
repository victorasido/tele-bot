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
async def process_counter_request(m: Message, hero_name: str):
    """
    Memproses permintaan strategi counter hero menggunakan AI.
    """
    # 1. Validasi Hero di Database
    hero_data = get_hero_by_name(hero_name)
    
    if not hero_data:
        await m.answer(
            f"❌ Hero <b>{hero_name}</b> tidak ditemukan.\n"
            "Pastikan ejaan benar (contoh: Fanny, Wanwan, Yin)."
        )
        return False

    real_name = hero_data.get('Hero', hero_name)
    role = hero_data.get('Role', 'Unknown')
    
    # 2. Kirim Pesan Loading
    loading_msg = await m.answer(f"🛡 <b>Analis AI sedang menyusun strategi melawan {real_name} ({role})...</b>")
    
    # 3. Siapkan Payload ke AI
    # Prompt 'counter' di gemini.py sudah dirancang untuk memberikan hero counter & item counter
    payload = {
        "type": "counter",
        "hero": hero_data,
        "input": f"Berikan counter hero dan tips melawan {real_name}."
    }
    
    try:
        # 4. Minta Jawaban Gemini
        response_text = compose_with_gemini(payload)
        
        # 5. Tampilkan Hasil
        await loading_msg.edit_text(response_text, parse_mode="Markdown")
        return True

    except Exception as e:
        await loading_msg.edit_text(f"❌ Gagal memuat data strategi.\nError: {str(e)}")
        return False

# =========================================================
# 1. HANDLER COMMAND (/counter <hero>)
# =========================================================
@router.message(Command("counter"))
async def counter_cmd(m: Message):
    """
    Contoh: /counter Fanny
    """
    args = m.text.split(maxsplit=1)
    if len(args) < 2:
        await m.answer("⚠️ Gunakan format: <code>/counter NamaHero</code>")
        return
    
    await process_counter_request(m, args[1])

# =========================================================
# 2. HANDLER INPUT DARI MENU (State FSM) - BARU!
# =========================================================
# Menangkap input untuk tombol 'Counter' DAN 'Recounter'
@router.message(BotStates.waiting_for_hero_counter)
async def counter_state_handler(m: Message, state: FSMContext):
    """
    Menangani input teks setelah user klik tombol Counter/Recounter.
    """
    text = m.text.strip()
    
    # Cek command batal
    if text.lower() in ['batal', 'cancel', '/cancel', 'exit']:
        await state.clear()
        await m.answer("✅ Aksi dibatalkan.")
        return

    # Proses request
    success = await process_counter_request(m, text)
    
    if success:
        await state.clear()