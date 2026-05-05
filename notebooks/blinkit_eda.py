# ============================================================
# BLINKIT DELIVERY & CUSTOMER ANALYTICS - EDA
# Author: Prathmesh Joshi
# Tools: Python (Pandas, NumPy, Matplotlib, Seaborn)
# ============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# ── Plot Style ───────────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor': '#f9f9f9',
    'axes.grid': True,
    'grid.alpha': 0.4,
    'font.family': 'DejaVu Sans',
    'axes.titlesize': 13,
    'axes.labelsize': 11,
})
COLORS = ['#2C7BB6','#D7191C','#1A9641','#FDAE61','#ABD9E9','#A6D96A']

# ── Load Data ────────────────────────────────────────────────
DATA = '../data/'
orders    = pd.read_csv(DATA + 'blinkit_orders.csv', parse_dates=['order_date','promised_delivery_time','actual_delivery_time'])
customers = pd.read_csv(DATA + 'blinkit_customers.csv')
delivery  = pd.read_csv(DATA + 'blinkit_delivery_performance.csv')
products  = pd.read_csv(DATA + 'blinkit_products.csv')
items     = pd.read_csv(DATA + 'blinkit_order_items.csv')
feedback  = pd.read_csv(DATA + 'blinkit_customer_feedback.csv')
inventory = pd.read_csv(DATA + 'blinkit_inventory.csv')

print("=" * 55)
print("BLINKIT ANALYTICS — DATA OVERVIEW")
print("=" * 55)
print(f"Orders      : {len(orders):,}")
print(f"Customers   : {len(customers):,}")
print(f"Delivery    : {len(delivery):,}")
print(f"Products    : {len(products):,}")
print(f"Order Items : {len(items):,}")
print(f"Feedback    : {len(feedback):,}")
print(f"Inventory   : {len(inventory):,}")

# ── Merge Main Dataset ───────────────────────────────────────
df = orders.merge(delivery, on='order_id', how='left') \
           .merge(customers, on='customer_id', how='left') \
           .merge(feedback[['order_id','rating','sentiment','feedback_category']], on='order_id', how='left')

# ============================================================
# SECTION 1: BUSINESS KPIs
# ============================================================
print("\n" + "=" * 55)
print("SECTION 1: BUSINESS KPIs")
print("=" * 55)
print(f"Total Revenue    : ₹{orders['order_total'].sum():,.2f}")
print(f"Avg Order Value  : ₹{orders['order_total'].mean():,.2f}")
print(f"Total Orders     : {len(orders):,}")
print(f"Unique Customers : {orders['customer_id'].nunique():,}")
print(f"\nDelivery Status:")
print(orders['delivery_status'].value_counts())

# ============================================================
# SECTION 2: DELIVERY PERFORMANCE
# ============================================================
print("\n" + "=" * 55)
print("SECTION 2: DELIVERY PERFORMANCE")
print("=" * 55)
print(f"Avg Delivery Time : {delivery['delivery_time_minutes'].mean():.2f} mins")
print(f"Max Delivery Time : {delivery['delivery_time_minutes'].max():.2f} mins")
delay_rate = (orders['delivery_status'] != 'On Time').mean() * 100
print(f"Delay Rate        : {delay_rate:.2f}%")
print("\nTop Delay Reasons:")
delay_reasons = delivery[delivery['reasons_if_delayed'].notna() & (delivery['reasons_if_delayed'] != '')]
print(delay_reasons['reasons_if_delayed'].value_counts().head(5))

# ============================================================
# SECTION 3: CUSTOMER SEGMENTATION
# ============================================================
print("\n" + "=" * 55)
print("SECTION 3: CUSTOMER SEGMENTATION")
print("=" * 55)
seg = df.merge(customers[['customer_id','customer_segment']], on='customer_id', how='left', suffixes=('','_c'))
seg_col = 'customer_segment_c' if 'customer_segment_c' in seg.columns else 'customer_segment'
seg_stats = df.groupby('customer_segment')['order_total'].agg(['count','sum','mean']).round(2)
seg_stats.columns = ['Orders','Revenue','Avg Order Value']
print(seg_stats.sort_values('Revenue', ascending=False))

