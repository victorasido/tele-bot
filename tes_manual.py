import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Ambil kunci manual
raw = os.getenv("GEMINI_API_KEYS", "")
keys = [k.strip() for k in raw.split(",") if k.strip()]

if not keys:
    print("❌ Gak ada kunci di .env!")
    exit()

print(f"🔍 Mengetes Key Pertama: {keys[0][:10]}...")

try:
    genai.configure(api_key=keys[0])
    model = genai.GenerativeModel('gemini-2.0-flash-lite')
    response = model.generate_content("Tes koneksi. Jawab 'OK' jika masuk.")
    print(f"✅ SUKSES: {response.text}")
except Exception as e:
    print(f"❌ GAGAL: {e}")
    print("\n💡 Kemungkinan Key Mati atau Salah Copy.")