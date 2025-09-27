from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from data.dal import get_hero_by_name
from core.rules import infer_counters_for_hero
from core.gemini import compose_with_gemini

router = Router()

@router.message(Command("counter"))
async def counter_cmd(m: Message):
    """
    /counter Wanwan
    """
    parts = (m.text or "").split(maxsplit=1)
    if len(parts) < 2:
        return await m.answer("Contoh: /counter Wanwan")

    target_name = parts[1].strip()
    hero = get_hero_by_name(target_name)
    if not hero:
        return await m.answer(f"Hero '{target_name}' tidak ada di dataset.")

    counters = infer_counters_for_hero(hero)
    payload = {"type": "counter", "target": hero["Hero"], "counters": counters}
    await m.answer(compose_with_gemini(payload))
