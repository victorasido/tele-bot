from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from data.dal import get_hero_by_name
from core.rules import lane_warning
from core.gemini import compose_with_gemini

router = Router()

@router.message(Command("gameplay"))
async def gameplay_cmd(m: Message):
    """
    /gameplay Harith lane=mid
    """
    parts = (m.text or "").split()
    if len(parts) < 2:
        return await m.answer("Contoh: /gameplay Harith lane=mid")

    hero_name = parts[1]
    lane = None
    for p in parts[2:]:
        if p.startswith("lane="):
            lane = p.split("=", 1)[1]

    hero = get_hero_by_name(hero_name)
    if not hero:
        return await m.answer(f"Hero '{hero_name}' tidak ditemukan.")

    payload = {
        "type": "gameplay",
        "hero": hero["Hero"],
        "lane": lane,
        "warning": lane_warning(hero, lane),
    }
    await m.answer(compose_with_gemini(payload))
