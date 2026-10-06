
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from scipy import stats

from database import get_connection
from streamlit_autorefresh import st_autorefresh


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Cart2Insights",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# AUTO REFRESH
# =========================================================

st_autorefresh(
    interval=60 * 1000,
    limit=None,
    key="cart2insights_refresh"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .main {
        background-color: #f7f9fc;
    }

    .dashboard-title {
        font-size: 42px;
        font-weight: 800;
        color: #1f2937;
        margin-bottom: 0;
    }

    .dashboard-subtitle {
        font-size: 18px;
        color: #64748b;
        margin-bottom: 20px;
    }

    .kpi-card {
        padding: 18px;
        border-radius: 15px;
        color: white;
        min-height: 125px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }

    .kpi-title {
        font-size: 15px;
        font-weight: 600;
        opacity: 0.9;
    }

    .kpi-value {
        font-size: 27px;
        font-weight: 800;
        margin-top: 10px;
    }

    .insight-box {
        padding: 15px;
        border-radius: 12px;
        background-color: #eef6ff;
        border-left: 5px solid #2563eb;
        margin-top: 10px;
        margin-bottom: 20px;
    }

    .recommendation-box {
        padding: 18px;
        border-radius: 12px;
        background-color: #fff7ed;
        border-left: 5px solid #f97316;
        margin-top: 10px;
        margin-bottom: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="dashboard-title">🛒 Cart2Insights</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="dashboard-subtitle">'
    'Decoding E-Commerce Performance'
    '</div>',
    unsafe_allow_html=True
)

st.caption(
    "📡 Live MySQL dashboard • Automatically refreshes every 60 seconds"
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

try:
    connection = get_connection()

except Exception as e:

    st.error(
        "❌ Database connection failed. "
        "Please check MySQL/XAMPP and database.py."
    )

    st.exception(e)
    st.stop()


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def run_query(query):
    return pd.read_sql(query, connection)


def format_currency(value):
    if pd.isna(value):
        return "₹0.00"
    return f"₹{float(value):,.2f}"


def format_number(value):
    if pd.isna(value):
        return "0"
    return f"{int(value):,}"


def kpi_card(column, title, value, gradient):
    with column:
        st.markdown(
            f"""
            <div class="kpi-card" style="background:{gradient};">
                <div class="kpi-title">{title}</div>
                <div class="kpi-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🎛️ Dashboard Filters")

st.sidebar.markdown("---")

st.sidebar.subheader("📅 Date Filter")


try:

    date_data = run_query(
        """
        SELECT
            MIN(order_purchase_timestamp) AS min_date,
            MAX(order_purchase_timestamp) AS max_date
        FROM orders
        """
    )

    min_date = pd.to_datetime(
        date_data.iloc[0]["min_date"]
    ).date()

    max_date = pd.to_datetime(
        date_data.iloc[0]["max_date"]
    ).date()

except Exception:

    min_date = datetime(2016, 1, 1).date()
    max_date = datetime(2018, 12, 31).date()


date_range = st.sidebar.date_input(
    "Select purchase date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)


# =========================================================
# CATEGORY FILTER
# =========================================================

st.sidebar.markdown("---")

st.sidebar.subheader("📦 Category Filter")


try:

    category_data = run_query(
        """
        SELECT DISTINCT
            COALESCE(
                t.product_category_name_english,
                p.product_category_name,
                'unknown'
            ) AS category

        FROM products p

        LEFT JOIN product_category_translation t
            ON p.product_category_name =
               t.product_category_name

        ORDER BY category
        """
    )

    categories = (
        category_data["category"]
        .dropna()
        .astype(str)
        .tolist()
    )

except Exception:

    categories = []


selected_categories = st.sidebar.multiselect(
    "Select categories",
    categories,
    default=[]
)


# =========================================================
# REFRESH BUTTON
# =========================================================

st.sidebar.markdown("---")

if st.sidebar.button(
    "🔄 Refresh Dashboard",
    width="stretch"
):

    st.rerun()


st.sidebar.info(
    "💡 Use the filters to explore different parts "
    "of the e-commerce business."
)


# =========================================================
# DATE FILTER VALUES
# =========================================================

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:

    start_date = date_range[0]
    end_date = date_range[1]

else:

    start_date = min_date
    end_date = max_date


start_datetime = f"{start_date} 00:00:00"

end_datetime = (
    pd.Timestamp(end_date)
    + pd.Timedelta(days=1)
).strftime("%Y-%m-%d %H:%M:%S")


# =========================================================
# CATEGORY CONDITION
# =========================================================

category_condition = ""

if selected_categories:

    safe_categories = [
        str(category).replace("'", "''")
        for category in selected_categories
    ]

    category_values = ",".join(
        f"'{category}'"
        for category in safe_categories
    )

    category_condition = f"""
        AND COALESCE(
            t.product_category_name_english,
            p.product_category_name,
            'unknown'
        ) IN ({category_values})
    """


# =========================================================
# COMMON FILTERED SALES DATA
# =========================================================

SALES_DATA_QUERY = f"""
SELECT
    o.order_id,
    o.customer_id,
    oi.product_id,
    oi.seller_id,
    o.order_purchase_timestamp,

    oi.price,
    oi.freight_value,

    COALESCE(
        t.product_category_name_english,
        p.product_category_name,
        'unknown'
    ) AS category

FROM orders o

JOIN order_items oi
    ON o.order_id = oi.order_id

LEFT JOIN products p
    ON oi.product_id = p.product_id

LEFT JOIN product_category_translation t
    ON p.product_category_name =
       t.product_category_name

WHERE o.order_purchase_timestamp >= '{start_datetime}'

AND o.order_purchase_timestamp < '{end_datetime}'

{category_condition}
"""


try:

    sales_data = run_query(
        SALES_DATA_QUERY
    )

except Exception as e:

    st.error(
        f"❌ Sales data error: {e}"
    )

    st.stop()


# =========================================================
# EMPTY DATA CHECK
# =========================================================

if sales_data.empty:

    st.warning(
        "⚠️ No data found for the selected filters."
    )

    st.stop()


# =========================================================
# BUSINESS OVERVIEW
# =========================================================

st.header("📊 Business Overview")

# Calculate KPI values
total_orders = sales_data["order_id"].nunique()

product_revenue = sales_data["price"].sum()

total_customers = sales_data["customer_id"].nunique()

total_sellers = sales_data["seller_id"].nunique()

# Average Order Value
# Product Revenue / Total Orders
average_order_value = (
    product_revenue / total_orders
    if total_orders > 0
    else 0
)

# Create 5 KPI cards
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

kpi_card(
    kpi1,
    "📦 Total Orders",
    format_number(total_orders),
    "linear-gradient(135deg,#2563eb,#60a5fa)"
)

kpi_card(
    kpi2,
    "💰 Product Revenue",
    format_currency(product_revenue),
    "linear-gradient(135deg,#059669,#34d399)"
)

kpi_card(
    kpi3,
    "👥 Customers",
    format_number(total_customers),
    "linear-gradient(135deg,#7c3aed,#a78bfa)"
)

kpi_card(
    kpi4,
    "🏪 Sellers",
    format_number(total_sellers),
    "linear-gradient(135deg,#ea580c,#fb923c)"
)

kpi_card(
    kpi5,
    "🛒 Avg Order Value",
    format_currency(average_order_value),
    "linear-gradient(135deg,#db2777,#f472b6)"
)

st.markdown("<br>", unsafe_allow_html=True)


# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "📈 Sales",
        "👥 Customers",
        "⭐ Experience",
        "🏪 Operations",
        "📊 Statistics",
        "💡 Insights"
    ]
)


# =========================================================
# SALES TAB
# =========================================================

with tab1:

    st.header("📈 Sales Analysis")


    # =====================================================
    # MONTHLY REVENUE
    # =====================================================

    monthly_revenue = (
        sales_data
        .assign(
            month=pd.to_datetime(
                sales_data[
                    "order_purchase_timestamp"
                ]
            ).dt.to_period("M").astype(str)
        )
        .groupby("month", as_index=False)
        ["price"]
        .sum()
    )


    monthly_revenue.rename(
        columns={
            "price": "revenue"
        },
        inplace=True
    )


    fig = px.line(
        monthly_revenue,
        x="month",
        y="revenue",
        markers=True,
        title="📈 Monthly Product Revenue Trend",
        labels={
            "month": "Month",
            "revenue": "Revenue (₹)"
        },
        template="plotly_white"
    )


    fig.update_traces(
        line_width=4
    )


    fig.update_layout(
        hovermode="x unified"
    )


    st.plotly_chart(
        fig,
        width="stretch"
    )


    # =====================================================
    # CATEGORY + PRODUCT
    # =====================================================

    col1, col2 = st.columns(2)


    # =====================================================
    # CATEGORY REVENUE
    # =====================================================

    with col1:

        category_revenue = (
            sales_data
            .groupby(
                "category",
                as_index=False
            )
            ["price"]
            .sum()
            .sort_values(
                "price",
                ascending=False
            )
            .head(10)
        )


        fig = px.bar(
            category_revenue,
            x="price",
            y="category",
            orientation="h",
            title="🏆 Top 10 Categories by Revenue",
            labels={
                "price": "Revenue (₹)",
                "category": "Category"
            },
            color="price",
            color_continuous_scale="Viridis",
            template="plotly_white"
        )


        st.plotly_chart(
            fig,
            width="stretch"
        )


    # =====================================================
    # TOP PRODUCTS
    # =====================================================

    with col2:

        top_products = (
            sales_data
            .groupby(
                [
                    "product_id",
                    "category"
                ],
                as_index=False
            )
            .agg(
                total_items=(
                    "product_id",
                    "count"
                ),

                revenue=(
                    "price",
                    "sum"
                )
            )
            .sort_values(
                "revenue",
                ascending=False
            )
            .head(10)
        )


        top_products["product"] = [
            f"Product {i+1}"
            for i in range(
                len(top_products)
            )
        ]


        fig = px.bar(
            top_products,
            x="revenue",
            y="product",
            orientation="h",
            title="🛍️ Top 10 Products",
            labels={
                "revenue": "Revenue (₹)",
                "product": "Product"
            },
            color="revenue",
            color_continuous_scale="Turbo",
            template="plotly_white"
        )


        st.plotly_chart(
            fig,
            width="stretch"
        )


    # =====================================================
    # SALES INSIGHT
    # =====================================================

    st.subheader("💡 Sales Insight")


    if not category_revenue.empty:

        top_category = category_revenue.iloc[0]


        st.info(
            f"🏆 **{top_category['category']}** is the "
            f"highest revenue-generating category in the "
            f"selected period, with product revenue of "
            f"**{format_currency(top_category['price'])}**."
        )


# =========================================================
# CUSTOMER TAB
# =========================================================

with tab2:

    st.header("👥 Customer Analysis")


    # =====================================================
    # CUSTOMER SPENDING
    # =====================================================

    customer_spending = run_query(
        f"""
        SELECT
            c.customer_unique_id,

            COUNT(DISTINCT o.order_id)
                AS total_orders,

            ROUND(
                SUM(
                    oi.price +
                    oi.freight_value
                ),
                2
            ) AS total_spending

        FROM customers c

        JOIN orders o
            ON c.customer_id =
               o.customer_id

        JOIN order_items oi
            ON o.order_id =
               oi.order_id

        LEFT JOIN products p
            ON oi.product_id =
               p.product_id

        LEFT JOIN product_category_translation t
            ON p.product_category_name =
               t.product_category_name

        WHERE o.order_purchase_timestamp >=
              '{start_datetime}'

        AND o.order_purchase_timestamp <
            '{end_datetime}'

        {category_condition}

        GROUP BY
            c.customer_unique_id

        ORDER BY
            total_spending DESC

        LIMIT 10;
        """
    )


    st.subheader(
        "💰 Top Customers by Spending"
    )


    if not customer_spending.empty:

        display_customer = (
            customer_spending.copy()
        )


        display_customer.columns = [
            "Customer ID",
            "Orders",
            "Total Spending"
        ]


        display_customer[
            "Total Spending"
        ] = (
            display_customer[
                "Total Spending"
            ].apply(
                format_currency
            )
        )


        st.dataframe(
            display_customer,
            width="stretch",
            hide_index=True
        )

    else:

        st.info(
            "No customer data available."
        )


    # =====================================================
    # CUSTOMER TYPE
    # =====================================================

    customer_type = run_query(
        f"""
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

                COUNT(
                    DISTINCT o.order_id
                ) AS total_orders

            FROM customers c

            JOIN orders o
                ON c.customer_id =
                   o.customer_id

            JOIN order_items oi
                ON o.order_id =
                   oi.order_id

            LEFT JOIN products p
                ON oi.product_id =
                   p.product_id

            LEFT JOIN product_category_translation t
                ON p.product_category_name =
                   t.product_category_name

            WHERE o.order_purchase_timestamp >=
                  '{start_datetime}'

            AND o.order_purchase_timestamp <
                '{end_datetime}'

            {category_condition}

            GROUP BY
                c.customer_unique_id

        ) AS customer_orders

        GROUP BY
            customer_type;
        """
    )


    col1, col2 = st.columns(2)


    with col1:

        if not customer_type.empty:

            fig = px.pie(
                customer_type,
                names="customer_type",
                values="customers",
                hole=0.45,
                title="🔄 One-Time vs Repeat Customers",
                color_discrete_sequence=(
                    px.colors.qualitative.Set2
                )
            )


            st.plotly_chart(
                fig,
                width="stretch"
            )


    with col2:

        repeat_count = 0
        one_time_count = 0


        for _, row in customer_type.iterrows():

            if row["customer_type"] == "Repeat Customer":

                repeat_count = row["customers"]

            else:

                one_time_count = row["customers"]


        total_customer_types = (
            repeat_count
            +
            one_time_count
        )


        repeat_percentage = (
            repeat_count
            /
            total_customer_types
            *
            100

            if total_customer_types > 0

            else 0
        )


        st.metric(
            "🔄 Repeat Customer %",
            f"{repeat_percentage:.2f}%"
        )


        st.info(
            "💡 Increasing repeat purchases can improve "
            "customer lifetime value and reduce dependence "
            "on acquiring new customers."
        )


# =========================================================
# EXPERIENCE TAB
# =========================================================

with tab3:

    st.header(
        "⭐ Customer Experience"
    )


    # =====================================================
    # REVIEW DATA
    # =====================================================

    review_data = run_query(
        f"""
        SELECT
            r.review_score,
            COUNT(*) AS review_count

        FROM order_reviews r

        JOIN orders o
            ON r.order_id =
               o.order_id

        WHERE o.order_purchase_timestamp >=
              '{start_datetime}'

        AND o.order_purchase_timestamp <
            '{end_datetime}'

        GROUP BY
            r.review_score

        ORDER BY
            r.review_score;
        """
    )


    if not review_data.empty:

        fig = px.bar(
            review_data,
            x="review_score",
            y="review_count",
            title="⭐ Customer Review Score Distribution",
            labels={
                "review_score": "Review Score",
                "review_count": "Number of Reviews"
            },
            color="review_score",
            color_continuous_scale="RdYlGn",
            template="plotly_white"
        )


        st.plotly_chart(
            fig,
            width="stretch"
        )


    # =====================================================
    # AVERAGE REVIEW
    # =====================================================

    average_review = run_query(
        f"""
        SELECT
            AVG(r.review_score)
            AS average_review

        FROM order_reviews r

        JOIN orders o
            ON r.order_id =
               o.order_id

        WHERE o.order_purchase_timestamp >=
              '{start_datetime}'

        AND o.order_purchase_timestamp <
            '{end_datetime}';
        """
    )


    average_score = (
        average_review.iloc[0]["average_review"]
    )


    if pd.notna(average_score):

        st.metric(
            "⭐ Average Customer Review",
            f"{average_score:.2f} / 5"
        )


    # =====================================================
    # DELIVERY + REVIEW
    # =====================================================

    st.subheader(
        "🚚 Delivery Performance & Customer Experience"
    )


    delivery_review_data = run_query(
        f"""
        SELECT

            CASE

                WHEN o.order_delivered_customer_date
                     <=
                     o.order_estimated_delivery_date

                THEN 'On Time'

                ELSE 'Delayed'

            END AS delivery_status,

            AVG(r.review_score)
                AS average_review

        FROM orders o

        JOIN order_reviews r
            ON o.order_id =
               r.order_id

        WHERE o.order_purchase_timestamp >=
              '{start_datetime}'

        AND o.order_purchase_timestamp <
            '{end_datetime}'

        AND o.order_delivered_customer_date
            IS NOT NULL

        AND o.order_estimated_delivery_date
            IS NOT NULL

        GROUP BY
            delivery_status;
        """
    )


    if not delivery_review_data.empty:

        on_time_score = (
            delivery_review_data.loc[
                delivery_review_data[
                    "delivery_status"
                ] == "On Time",
                "average_review"
            ].iloc[0]
            if "On Time"
            in delivery_review_data[
                "delivery_status"
            ].values
            else 0
        )


        delayed_score = (
            delivery_review_data.loc[
                delivery_review_data[
                    "delivery_status"
                ] == "Delayed",
                "average_review"
            ].iloc[0]
            if "Delayed"
            in delivery_review_data[
                "delivery_status"
            ].values
            else 0
        )


        col1, col2 = st.columns(2)


        with col1:

            st.metric(
                "✅ On-Time Review Score",
                f"{on_time_score:.2f} / 5"
            )


        with col2:

            st.metric(
                "⚠️ Delayed Review Score",
                f"{delayed_score:.2f} / 5"
            )


        if delayed_score < on_time_score:

            st.warning(
                "⚠️ Delayed deliveries are associated "
                "with lower customer review scores."
            )


# =========================================================
# OPERATIONS TAB
# =========================================================

with tab4:

    st.header(
        "🏪 Operations Analysis"
    )


    # =====================================================
    # TOP SELLERS
    # =====================================================

    st.subheader(
        "🏆 Top Sellers by Revenue"
    )


    seller_data = run_query(
        f"""
        SELECT

            oi.seller_id,

            COUNT(DISTINCT oi.order_id)
                AS total_orders,

            COUNT(oi.product_id)
                AS total_items,

            ROUND(
                SUM(oi.price),
                2
            ) AS revenue

        FROM orders o

        JOIN order_items oi
            ON o.order_id =
               oi.order_id

        LEFT JOIN products p
            ON oi.product_id =
               p.product_id

        LEFT JOIN product_category_translation t
            ON p.product_category_name =
               t.product_category_name

        WHERE o.order_purchase_timestamp >=
              '{start_datetime}'

        AND o.order_purchase_timestamp <
            '{end_datetime}'

        {category_condition}

        GROUP BY
            oi.seller_id

        ORDER BY
            revenue DESC

        LIMIT 10;
        """
    )


    if not seller_data.empty:

        seller_data["seller_name"] = [
            f"Seller {i+1}"
            for i in range(
                len(seller_data)
            )
        ]


        seller_data["rank"] = range(
            1,
            len(seller_data) + 1
        )


        display_sellers = seller_data[
            [
                "rank",
                "seller_name",
                "total_orders",
                "total_items",
                "revenue"
            ]
        ].copy()


        display_sellers.columns = [
            "Rank",
            "Seller",
            "Orders",
            "Items",
            "Revenue"
        ]


        display_sellers["Revenue"] = (
            display_sellers[
                "Revenue"
            ].apply(
                format_currency
            )
        )


        st.dataframe(
            display_sellers,
            width="stretch",
            hide_index=True
        )


        fig = px.bar(
            seller_data,
            x="revenue",
            y="seller_name",
            orientation="h",
            title="💰 Top 10 Seller Revenue",
            labels={
                "revenue": "Revenue (₹)",
                "seller_name": "Seller"
            },
            color="revenue",
            color_continuous_scale="Plasma",
            template="plotly_white"
        )


        st.plotly_chart(
            fig,
            width="stretch"
        )


    # =====================================================
    # PAYMENT
    # =====================================================

    st.subheader(
        "💳 Payment Methods"
    )


    payment_data = run_query(
        f"""
        SELECT

            op.payment_type,

            COUNT(DISTINCT op.order_id)
                AS total_orders,

            ROUND(
                SUM(op.payment_value),
                2
            ) AS total_value

        FROM order_payments op

        JOIN orders o
            ON op.order_id =
               o.order_id

        WHERE o.order_purchase_timestamp >=
              '{start_datetime}'

        AND o.order_purchase_timestamp <
            '{end_datetime}'

        GROUP BY
            op.payment_type

        ORDER BY
            total_orders DESC;
        """
    )


    if not payment_data.empty:

        col1, col2 = st.columns(2)


        with col1:

            fig = px.pie(
                payment_data,
                names="payment_type",
                values="total_orders",
                hole=0.45,
                title="💳 Orders by Payment Method",
                color_discrete_sequence=(
                    px.colors.qualitative.Bold
                )
            )


            st.plotly_chart(
                fig,
                width="stretch"
            )


        with col2:

            fig = px.bar(
                payment_data,
                x="payment_type",
                y="total_value",
                title="💰 Payment Value",
                labels={
                    "payment_type":
                        "Payment Method",

                    "total_value":
                        "Payment Value (₹)"
                },
                color="payment_type",
                template="plotly_white"
            )


            st.plotly_chart(
                fig,
                width="stretch"
            )


    # =====================================================
    # DELIVERY PERFORMANCE
    # =====================================================

    st.subheader(
        "🚚 Delivery Performance"
    )


    delivery_data = run_query(
        f"""
        SELECT

            CASE

                WHEN o.order_delivered_customer_date
                     <=
                     o.order_estimated_delivery_date

                THEN 'On Time'

                ELSE 'Delayed'

            END AS delivery_status,

            COUNT(DISTINCT o.order_id) AS orders,

            AVG(
                DATEDIFF(
                    o.order_delivered_customer_date,
                    o.order_purchase_timestamp
                )
            ) AS average_delivery_days

        FROM orders o

        JOIN order_items oi
            ON o.order_id =
               oi.order_id

        LEFT JOIN products p
            ON oi.product_id =
               p.product_id

        LEFT JOIN product_category_translation t
            ON p.product_category_name =
               t.product_category_name

        WHERE o.order_purchase_timestamp >=
              '{start_datetime}'

        AND o.order_purchase_timestamp <
            '{end_datetime}'

        AND o.order_delivered_customer_date
            IS NOT NULL

        AND o.order_estimated_delivery_date
            IS NOT NULL

        {category_condition}

        GROUP BY
            delivery_status;
        """
    )


    if not delivery_data.empty:

        total_delivery_orders = (
            delivery_data["orders"].sum()
        )


        on_time_orders = delivery_data.loc[
            delivery_data[
                "delivery_status"
            ] == "On Time",
            "orders"
        ].sum()


        delayed_orders = delivery_data.loc[
            delivery_data[
                "delivery_status"
            ] == "Delayed",
            "orders"
        ].sum()


        col1, col2, col3 = st.columns(3)


        with col1:

            st.metric(
                "🚚 Total Delivered",
                format_number(
                    total_delivery_orders
                )
            )


        with col2:

            st.metric(
                "✅ On-Time",
                format_number(
                    on_time_orders
                )
            )


        with col3:

            delayed_percentage = (
                delayed_orders
                /
                total_delivery_orders
                *
                100

                if total_delivery_orders > 0

                else 0
            )


            st.metric(
                "⚠️ Delayed",
                f"{delayed_percentage:.2f}%"
            )


        col1, col2 = st.columns(2)


        with col1:

            fig = px.pie(
                delivery_data,
                names="delivery_status",
                values="orders",
                hole=0.45,
                title="🚚 On-Time vs Delayed Deliveries",
                color_discrete_sequence=[
                    "#22c55e",
                    "#ef4444"
                ]
            )


            st.plotly_chart(
                fig,
                width="stretch"
            )


        with col2:

            fig = px.bar(
                delivery_data,
                x="delivery_status",
                y="average_delivery_days",
                title="⏱️ Average Delivery Time",
                labels={
                    "delivery_status":
                        "Delivery Status",

                    "average_delivery_days":
                        "Average Delivery Days"
                },
                color="delivery_status",
                template="plotly_white"
            )


            st.plotly_chart(
                fig,
                width="stretch"
            )


# =========================================================
# STATISTICS TAB
# =========================================================

with tab5:

    st.header(
        "📊 Statistical Analysis"
    )


    # =====================================================
    # H1
    # =====================================================

    st.subheader(
        "H1 — Does Late Delivery Affect Customer Reviews?"
    )


    h1_data = run_query(
        f"""
        SELECT

            CASE

                WHEN o.order_delivered_customer_date
                     <=
                     o.order_estimated_delivery_date

                THEN 'On Time'

                ELSE 'Delayed'

            END AS delivery_status,

            r.review_score

        FROM orders o

        JOIN order_reviews r
            ON o.order_id =
               r.order_id

        WHERE o.order_purchase_timestamp >=
              '{start_datetime}'

        AND o.order_purchase_timestamp <
            '{end_datetime}'

        AND o.order_delivered_customer_date
            IS NOT NULL

        AND o.order_estimated_delivery_date
            IS NOT NULL;
        """
    )


    on_time_reviews = h1_data.loc[
        h1_data[
            "delivery_status"
        ] == "On Time",
        "review_score"
    ].dropna()


    delayed_reviews = h1_data.loc[
        h1_data[
            "delivery_status"
        ] == "Delayed",
        "review_score"
    ].dropna()


    if (
        len(on_time_reviews) > 1
        and
        len(delayed_reviews) > 1
    ):

        t_stat, p_value = stats.ttest_ind(
            on_time_reviews,
            delayed_reviews,
            equal_var=False
        )


        col1, col2, col3, col4 = st.columns(4)


        with col1:

            st.metric(
                "On-Time Avg Review",
                f"{on_time_reviews.mean():.2f}"
            )


        with col2:

            st.metric(
                "Delayed Avg Review",
                f"{delayed_reviews.mean():.2f}"
            )


        with col3:

            st.metric(
                "t-statistic",
                f"{t_stat:.2f}"
            )


        with col4:

            st.metric(
                "p-value",
                f"{p_value:.4f}"
            )


        if p_value < 0.05:

            st.success(
                "✅ Significant result: delivery status "
                "is associated with a statistically "
                "significant difference in review scores."
            )

        else:

            st.info(
                "ℹ️ No statistically significant difference "
                "was detected at the 5% significance level."
            )


        st.caption(
            "Test: Welch's Independent Samples t-test"
        )


    else:

        st.warning(
            "Not enough data to perform H1 statistical test."
        )


    # =====================================================
    # H2
    # =====================================================

    st.subheader(
        "H2 — Do Product Categories Differ in Average Order Value?"
    )


    h2_data = sales_data.copy()


    h2_data["order_value"] = (
        h2_data["price"]
        +
        h2_data["freight_value"]
    )


    category_groups = [
        group["order_value"].values

        for _, group

        in h2_data.groupby("category")

        if len(group) > 1
    ]


    if len(category_groups) >= 2:

        f_stat, p_value = stats.f_oneway(
            *category_groups
        )


        col1, col2 = st.columns(2)


        with col1:

            st.metric(
                "F-statistic",
                f"{f_stat:.2f}"
            )


        with col2:

            st.metric(
                "p-value",
                f"{p_value:.4f}"
            )


        if p_value < 0.05:

            st.success(
                "✅ Significant result: average order "
                "value differs significantly across "
                "product categories."
            )

        else:

            st.info(
                "ℹ️ No statistically significant difference "
                "was detected across categories."
            )


        st.caption(
            "Test: One-Way ANOVA"
        )


    else:

        st.warning(
            "Not enough categories to perform ANOVA."
        )


    # =====================================================
    # H3
    # =====================================================

    st.subheader(
        "H3 — Is Payment Method Associated with Order Status?"
    )


    h3_data = run_query(
        f"""
        SELECT

            op.payment_type,

            o.order_status

        FROM order_payments op

        JOIN orders o
            ON op.order_id =
               o.order_id

        WHERE o.order_purchase_timestamp >=
              '{start_datetime}'

        AND o.order_purchase_timestamp <
            '{end_datetime}';
        """
    )


    if not h3_data.empty:

        contingency_table = pd.crosstab(
            h3_data["payment_type"],
            h3_data["order_status"]
        )


        if (
            contingency_table.shape[0] >= 2
            and
            contingency_table.shape[1] >= 2
        ):

            chi2, p_value, dof, expected = (
                stats.chi2_contingency(
                    contingency_table
                )
            )


            col1, col2, col3 = st.columns(3)


            with col1:

                st.metric(
                    "Chi-square",
                    f"{chi2:.2f}"
                )


            with col2:

                st.metric(
                    "Degrees of Freedom",
                    str(dof)
                )


            with col3:

                st.metric(
                    "p-value",
                    f"{p_value:.4f}"
                )


            if p_value < 0.05:

                st.success(
                    "✅ Significant association: payment "
                    "method and order status are "
                    "statistically associated."
                )

            else:

                st.info(
                    "ℹ️ No statistically significant "
                    "association was detected."
                )


            st.caption(
                "Test: Chi-Square Test of Independence"
            )


            st.warning(
                "⚠️ Statistical association does not "
                "prove causation."
            )


        else:

            st.warning(
                "Not enough variation in payment/order "
                "status data for Chi-square testing."
            )


    else:

        st.warning(
            "No payment data available for H3."
        )


# =========================================================
# INSIGHTS TAB
# =========================================================

with tab6:

    st.header(
        "💡 Business Insights & Recommendations"
    )


    # =====================================================
    # KEY INSIGHTS
    # =====================================================

    st.subheader(
        "🔎 Key Business Insights"
    )


    # =====================================================
    # INSIGHT 1
    # =====================================================

    if not sales_data.empty:

        top_category_row = (
            sales_data
            .groupby("category")["price"]
            .sum()
            .sort_values(
                ascending=False
            )
            .head(1)
        )


        if not top_category_row.empty:

            top_category = (
                top_category_row.index[0]
            )


            top_category_revenue = (
                top_category_row.iloc[0]
            )


            st.markdown(
                f"""
                <div class="insight-box">

                <b>1️⃣ Revenue Concentration</b><br>

                <b>{top_category}</b> is the
                highest revenue-generating category
                in the selected period, generating
                approximately
                <b>{format_currency(top_category_revenue)}</b>
                in product revenue.

                </div>
                """,
                unsafe_allow_html=True
            )


    # =====================================================
    # INSIGHT 2
    # =====================================================

    if not delivery_review_data.empty:

        st.markdown(
            """
            <div class="insight-box">

            <b>2️⃣ Delivery Performance Matters</b><br>

            Delivery performance is associated with
            customer satisfaction. Orders delivered
            late should receive additional operational
            attention.

            </div>
            """,
            unsafe_allow_html=True
        )


    # =====================================================
    # INSIGHT 3
    # =====================================================

    st.markdown(
        f"""
        <div class="insight-box">

        <b>3️⃣ Customer Retention</b><br>

        The dashboard currently contains
        <b>{format_number(total_customers)}</b>
        customers in the selected period.
        Increasing repeat purchases can improve
        customer lifetime value.

        </div>
        """,
        unsafe_allow_html=True
    )


    # =====================================================
    # INSIGHT 4
    # =====================================================

    try:

        payment_insight = run_query(
            f"""
            SELECT

                payment_type,

                COUNT(DISTINCT op.order_id)
                    AS total_orders

            FROM order_payments op

            JOIN orders o
                ON op.order_id =
                   o.order_id

            WHERE o.order_purchase_timestamp >=
                  '{start_datetime}'

            AND o.order_purchase_timestamp <
                '{end_datetime}'

            GROUP BY
                payment_type

            ORDER BY
                total_orders DESC

            LIMIT 1;
            """
        )


        if not payment_insight.empty:

            top_payment = (
                payment_insight.iloc[0][
                    "payment_type"
                ]
            )


            st.markdown(
                f"""
                <div class="insight-box">

                <b>4️⃣ Payment Behavior</b><br>

                <b>{top_payment}</b> is the most
                frequently used payment method
                in the selected period.

                </div>
                """,
                unsafe_allow_html=True
            )

    except Exception:

        pass


    # =====================================================
    # RECOMMENDATIONS
    # =====================================================

    st.subheader(
        "🎯 Actionable Recommendations"
    )


    st.markdown(
        """
        <div class="recommendation-box">

        <b>🚚 Recommendation 1 — Reduce Delivery Delays</b><br>

        Identify sellers and logistics routes with
        frequent delays and improve delivery planning
        for those areas.

        </div>
        """,
        unsafe_allow_html=True
    )


    st.markdown(
        """
        <div class="recommendation-box">

        <b>⭐ Recommendation 2 — Protect Customer Experience</b><br>

        Prioritize delayed orders because lower delivery
        performance can be associated with lower customer
        ratings.

        </div>
        """,
        unsafe_allow_html=True
    )


    st.markdown(
        """
        <div class="recommendation-box">

        <b>🛍️ Recommendation 3 — Focus on High-Revenue Categories</b><br>

        Allocate marketing campaigns and inventory planning
        toward consistently high-performing categories.

        </div>
        """,
        unsafe_allow_html=True
    )


    st.markdown(
        """
        <div class="recommendation-box">

        <b>🔄 Recommendation 4 — Increase Repeat Purchases</b><br>

        Use loyalty offers, personalized recommendations
        and targeted promotions to convert one-time
        customers into repeat customers.

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")


st.caption(
    "🛒 Cart2Insights | E-Commerce Performance Analytics | "
    "Powered by Python • MySQL • Pandas • Plotly • Streamlit"
)


st.caption(
    "🔄 Dashboard automatically refreshes every 60 seconds."
)



