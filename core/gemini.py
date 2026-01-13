import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Konfigurasi API Key
API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("[WARNING] GEMINI_API_KEY tidak ditemukan di .env")

# Konfigurasi Model
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024,
}

# Inisialisasi Model (Pakai gemini-2.0-flash sesuai akunmu)
try:
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash", 
        generation_config=generation_config
    )
except Exception as e:
    print(f"[ERROR INIT AI] Gagal load gemini-2.0-flash: {e}")
    model = genai.GenerativeModel("gemini-pro")

# --- FUNGSI ASYNC (AGAR TIDAK LEMOT) ---
async def compose_with_gemini(payload: dict) -> str:
    """
    Mengirim prompt ke Gemini secara Asynchronous.
    Bot tidak akan freeze saat menunggu jawaban.
    """
    if not API_KEY:
        return "⚠️ API Key belum diisi di .env"

    task_type = payload.get("type", "chat")
    hero_data = payload.get("hero", {})
    user_input = payload.get("input", "")

    # Ambil info hero
    hero_name = hero_data.get("Hero", user_input) if isinstance(hero_data, dict) else str(user_input)
    hero_role = hero_data.get("Role", "") if isinstance(hero_data, dict) else ""
    
    # Prompt Engineering
    prompts = {
        "comp": (
            f"Bertindaklah sebagai pelatih pro MLBB. User ingin bermain hero **{hero_name}** ({hero_role}).\n"
            f"Buatkan **Komposisi Tim 5 Hero** yang sempurna. Jelaskan synergy dan nama strateginya."
        ),
        "counter": (
            f"Bertindaklah sebagai analis MLBB. User kesulitan melawan hero **{hero_name}** ({hero_role}).\n"
            f"Sebutkan 3 Hero Counter Telak, Item Counter wajib, dan Tips Gameplay/Rotasi."
        ),
        "gameplay": (
            f"Buatkan panduan gameplay Micro & Macro untuk hero **{hero_name}** ({hero_role}).\n"
            f"Fokus pada Skill Combo, Fase Game (Early/Late), dan Power Spike."
        ),
        "tierlist": (
            f"Buatkan **Tier List Meta MLBB Terbaru** untuk role/lane: **{user_input}**.\n"
            f"Klasifikasikan ke Tier S, A, dan B beserta alasannya."
        ),
        "chat": f"Jawab singkat ala pro player: {user_input}"
    }

    final_prompt = prompts.get(task_type, prompts["chat"])

    try:
        # PENTING: Pakai await generate_content_async
        response = await model.generate_content_async(final_prompt)
        return response.text.strip()
    except Exception as e:
        return f"❌ Maaf, AI sedang sibuk/error. Detail: {str(e)}"