import os
import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import AsyncOpenAI  # Library baru

load_dotenv()

# ==========================================
# 1. SETUP OPENAI (GANTIKAN GEMINI)
# ==========================================
API_KEY = os.getenv("OPENAI_API_KEY")
client = None

if API_KEY:
    client = AsyncOpenAI(api_key=API_KEY)
    print("✅ [SYSTEM] Menggunakan Engine: GPT-3.5 Turbo (OpenAI)")
else:
    print("❌ [CRITICAL] OPENAI_API_KEY belum diisi di .env!")

# ==========================================
# 2. SISTEM CACHING (BIAR IRIT SALDO)
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
# 3. CORE LOGIC (PANGGIL GPT)
# ==========================================
async def _process_request(payload: dict) -> str:
    if not client: return "⚠️ API Key OpenAI belum diisi."

    # Prompt Builder (Sama kayak kemaren)
    task_type = payload.get("type", "chat")
    hero_data = payload.get("hero", {})
    user_input = payload.get("input", "")
    h_name = hero_data.get("Hero", str(user_input))
    
    context = f"Hero: {h_name} | Role: {hero_data.get('Role','-')}"
    
    system_instruction = "You are a Professional Mobile Legends Coach & Analyst. Answer in Indonesian (Bahasa Gaul/Santai)."
    
    prompts = {
        "comp": f"Data: {context}. Buatkan Draft Pick 5 Hero yang sinergi banget sama {h_name}. Jelaskan strateginya.",
        "counter": f"Data: {context}. Sebutkan 3 HARD COUNTER buat {h_name}. Jelaskan kenapa skill mereka bikin {h_name} mati kutu.",
        "gameplay": f"Data: {context}. Kasih guide gameplay (Early, Mid, Late game) buat {h_name}. Apa combo skill mematikannya?",
        "tierlist": f"Buatkan Tier List Meta singkat untuk role/kategori: {user_input}.",
        "chat": f"Jawab pertanyaan MLBB ini: {user_input}"
    }
    user_prompt = prompts.get(task_type, prompts["chat"])

    try:
        # Panggil GPT-3.5-Turbo (Murah & Cepat)
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        err = str(e)
        print(f"⚠️ [ERROR GPT] {err}")
        if "insufficient_quota" in err:
            return "❌ Saldo API OpenAI Habis (Isi dulu di dashboard)."
        return f"❌ Error OpenAI: {err}"

# ==========================================
# 4. QUEUE WORKER (ANTRIAN)
# ==========================================
request_queue = asyncio.Queue()

async def queue_worker():
    print("🚀 [SYSTEM] GPT Worker Berjalan...")
    while True:
        payload, cache_key, future = await request_queue.get()
        try:
            result = await _process_request(payload)
            # Simpan ke cache kalau sukses (Biar gak bayar dobel buat pertanyaan sama)
            if "❌" not in result and "⚠️" not in result:
                save_to_cache(cache_key, result)
            future.set_result(result)
        except Exception as e:
            future.set_exception(e)
        finally:
            request_queue.task_done()
            await asyncio.sleep(0.5) # GPT lebih ngebut, jeda dikit aja

async def init_gemini_worker(): # Nama fungsi tetap biar gak usah ubah bot.py
    asyncio.create_task(queue_worker())

# ==========================================
# 5. ENTRY POINT
# ==========================================
async def compose_with_gemini(payload: dict) -> str: # Nama fungsi tetap
    task = payload.get("type", "chat")
    inp = payload.get("input", "")
    h_name = payload.get("hero", {}).get("Hero", inp)
    cache_key = f"{task}_{h_name}".lower().replace(" ", "_")

    # Cek Cache (Gratis)
    memory = load_cache()
    if cache_key in memory:
        print(f"⚡ [CACHE HIT] {cache_key} (Hemat Saldo!)")
        return memory[cache_key]

    # Masuk Antrian (Bayar)
    print(f"💸 [CACHE MISS] {cache_key} -> Request ke GPT...")
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    await request_queue.put((payload, cache_key, future))
    return await future