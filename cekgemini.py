import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load API Key dari .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ API Key tidak ditemukan di .env")
else:
    print(f"✅ API Key terdeteksi: {api_key[:5]}...*****")
    
    try:
        genai.configure(api_key=api_key)
        print("\n🔍 Sedang mengambil daftar model yang tersedia untuk key ini...")
        
        found_models = []
        for m in genai.list_models():
            # Kita cuma butuh model yang bisa generateContent (Chat)
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
                found_models.append(m.name)
        
        print("\nKESIMPULAN:")
        if "models/gemini-1.5-flash" in found_models:
            print("✅ gemini-1.5-flash TERSEDIA. Masalah mungkin di library/koneksi.")
        elif "models/gemini-pro" in found_models:
            print("⚠️ Flash tidak ada. GANTI kodingan core/gemini.py jadi 'gemini-pro'.")
        else:
            print("❌ Tidak ada model chat yang cocok. Cek billing/akun Google AI Studio.")
            
    except Exception as e:
        print(f"\n❌ Error saat koneksi: {e}")