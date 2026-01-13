from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from data.dal import get_hero_by_name
from core.gemini import compose_with_gemini

router = Router()

@router.message(Command("comp"))
async def comp_cmd(m: Message):
    """
    Handler untuk command /comp <Hero>.
    Menggunakan AI untuk menyusun komposisi tim terbaik.
    """
    # 1. Validasi Input
    args = m.text.split(maxsplit=1)
    if len(args) < 2:
        await m.answer(
            "⚠️ <b>Format Salah</b>\n"
            "Gunakan: <code>/comp NamaHero</code>\n"
            "Contoh: <code>/comp Tigreal</code>"
        )
        return

    hero_name = args[1]
    
    # 2. Cek apakah Hero ada di Database (Validasi)
    # Ini penting agar AI mendapat konteks Role/Lane yang benar dari CSV
    hero_data = get_hero_by_name(hero_name)
    
    if not hero_data:
        await m.answer(f"❌ Hero <b>{hero_name}</b> tidak ditemukan di database.")
        return

    real_name = hero_data.get('Hero', hero_name)

    # 3. Tampilkan status "Sedang mengetik..." atau pesan Loading
    loading_msg = await m.answer(f"🤖 <b>Coach AI sedang meracik tim untuk {real_name}...</b>")

    # 4. Siapkan Payload untuk AI
    # Type 'comp' akan memicu prompt khusus pelatih pro di core/gemini.py
    payload = {
        "type": "comp",
        "hero": hero_data,  # Data CSV dikirim agar AI tau role hero ini
    }

    try:
        # 5. Minta jawaban dari Gemini
        response_text = compose_with_gemini(payload)
        
        # 6. Tampilkan Hasil
        # Kita edit pesan loading sebelumnya agar chat tidak nyampah
        await loading_msg.edit_text(
            response_text,
            parse_mode="Markdown" # Gemini biasanya pakai format markdown (**bold**)
        )
        
    except Exception as e:
        # Error handling jika terjadi masalah jaringan/API
        await loading_msg.edit_text(f"❌ Gagal mengambil analisis AI.\nError: {str(e)}")