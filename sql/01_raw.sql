-- sql/01_raw.sql
-- Lapisan 1: Pengecekan dan Verifikasi Tabel Mentah (Raw Layer)
-- Tahap Pembersihan Data Historis

-- 1. Verifikasi Jumlah Baris Tiap Tabel Mentah
SELECT 'raw_orders' AS table_name, COUNT(*) AS row_count FROM raw_orders
UNION ALL
SELECT 'raw_order_items', COUNT(*) FROM raw_order_items
UNION ALL
SELECT 'raw_order_payments', COUNT(*) FROM raw_order_payments
UNION ALL
SELECT 'raw_order_reviews', COUNT(*) FROM raw_order_reviews
UNION ALL
SELECT 'raw_products', COUNT(*) FROM raw_products
UNION ALL
SELECT 'raw_sellers', COUNT(*) FROM raw_sellers
UNION ALL
SELECT 'raw_customers', COUNT(*) FROM raw_customers
UNION ALL
SELECT 'raw_geolocation', COUNT(*) FROM raw_geolocation
UNION ALL
SELECT 'raw_category_translation', COUNT(*) FROM raw_category_translation;

-- 2. Sampel Data Mentah Tabel Pesanan
SELECT 
    order_id, 
    customer_id, 
    order_status, 
    order_purchase_timestamp, 
    order_estimated_delivery_date
FROM raw_orders 
LIMIT 5;
