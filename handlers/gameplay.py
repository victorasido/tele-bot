from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from core.states import BotStates
from data.dal import get_hero_by_name
from core.gemini import compose_with_gemini

router = Router()

async def process_gameplay_request(m: Message, hero_name: str):
    hero_data = get_hero_by_name(hero_name)
    if not hero_data:
        await m.answer(f"❌ Hero <b>{hero_name}</b> tidak ditemukan.", parse_mode="HTML")
        return False

    real_name = hero_data.get('Hero', hero_name)
    
    loading_msg = await m.answer(
        f"📚 <b>Mencari Guide Top Global {real_name}...</b>\n"
        f"⚡ <i>Mengecek Cache & Database...</i>",
        parse_mode="HTML"
    )

    payload = {
        "type": "gameplay",
        "hero": hero_data,
        "input": real_name
    }

    try:
        response_text = await compose_with_gemini(payload)
        await loading_msg.edit_text(response_text, parse_mode="Markdown")
        return True
    except Exception as e:
        await loading_msg.edit_text(f"❌ Error: {e}")
        return False

@router.message(Command("gameplay"))
async def gameplay_cmd(m: Message):
    args = m.text.split(maxsplit=1)
    if len(args) < 2:
        await m.answer("⚠️ Gunakan: <code>/gameplay NamaHero</code>", parse_mode="HTML")
        return
    await process_gameplay_request(m, args[1])

@router.message(BotStates.waiting_for_hero_gameplay)
async def gameplay_state_handler(m: Message, state: FSMContext):
    text = m.text.strip()
    if text.lower() in ['batal', 'cancel']:
        await state.clear()
        await m.answer("✅ Batal.")
        return
    if await process_gameplay_request(m, text):
        await state.clear()