# ============================================================
# SECTION 4: PRODUCT ANALYSIS
# ============================================================
print("\n" + "=" * 55)
print("SECTION 4: PRODUCT ANALYSIS")
print("=" * 55)
items_p = items.merge(products, on='product_id', how='left')
items_p['line_revenue'] = items_p['quantity'] * items_p['unit_price']
cat_rev = items_p.groupby('category')['line_revenue'].sum().sort_values(ascending=False)
print("Top Categories by Revenue:")
print(cat_rev.head(8))

# ============================================================
# SECTION 5: FEEDBACK ANALYSIS
# ============================================================
print("\n" + "=" * 55)
print("SECTION 5: FEEDBACK & SENTIMENT")
print("=" * 55)
print(feedback['sentiment'].value_counts())
print(f"\nAvg Rating: {feedback['rating'].mean():.2f}")
print("\nAvg Rating by Feedback Category:")
print(feedback.groupby('feedback_category')['rating'].mean().round(2).sort_values())

# ============================================================
# SECTION 6: VISUALIZATIONS
# ============================================================
print("\n Generating charts...")

fig, axes = plt.subplots(3, 3, figsize=(18, 14))
fig.suptitle('Blinkit Delivery & Customer Analytics — EDA Dashboard', fontsize=16, fontweight='bold', y=1.01)

# 1. Monthly Revenue Trend
ax1 = axes[0, 0]
monthly = orders.set_index('order_date').resample('ME')['order_total'].sum()
ax1.bar(range(len(monthly)), monthly.values, color=COLORS[0], alpha=0.85)
ax1.set_xticks(range(len(monthly)))
ax1.set_xticklabels([d.strftime('%b %y') for d in monthly.index], rotation=45, ha='right', fontsize=8)
ax1.set_title('Monthly Revenue Trend')
ax1.set_ylabel('Revenue (₹)')
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'₹{x/1e6:.1f}M'))

# 2. Delivery Status Pie
ax2 = axes[0, 1]
status_counts = orders['delivery_status'].value_counts()
ax2.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%',
        colors=COLORS[:len(status_counts)], startangle=90)
ax2.set_title('Delivery Status Distribution')

# 3. Delivery Time Distribution
ax3 = axes[0, 2]
valid_time = delivery['delivery_time_minutes'][delivery['delivery_time_minutes'] >= 0]
ax3.hist(valid_time, bins=30, color=COLORS[2], alpha=0.8, edgecolor='white')
ax3.axvline(valid_time.mean(), color='red', linestyle='--', label=f'Mean: {valid_time.mean():.1f} min')
ax3.set_title('Delivery Time Distribution')
ax3.set_xlabel('Minutes')
ax3.legend()

# 4. Customer Segment Revenue
ax4 = axes[1, 0]
seg_rev = df.groupby('customer_segment')['order_total'].sum().sort_values(ascending=True)
bars = ax4.barh(seg_rev.index, seg_rev.values, color=COLORS[:len(seg_rev)])
ax4.set_title('Revenue by Customer Segment')
ax4.set_xlabel('Revenue (₹)')
ax4.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'₹{x/1e6:.1f}M'))
for bar, val in zip(bars, seg_rev.values):
    ax4.text(val, bar.get_y() + bar.get_height()/2, f' ₹{val/1e6:.1f}M', va='center', fontsize=9)

# 5. Category Revenue
ax5 = axes[1, 1]
top_cat = cat_rev.head(8).sort_values(ascending=True)
ax5.barh(top_cat.index, top_cat.values, color=COLORS[1], alpha=0.85)
ax5.set_title('Top Categories by Revenue')
ax5.set_xlabel('Revenue (₹)')
ax5.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'₹{x/1e6:.1f}M'))

