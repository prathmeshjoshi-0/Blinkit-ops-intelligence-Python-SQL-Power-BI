# Blinkit Delivery & Customer Analytics

## Project Overview
End-to-end analytics project on Blinkit's delivery operations and customer behavior using **SQL**, **Python**, and **Power BI**.

Analyzed 5,000 orders, 2,500 customers, 268 products, and 75,000+ inventory records to uncover delivery performance gaps, customer segmentation insights, and product revenue drivers.

---

## Business Problem
Blinkit operates a 10-minute grocery delivery model across multiple cities. Key challenges:
- High delay rate (30.6%) impacting customer satisfaction
- Need to identify high-value customer segments for retention
- Inventory damage rates affecting product availability
- Understanding which categories and products drive maximum revenue

---

## Key Findings

| Metric | Value |
|--------|-------|
| Total Revenue | ₹1.10 Cr |
| Total Orders | 5,000 |
| Avg Order Value | ₹2,201.86 |
| On-Time Delivery Rate | 69.4% |
| Delay Rate | 30.6% |
| Avg Delivery Time | 4.44 mins |
| Avg Customer Rating | 3.34 / 5 |

### Delivery Performance
- 30.6% of orders were delayed — primary reason: **Traffic (100% of delay cases)**
- On-time deliveries received higher average ratings
- Max delivery time recorded: 30 minutes

### Customer Segmentation
- Regular customers generated highest revenue: ₹28.9L
- New customers had highest avg order value: ₹2,287
- Inactive segment needs re-engagement campaigns

### Product & Category Insights
- **Dairy & Breakfast** is the top revenue category: ₹6.39L
- **Pharmacy** and **Fruits & Vegetables** are top 2 & 3
- 268 unique products across multiple categories

### Feedback & Sentiment
- Neutral: 34.8% | Negative: 32.8% | Positive: 32.4%
- Product Quality received lowest avg rating: 3.32
- High negative feedback signals quality & delivery issues

---

## Tools & Technologies

| Tool | Usage |
|------|-------|
| MySQL | Data extraction, joins, CTEs, window functions |
| Python (Pandas, NumPy) | EDA, data cleaning, trend analysis |
| Matplotlib / Seaborn | Data visualization |
| Power BI | Interactive dashboard |

---

## Project Structure

```
blinkit_project/
├── data/
│   ├── blinkit_orders.csv
│   ├── blinkit_customers.csv
│   ├── blinkit_delivery_performance.csv
│   ├── blinkit_products.csv
│   ├── blinkit_order_items.csv
│   ├── blinkit_customer_feedback.csv
│   └── blinkit_inventory.csv
├── sql/
│   └── blinkit_analysis.sql
├── notebooks/
│   └── blinkit_eda.py
├── outputs/
│   ├── blinkit_eda_dashboard.png
│   └── delivery_satisfaction_analysis.png
└── README.md
```

---

## SQL Highlights
- **6 analysis sections** covering KPIs, delivery, customers, products, inventory, feedback
- **CTEs** for top customer revenue ranking and stock classification
- **Window Functions** (RANK, PARTITION BY) for delivery partner performance
- **Multi-table JOINs** across 7 tables

---

## Python EDA Highlights
- Full data cleaning and null checks across all 7 datasets
- Monthly revenue trend analysis
- Customer segmentation by revenue and order value
- Delivery time distribution with mean markers
- Sentiment analysis across feedback categories
- Correlation analysis: delivery time vs order value

---

## Recommendations

1. **Reduce Traffic Delays** — Route optimization needed; traffic is the sole delay cause
2. **Re-engage Inactive Customers** — 1,190 orders from inactive segment — targeted offers can convert them
3. **Focus on Dairy & Pharmacy** — Top revenue categories; ensure consistent stock availability
4. **Improve Product Quality Ratings** — Lowest rated category; quality checks needed
5. **Push UPI & Digital Payments** — Analyze payment method trends for operational efficiency

---

## Author
**Prathmesh Joshi**  
Workforce Data Analyst | Mumbai  
[LinkedIn](https://linkedin.com) | [GitHub](https://github.com)
