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
    print("[WARNING] GEMINI_API_KEY tidak ditemukan di .env. Fitur AI tidak akan jalan.")

# Konfigurasi Model (Gunakan gemini-1.5-flash agar cepat & hemat, atau gemini-pro)
generation_config = {
    "temperature": 0.7,      # Kreativitas: 0.7 pas untuk strategi game
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024, # Batasi panjang jawaban biar gak spam
}

# Inisialisasi Model
try:
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash", 
        generation_config=generation_config
    )
except:
    # Fallback jika model flash belum tersedia di akun user
    model = genai.GenerativeModel("gemini-pro")

def compose_with_gemini(payload: dict) -> str:
    """
    Fungsi sentral untuk komunikasi dengan Gemini AI.
    
    Args:
        payload (dict): Harus berisi:
            - 'type': 'comp', 'counter', 'gameplay', 'tierlist', 'chat'
            - 'hero': (dict) Data hero dari CSV (opsional)
            - 'input': (str) Input tambahan user (opsional)
            
    Returns:
        str: Jawaban dari AI
    """
    if not API_KEY:
        return (
            "⚠️ **Fitur AI belum aktif.**\n"
            "API Key Gemini tidak ditemukan. Silakan isi `GEMINI_API_KEY` di file `.env`."
        )

    # Ekstrak data payload
    task_type = payload.get("type", "chat")
    hero_data = payload.get("hero", {})
    user_input = payload.get("input", "")

    # Ambil info hero biar AI tau konteks (cegah halusinasi role)
    hero_name = hero_data.get("Hero", user_input) if isinstance(hero_data, dict) else str(user_input)
    hero_role = hero_data.get("Role", "") if isinstance(hero_data, dict) else ""
    
    # --- PROMPT ENGINEERING (OTAK STRATEGI) ---
    prompts = {
        "comp": (
            f"Bertindaklah sebagai pelatih pro Mobile Legends. User ingin bermain hero **{hero_name}** (Role: {hero_role}).\n"
            f"Tugas: Buatkan **Draft Pick / Komposisi Tim 5 Hero** yang sempurna untuk menemani {hero_name} di Meta saat ini.\n\n"
            f"Syarat:\n"
            f"1. Sebutkan 4 hero teman satu tim (Lengkap: Roam, Mid, Gold, Exp, Jungle).\n"
            f"2. Jelaskan 'Team Synergy': Kenapa hero-hero ini cocok (misal: Combo Ulti, Cover, CC Chain).\n"
            f"3. Berikan nama strategi tim ini (contoh: 'Wombo Combo Area' atau 'Pick-off Strategy').\n"
            f"Gunakan format poin-poin yang rapi."
        ),
        
        "counter": (
            f"Bertindaklah sebagai analis data MLBB. User kesulitan melawan hero **{hero_name}** ({hero_role}).\n"
            f"Tugas: Berikan strategi untuk mengalahkan {hero_name}.\n\n"
            f"Jelaskan:\n"
            f"1. **Hero Counter Telak**: Sebutkan 3 hero yang skill-nya membatalkan {hero_name} (Hard Counter) dan alasannya.\n"
            f"2. **Item Counter**: Item apa yang wajib dibeli untuk menahan damage/efek {hero_name}?\n"
            f"3. **Tips Gameplay**: Cara rotasi atau posisi saat melawan {hero_name} (misal: 'Jangan berkumpul', 'Invade jungle-nya')."
        ),
        
        "gameplay": (
            f"Buatkan panduan 'Micro & Macro' gameplay untuk hero **{hero_name}** ({hero_role}).\n"
            f"Fokus pada:\n"
            f"1. **Skill Combo**: Urutan skill paling mematikan.\n"
            f"2. **Fase Game**: Apa yang harus dilakukan di Early Game (0-5 menit) vs Late Game (12+ menit).\n"
            f"3. **Power Spike**: Kapan hero ini paling kuat?\n"
            f"4. **Tips Mekanik**: Trik rahasia yang jarang diketahui user biasa."
        ),
        
        "tierlist": (
            f"Buatkan **Tier List Meta Mobile Legends Terbaru** untuk kategori/role: **{user_input}**.\n"
            f"Klasifikasikan hero ke dalam:\n"
            f"- 🔥 **Tier S (Priortias Pick/Ban)**: Hero OP saat ini.\n"
            f"- ✨ **Tier A (Meta)**: Hero kuat dan stabil.\n"
            f"- 🛡 **Tier B (Situasional)**: Bagus di kondisi tertentu.\n\n"
            f"Berikan alasan singkat kenapa hero Tier S sangat kuat di patch ini."
        ),
        
        "chat": (
            f"Jawab pertanyaan user tentang Mobile Legends ini dengan gaya santai ala pro player: \"{user_input}\".\n"
            f"Pastikan jawaban singkat, padat, dan akurat secara taktis."
        )
    }

    # Pilih prompt yang sesuai
    final_prompt = prompts.get(task_type, prompts["chat"])

    try:
        # Kirim request ke AI
        response = model.generate_content(final_prompt)
        return response.text.strip()
    except Exception as e:
        # Error Handling (misal: Safety trigger atau kuota habis)
        print(f"[ERROR GEMINI] {e}")
        return (
            "❌ **Maaf, AI sedang ngambek (Error).**\n"
            "Mungkin server sedang sibuk atau safety filter terpicu.\n"
            "Silakan coba lagi nanti atau gunakan pertanyaan yang berbeda."
        )