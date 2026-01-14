import pandas as pd
import glob
import os

# 1. Ambil semua file csv yang depannya 'build_meta2025' di folder datamine
files = glob.glob(os.path.join("datamine", "build_meta2025_*.csv"))

# 2. Baca dan gabungin jadi satu
df_list = [pd.read_csv(f) for f in files]
combined_df = pd.concat(df_list, ignore_index=True)

# 3. Simpan jadi file baru buat di-upload ke Google Sheets
combined_df.to_csv("datamine/FULL_HERO_DATA.csv", index=False)

print(f"Sukses gabungin {len(files)} file jadi 'datamine/FULL_HERO_DATA.csv'")