-- sql/03_mart.sql
-- Lapisan 3: Tabel Analisis dan Mart Terintegrasi (Mart Layer)
-- Mengacu pada PRD §4.1 dan PRD §5 (Langkah 1)

DROP TABLE IF EXISTS mart_orders;

CREATE TABLE mart_orders AS
WITH 
-- 1. Agregasi per Pesanan dari Tabel Items
items_agg AS (
    SELECT 
        i.order_id,
        COUNT(*) AS item_count,
        SUM(i.price) AS total_items_value,
        SUM(i.freight_value) AS total_freight_value,
        COUNT(DISTINCT i.seller_id) AS unique_sellers_count,
        MIN(i.seller_id) AS primary_seller_id,
        MIN(p.product_category) AS primary_category,
        AVG(p.product_weight_g) AS avg_product_weight_g
    FROM clean_order_items i
    LEFT JOIN clean_products p ON i.product_id = p.product_id
    GROUP BY i.order_id
),

-- 2. Agregasi per Pesanan dari Tabel Pembayaran
payments_agg AS (
    SELECT 
        order_id,
        SUM(payment_value) AS total_payment_value,
        MAX(payment_installments) AS max_installments,
        COUNT(payment_sequential) AS payment_count,
        MIN(payment_type) AS primary_payment_type
    FROM clean_order_payments
    GROUP BY order_id
),

-- 3. Agregasi per Pesanan dari Tabel Ulasan (Gunakan ulasan terburuk/terbaru jika duplikat)
reviews_agg AS (
    SELECT 
        order_id,
        MIN(review_score) AS min_review_score,
        AVG(review_score) AS avg_review_score,
        MAX(CASE WHEN review_score IN (1, 2) THEN 1 ELSE 0 END) AS is_bad_review,
        MAX(CASE WHEN review_comment_message IS NOT NULL AND TRIM(review_comment_message) != '' THEN 1 ELSE 0 END) AS has_review_text,
        MAX(review_comment_message) AS review_comment_message
    FROM clean_order_reviews
    GROUP BY order_id
)

-- 4. Penggabungan Utama (Master Mart Order Table)
SELECT 
    -- Identitas Pesanan & Pelanggan
    o.order_id,
    o.customer_id,
    c.customer_unique_id,
    c.customer_zip_code_prefix,
    c.customer_city,
    c.customer_state,
    o.order_status,
    
    -- Tanggal-tanggal Penting (ISO String Format)
    o.order_purchase_timestamp,
    o.order_approved_at,
    o.order_delivered_carrier_date,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    
    -- Durasi Pengiriman (Hari)
    ROUND(JULIANDAY(o.order_delivered_customer_date) - JULIANDAY(o.order_purchase_timestamp), 2) AS actual_delivery_days,
    ROUND(JULIANDAY(o.order_estimated_delivery_date) - JULIANDAY(o.order_purchase_timestamp), 2) AS estimated_delivery_days,
    ROUND(JULIANDAY(o.order_delivered_carrier_date) - JULIANDAY(o.order_purchase_timestamp), 2) AS seller_handling_days,
    ROUND(JULIANDAY(o.order_delivered_customer_date) - JULIANDAY(o.order_delivered_carrier_date), 2) AS carrier_transit_days,
    
    -- Target Bisnis Utama
    CASE 
        WHEN o.order_status = 'delivered' AND o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1
        WHEN o.order_status = 'delivered' THEN 0
        ELSE NULL 
    END AS is_late,
    
    -- Agregasi Barang & Seller
    COALESCE(i.item_count, 0) AS item_count,
    COALESCE(i.total_items_value, 0.0) AS total_items_value,
    COALESCE(i.total_freight_value, 0.0) AS total_freight_value,
    COALESCE(i.unique_sellers_count, 0) AS unique_sellers_count,
    i.primary_seller_id,
    s.seller_city,
    s.seller_state,
    COALESCE(i.primary_category, 'unknown') AS primary_category,
    i.avg_product_weight_g,
    
    -- Agregasi Pembayaran
    COALESCE(p.total_payment_value, 0.0) AS total_payment_value,
    COALESCE(p.max_installments, 1) AS max_installments,
    COALESCE(p.primary_payment_type, 'unknown') AS primary_payment_type,
    
    -- Agregasi Ulasan Pelanggan
    r.min_review_score,
    r.avg_review_score,
    COALESCE(r.is_bad_review, 0) AS is_bad_review,
    COALESCE(r.has_review_text, 0) AS has_review_text,
    r.review_comment_message

FROM clean_orders o
LEFT JOIN clean_customers c ON o.customer_id = c.customer_id
LEFT JOIN items_agg i ON o.order_id = i.order_id
LEFT JOIN clean_sellers s ON i.primary_seller_id = s.seller_id
LEFT JOIN payments_agg p ON o.order_id = p.order_id
LEFT JOIN reviews_agg r ON o.order_id = r.order_id;

-- Indexing untuk mempercepat query analisis dan pemodelan berikutnya
CREATE INDEX IF NOT EXISTS idx_mart_purchase_ts ON mart_orders(order_purchase_timestamp);
CREATE INDEX IF NOT EXISTS idx_mart_cust_unique ON mart_orders(customer_unique_id);
CREATE INDEX IF NOT EXISTS idx_mart_seller ON mart_orders(primary_seller_id);
CREATE INDEX IF NOT EXISTS idx_mart_category ON mart_orders(primary_category);
CREATE INDEX IF NOT EXISTS idx_mart_is_late ON mart_orders(is_late);
