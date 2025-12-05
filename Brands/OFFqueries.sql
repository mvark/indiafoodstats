/* 
Queries used while researching Open Food Facts data for UPF article
Mirabelle is OFF's hosted version of Datasette which runs on Sqlite - https://mirabelle.openfoodfacts.org/
*/

-- Top 5 Brands
SELECT
  LOWER(TRIM(brands)) AS brand,
  COUNT(*) AS product_count
FROM [all]
WHERE
  countries_en = 'India'
  AND TRIM(nova_group) IN ('1','2','3','4')
  AND TRIM(brands) <> ''
GROUP BY brand
ORDER BY product_count DESC
LIMIT 5;

/*
SQL query that takes top 5 brands on OFF and returns for each brand:

NOVA grouping

Product count for each NOVA group

Percentage distribution of NOVA 1–4

Brands sorted by total product count (descending)

Uses only products from India

Uses only valid NOVA values (1–4)
*/
SELECT
  code,
  product_name,
  brands,
  categories,
  nova_group,
  nutriscore_grade,
  url
FROM [all]
WHERE
  countries_en = 'India'
  AND TRIM(nova_group) IN ('1','2','3','4')
  AND LOWER(TRIM(brands)) IN (
    'amul',
    'britannia',
    'cadbury',
    'parle',
    'haldiram''s'
  )
ORDER BY brands, product_name;

-- NOVA % Distribution per Brand to use for chart in DataWrapper
WITH filtered AS (
  SELECT
    LOWER(TRIM(brands)) AS brand,
    TRIM(nova_group) AS nova
  FROM [all]
  WHERE countries_en = 'India'
    AND TRIM(nova_group) IN ('1','2','3','4')
    AND LOWER(TRIM(brands)) IN (
      'amul',
      'britannia',
      'cadbury',
      'parle',
      'haldiram''s'
    )
),
counts AS (
  SELECT
    brand,
    nova,
    COUNT(*) AS product_count
  FROM filtered
  GROUP BY brand, nova
),
totals AS (
  SELECT
    brand,
    SUM(product_count) AS total_products
  FROM counts
  GROUP BY brand
),
percentages AS (
  SELECT
    c.brand,
    c.nova,
    c.product_count,
    ROUND(100.0 * c.product_count / t.total_products, 2) AS pct
  FROM counts c
  JOIN totals t ON c.brand = t.brand
)
SELECT
  brand,
  SUM(CASE WHEN nova = '1' THEN pct ELSE 0 END) AS nova_1_pct,
  SUM(CASE WHEN nova = '2' THEN pct ELSE 0 END) AS nova_2_pct,
  SUM(CASE WHEN nova = '3' THEN pct ELSE 0 END) AS nova_3_pct,
  SUM(CASE WHEN nova = '4' THEN pct ELSE 0 END) AS nova_4_pct,
  (SELECT total_products FROM totals t WHERE t.brand = p.brand) AS total_products
FROM percentages p
GROUP BY brand
ORDER BY total_products DESC;

-- NOVA % Distribution & total_products per Brand 
WITH filtered AS (
  SELECT
    LOWER(TRIM(brands)) AS brand,
    TRIM(nova_group) AS nova
  FROM [all]
  WHERE countries_en = 'India'
    AND TRIM(nova_group) IN ('1','2','3','4')
    AND LOWER(TRIM(brands)) IN (
      'amul',
      'britannia',
      'cadbury',
      'parle',
      'haldiram''s'
    )
),
counts AS (
  SELECT
    brand,
    nova,
    COUNT(*) AS product_count
  FROM filtered
  GROUP BY brand, nova
),
totals AS (
  SELECT
    brand,
    SUM(product_count) AS total_products
  FROM counts
  GROUP BY brand
),
percentages AS (
  SELECT
    c.brand,
    c.nova,
    ROUND(100.0 * c.product_count / t.total_products, 2) AS pct
  FROM counts c
  JOIN totals t ON c.brand = t.brand
)
SELECT
  brand,
  SUM(CASE WHEN nova = '1' THEN pct ELSE 0 END) AS nova_1_pct,
  SUM(CASE WHEN nova = '2' THEN pct ELSE 0 END) AS nova_2_pct,
  SUM(CASE WHEN nova = '3' THEN pct ELSE 0 END) AS nova_3_pct,
  SUM(CASE WHEN nova = '4' THEN pct ELSE 0 END) AS nova_4_pct
FROM percentages
GROUP BY brand
ORDER BY brand;

-- Get the raw first ingredient (split on comma) from ingredients_text of Cadbury products in India
SELECT
  code,
  product_name,
  ingredients_text,
  TRIM(SUBSTR(ingredients_text, 1, INSTR(ingredients_text || ',', ',') - 1)) 
    AS first_ingredient
FROM [all]
WHERE 
  countries_en = 'India'
  AND LOWER(TRIM(brands)) = 'cadbury'
  AND TRIM(ingredients_text) <> ''
ORDER BY product_name;
