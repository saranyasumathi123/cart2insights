# =========================================================
# BUSINESS OVERVIEW
# =========================================================

TOTAL_ORDERS_QUERY = """
SELECT
    COUNT(*) AS total_orders
FROM orders;
"""


TOTAL_REVENUE_QUERY = """
SELECT
    ROUND(SUM(price), 2) AS total_revenue
FROM order_items;
"""


TOTAL_CUSTOMERS_QUERY = """
SELECT
    COUNT(*) AS total_customers
FROM customers;
"""


TOTAL_SELLERS_QUERY = """
SELECT
    COUNT(*) AS total_sellers
FROM sellers;
"""


AVERAGE_ORDER_VALUE_QUERY = """
SELECT
    ROUND(
        SUM(price) / COUNT(DISTINCT order_id),
        2
    ) AS average_order_value
FROM order_items;
"""


# =========================================================
# SALES ANALYSIS
# =========================================================

MONTHLY_REVENUE_QUERY = """
SELECT
    DATE_FORMAT(
        o.order_purchase_timestamp,
        '%Y-%m'
    ) AS month,
    ROUND(
        SUM(oi.price),
        2
    ) AS revenue
FROM orders o
JOIN order_items oi
    ON o.order_id = oi.order_id
GROUP BY month
ORDER BY month;
"""


CATEGORY_REVENUE_QUERY = """
SELECT
    COALESCE(
        t.product_category_name_english,
        p.product_category_name,
        'unknown'
    ) AS category,
    ROUND(
        SUM(oi.price),
        2
    ) AS revenue
FROM order_items oi
JOIN products p
    ON oi.product_id = p.product_id
LEFT JOIN product_category_translation t
    ON p.product_category_name =
       t.product_category_name
GROUP BY category
ORDER BY revenue DESC;
"""


TOP_PRODUCTS_QUERY = """
SELECT
    oi.product_id,
    COALESCE(
        t.product_category_name_english,
        p.product_category_name,
        'unknown'
    ) AS category,
    COUNT(*) AS total_items,
    ROUND(
        SUM(oi.price),
        2
    ) AS revenue
FROM order_items oi
JOIN products p
    ON oi.product_id = p.product_id
LEFT JOIN product_category_translation t
    ON p.product_category_name =
       t.product_category_name
GROUP BY
    oi.product_id,
    category
ORDER BY revenue DESC
LIMIT 10;
"""


# =========================================================
# SELLER ANALYSIS
# =========================================================

TOP_SELLERS_QUERY = """
SELECT
    seller_id,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(*) AS total_items,
    ROUND(
        SUM(price),
        2
    ) AS revenue
FROM order_items
GROUP BY seller_id
ORDER BY revenue DESC
LIMIT 10;
"""


# =========================================================
# PAYMENT ANALYSIS
# =========================================================

PAYMENT_METHOD_QUERY = """
SELECT
    payment_type,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(
        SUM(payment_value),
        2
    ) AS total_value
FROM order_payments
GROUP BY payment_type
ORDER BY total_orders DESC;
"""


# =========================================================
# DELIVERY ANALYSIS
# =========================================================

DELIVERY_QUERY = """
SELECT
    CASE
        WHEN order_delivered_customer_date
             <= order_estimated_delivery_date
        THEN 'On Time'
        ELSE 'Delayed'
    END AS delivery_status,

    COUNT(*) AS orders,

    ROUND(
        AVG(
            DATEDIFF(
                order_delivered_customer_date,
                order_purchase_timestamp
            )
        ),
        2
    ) AS average_delivery_days

FROM orders

WHERE order_delivered_customer_date IS NOT NULL
  AND order_estimated_delivery_date IS NOT NULL

GROUP BY delivery_status;
"""


