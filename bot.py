import os
import asyncio
import json
from pathlib import Path
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# 1. SETUP API & MULTI-KEY (LEBIH BADAK)
# ==========================================
def load_api_keys():
    """Fungsi pembersih kunci biar gak ada spasi/enter nyelip"""
    raw_keys = os.getenv("GEMINI_API_KEYS", "")
    if not raw_keys:
        raw_keys = os.getenv("GEMINI_API_KEY", "") # Fallback lama
    
    # Pecah koma, lalu bersihkan spasi kiri/kanan setiap kunci
    cleaned_keys = [k.strip() for k in raw_keys.split(",") if k.strip()]
    
    if cleaned_keys:
        print(f"🔑 [SYSTEM] Berhasil memuat {len(cleaned_keys)} API Key.")
    else:
        print("❌ [CRITICAL] Tidak ada API Key yang terbaca dari .env!")
    
    return cleaned_keys

API_KEYS = load_api_keys()
current_key_index = 0

def get_active_model():
    global current_key_index
    if not API_KEYS: return None
    
    active_key = API_KEYS[current_key_index]
    
    # Debug print (hanya 5 huruf depan biar aman)
    # print(f"🔌 Menggunakan Key: {active_key[:5]}...") 

    genai.configure(api_key=active_key)
    
    safety = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
    config = {"temperature": 0.7, "top_p": 0.95, "max_output_tokens": 1024}

    # Prioritas Model: Flash Lite (Cepat) -> Flash -> Pro
    try:
        return genai.GenerativeModel("gemini-2.0-flash-lite", generation_config=config, safety_settings=safety)
    except:
        return genai.GenerativeModel("gemini-1.5-flash", generation_config=config, safety_settings=safety)

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
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Gagal simpan cache: {e}")

# ==========================================
# 3. CORE LOGIC
# ==========================================
async def _process_gemini_request(payload: dict) -> str:
    if not API_KEYS: return "⚠️ API Key belum diisi/terbaca."

    task_type = payload.get("type", "chat")
    hero_data = payload.get("hero", {})
    user_input = payload.get("input", "")
    h_name = hero_data.get("Hero", str(user_input))
    
    context = f"Hero: {h_name} | Role: {hero_data.get('Role','-')}"
    prompts = {
        "comp": f"Roleplay: Coach MLBB. Data: {context}. Draft Pick 5 Hero sinergi & Strategi.",
        "counter": f"Roleplay: Analis MLBB. Data: {context}. 3 Hard Counter & Tips Gameplay.",
        "gameplay": f"Roleplay: Top Global {h_name}. Data: {context}. Guide Mikro/Makro.",
        "tierlist": f"Tier List MLBB: {user_input}.",
        "chat": f"Jawab singkat MLBB: {user_input}"
    }
    final_prompt = prompts.get(task_type, prompts["chat"])

    for attempt in range(2):
        try:
            model = get_active_model()
            if not model: return "❌ Init Error."
            response = await model.generate_content_async(final_prompt)
            return response.text.strip()
        except Exception as e:
            err = str(e)
            print(f"⚠️ [ERROR API] {err}") # <--- INI PENTING BUAT DEBUG

            if "429" in err or "ResourceExhausted" in err:
                if rotate_key(): 
                    await asyncio.sleep(1)
                    continue
                return "⏳ Server Penuh."
            
            if "400" in err or "API_KEY_INVALID" in err:
                return "❌ API Key Invalid/Salah."
                
            await asyncio.sleep(1)
            
    return "❌ Gagal koneksi AI."

# ==========================================
# 4. QUEUE WORKER
# ==========================================
request_queue = asyncio.Queue()

async def queue_worker():
    print("🚀 [SYSTEM] Smart Worker Berjalan...")
    while True:
        payload, cache_key, future = await request_queue.get()
        try:
            result = await _process_gemini_request(payload)
            # Simpan jika bukan error
            if not result.startswith("❌") and not result.startswith("⏳") and not result.startswith("⚠️"):
                save_to_cache(cache_key, result)
            future.set_result(result)
        except Exception as e:
            future.set_exception(e)
        finally:
            request_queue.task_done()
            await asyncio.sleep(1.5) 

async def init_gemini_worker():
    asyncio.create_task(queue_worker())

# ==========================================
# 5. ENTRY POINT
# ==========================================
async def compose_with_gemini(payload: dict) -> str:
    task = payload.get("type", "chat")
    inp = payload.get("input", "")
    h_name = payload.get("hero", {}).get("Hero", inp)
    cache_key = f"{task}_{h_name}".lower().replace(" ", "_")

    memory = load_cache()
    if cache_key in memory:
        print(f"⚡ [CACHE HIT] {cache_key}")
        return memory[cache_key]

    print(f"🐢 [CACHE MISS] {cache_key} -> Queue")
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    await request_queue.put((payload, cache_key, future))
    return await future