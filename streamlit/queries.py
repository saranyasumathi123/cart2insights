# =========================================================
# BUSINESS OVERVIEW - TEST
# =========================================================

st.header("📊 Business Overview")

total_orders = sales_data["order_id"].nunique()
product_revenue = sales_data["price"].sum()

total_customers = sales_data["customer_id"].nunique()
total_sellers = sales_data["seller_id"].nunique()

average_order_value = product_revenue / total_orders

# TEST VALUES
st.write("Orders =", total_orders)
st.write("Product Revenue =", product_revenue)
st.write("AOV =", average_order_value)

st.write(
    "Expected AOV =",
    13215599.18 / 96439
)

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


