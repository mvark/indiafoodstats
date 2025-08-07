import os
import sys
import requests
import pandas as pd
from datetime import datetime
from urllib.parse import quote

# --- CONFIG ---
BRAND = sys.argv[1] if len(sys.argv) > 1 else "amul"
BRAND_FILE = BRAND.lower().replace(" ", "_") + ".csv"
CSV_PATH = os.path.join("Brands", BRAND_FILE)
README_PATH = "README.md"
DATE_CUTOFF = "2025-07-21"
OFF_SQL_API = "https://mirabelle.openfoodfacts.org/products.json"

# --- Load existing product codes ---
try:
    existing_df = pd.read_csv(CSV_PATH, dtype=str)
    known_codes = set(existing_df["code"].dropna())
except FileNotFoundError:
    existing_df = pd.DataFrame()
    known_codes = set()

# --- SQL Query ---
sql = f"""
SELECT 
  code, product_name, brands, 
  "energy-kcal_100g", carbohydrates_100g, sugars_100g, 
  proteins_100g, fat_100g, "saturated-fat_100g", salt_100g,
  nova_group, nutriscore_grade, url
FROM [all]
WHERE 
  LOWER(brands) = '{BRAND.lower()}'
  AND countries_en = 'India'
  AND nova_group IN ('1', '2', '3', '4')
  AND nutriscore_grade IN ('a', 'b', 'c', 'd', 'e')
  AND datetime(last_modified_datetime) > '{DATE_CUTOFF}T00:00:00Z';
""".strip()

# --- Fetch data from OFF API ---
response = requests.get(f"{OFF_SQL_API}?sql={quote(sql)}&_shape=array")
if response.status_code != 200:
    print(f"❌ Failed to fetch data: {response.status_code}")
    sys.exit(1)

data = response.json()
df = pd.DataFrame(data)

# --- Filter out already known codes ---
if not df.empty:
    df = df[~df["code"].isin(known_codes)]

# --- Safeguard: Skip update if no real change ---
if df.empty:
    print("✅ No new valid records found. Nothing to update.")
    sys.exit(0)

# --- Append to CSV ---
combined_df = pd.concat([existing_df, df], ignore_index=True)
os.makedirs("Brands", exist_ok=True)
combined_df.to_csv(CSV_PATH, index=False)
print(f"✅ Added {len(df)} new records to {CSV_PATH}")

# --- Update README.md with last updated date ---
today = datetime.utcnow().strftime("%Y-%m-%d")

def update_readme_date(readme_path, brand, date_str):
    line_prefix = f"**Last updated for `{brand}`**:"
    updated_line = f"{line_prefix} {date_str}"
    lines = []
    updated = False

    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        for idx, line in enumerate(lines):
            if line.startswith(line_prefix):
                lines[idx] = updated_line + "\n"
                updated = True
                break

    if not updated:
        lines.append("\n" + updated_line + "\n")

    with open(readme_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"📅 Updated README.md with last updated date for {brand}")

update_readme_date(README_PATH, BRAND, today)

# --- Optional: Create Pull Request instead of direct push ---
# Enable this in GitHub Actions by replacing push step with:
# - uses: peter-evans/create-pull-request@v5
