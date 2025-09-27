from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from data.dal import list_heroes_by_role, list_heroes_by_lane
from core.gemini import compose_with_gemini

router = Router()

@router.message(Command("tierrole"))
async def tier_by_role(m: Message):
    """
    /tierrole mage
    """
    parts = (m.text or "").split(maxsplit=1)
    if len(parts) < 2:
        return await m.answer("Contoh: /tierrole mage")
    role = parts[1].strip().lower()
    heroes = list_heroes_by_role(role)[:10]
    payload = {"type": "tier-role", "role": role, "heroes": heroes}
    await m.answer(compose_with_gemini(payload))

@router.message(Command("tierlane"))
async def tier_by_lane(m: Message):
    """
    /tierlane gold
    """
    parts = (m.text or "").split(maxsplit=1)
    if len(parts) < 2:
        return await m.answer("Contoh: /tierlane gold")
    lane = parts[1].strip().lower()
    heroes = list_heroes_by_lane(lane)[:10]
    payload = {"type": "tier-lane", "lane": lane, "heroes": heroes}
    await m.answer(compose_with_gemini(payload))

@router.message(Command("tierlist"))
async def tier_overview(m: Message):
    """
    /tierlist
    """
    payload = {"type": "tier-overview", "note": "Ringkasan meta singkat (role & lane)."}
    await m.answer(compose_with_gemini(payload))
