from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from core.gemini import compose_with_gemini

router = Router()

async def process_tierlist_request(message_obj, role_or_lane: str):
    if isinstance(message_obj, CallbackQuery):
        msg = message_obj.message
        await message_obj.answer() 
    else:
        msg = message_obj

    loading_msg = await msg.answer(f"📊 <b>Analis AI menyusun Tier List {role_or_lane}...</b>")

    payload = {"type": "tierlist", "input": role_or_lane}

    try:
        # Tambahkan await
        response_text = await compose_with_gemini(payload)
        await loading_msg.edit_text(response_text, parse_mode="Markdown")
    except Exception as e:
        await loading_msg.edit_text(f"❌ Error: {str(e)}")

@router.callback_query(F.data.startswith("tier:role:"))
async def on_tier_role_click(c: CallbackQuery):
    role_selected = c.data.split(":")[2].capitalize() 
    await process_tierlist_request(c, role_selected)

@router.callback_query(F.data.startswith("tier:lane:"))
async def on_tier_lane_click(c: CallbackQuery):
    lane_selected = c.data.split(":")[2].capitalize()
    lane_input = f"{lane_selected} Lane" if lane_selected.lower() not in ["jungle", "roam"] else lane_selected
    await process_tierlist_request(c, lane_input)

@router.message(Command("tierlist"))
async def tier_general_cmd(m: Message):
    await m.answer("Gunakan: /tierrole [Role] atau /tierlane [Lane]")

@router.message(Command("tierrole"))
async def tier_role_cmd(m: Message):
    args = m.text.split(maxsplit=1)
    if len(args) < 2: return
    await process_tierlist_request(m, args[1])

@router.message(Command("tierlane"))
async def tier_lane_cmd(m: Message):
    args = m.text.split(maxsplit=1)
    if len(args) < 2: return
    await process_tierlist_request(m, args[1])