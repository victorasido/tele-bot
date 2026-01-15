import asyncio
import os
from dotenv import load_dotenv
from data.dal import get_all_hero_names, get_hero_by_name
from core.gemini import compose_with_gemini, init_gemini_worker

# Load Env
load_dotenv()

async def warmup_process():
    print("🔥 MEMULAI PROSES WARMUP (PEMBELAJARAN OTOMATIS)...")
    print("⚠️  Pastikan API Key sudah diisi di .env")
    
    # Nyalakan Worker dulu biar antrian jalan
    await init_gemini_worker()
    
    # Ambil semua nama hero dari CSV
    heroes = get_all_hero_names()
    print(f"📋 Total Hero ditemukan: {len(heroes)}")
    
    # Fokus kita: Isi cache untuk fitur COUNTER (Paling sering dipake)
    tasks = []
    
    print("🚀 Mengirim tugas ke antrian...")
    for i, name in enumerate(heroes):
        hero_data = get_hero_by_name(name)
        if not hero_data: continue

        # Kita simulasikan request 'counter'
        payload = {
            "type": "counter",
            "hero": hero_data
        }
        
        # Panggil fungsi compose (dia bakal cek cache -> kalau null -> masuk queue)
        # Kita pakai asyncio.create_task biar paralel masuk antriannya
        task = asyncio.create_task(compose_with_gemini(payload))
        tasks.append(task)
        
        print(f"   [{i+1}/{len(heroes)}] Queued: Counter {name}")

    print("\n⏳ Menunggu Worker menyelesaikan semua tugas...")
    print("   (Bisa ditinggal ngopi, bot akan proses 1 hero per 1.5 detik)")
    
    # Tunggu semua selesai
    results = await asyncio.gather(*tasks)
    
    print("\n✅ WARMUP SELESAI!")
    print("💾 Cek file 'data/ai_cache.json' untuk melihat hasilnya.")

if __name__ == "__main__":
    try:
        asyncio.run(warmup_process())
    except KeyboardInterrupt:
        print("Warmup dihentikan.")