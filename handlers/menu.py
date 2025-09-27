# handlers/menu.py
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

# =========================
# Root & Entry
# =========================
@router.message(CommandStart())
async def start(m: Message):
    await m.answer("Halo! 👋\nGunakan /menu atau klik tombol di bawah untuk mulai.")
    await show_root_menu(m)

@router.message(Command("menu"))
async def menu(m: Message):
    await show_root_menu(m)

async def show_root_menu(m: Message | CallbackQuery):
    """
    Level 1 (sesuai kerangka):
    - Hero
    - Tier List
    - Tidak Rekomendasikan
    """
    kb = InlineKeyboardBuilder()
    kb.button(text="🧝‍♂️ Hero", callback_data="menu:hero")
    kb.button(text="📊 Tier List", callback_data="menu:tier")
    kb.button(text="⛔ Tidak Rekomendasikan", callback_data="menu:lowest")
    kb.adjust(1)

    text = "Menu:"
    if isinstance(m, CallbackQuery):
        await m.message.edit_text(text, reply_markup=kb.as_markup())
        await m.answer()
    else:
        await m.answer(text, reply_markup=kb.as_markup())

# =========================
# Submenu: Hero
# =========================
@router.callback_query(F.data == "menu:hero")
async def menu_hero(c: CallbackQuery):
    """
    Level 2 Hero:
    -- Build
    -- Recounter
    -- Counter
    -- Gameplay
    -- Komposisi team
    """
    kb = InlineKeyboardBuilder()
    kb.button(text="🔧 Build", callback_data="hero:build")
    kb.button(text="🔁 Recounter", callback_data="hero:recounter")
    kb.button(text="🛡 Counter", callback_data="hero:counter")
    kb.button(text="🎮 Gameplay", callback_data="hero:gameplay")
    kb.button(text="👥 Komposisi Team", callback_data="hero:comp")
    kb.button(text="⬅️ Kembali", callback_data="menu:root")
    kb.adjust(2, 2, 1, 1)

    await c.message.edit_text("Menu lanjutan Hero:", reply_markup=kb.as_markup())
    await c.answer()

# Trigger per aksi Hero
@router.callback_query(F.data.startswith("hero:"))
async def hero_actions(c: CallbackQuery):
    action = c.data.split(":")[1]
    examples = {
        "build": "Masukkan perintah:\n/build <Hero> lane=<mid|gold|exp|roam|jungle> enemy=<magic|physical|campur>\nContoh: /build Harith lane=mid enemy=campur",
        "recounter": "Masukkan perintah:\n/counter <HeroLawan>\nContoh: /counter Wanwan\n(catatan: recounter=hero yang ‘balik meng-counter’)",
        "counter": "Masukkan perintah:\n/counter <HeroLawan>\nContoh: /counter Wanwan",
        "gameplay": "Masukkan perintah:\n/gameplay <Hero> lane=<lane?>\nContoh: /gameplay Harith lane=mid",
        "comp": "Masukkan perintah:\n/komposisi",
    }
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Kembali", callback_data="menu:hero")
    kb.button(text="🏠 Menu", callback_data="menu:root")
    kb.adjust(2)
    await c.message.edit_text(examples.get(action, "Fitur belum tersedia."), reply_markup=kb.as_markup())
    await c.answer()

# =========================
# Submenu: Tier List
# =========================
@router.callback_query(F.data == "menu:tier")
async def menu_tier(c: CallbackQuery):
    """
    Level 2 Tier List:
    -- Prioritas rate
       --- Pick % 10
       --- Ban % 10
    -- Role
       --- Tank / Fighter / Marksman / Mage / Support
    -- Lane
       --- Roam / Exp / Mid / Gold / Jungle
    """
    kb = InlineKeyboardBuilder()
    kb.button(text="⭐ Prioritas Rate", callback_data="tier:prio")
    kb.button(text="🧩 Role", callback_data="tier:role")
    kb.button(text="🗺 Lane", callback_data="tier:lane")
    kb.button(text="⬅️ Kembali", callback_data="menu:root")
    kb.adjust(2, 2)
    await c.message.edit_text("Menu lanjutan Tier List:", reply_markup=kb.as_markup())
    await c.answer()

