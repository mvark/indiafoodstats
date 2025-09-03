import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Brand list
BRANDS = [
    'amul','britannia','nestle','dabur','parle','patanjali','haldiram',
    'sunfeast','heritage',"kellogg's",'cadbury','maggi','nandini',
    'aashirvaad','milky mist','unibic','veeba','yoga bar','good life','saffola'
]

BASE_URL = "https://mirabelle.openfoodfacts.org/products.json?sql="

def encode_sql(sql):
    from urllib.parse import quote
    return quote(sql).replace("%20", "+")

def fetch_brand_data(brand):
    # Escape apostrophes in SQL string
    safe_brand = brand.replace("'", "''")
    sql = f"""
    SELECT
      CASE
        WHEN TRIM(nova_group) = '' OR nova_group IS NULL THEN 'Unrated'
        ELSE 'NOVA ' || nova_group
      END AS nova_status,
      COUNT(*) AS product_count
    FROM [all]
    WHERE countries_en = 'India'
      AND LOWER(brands) = '{safe_brand}'
    GROUP BY nova_status;
    """.strip()
    url = f"{BASE_URL}{encode_sql(sql)}&_shape=array"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    df = pd.DataFrame(data)
    df["brand"] = brand
    return df

# Collect data for all brands
dfs = []
for b in BRANDS:
    df = fetch_brand_data(b)
    dfs.append(df)
data = pd.concat(dfs, ignore_index=True)

# Pivot for stacked bar
pivot = data.pivot_table(index="brand", columns="nova_status",
                         values="product_count", fill_value=0)

# Convert to percentages
pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100

# Sort by % of NOVA 4 descending
if "NOVA 4" in pivot_pct.columns:
    pivot_pct = pivot_pct.sort_values("NOVA 4", ascending=False)

# Plot
plt.figure(figsize=(10, 8))
colors = {
    "NOVA 1": "#4caf50",   # Green
    "NOVA 2": "#ff9800",   # Orange
    "NOVA 3": "#9c27b0",   # Purple
    "NOVA 4": "#f44336",   # Red
    "Unrated": "#bdbdbd"   # Grey
}
pivot_pct[list(colors.keys())].plot(
    kind="barh", stacked=True, color=colors, ax=plt.gca()
)

plt.xlabel("Percentage of Products")
plt.ylabel("Brand")
plt.title("NOVA Classification of Products by Brand (India)", fontsize=14)
plt.legend(title="NOVA Group", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()

# Save
output_file = "Charts/nova_distribution_top20.png"
plt.savefig(output_file, dpi=150)
print(f"Chart saved as {output_file}")
