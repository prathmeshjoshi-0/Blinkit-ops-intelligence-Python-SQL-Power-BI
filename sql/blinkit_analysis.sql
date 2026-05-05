-- ============================================================
-- BLINKIT DELIVERY & CUSTOMER ANALYTICS
-- Author: Prathmesh Joshi
-- Tool: MySQL
-- Dataset: 5,000 Orders | 2,500 Customers | 268 Products
-- ============================================================

-- ============================================================
-- SECTION 1: BUSINESS KPIs
-- ============================================================

-- 1.1 Overall Business Summary
SELECT 
    COUNT(order_id)                          AS total_orders,
    ROUND(SUM(order_total), 2)               AS total_revenue,
    ROUND(AVG(order_total), 2)               AS avg_order_value,
    COUNT(DISTINCT customer_id)              AS unique_customers,
    COUNT(DISTINCT store_id)                 AS total_stores
FROM blinkit_orders;

-- 1.2 Delivery Status Breakdown
SELECT 
    delivery_status,
    COUNT(*)                                                          AS total_orders,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM blinkit_orders), 2) AS percentage
FROM blinkit_orders
GROUP BY delivery_status
ORDER BY total_orders DESC;

-- 1.3 Monthly Revenue Trend
SELECT 
    DATE_FORMAT(order_date, '%Y-%m')    AS month,
    COUNT(order_id)                     AS total_orders,
    ROUND(SUM(order_total), 2)          AS monthly_revenue,
    ROUND(AVG(order_total), 2)          AS avg_order_value
FROM blinkit_orders
GROUP BY month
ORDER BY month;

-- ============================================================
-- SECTION 2: DELIVERY PERFORMANCE ANALYSIS
-- ============================================================

-- 2.1 Overall Delivery Performance
SELECT 
    ROUND(AVG(delivery_time_minutes), 2)                                          AS avg_delivery_time_mins,
    ROUND(MIN(delivery_time_minutes), 2)                                          AS min_delivery_time,
    ROUND(MAX(delivery_time_minutes), 2)                                          AS max_delivery_time,
    COUNT(CASE WHEN delivery_status = 'On Time' THEN 1 END)                       AS on_time_orders,
    COUNT(CASE WHEN delivery_status != 'On Time' THEN 1 END)                      AS delayed_orders,
    ROUND(COUNT(CASE WHEN delivery_status != 'On Time' THEN 1 END) * 100.0 
          / COUNT(*), 2)                                                           AS delay_rate_pct
FROM blinkit_delivery_performance;

-- 2.2 Delay Reasons Analysis
SELECT 
    reasons_if_delayed,
    COUNT(*)     AS occurrences,
    ROUND(COUNT(*) * 100.0 / (
        SELECT COUNT(*) FROM blinkit_delivery_performance 
        WHERE reasons_if_delayed IS NOT NULL AND reasons_if_delayed != ''
    ), 2)        AS pct_of_delays
FROM blinkit_delivery_performance
WHERE reasons_if_delayed IS NOT NULL AND reasons_if_delayed != ''
GROUP BY reasons_if_delayed
ORDER BY occurrences DESC;

-- 2.3 Monthly Delay Rate Trend
SELECT 
    DATE_FORMAT(o.order_date, '%Y-%m')                                              AS month,
    COUNT(o.order_id)                                                               AS total_orders,
    COUNT(CASE WHEN o.delivery_status != 'On Time' THEN 1 END)                     AS delayed_orders,
    ROUND(COUNT(CASE WHEN o.delivery_status != 'On Time' THEN 1 END) * 100.0 
          / COUNT(*), 2)                                                            AS delay_rate_pct,
    ROUND(AVG(d.delivery_time_minutes), 2)                                          AS avg_delivery_time
FROM blinkit_orders o
JOIN blinkit_delivery_performance d ON o.order_id = d.order_id
GROUP BY month
ORDER BY month;

-- 2.4 Top 10 Delivery Partners by Performance (Window Function)
WITH partner_stats AS (
    SELECT 
        delivery_partner_id,
        COUNT(order_id)                      AS total_deliveries,
        ROUND(AVG(delivery_time_minutes), 2) AS avg_delivery_time,
        ROUND(AVG(distance_km), 2)           AS avg_distance_km,
        COUNT(CASE WHEN delivery_status != 'On Time' THEN 1 END) AS delayed_count
    FROM blinkit_delivery_performance
    GROUP BY delivery_partner_id
)
SELECT *,
    RANK() OVER (ORDER BY avg_delivery_time ASC)   AS speed_rank,
    RANK() OVER (ORDER BY delayed_count ASC)        AS reliability_rank
FROM partner_stats
ORDER BY speed_rank
LIMIT 10;

-- ============================================================
-- SECTION 3: CUSTOMER SEGMENTATION
-- ============================================================

-- 3.1 Revenue by Customer Segment
SELECT 
    c.customer_segment,
    COUNT(DISTINCT o.customer_id)       AS total_customers,
    COUNT(o.order_id)                   AS total_orders,
    ROUND(SUM(o.order_total), 2)        AS total_revenue,
    ROUND(AVG(o.order_total), 2)        AS avg_order_value,
    ROUND(SUM(o.order_total) * 100.0 / (SELECT SUM(order_total) FROM blinkit_orders), 2) AS revenue_share_pct
FROM blinkit_orders o
JOIN blinkit_customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_segment
ORDER BY total_revenue DESC;

