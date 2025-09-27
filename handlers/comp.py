from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from data.dal import list_heroes_by_lane
from core.gemini import compose_with_gemini

router = Router()

@router.message(Command("komposisi"))
async def comp_cmd(m: Message):
    """
    /komposisi
    """
    lanes = ["roam", "exp", "mid", "gold", "jungle"]
    team = []
    for lane in lanes:
        lst = list_heroes_by_lane(lane)
        team.append({"lane": lane, "hero": lst[0] if lst else None})

    payload = {"type": "comp", "team": team}
    await m.answer(compose_with_gemini(payload))
