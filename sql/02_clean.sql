-- sql/02_clean.sql
-- Lapisan 2: Pembersihan Data dan Penyelarasan Tipe (Clean Layer)
-- Tahap Pembersihan Data Historis

DROP TABLE IF EXISTS clean_customers;
CREATE TABLE clean_customers AS
SELECT 
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    TRIM(LOWER(customer_city)) AS customer_city,
    UPPER(customer_state) AS customer_state
FROM raw_customers;

DROP TABLE IF EXISTS clean_sellers;
CREATE TABLE clean_sellers AS
SELECT 
    seller_id,
    seller_zip_code_prefix,
    TRIM(LOWER(seller_city)) AS seller_city,
    UPPER(seller_state) AS seller_state
FROM raw_sellers;

DROP TABLE IF EXISTS clean_products;
CREATE TABLE clean_products AS
SELECT 
    p.product_id,
    COALESCE(t.product_category_name_english, p.product_category_name, 'unknown') AS product_category,
    p.product_name_lenght AS product_name_length,
    p.product_description_lenght AS product_description_length,
    p.product_photos_qty,
    p.product_weight_g,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm
FROM raw_products p
LEFT JOIN raw_category_translation t 
    ON p.product_category_name = t.product_category_name;

DROP TABLE IF EXISTS clean_orders;
CREATE TABLE clean_orders AS
SELECT 
    order_id,
    customer_id,
    order_status,
    order_purchase_timestamp,
    order_approved_at,
    order_delivered_carrier_date,
    order_delivered_customer_date,
    order_estimated_delivery_date
FROM raw_orders
-- Bersihkan 8 baris anomali status delivered tapi tanggal terima kosong
WHERE NOT (order_status = 'delivered' AND order_delivered_customer_date IS NULL);

DROP TABLE IF EXISTS clean_order_items;
CREATE TABLE clean_order_items AS
SELECT 
    order_id,
    order_item_id,
    product_id,
    seller_id,
    shipping_limit_date,
    CAST(price AS REAL) AS price,
    CAST(freight_value AS REAL) AS freight_value
FROM raw_order_items
WHERE price >= 0 AND freight_value >= 0;

DROP TABLE IF EXISTS clean_order_payments;
CREATE TABLE clean_order_payments AS
SELECT 
    order_id,
    payment_sequential,
    payment_type,
    payment_installments,
    CAST(payment_value AS REAL) AS payment_value
FROM raw_order_payments
WHERE payment_value >= 0;

DROP TABLE IF EXISTS clean_order_reviews;
CREATE TABLE clean_order_reviews AS
SELECT 
    review_id,
    order_id,
    CAST(review_score AS INTEGER) AS review_score,
    review_comment_title,
    review_comment_message,
    review_creation_date,
    review_answer_timestamp
FROM raw_order_reviews;
