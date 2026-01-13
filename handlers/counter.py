from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from core.states import BotStates
from data.dal import get_hero_by_name
from core.gemini import compose_with_gemini

router = Router()

async def process_counter(m: Message, hero_name: str):
    # 1. Validasi Hero di Dataset
    hero_data = get_hero_by_name(hero_name)
    
    if not hero_data:
        await m.answer(
            f"❌ Hero <b>{hero_name}</b> tidak ditemukan.\n"
            "Pastikan ejaan benar."
        )
        return False

    real_name = hero_data.get('Hero', hero_name)
    role = hero_data.get('Role', 'Unknown')
    
    # 2. Loading Msg
    loading = await m.answer(f"🛡 Menganalisis strategi lawan <b>{real_name}</b>...")
    
    # 3. Payload AI
    payload = {
        "type": "counter",
        "hero": hero_data,
        "input": f"Berikan counter hero dan tips melawan {real_name}."
    }
    
    try:
        response = compose_with_gemini(payload)
        await loading.edit_text(response, parse_mode="Markdown")
    except Exception as e:
        await loading.edit_text(f"❌ Gagal memuat data.\nError: {str(e)}")
    
    return True

# Handler Command /counter
@router.message(Command("counter"))
async def counter_cmd(m: Message):
    args = m.text.split(maxsplit=1)
    if len(args) < 2:
        await m.answer("Gunakan: <code>/counter NamaHero</code>\nContoh: <code>/counter Fanny</code>")
        return
    await process_counter(m, args[1])

# Handler State (Input dari Menu Counter & Recounter)
# Kita pakai satu handler untuk keduanya karena logikanya sama
@router.message(BotStates.waiting_for_hero_counter)
async def counter_state(m: Message, state: FSMContext):
    text = m.text.strip()
    
    if text.lower() in ['batal', 'cancel', '/cancel']:
        await state.clear()
        await m.answer("✅ Aksi dibatalkan.")
        return

    success = await process_counter(m, text)
    if success:
        await state.clear()