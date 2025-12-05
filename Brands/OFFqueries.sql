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

