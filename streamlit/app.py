import streamlit as st
import pandas as pd

from database import get_connection
from utils import (
    format_currency,
    format_number,
    create_bar_chart,
    create_line_chart
)

import queries


# -----------------------------
# PAGE CONFIGURATION
# -----------------------------

st.set_page_config(
    page_title="Cart2Insights",
    page_icon="🛒",
    layout="wide"
)


# -----------------------------
# TITLE
# -----------------------------

st.title("🛒 Cart2Insights")
st.subheader("Decoding E-Commerce Performance")

st.write(
    "Interactive e-commerce analytics dashboard "
    "covering sales, customers, products, sellers, "
    "delivery performance and customer experience."
)


# -----------------------------
# DATABASE CONNECTION
# -----------------------------

try:

    connection = get_connection()

except Exception as e:

    st.error(
        "Database connection failed. "
        "Please check database.py."
    )

    st.stop()


# -----------------------------
# HELPER FUNCTION
# -----------------------------

def run_query(query):

    return pd.read_sql(
        query,
        connection
    )


# =========================================================
# BUSINESS OVERVIEW
# =========================================================

st.header("📊 Business Overview")

try:

    total_orders = run_query(
        queries.TOTAL_ORDERS_QUERY
    ).iloc[0, 0]

    total_revenue = run_query(
        queries.TOTAL_REVENUE_QUERY
    ).iloc[0, 0]

    total_customers = run_query(
        queries.TOTAL_CUSTOMERS_QUERY
    ).iloc[0, 0]

    total_sellers = run_query(
        queries.TOTAL_SELLERS_QUERY
    ).iloc[0, 0]

    average_order_value = run_query(
        queries.AVERAGE_ORDER_VALUE_QUERY
    ).iloc[0, 0]


    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "📦 Total Orders",
            format_number(total_orders)
        )

    with col2:
        st.metric(
            "💰 Product Revenue",
            format_currency(total_revenue)
        )

    with col3:
        st.metric(
            "👥 Customers",
            format_number(total_customers)
        )

    with col4:
        st.metric(
            "🏪 Sellers",
            format_number(total_sellers)
        )

    with col5:
        st.metric(
            "🛒 Average Order Value",
            format_currency(average_order_value)
        )

except Exception as e:

    st.error(f"Business overview error: {e}")


# =========================================================
# SALES ANALYSIS
# =========================================================

st.header("💰 Sales Analysis")


# -----------------------------
# Monthly Revenue
# -----------------------------

st.subheader("📈 Monthly Revenue")

try:

    monthly_revenue = run_query(
        queries.MONTHLY_REVENUE_QUERY
    )

    fig = create_line_chart(
        monthly_revenue,
        "month",
        "revenue",
        "Monthly Revenue Trend",
        "Month",
        "Revenue (₹)"
    )

    st.pyplot(fig)

except Exception as e:

    st.error(f"Monthly revenue error: {e}")


# -----------------------------
# Revenue by Category
# -----------------------------

st.subheader("📊 Revenue by Category")

try:

    category_revenue = run_query(
        queries.CATEGORY_REVENUE_QUERY
    ).head(10)

    fig = create_bar_chart(
        category_revenue,
        "category",
        "revenue",
        "Top 10 Categories by Revenue",
        "Category",
        "Revenue (₹)",
        45
    )

    st.pyplot(fig)

except Exception as e:

    st.error(f"Category revenue error: {e}")


# -----------------------------
# Top Products
# -----------------------------

st.subheader("🛍️ Top 10 Products")

try:

    top_products = run_query(
        queries.TOP_PRODUCTS_QUERY
    )

    st.dataframe(
        top_products,
        use_container_width=True
    )

except Exception as e:

    st.error(f"Product analysis error: {e}")


# =========================================================
# CUSTOMER ANALYSIS
# =========================================================

st.header("👥 Customer Analysis")


# -----------------------------
# Customer Spending
# -----------------------------

st.subheader("📊 Customer Spending")

