import os
import asyncio
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)

# --- SAFETY SETTINGS (Anti Baper) ---
safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024,
}

# --- UPDATE MODEL: Pindah ke FLASH-LITE (Lebih Tahan Banting) ---
try:
    # Prioritas 1: Gemini 2.0 Flash Lite (Kuota 30 RPM - Lebih Banyak)
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-lite",
        generation_config=generation_config,
        safety_settings=safety_settings
    )
except Exception:
    try:
        # Prioritas 2: Gemini 2.0 Flash (Kuota 15 RPM)
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-lite", 
            generation_config=generation_config,
            safety_settings=safety_settings
        )
    except:
        # Fallback terakhir
        model = genai.GenerativeModel("gemini-pro", safety_settings=safety_settings)

async def compose_with_gemini(payload: dict, retries=2) -> str:
    if not API_KEY:
        return "⚠️ API Key belum diisi."

    # -- Persiapan Prompt --
    task_type = payload.get("type", "chat")
    hero_data = payload.get("hero", {})
    user_input = payload.get("input", "")

    hero_name = hero_data.get("Hero", user_input) if isinstance(hero_data, dict) else str(user_input)
    hero_role = hero_data.get("Role", "") if isinstance(hero_data, dict) else ""
    
    prompts = {
        "comp": (
            f"Roleplay: Pro Coach MLBB. Konteks: Game Strategy.\n"
            f"User pick hero **{hero_name}** ({hero_role}).\n"
            f"Buatkan draft pick tim 5 hero yang sinergi & nama strateginya."
        ),
        "counter": (
            f"Roleplay: Analis MLBB. Konteks: Game Strategy.\n"
            f"Musuh pick **{hero_name}** ({hero_role}).\n"
            f"Sebutkan 3 Hero Counter (Hard Counter), Item Counter, dan Tips Gameplay."
        ),
        "gameplay": (
            f"Roleplay: Guide MLBB. Konteks: Game Strategy.\n"
            f"Guide **{hero_name}** ({hero_role}): Combo Skill, Power Spike, Rotasi."
        ),
        "tierlist": (
            f"Tier List Meta MLBB terbaru untuk: **{user_input}**.\n"
            f"Klasifikasikan Tier S, A, B. Singkat saja."
        ),
        "chat": f"Jawab singkat soal MLBB: {user_input}"
    }

    final_prompt = prompts.get(task_type, prompts["chat"])

    # -- RETRY LOGIC --
    for attempt in range(retries + 1):
        try:
            response = await model.generate_content_async(final_prompt)
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                return "⚠️ Konten diblokir filter AI."
            return response.text.strip()

        except Exception as e:
            error_msg = str(e)
            # Jika server penuh (429), kita tunggu lebih lama (3-5 detik)
            if "429" in error_msg or "ResourceExhausted" in error_msg:
                if attempt < retries:
                    wait_time = 3 * (attempt + 1) # Tunggu 3 detik, lalu 6 detik
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    return "⏳ Server AI lagi rame banget (Limit Habis). Coba 1 menit lagi ya!"
            
            print(f"[ERROR GEMINI] Attempt {attempt+1}: {e}")
            if attempt < retries:
                await asyncio.sleep(1)
                continue
            
    return "❌ Gagal terhubung ke AI."