# --- Prioritas Rate sub-submenu
@router.callback_query(F.data == "tier:prio")
async def tier_prio(c: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="⬆️ Pick % 10", callback_data="tier:pick10")
    kb.button(text="⛔ Ban % 10", callback_data="tier:ban10")
    kb.button(text="⬅️ Kembali", callback_data="menu:tier")
    kb.adjust(2, 1)
    await c.message.edit_text("Prioritas Rate:", reply_markup=kb.as_markup())
    await c.answer()

@router.callback_query(F.data.in_(["tier:pick10", "tier:ban10"]))
async def tier_prio_actions(c: CallbackQuery):
    # NOTE: fitur ini butuh dataset pick_rate/ban_rate; sementara beri informasi
    mapping = {
        "tier:pick10": "Gunakan: /pick10\n(catatan: butuh dataset pick_rate)",
        "tier:ban10": "Gunakan: /ban10\n(catatan: butuh dataset ban_rate)",
    }
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Kembali", callback_data="tier:prio")
    kb.adjust(1)
    await c.message.edit_text(mapping[c.data], reply_markup=kb.as_markup())
    await c.answer()

# --- Role sub-submenu
@router.callback_query(F.data == "tier:role")
async def tier_role(c: CallbackQuery):
    kb = InlineKeyboardBuilder()
    for r in ["Tank", "Fighter", "Marksman", "Mage", "Support"]:
        kb.button(text=r, callback_data=f"tier:role:{r.lower()}")
    kb.button(text="⬅️ Kembali", callback_data="menu:tier")
    kb.adjust(3, 3)
    await c.message.edit_text("Pilih Role:", reply_markup=kb.as_markup())
    await c.answer()

@router.callback_query(F.data.startswith("tier:role:"))
async def tier_role_run(c: CallbackQuery):
    role = c.data.split(":")[2]
    # Di sini kita arahkan user ke command yang sudah ada (/tierrole)
    text = f"Gunakan: /tierrole {role}"
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Kembali", callback_data="tier:role")
    kb.adjust(1)
    await c.message.edit_text(text, reply_markup=kb.as_markup())
    await c.answer()

# --- Lane sub-submenu
@router.callback_query(F.data == "tier:lane")
async def tier_lane(c: CallbackQuery):
    kb = InlineKeyboardBuilder()
    for l in ["Roam", "Exp", "Mid", "Gold", "Jungle"]:
        kb.button(text=l, callback_data=f"tier:lane:{l.lower()}")
    kb.button(text="⬅️ Kembali", callback_data="menu:tier")
    kb.adjust(3, 3)
    await c.message.edit_text("Pilih Lane:", reply_markup=kb.as_markup())
    await c.answer()

@router.callback_query(F.data.startswith("tier:lane:"))
async def tier_lane_run(c: CallbackQuery):
    lane = c.data.split(":")[2]
    text = f"Gunakan: /tierlane {lane}"
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Kembali", callback_data="tier:lane")
    kb.adjust(1)
    await c.message.edit_text(text, reply_markup=kb.as_markup())
    await c.answer()

# =========================
# Submenu: Tidak Rekomendasikan
# =========================
@router.callback_query(F.data == "menu:lowest")
async def menu_lowest(c: CallbackQuery):
    """
    Level 2:
    - Tidak Rekomendasikan → 10 Lowest
    """
    kb = InlineKeyboardBuilder()
    kb.button(text="📉 10 Lowest", callback_data="lowest:10")
    kb.button(text="⬅️ Kembali", callback_data="menu:root")
    kb.adjust(1, 1)
    await c.message.edit_text("Tidak Rekomendasikan:", reply_markup=kb.as_markup())
    await c.answer()

@router.callback_query(F.data == "lowest:10")
async def lowest_run(c: CallbackQuery):
    # NOTE: butuh dataset win_rate atau power metric.
    text = "Gunakan: /lowest10\n(catatan: butuh win_rate/power metric di dataset)"
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Kembali", callback_data="menu:lowest")
    kb.adjust(1)
    await c.message.edit_text(text, reply_markup=kb.as_markup())
    await c.answer()

# =========================
# Back to root shortcut
# =========================
@router.callback_query(F.data == "menu:root")
async def back_root(c: CallbackQuery):
    await show_root_menu(c)