try:

    customer_spending = run_query("""
        SELECT
            c.customer_unique_id,
            COUNT(DISTINCT o.order_id) AS total_orders,
            ROUND(
                SUM(oi.price + oi.freight_value),
                2
            ) AS total_spending
        FROM customers c
        JOIN orders o
            ON c.customer_id = o.customer_id
        JOIN order_items oi
            ON o.order_id = oi.order_id
        GROUP BY c.customer_unique_id
        ORDER BY total_spending DESC;
    """)

    st.dataframe(
        customer_spending.head(10),
        use_container_width=True
    )

except Exception as e:

    st.error(f"Customer spending error: {e}")


# -----------------------------
# One-Time vs Repeat Customers
# -----------------------------

st.subheader("🔄 One-Time vs Repeat Customers")

try:

    customer_type = run_query("""
        SELECT
            CASE
                WHEN total_orders > 1
                THEN 'Repeat Customer'
                ELSE 'One-time Customer'
            END AS customer_type,
            COUNT(*) AS customers
        FROM (
            SELECT
                c.customer_unique_id,
                COUNT(DISTINCT o.order_id) AS total_orders
            FROM customers c
            JOIN orders o
                ON c.customer_id = o.customer_id
            GROUP BY c.customer_unique_id
        ) AS customer_orders
        GROUP BY customer_type;
    """)

    st.dataframe(
        customer_type,
        use_container_width=True
    )

    fig = create_bar_chart(
        customer_type,
        "customer_type",
        "customers",
        "One-Time vs Repeat Customers",
        "Customer Type",
        "Number of Customers"
    )

    st.pyplot(fig)

except Exception as e:

    st.error(f"Customer type analysis error: {e}")


# =========================================================
# CUSTOMER EXPERIENCE
# =========================================================

st.header("⭐ Customer Experience")


# -----------------------------
# Review Score Distribution
# -----------------------------

st.subheader("⭐ Review Score Distribution")

try:

    review_data = run_query("""
        SELECT
            review_score,
            COUNT(*) AS review_count
        FROM order_reviews
        GROUP BY review_score
        ORDER BY review_score;
    """)

    st.dataframe(
        review_data,
        use_container_width=True
    )

    fig = create_bar_chart(
        review_data,
        "review_score",
        "review_count",
        "Customer Review Score Distribution",
        "Review Score",
        "Number of Reviews"
    )

    st.pyplot(fig)

except Exception as e:

    st.error(f"Review analysis error: {e}")


# -----------------------------
# Average Review Score
# -----------------------------

st.subheader("📊 Average Review Score")

try:

    average_review = run_query("""
        SELECT
            ROUND(
                AVG(review_score),
                2
            ) AS average_review_score
        FROM order_reviews;
    """)

    average_score = average_review.iloc[0]["average_review_score"]

    if pd.notna(average_score):

        st.metric(
            "⭐ Average Customer Review",
            f"{average_score:.2f}"
        )

except Exception as e:

    st.error(f"Average review error: {e}")


# =========================
# SELLER ANALYSIS
# =========================

st.header("🏪 Seller Analysis")

seller_data = run_query(queries.TOP_SELLERS_QUERY)

# Create a clean display name
seller_data["seller_name"] = [
    f"Seller {i+1}" for i in range(len(seller_data))
]

# Add rank
seller_data["rank"] = range(1, len(seller_data) + 1)

# Display clean table
display_sellers = seller_data[
    ["rank", "seller_name", "total_orders", "total_items", "revenue"]
].copy()

display_sellers.columns = [
    "Rank",
    "Seller",
    "Orders",
    "Items",
    "Revenue"
]

display_sellers["Revenue"] = display_sellers["Revenue"].apply(
    lambda x: f"₹{x:,.2f}"
)

st.subheader("🏆 Top 10 Sellers by Revenue")

st.dataframe(
    display_sellers,
    use_container_width=True,
    hide_index=True
)

# Revenue chart
st.subheader("💰 Seller Revenue Comparison")

seller_chart = seller_data.copy()

create_bar_chart(
    seller_chart,
    "seller_name",
    "revenue",
    "Seller",
    "Revenue",
    "Top 10 Sellers by Revenue"
)


# =========================================================
# PAYMENT ANALYSIS
# =========================================================

