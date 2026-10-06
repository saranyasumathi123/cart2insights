# Cart2Insights – Decoding E-Commerce Performance

## 📌 Project Overview

Cart2Insights is an e-commerce data analytics project built using the Olist
Brazilian E-Commerce dataset.

The project analyzes customer behavior, sales performance, product
categories, sellers, payment methods, delivery performance, and customer
reviews.

The project combines Python, SQL, MySQL, statistical analysis, and
Streamlit to transform raw e-commerce data into meaningful business
insights.

---

## 🎯 Business Objectives

The main objectives of this project are:

- Analyze overall e-commerce sales performance
- Understand customer purchasing behavior
- Identify high-performing product categories
- Identify top-performing products and sellers
- Analyze payment method usage
- Evaluate delivery performance
- Understand the relationship between delivery delays and customer reviews
- Analyze differences in order value across product categories
- Study the relationship between payment methods and order status
- Build an interactive Streamlit dashboard

---

## 📂 Dataset

The project uses the following datasets:

1. Customers
2. Orders
3. Order Items
4. Order Payments
5. Order Reviews
6. Products
7. Sellers
8. Geolocation
9. Product Category Translation

---

## 🛠️ Technologies Used

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- SciPy
- Statsmodels
- MySQL
- MySQL Connector/Python
- Streamlit
- Jupyter Notebook
- Git
- GitHub

---

## 🔄 Project Workflow

Raw Data
↓
Data Understanding
↓
Data Quality Analysis
↓
Data Cleaning
↓
MySQL Database
↓
SQL Analysis
↓
Feature Engineering
↓
Exploratory Data Analysis
↓
Statistical Analysis
↓
Streamlit Dashboard
↓
Business Insights

---

## 📊 Key Analyses

### Sales Analysis

- Total orders
- Revenue
- Average order value
- Monthly revenue
- Category-wise revenue
- Top products

### Customer Analysis

- Customer spending
- One-time customers
- Repeat customers

### Seller Analysis

- Top sellers
- Seller order volume
- Seller revenue

### Payment Analysis

- Payment method usage
- Payment value by payment type

### Delivery Analysis

- On-time deliveries
- Delayed deliveries
- Average delivery time

### Customer Experience

- Review score distribution
- Average review score
- Delivery performance vs review score

---

## 📈 Statistical Hypotheses

### Hypothesis 1

**Does late delivery affect customer reviews?**

Welch's t-test was used.

Result:

- t = 89.55
- p < 0.001

The analysis found a statistically significant difference in review scores
between on-time and delayed deliveries.

---

### Hypothesis 2

**Do product categories differ in average order value?**

One-way ANOVA was used.

Result:

- F = 173.57
- p < 0.001

The analysis found a statistically significant difference in average order
value across product categories.

---

### Hypothesis 3

**Is payment method associated with order status?**

Chi-square test of independence was used.

Result:

- χ² = 939.51
- df = 28
- p < 0.001

The analysis found a statistically significant association between payment
method and order status.

Statistical association does not imply causation.

---

## 🖥️ Streamlit Dashboard

The project includes an interactive Streamlit dashboard containing:

- Business Overview
- Sales Analysis
- Customer Analysis
- Customer Experience
- Seller Analysis
- Payment Analysis
- Delivery Analysis
- Statistical Analysis

---

## 📁 Project Structure

cart2insights/

├── data/

│   ├── raw/

│   └── cleaned/

│

├── notebooks/

│   ├── data_understanding.ipynb

│   ├── data_quality_analysis.ipynb

│   ├── data_cleaning.ipynb

│   ├── sql_analysis.ipynb

│   ├── feature_engineering.ipynb

│   ├── eda.ipynb

│   └── statistical_analysis.ipynb

│

├── streamlit/

│   ├── app.py

│   ├── database.py

│   ├── queries.py

│   └── utils.py

│

└── README.md

---

## ▶️ How to Run the Project

### 1. Install required packages

```bash
pip install pandas numpy matplotlib seaborn scipy statsmodels
pip install mysql-connector-python streamlit