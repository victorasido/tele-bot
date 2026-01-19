import os
from dotenv import load_dotenv

load_dotenv()

raw_keys = os.getenv("GEMINI_API_KEYS", "")
print(f"📂 Isi Mentah dari .env: '{raw_keys}'")

if not raw_keys:
    print("❌ PERINGATAN: Variabel GEMINI_API_KEYS kosong atau tidak ditemukan!")
    # Cek fallback
    single = os.getenv("GEMINI_API_KEY")
    print(f"   Cek Single Key: {single}")
else:
    # Simulasi cara bot memecah kunci
    key_list = [k.strip() for k in raw_keys.split(",") if k.strip()]
    
    print(f"\n🔍 Bot mendeteksi {len(key_list)} kunci:")
    for i, k in enumerate(key_list):
        status = "✅ OK"
        if '"' in k or "'" in k:
            status = "❌ ERROR (Ada Tanda Kutip)"
        elif " " in k:
            status = "❌ ERROR (Ada Spasi di tengah)"
        elif len(k) < 30:
            status = "⚠️ MENCURIGAKAN (Kependekan)"
            
        # Tampilkan 5 huruf depan & belakang aja biar aman
        mask = f"{k[:5]}...{k[-5:]}" if len(k) > 10 else k
        print(f"   {i+1}. {mask} -> {status}")

    print("\n💡 PETUNJUK:")
    print("- Kalau statusnya ERROR, hapus tanda kutip/spasi di .env")
    print("- Pastikan format: KEY1,KEY2,KEY3 (Rapat, dipisah koma)")