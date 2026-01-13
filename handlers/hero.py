# handlers/hero.py
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from core.states import BotStates

# Import DAL yang baru diperbaiki
from data.dal import get_hero_by_name

router = Router()

# =========================================================
# 1. LOGIC UTAMA: FORMAT & KIRIM PESAN BUILD
# =========================================================
async def send_hero_build(m: Message, hero_name: str):
    # 1. Cari data hero di CSV via DAL
    hero = get_hero_by_name(hero_name)
    
    if not hero:
        # Jika hero tidak ditemukan
        await m.answer(
            f"❌ Hero <b>{hero_name}</b> tidak ditemukan.\n"
            "Pastikan ejaan benar (contoh: <i>/build Miya</i>)."
        )
        return False

    # 2. Ambil data dari dictionary hero (sesuai kolom di HeroData.csv)
    name = hero.get('Hero', 'Unknown')
    role = hero.get('Role', '-')
    lane = hero.get('PrimaryLane', '-')
    sec_lane = hero.get('SecondaryLane', '-')
    dmg_type = hero.get('Type', '-')  # Kolom Type biasanya berisi Physical/Magic
    patch = hero.get('Patch', 'Terbaru')
    
    # Ambil 6 item
    items = [
        hero.get('Item1', '-'),
        hero.get('Item2', '-'),
        hero.get('Item3', '-'),
        hero.get('Item4', '-'),
        hero.get('Item5', '-'),
        hero.get('Item6', '-')
    ]
    
    # Bersihkan nama item (hapus nan/strip)
    build_list = []
    for i, item in enumerate(items, 1):
        if item and str(item).lower() != 'nan':
            build_list.append(f"{i}. {item}")
    
    build_text = "\n".join(build_list) if build_list else "Belum ada data item."

    # 3. Susun Pesan Jawaban (Format Rapi)
    response_text = (
        f"🛠 <b>Rekomendasi Build: {name}</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🎭 <b>Role:</b> {role}\n"
        f"📍 <b>Lane:</b> {lane} / {sec_lane}\n"
        f"⚔️ <b>Tipe:</b> {dmg_type}\n"
        f"🔖 <b>Patch:</b> {patch}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<b>⚔️ Core Build Item:</b>\n"
        f"{build_text}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<i>💡 Gunakan /counter {name} untuk melihat kelemahannya.</i>"
    )

    await m.answer(response_text)
    return True

# =========================================================
# 2. HANDLER COMMAND MANUAL (/build nama_hero)
# =========================================================
@router.message(Command("build"))
async def build_cmd(m: Message):
    """
    Contoh: /build Miya
    """
    text = m.text.strip()
    parts = text.split(maxsplit=1)
    
    if len(parts) < 2:
        await m.answer("Gunakan format: <code>/build NamaHero</code>\nContoh: <code>/build Gusion</code>")
        return

    hero_input = parts[1]
    await send_hero_build(m, hero_input)

# =========================================================
# 3. HANDLER INPUT DARI MENU (State FSM)
# =========================================================
@router.message(BotStates.waiting_for_hero_build)
async def process_build_input(m: Message, state: FSMContext):
    hero_name = m.text.strip()
    
    # Cek input batal
    if hero_name.lower() in ["batal", "cancel", "exit", "/cancel"]:
        await state.clear()
        await m.answer("✅ Aksi dibatalkan.")
        return

    # Panggil fungsi pengirim build
    success = await send_hero_build(m, hero_name)
    
    # Jika berhasil, reset state agar bot tidak nunggu input lagi
    # Jika gagal (hero typo), biarkan state aktif agar user bisa coba ketik ulang
    if success:
        await state.clear()

# =========================================================
# 4. HANDLER INFO HERO LAINNYA (/hero, /role)
# =========================================================
@router.message(Command("hero"))
async def hero_info_cmd(m: Message):
    """
    Menampilkan info dasar hero (sama kayak build tapi tanpa item detail, opsional)
    """
    # Gunakan logic yang sama dulu
    await build_cmd(m)