st.header("💳 Payment Analysis")

try:

    payment_data = run_query(
        queries.PAYMENT_METHOD_QUERY
    )

    st.dataframe(
        payment_data,
        use_container_width=True
    )

    fig = create_bar_chart(
        payment_data,
        "payment_type",
        "total_orders",
        "Orders by Payment Method",
        "Payment Method",
        "Number of Orders"
    )

    st.pyplot(fig)

except Exception as e:

    st.error(f"Payment analysis error: {e}")


# =========================================================
# DELIVERY ANALYSIS
# =========================================================

st.header("🚚 Delivery Analysis")

try:

    delivery_data = run_query(
        queries.DELIVERY_QUERY
    )

    st.dataframe(
        delivery_data,
        use_container_width=True
    )

    col1, col2 = st.columns(2)

    on_time = delivery_data[
        delivery_data["delivery_status"] == "On Time"
    ]

    delayed = delivery_data[
        delivery_data["delivery_status"] == "Delayed"
    ]


    with col1:

        if not on_time.empty:

            st.metric(
                "✅ On-Time Deliveries",
                f"{int(on_time.iloc[0]['orders']):,}"
            )

            st.metric(
                "On-Time %",
                f"{(
                    on_time.iloc[0]["orders"]
                    / delivery_data["orders"].sum()
                    * 100
                ):.2f}%"
            )


    with col2:

        if not delayed.empty:

            st.metric(
                "⚠️ Delayed Deliveries",
                f"{int(delayed.iloc[0]['orders']):,}"
            )

            st.metric(
                "Delayed %",
                f"{(
                    delayed.iloc[0]["orders"]
                    / delivery_data["orders"].sum()
                    * 100
                ):.2f}%"
            )


    # Delivery count chart

    fig = create_bar_chart(
        delivery_data,
        "delivery_status",
        "orders",
        "On-Time vs Delayed Deliveries",
        "Delivery Status",
        "Number of Orders"
    )

    st.pyplot(fig)


    # Average delivery time chart

    fig = create_bar_chart(
        delivery_data,
        "delivery_status",
        "average_delivery_days",
        "Average Delivery Time",
        "Delivery Status",
        "Average Delivery Days"
    )

    st.pyplot(fig)

except Exception as e:

    st.error(f"Delivery analysis error: {e}")


# =========================================================
# STATISTICAL ANALYSIS
# =========================================================

st.header("📈 Statistical Analysis")


# -----------------------------
# H1
# -----------------------------

st.subheader(
    "H1: Does Late Delivery Affect Customer Reviews?"
)

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "On-Time Avg Review",
        "4.29"
    )

with col2:

    st.metric(
        "Delayed Avg Review",
        "2.57"
    )

with col3:

    st.metric(
        "t-statistic",
        "89.55"
    )

with col4:

    st.metric(
        "p-value",
        "< 0.001"
    )

st.write(
    "**Test:** Welch's Independent Samples t-test"
)

st.info(
    "There is a statistically significant difference "
    "between review scores for on-time and delayed deliveries. "
    "Delayed deliveries are associated with lower average review scores."
)


# -----------------------------
# H2
# -----------------------------

st.subheader(
    "H2: Do Product Categories Differ in Average Order Value?"
)

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "F-statistic",
        "173.57"
    )

with col2:

    st.metric(
        "p-value",
        "< 0.001"
    )

st.write(
    "**Test:** One-Way ANOVA"
)

st.info(
    "There is a statistically significant difference "
    "in average order value across product categories."
)


# -----------------------------
# H3
# -----------------------------

st.subheader(
    "H3: Is Payment Method Associated with Order Status?"
)

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Chi-square",
        "939.51"
    )

with col2:

    st.metric(
        "Degrees of Freedom",
        "28"
    )

with col3:

    st.metric(
        "p-value",
        "< 0.001"
    )

st.write(
    "**Test:** Chi-Square Test of Independence"
)

st.info(
    "Payment method and order status are statistically "
    "associated. This does not establish causation."
)


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.write(
    "Cart2Insights | E-Commerce Performance Analytics"
)

