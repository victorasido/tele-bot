import os, json
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM = (
  "Kamu analis MLBB. Jangan menambahkan hero atau item di luar payload JSON.\n"
  "Jika data kurang, katakan: data belum tersedia di dataset.\n"
  "Jawab ringkas (maks 6 baris) dan to-the-point."
)

def compose_with_gemini(payload: dict) -> str:
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""{SYSTEM}

Buat rekomendasi build untuk {payload.get('hero',{}).get('Hero','-')}
lane {payload.get('input',{}).get('lane','-')} vs {payload.get('input',{}).get('enemy_mix','-')}.
Gunakan HANYA data berikut (JSON). Format:
1) (Opsional) Peringatan lane
2) Build: Boots | Core(2) | Situasional(2-3) | Emblem | Spell
3) Alasan singkat (hubungkan item dengan kebutuhan hero/komposisi lawan)

JSON:
{json.dumps(payload, ensure_ascii=False)}
"""
    resp = model.generate_content(prompt)
    return resp.text
