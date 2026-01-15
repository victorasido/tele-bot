import os
import asyncio
import json
from pathlib import Path
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# 1. SETUP API & MULTI-KEY
# ==========================================
KEYS_STRING = os.getenv("GEMINI_API_KEYS", "")
API_KEYS = [k.strip() for k in KEYS_STRING.split(",") if k.strip()]

if not API_KEYS:
    single = os.getenv("GEMINI_API_KEY")
    if single: API_KEYS = [single]

current_key_index = 0

def get_active_model():
    global current_key_index
    if not API_KEYS: return None
    genai.configure(api_key=API_KEYS[current_key_index])
    
    safety = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
    config = {"temperature": 0.7, "top_p": 0.95, "max_output_tokens": 1024}

    try:
        return genai.GenerativeModel("gemini-2.0-flash-lite", generation_config=config, safety_settings=safety)
    except:
        return genai.GenerativeModel("gemini-pro", generation_config=config, safety_settings=safety)

def rotate_key():
    global current_key_index
    if len(API_KEYS) > 1:
        current_key_index = (current_key_index + 1) % len(API_KEYS)
        print(f"🔄 [QUEUE] Switch Key ke Index: {current_key_index}")
        return True
    return False

# ==========================================
# 2. SISTEM CACHING (MEMORI)
# ==========================================
CACHE_FILE = Path(__file__).resolve().parent.parent / "data" / "ai_cache.json"

def load_cache():
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {}
    return {}

def save_to_cache(key, value):
    try:
        data = load_cache()
        data[key] = value
        # Pastikan folder data ada
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Gagal simpan cache: {e}")

# ==========================================
# 3. CORE LOGIC (INTERNAL)
# ==========================================
async def _process_gemini_request(payload: dict) -> str:
    if not API_KEYS: return "⚠️ API Key belum diisi."

    # Prompt Engineering
    task_type = payload.get("type", "chat")
    hero_data = payload.get("hero", {})
    user_input = payload.get("input", "")
    h_name = hero_data.get("Hero", str(user_input))
    h_role = hero_data.get("Role", "Unknown")
    
    context = f"Hero: {h_name} | Role: {h_role}"
    prompts = {
        "comp": f"Roleplay: Coach MLBB. Data: {context}. Draft Pick 5 Hero sinergi & Strategi.",
        "counter": f"Roleplay: Analis MLBB. Data: {context}. 3 Hard Counter & Tips Gameplay.",
        "gameplay": f"Roleplay: Top Global {h_name}. Data: {context}. Guide Mikro/Makro.",
        "tierlist": f"Tier List MLBB singkat: {user_input}.",
        "chat": f"Jawab singkat MLBB: {user_input}"
    }
    final_prompt = prompts.get(task_type, prompts["chat"])

    for attempt in range(2):
        try:
            model = get_active_model()
            if not model: return "❌ Init Error."
            response = await model.generate_content_async(final_prompt)
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                return "⚠️ Terblokir Safety Filter."
            return response.text.strip()
        except Exception as e:
            err = str(e)
            if "429" in err or "ResourceExhausted" in err:
                if rotate_key(): 
                    await asyncio.sleep(1)
                    continue
                return "⏳ Server Penuh."
            await asyncio.sleep(1)
    return "❌ Gagal koneksi AI."

# ==========================================
# 4. QUEUE WORKER
# ==========================================
request_queue = asyncio.Queue()

async def queue_worker():
    print("🚀 [SYSTEM] Smart Worker Berjalan (Cache + Queue)...")
    while True:
        payload, cache_key, future = await request_queue.get()
        try:
            result = await _process_gemini_request(payload)
            # Simpan ke cache jika sukses
            if "❌" not in result and "⏳" not in result:
                save_to_cache(cache_key, result)
            future.set_result(result)
        except Exception as e:
            future.set_exception(e)
        finally:
            request_queue.task_done()
            await asyncio.sleep(1.5) # Jeda aman

async def init_gemini_worker():
    asyncio.create_task(queue_worker())

# ==========================================
# 5. PUBLIC FUNCTION (ENTRY POINT)
# ==========================================
async def compose_with_gemini(payload: dict) -> str:
    # 1. GENERATE CACHE KEY
    task = payload.get("type", "chat")
    inp = payload.get("input", "")
    h_name = payload.get("hero", {}).get("Hero", inp)
    cache_key = f"{task}_{h_name}".lower().replace(" ", "_")

    # 2. CEK CACHE (JALUR CEPAT)
    memory = load_cache()
    if cache_key in memory:
        print(f"⚡ [CACHE HIT] {cache_key} ditemukan! Skip AI.")
        return memory[cache_key]

    # 3. MASUK ANTRIAN (JALUR LAMBAT)
    print(f"🐢 [CACHE MISS] {cache_key} masuk antrian...")
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    await request_queue.put((payload, cache_key, future))
    return await future