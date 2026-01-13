from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from core.states import BotStates
from data.dal import get_hero_by_name
from core.gemini import compose_with_gemini

router = Router()

async def process_comp_request(m: Message, hero_name: str):
    hero_data = get_hero_by_name(hero_name)
    if not hero_data:
        await m.answer(f"❌ Hero <b>{hero_name}</b> tidak ditemukan.")
        return False

    real_name = hero_data.get('Hero', hero_name)
    role = hero_data.get('Role', 'Unknown')

    loading_msg = await m.answer(f"🤖 <b>Coach AI sedang meracik tim untuk {real_name}...</b>")

    payload = {"type": "comp", "hero": hero_data}

    try:
        # Tambahkan await
        response_text = await compose_with_gemini(payload)
        await loading_msg.edit_text(response_text, parse_mode="Markdown")
        return True
    except Exception as e:
        await loading_msg.edit_text(f"❌ Error: {str(e)}")
        return False

@router.message(Command("comp"))
async def comp_cmd(m: Message):
    args = m.text.split(maxsplit=1)
    if len(args) < 2:
        await m.answer("⚠️ Gunakan: <code>/comp NamaHero</code>")
        return
    await process_comp_request(m, args[1])

@router.message(BotStates.waiting_for_hero_comp)
async def comp_state_handler(m: Message, state: FSMContext):
    text = m.text.strip()
    if text.lower() in ['batal', 'cancel', '/cancel', 'exit']:
        await state.clear()
        await m.answer("✅ Aksi dibatalkan.")
        return
    success = await process_comp_request(m, text)
    if success:
        await state.clear()