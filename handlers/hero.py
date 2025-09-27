from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from data.dal import get_hero_by_name
from core.rules import make_default_build, adjust_by_enemy_mix, lane_warning
from core.gemini import compose_with_gemini

router = Router()

@router.message(Command("build"))
async def build_cmd(m: Message):
    """
    /build Harith lane=mid enemy=campur
    """
    try:
        parts = (m.text or "").split()
        if len(parts) < 2:
            return await m.answer("Contoh: /build Harith lane=mid enemy=campur")

        hero_name = parts[1]
        lane = None
        enemy = "campur"
        for p in parts[2:]:
            if p.startswith("lane="):
                lane = p.split("=", 1)[1]
            if p.startswith("enemy="):
                enemy = p.split("=", 1)[1]

        hero = get_hero_by_name(hero_name)
        if not hero:
            return await m.answer(f"Hero '{hero_name}' tidak ditemukan di dataset.")

        base_build = make_default_build(hero, lane)
        build = adjust_by_enemy_mix(base_build, enemy)
        warn = lane_warning(hero, lane)

        payload = {
            "type": "build",
            "hero": hero["Hero"],
            "input": {"lane": lane, "enemy_mix": enemy},
            "build": build,
            "warning": warn,
        }
        await m.answer(compose_with_gemini(payload))
    except Exception as e:
        await m.answer(f"Error: {e}")