-- 3.2 Top 10 Customers by Revenue (CTE + Window Function)
WITH customer_revenue AS (
    SELECT 
        o.customer_id,
        c.customer_name,
        c.customer_segment,
        c.area,
        COUNT(o.order_id)               AS total_orders,
        ROUND(SUM(o.order_total), 2)    AS total_spent,
        ROUND(AVG(o.order_total), 2)    AS avg_order_value
    FROM blinkit_orders o
    JOIN blinkit_customers c ON o.customer_id = c.customer_id
    GROUP BY o.customer_id, c.customer_name, c.customer_segment, c.area
)
SELECT *,
    RANK() OVER (ORDER BY total_spent DESC) AS revenue_rank
FROM customer_revenue
ORDER BY revenue_rank
LIMIT 10;

-- 3.3 Customer Segment vs Delivery Satisfaction
SELECT 
    c.customer_segment,
    ROUND(AVG(f.rating), 2)                                             AS avg_rating,
    COUNT(CASE WHEN f.sentiment = 'Positive' THEN 1 END)               AS positive_feedback,
    COUNT(CASE WHEN f.sentiment = 'Negative' THEN 1 END)               AS negative_feedback,
    ROUND(AVG(d.delivery_time_minutes), 2)                              AS avg_delivery_time
FROM blinkit_orders o
JOIN blinkit_customers c ON o.customer_id = c.customer_id
JOIN blinkit_customer_feedback f ON o.order_id = f.order_id
JOIN blinkit_delivery_performance d ON o.order_id = d.order_id
GROUP BY c.customer_segment
ORDER BY avg_rating DESC;

-- ============================================================
-- SECTION 4: PRODUCT & REVENUE ANALYSIS
-- ============================================================

-- 4.1 Top 10 Products by Revenue (Window Function)
SELECT 
    p.product_name,
    p.category,
    p.brand,
    SUM(oi.quantity)                            AS units_sold,
    ROUND(SUM(oi.quantity * oi.unit_price), 2)  AS total_revenue,
    ROUND(AVG(p.margin_percentage), 2)           AS avg_margin_pct,
    RANK() OVER (ORDER BY SUM(oi.quantity * oi.unit_price) DESC) AS revenue_rank
FROM blinkit_order_items oi
JOIN blinkit_products p ON oi.product_id = p.product_id
GROUP BY p.product_name, p.category, p.brand
ORDER BY revenue_rank
LIMIT 10;

-- 4.2 Category Performance Summary
SELECT 
    p.category,
    COUNT(DISTINCT p.product_id)                AS total_products,
    SUM(oi.quantity)                            AS units_sold,
    ROUND(SUM(oi.quantity * oi.unit_price), 2)  AS total_revenue,
    ROUND(AVG(p.margin_percentage), 2)           AS avg_margin_pct,
    ROUND(AVG(p.shelf_life_days), 1)            AS avg_shelf_life_days
FROM blinkit_order_items oi
JOIN blinkit_products p ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY total_revenue DESC;

-- 4.3 Payment Method Analysis
SELECT 
    payment_method,
    COUNT(*)                                AS total_orders,
    ROUND(SUM(order_total), 2)              AS total_revenue,
    ROUND(AVG(order_total), 2)              AS avg_order_value,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM blinkit_orders), 2) AS order_share_pct
FROM blinkit_orders
GROUP BY payment_method
ORDER BY total_revenue DESC;

-- ============================================================
-- SECTION 5: INVENTORY ANALYSIS
-- ============================================================

-- 5.1 Stock Status Classification (CTE)
WITH stock_status AS (
    SELECT 
        i.product_id,
        p.product_name,
        p.category,
        SUM(i.stock_received)               AS total_stock_received,
        SUM(i.damaged_stock)                AS total_damaged,
        ROUND(SUM(i.damaged_stock) * 100.0 / NULLIF(SUM(i.stock_received), 0), 2) AS damage_rate_pct
    FROM blinkit_inventory i
    JOIN blinkit_products p ON i.product_id = p.product_id
    GROUP BY i.product_id, p.product_name, p.category
)
SELECT 
    category,
    COUNT(product_id)               AS total_products,
    SUM(total_stock_received)       AS total_stock,
    SUM(total_damaged)              AS total_damaged,
    ROUND(AVG(damage_rate_pct), 2)  AS avg_damage_rate_pct
FROM stock_status
GROUP BY category
ORDER BY avg_damage_rate_pct DESC;

-- ============================================================
-- SECTION 6: FEEDBACK & SENTIMENT ANALYSIS
-- ============================================================

-- 6.1 Overall Sentiment Distribution
SELECT 
    sentiment,
    COUNT(*)    AS total_feedback,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM blinkit_customer_feedback), 2) AS percentage
FROM blinkit_customer_feedback
GROUP BY sentiment
ORDER BY total_feedback DESC;

-- 6.2 Rating by Feedback Category
SELECT 
    feedback_category,
    ROUND(AVG(rating), 2)                                               AS avg_rating,
    COUNT(*)                                                            AS total_reviews,
    COUNT(CASE WHEN sentiment = 'Negative' THEN 1 END)                 AS negative_count,
    COUNT(CASE WHEN sentiment = 'Positive' THEN 1 END)                 AS positive_count
FROM blinkit_customer_feedback
GROUP BY feedback_category
ORDER BY avg_rating ASC;

-- 6.3 Delivery Performance Impact on Rating (CTE)
WITH delivery_rating AS (
    SELECT 
        o.delivery_status,
        ROUND(AVG(f.rating), 2)     AS avg_rating,
        COUNT(f.feedback_id)        AS total_reviews,
        COUNT(CASE WHEN f.sentiment = 'Negative' THEN 1 END) AS negative_reviews
    FROM blinkit_orders o
    JOIN blinkit_customer_feedback f ON o.order_id = f.order_id
    GROUP BY o.delivery_status
)
SELECT *,
    RANK() OVER (ORDER BY avg_rating DESC) AS satisfaction_rank
FROM delivery_rating
ORDER BY satisfaction_rank;