# 6. Sentiment Distribution
ax6 = axes[1, 2]
sent = feedback['sentiment'].value_counts()
colors_sent = {'Positive': '#1A9641', 'Neutral': '#FDAE61', 'Negative': '#D7191C'}
bars6 = ax6.bar(sent.index, sent.values, color=[colors_sent.get(s, '#999') for s in sent.index])
ax6.set_title('Customer Sentiment Distribution')
ax6.set_ylabel('Count')
for bar, val in zip(bars6, sent.values):
    ax6.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 20, str(val), ha='center', fontsize=10)

# 7. Delay Reasons
ax7 = axes[2, 0]
delay_df = delivery[delivery['reasons_if_delayed'].notna() & (delivery['reasons_if_delayed'] != '')]
delay_counts = delay_df['reasons_if_delayed'].value_counts().head(6)
ax7.barh(delay_counts.index, delay_counts.values, color=COLORS[3], alpha=0.9)
ax7.set_title('Top Delay Reasons')
ax7.set_xlabel('Count')

# 8. Avg Rating by Feedback Category
ax8 = axes[2, 1]
avg_rating = feedback.groupby('feedback_category')['rating'].mean().sort_values()
bars8 = ax8.barh(avg_rating.index, avg_rating.values, color=COLORS[0], alpha=0.85)
ax8.set_title('Avg Rating by Feedback Category')
ax8.set_xlabel('Rating (out of 5)')
ax8.set_xlim(0, 5)
for bar, val in zip(bars8, avg_rating.values):
    ax8.text(val + 0.05, bar.get_y() + bar.get_height()/2, f'{val:.2f}', va='center', fontsize=9)

# 9. Payment Method Distribution
ax9 = axes[2, 2]
pay = orders['payment_method'].value_counts()
ax9.pie(pay, labels=pay.index, autopct='%1.1f%%', colors=COLORS[:len(pay)], startangle=90)
ax9.set_title('Payment Method Distribution')

plt.tight_layout()
plt.savefig('../outputs/blinkit_eda_dashboard.png', dpi=150, bbox_inches='tight')
print(" Dashboard saved: outputs/blinkit_eda_dashboard.png")

# ── Chart 2: Delivery Impact on Rating ──────────────────────
fig2, axes2 = plt.subplots(1, 2, figsize=(12, 5))
fig2.suptitle('Delivery Performance vs Customer Satisfaction', fontsize=14, fontweight='bold')

# Delivery status vs avg rating
ax_a = axes2[0]
status_rating = df.groupby('delivery_status_x')['rating'].mean().sort_values(ascending=False)
bars_a = ax_a.bar(status_rating.index, status_rating.values, color=[COLORS[2], COLORS[3], COLORS[1]])
ax_a.set_title('Avg Rating by Delivery Status')
ax_a.set_ylabel('Rating (out of 5)')
ax_a.set_ylim(0, 5)
for bar, val in zip(bars_a, status_rating.values):
    ax_a.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05, f'{val:.2f}', ha='center', fontsize=11, fontweight='bold')

# Delivery time vs order total scatter
ax_b = axes2[1]
scatter_df = df[df['delivery_time_minutes'] >= 0].sample(min(500, len(df)))
ax_b.scatter(scatter_df['delivery_time_minutes'], scatter_df['order_total'], alpha=0.4, color=COLORS[0], s=20)
z = np.polyfit(scatter_df['delivery_time_minutes'].dropna(), scatter_df['order_total'].dropna(), 1)
p = np.poly1d(z)
x_line = np.linspace(scatter_df['delivery_time_minutes'].min(), scatter_df['delivery_time_minutes'].max(), 100)
ax_b.plot(x_line, p(x_line), 'r--', linewidth=2, label='Trend')
ax_b.set_title('Delivery Time vs Order Value')
ax_b.set_xlabel('Delivery Time (mins)')
ax_b.set_ylabel('Order Total (₹)')
ax_b.legend()

plt.tight_layout()
plt.savefig('../outputs/delivery_satisfaction_analysis.png', dpi=150, bbox_inches='tight')
print(" Chart saved: outputs/delivery_satisfaction_analysis.png")

print("\n All analysis complete!")
print("=" * 55)
