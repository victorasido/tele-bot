import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)

# Config Model
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024,
}

try:
    # Menggunakan Gemini 2.0 Flash (Sesuai akunmu)
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash", 
        generation_config=generation_config
    )
except:
    model = genai.GenerativeModel("gemini-pro")

# --- PERUBAHAN UTAMA DI SINI (JADI ASYNC) ---
async def compose_with_gemini(payload: dict) -> str:
    """
    Versi ASYNC: Tidak memblokir bot saat menunggu jawaban.
    """
    if not API_KEY:
        return "⚠️ API Key belum diisi."

    task_type = payload.get("type", "chat")
    hero_data = payload.get("hero", {})
    user_input = payload.get("input", "")

    hero_name = hero_data.get("Hero", user_input) if isinstance(hero_data, dict) else str(user_input)
    hero_role = hero_data.get("Role", "") if isinstance(hero_data, dict) else ""
    
    # Prompt (Sama seperti sebelumnya, disingkat biar rapi di chat ini)
    prompts = {
        "comp": f"Bertindaklah sebagai pelatih pro MLBB. Buatkan komposisi tim untuk hero {hero_name} ({hero_role})...",
        "counter": f"Bertindaklah sebagai analis MLBB. Bagaimana cara counter hero {hero_name} ({hero_role})?...",
        "gameplay": f"Buatkan guide gameplay Micro & Macro untuk hero {hero_name} ({hero_role})...",
        "tierlist": f"Buatkan Tier List Meta MLBB terbaru untuk role {user_input}...",
        "chat": f"Jawab santai: {user_input}"
    }

    final_prompt = prompts.get(task_type, prompts["chat"])

    try:
        # PENTING: Pakai generate_content_async + await
        response = await model.generate_content_async(final_prompt)
        return response.text.strip()
    except Exception as e:
        return f"❌ Maaf, AI sedang sibuk. Error: {str(e)}"