from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext  # <--- Import baru
from core.states import BotStates           # <--- Import baru

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

# Trigger per aksi Hero (UPDATED WITH FSM)
@router.callback_query(F.data.startswith("hero:"))
async def hero_actions(c: CallbackQuery, state: FSMContext):
    action = c.data.split(":")[1]

    # Mapping aksi ke State yang sesuai
    state_mapping = {
        "build": (BotStates.waiting_for_hero_build, "🔧 Mode Build Aktif.\nSilakan ketik **Nama Hero** yang ingin kamu build (misal: Harith)."),
        "counter": (BotStates.waiting_for_hero_counter, "🛡 Mode Counter Aktif.\nSilakan ketik **Nama Hero** lawan yang ingin dicounter (misal: Fanny)."),
        "gameplay": (BotStates.waiting_for_hero_gameplay, "🎮 Mode Gameplay Aktif.\nSilakan ketik **Nama Hero** (misal: Ling)."),
        # Recounter sementara diarahkan ke counter biasa dulu
        "recounter": (BotStates.waiting_for_hero_counter, "🔁 Mode Recounter Aktif.\nSilakan ketik **Nama Hero** lawan (misal: Wanwan)."),
    }

    if action in state_mapping:
        target_state, reply_text = state_mapping[action]
        await state.set_state(target_state) # Bot sekarang "mengingat" dia lagi nunggu input
        
        # Tombol cancel
        kb = InlineKeyboardBuilder()
        kb.button(text="❌ Batal", callback_data="cancel_action")
        
        await c.message.edit_text(reply_text, reply_markup=kb.as_markup())
        await c.answer()
    
    elif action == "comp":
        # Komposisi tidak butuh input hero, arahkan ke command komposisi
        await c.message.edit_text("Gunakan command: /komposisi\n(Fitur auto-run bisa ditambahkan nanti)")
        await c.answer()
    
    else:
        await c.message.edit_text("Fitur ini belum tersedia.")
        await c.answer()

# Handler tombol Batal (BARU)
@router.callback_query(F.data == "cancel_action")
async def cancel_handler(c: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.clear()
    await c.message.edit_text("Aksi dibatalkan. Kembali ke menu utama.")
    # Kita panggil menu root lagi
    await show_root_menu(c)

# =========================
# Submenu: Tier List (Tidak berubah)
# =========================
@router.callback_query(F.data == "menu:tier")
async def menu_tier(c: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="⭐ Prioritas Rate", callback_data="tier:prio")
    kb.button(text="🧩 Role", callback_data="tier:role")
    kb.button(text="🗺 Lane", callback_data="tier:lane")
    kb.button(text="⬅️ Kembali", callback_data="menu:root")
    kb.adjust(2, 2)
    await c.message.edit_text("Menu lanjutan Tier List:", reply_markup=kb.as_markup())
    await c.answer()

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
    mapping = {
        "tier:pick10": "Gunakan: /pick10\n(catatan: butuh dataset pick_rate)",
        "tier:ban10": "Gunakan: /ban10\n(catatan: butuh dataset ban_rate)",
    }
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Kembali", callback_data="tier:prio")
    kb.adjust(1)
    await c.message.edit_text(mapping[c.data], reply_markup=kb.as_markup())
    await c.answer()

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
    text = f"Gunakan: /tierrole {role}"
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Kembali", callback_data="tier:role")
    kb.adjust(1)
    await c.message.edit_text(text, reply_markup=kb.as_markup())
    await c.answer()

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
# Submenu: Tidak Rekomendasikan (Tidak berubah)
# =========================
@router.callback_query(F.data == "menu:lowest")
async def menu_lowest(c: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="📉 10 Lowest", callback_data="lowest:10")
    kb.button(text="⬅️ Kembali", callback_data="menu:root")
    kb.adjust(1, 1)
    await c.message.edit_text("Tidak Rekomendasikan:", reply_markup=kb.as_markup())
    await c.answer()

@router.callback_query(F.data == "lowest:10")
async def lowest_run(c: CallbackQuery):
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