from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from core.states import BotStates

router = Router()

# =========================================================
# 1. ROOT MENU (Menu Utama)
# =========================================================
@router.message(CommandStart())
async def start(m: Message):
    await m.answer("Halo! 👋\nSaya adalah Asisten Mobile Legends.\nGunakan /menu atau klik tombol di bawah untuk mulai.")
    await show_root_menu(m)

@router.message(Command("menu"))
async def menu(m: Message):
    await show_root_menu(m)

async def show_root_menu(m: Message | CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="🧝‍♂️ Hero & Strategi", callback_data="menu:hero")
    kb.button(text="📊 Tier List Meta", callback_data="menu:tier")
    # Fitur 'lowest' bisa diaktifkan jika nanti ada datanya
    # kb.button(text="⛔ Tidak Rekomendasikan", callback_data="menu:lowest")
    kb.adjust(1)

    text = "<b>🤖 Main Menu</b>\nPilih kategori bantuan yang kamu butuhkan:"
    
    if isinstance(m, CallbackQuery):
        await m.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")
        await m.answer()
    else:
        await m.answer(text, reply_markup=kb.as_markup(), parse_mode="HTML")

# =========================================================
# 2. SUBMENU: HERO & STRATEGI
# =========================================================
@router.callback_query(F.data == "menu:hero")
async def menu_hero(c: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="🔧 Build Item", callback_data="hero:build")
    kb.button(text="🛡 Counter Hero", callback_data="hero:counter")
    kb.button(text="🔁 Recounter", callback_data="hero:recounter")
    kb.button(text="🎮 Gameplay Guide", callback_data="hero:gameplay")
    kb.button(text="👥 Komposisi Team", callback_data="hero:comp")
    kb.button(text="⬅️ Kembali", callback_data="menu:root")
    kb.adjust(2, 2, 1, 1)

    await c.message.edit_text(
        "<b>⚔️ Menu Strategi Hero</b>\nPilih fitur yang ingin digunakan:", 
        reply_markup=kb.as_markup(), 
        parse_mode="HTML"
    )
    await c.answer()

# --- LOGIC PENANGKAP TOMBOL HERO (PENTING) ---
@router.callback_query(F.data.startswith("hero:"))
async def hero_actions(c: CallbackQuery, state: FSMContext):
    action = c.data.split(":")[1]

    # Mapping setiap tombol ke Memory (State) dan Pesan Instruksi
    state_mapping = {
        "build": (
            BotStates.waiting_for_hero_build, 
            "🔧 <b>Mode Build Item</b>\nKetik nama hero yang ingin kamu build (contoh: <i>Layla</i>)."
        ),
        "counter": (
            BotStates.waiting_for_hero_counter, 
            "🛡 <b>Mode Counter Hero</b>\nKetik nama hero musuh yang ingin kamu lawan (contoh: <i>Fanny</i>)."
        ),
        "recounter": (
            BotStates.waiting_for_hero_counter, 
            "🔁 <b>Mode Recounter</b>\nKetik nama hero musuh yang menyulitkanmu (contoh: <i>Wanwan</i>)."
        ),
        "gameplay": (
            BotStates.waiting_for_hero_gameplay, 
            "🎮 <b>Mode Gameplay Guide</b>\nKetik nama hero yang ingin kamu pelajari (contoh: <i>Gusion</i>)."
        ),
        "comp": (
            BotStates.waiting_for_hero_comp, 
            "👥 <b>Mode Komposisi Tim</b>\nKetik nama hero andalanmu, Coach AI akan mencarikan teman setim yang cocok (contoh: <i>Tigreal</i>)."
        ),
    }

    if action in state_mapping:
        target_state, reply_text = state_mapping[action]
        
        # Aktifkan State (Bot mulai menyimak input user)
        await state.set_state(target_state)
        
        # Tombol Batal untuk keluar dari mode input
        kb = InlineKeyboardBuilder()
        kb.button(text="❌ Batal", callback_data="cancel_action")
        
        await c.message.edit_text(reply_text, reply_markup=kb.as_markup(), parse_mode="HTML")
        await c.answer()
    
    else:
        await c.message.edit_text("⚠️ Fitur ini sedang dalam pengembangan.")
        await c.answer()

# Handler Tombol Batal (Universal)
@router.callback_query(F.data == "cancel_action")
async def cancel_handler(c: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.clear()
    
    await c.answer("Aksi dibatalkan")
    # Kembali ke menu utama setelah batal
    await show_root_menu(c)

# =========================================================
# 3. SUBMENU: TIER LIST (META)
# =========================================================
@router.callback_query(F.data == "menu:tier")
async def menu_tier(c: CallbackQuery):
    kb = InlineKeyboardBuilder()
    # kb.button(text="⭐ Prioritas Rate", callback_data="tier:prio") # Bisa diaktifkan kalau ada data
    kb.button(text="🧩 By Role", callback_data="tier:role")
    kb.button(text="🗺 By Lane", callback_data="tier:lane")
    kb.button(text="⬅️ Kembali", callback_data="menu:root")
    kb.adjust(2, 1)
    
    await c.message.edit_text(
        "<b>📊 Tier List Meta</b>\nLihat tren hero terkuat berdasarkan:", 
        reply_markup=kb.as_markup(), 
        parse_mode="HTML"
    )
    await c.answer()

# Pilihan Role
@router.callback_query(F.data == "tier:role")
async def tier_role(c: CallbackQuery):
    kb = InlineKeyboardBuilder()
    roles = ["Tank", "Fighter", "Marksman", "Mage", "Assassin", "Support"]
    
    for r in roles:
        kb.button(text=r, callback_data=f"tier:role:{r.lower()}")
    
    kb.button(text="⬅️ Kembali", callback_data="menu:tier")
    kb.adjust(3, 3, 1)
    
    await c.message.edit_text("Pilih <b>Role</b> untuk melihat Tier List:", reply_markup=kb.as_markup(), parse_mode="HTML")
    await c.answer()

# Pilihan Lane
@router.callback_query(F.data == "tier:lane")
async def tier_lane(c: CallbackQuery):
    kb = InlineKeyboardBuilder()
    lanes = ["Roam", "Exp", "Mid", "Gold", "Jungle"]
    
    for l in lanes:
        kb.button(text=l, callback_data=f"tier:lane:{l.lower()}")
        
    kb.button(text="⬅️ Kembali", callback_data="menu:tier")
    kb.adjust(3, 2, 1)
    
    await c.message.edit_text("Pilih <b>Lane</b> untuk melihat Tier List:", reply_markup=kb.as_markup(), parse_mode="HTML")
    await c.answer()

# =========================================================
# 4. NAVIGATION SHORTCUTS
# =========================================================
@router.callback_query(F.data == "menu:root")
async def back_root(c: CallbackQuery):
    await show_root_menu(c)