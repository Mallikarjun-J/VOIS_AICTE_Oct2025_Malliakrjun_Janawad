"""
Visualization Script for Real Air BNB Dataset
Creates comprehensive visualizations from your actual data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import warnings
import os

warnings.filterwarnings('ignore')
sns.set_style('whitegrid')

# Create output directory
os.makedirs('reports/figures', exist_ok=True)

print("Loading data...")
df = pd.read_csv('Airbnb_dataset.csv')

print(f"Loaded {len(df):,} records")
print("\nGenerating visualizations...")

# 1. Price Distribution
print("  1/10: Price distribution...")
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Histogram
axes[0].hist(df['price'], bins=50, edgecolor='black', alpha=0.7, color='skyblue')
axes[0].axvline(df['price'].mean(), color='red', linestyle='--', label=f"Mean: ${df['price'].mean():.2f}")
axes[0].axvline(df['price'].median(), color='green', linestyle='--', label=f"Median: ${df['price'].median():.2f}")
axes[0].set_xlabel('Price ($)')
axes[0].set_ylabel('Frequency')
axes[0].set_title('Price Distribution', fontsize=14, fontweight='bold')
axes[0].legend()
axes[0].grid(alpha=0.3)

# Box plot by room type
room_types = df['room_type'].unique()
data_to_plot = [df[df['room_type'] == rt]['price'] for rt in room_types]
bp = axes[1].boxplot(data_to_plot, labels=room_types, patch_artist=True)
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
axes[1].set_xlabel('Room Type')
axes[1].set_ylabel('Price ($)')
axes[1].set_title('Price by Room Type', fontsize=14, fontweight='bold')
axes[1].tick_params(axis='x', rotation=45)
axes[1].grid(alpha=0.3)

# Log scale
axes[2].hist(np.log10(df['price'][df['price'] > 0]), bins=50, edgecolor='black', alpha=0.7, color='coral')
axes[2].set_xlabel('Log10(Price)')
axes[2].set_ylabel('Frequency')
axes[2].set_title('Price Distribution (Log Scale)', fontsize=14, fontweight='bold')
axes[2].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('reports/figures/01_price_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# 2. Neighbourhood Analysis
if 'neighbourhood_group' in df.columns:
    print("  2/10: Neighbourhood analysis...")
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Neighbourhood group distribution
    ng_counts = df['neighbourhood_group'].value_counts()
    axes[0, 0].bar(ng_counts.index, ng_counts.values, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#95E1D3'])
    axes[0, 0].set_xlabel('Neighbourhood Group')
    axes[0, 0].set_ylabel('Count')
    axes[0, 0].set_title('Listings by Neighbourhood Group', fontsize=14, fontweight='bold')
    axes[0, 0].tick_params(axis='x', rotation=45)
    axes[0, 0].grid(alpha=0.3)
    
    # Average price by neighbourhood group
    ng_price = df.groupby('neighbourhood_group')['price'].mean().sort_values(ascending=False)
    axes[0, 1].barh(ng_price.index, ng_price.values, color='steelblue')
    axes[0, 1].set_xlabel('Average Price ($)')
    axes[0, 1].set_title('Average Price by Neighbourhood Group', fontsize=14, fontweight='bold')
    axes[0, 1].grid(alpha=0.3)
    
    # Top 15 neighbourhoods by count
    top_neighbourhoods = df['neighbourhood'].value_counts().head(15)
    axes[1, 0].barh(top_neighbourhoods.index, top_neighbourhoods.values, color='coral')
    axes[1, 0].set_xlabel('Number of Listings')
    axes[1, 0].set_title('Top 15 Neighbourhoods by Listings', fontsize=14, fontweight='bold')
    axes[1, 0].grid(alpha=0.3)
    
    # Top 15 most expensive neighbourhoods
    neighbourhood_avg = df.groupby('neighbourhood')['price'].mean().sort_values(ascending=False).head(15)
    axes[1, 1].barh(neighbourhood_avg.index, neighbourhood_avg.values, color='mediumseagreen')
    axes[1, 1].set_xlabel('Average Price ($)')
    axes[1, 1].set_title('Top 15 Most Expensive Neighbourhoods', fontsize=14, fontweight='bold')
    axes[1, 1].grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('reports/figures/02_neighbourhood_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

# 3. Room Type Analysis
print("  3/10: Room type analysis...")
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Pie chart
room_counts = df['room_type'].value_counts()
axes[0].pie(room_counts.values, labels=room_counts.index, autopct='%1.1f%%', 
           colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'])
axes[0].set_title('Room Type Distribution', fontsize=14, fontweight='bold')

# Average price by room type
room_price = df.groupby('room_type')['price'].mean().sort_values()
axes[1].barh(room_price.index, room_price.values, color='steelblue')
axes[1].set_xlabel('Average Price ($)')
axes[1].set_title('Average Price by Room Type', fontsize=14, fontweight='bold')
axes[1].grid(alpha=0.3)

# Count by room type
axes[2].bar(room_counts.index, room_counts.values, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'])
axes[2].set_xlabel('Room Type')
axes[2].set_ylabel('Count')
axes[2].set_title('Listings Count by Room Type', fontsize=14, fontweight='bold')
axes[2].tick_params(axis='x', rotation=45)
axes[2].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('reports/figures/03_room_type_analysis.png', dpi=300, bbox_inches='tight')
plt.close()

# 4. Reviews Analysis
print("  4/10: Reviews analysis...")
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Review distribution
axes[0, 0].hist(df['number_of_reviews'], bins=50, edgecolor='black', alpha=0.7, color='coral')
axes[0, 0].set_xlabel('Number of Reviews')
axes[0, 0].set_ylabel('Frequency')
axes[0, 0].set_title('Distribution of Reviews', fontsize=14, fontweight='bold')
axes[0, 0].grid(alpha=0.3)

# Reviews per month
df_reviews = df[df['reviews_per_month'].notna()]
axes[0, 1].hist(df_reviews['reviews_per_month'], bins=50, edgecolor='black', alpha=0.7, color='mediumseagreen')
axes[0, 1].set_xlabel('Reviews per Month')
axes[0, 1].set_ylabel('Frequency')
axes[0, 1].set_title('Distribution of Reviews per Month', fontsize=14, fontweight='bold')
axes[0, 1].grid(alpha=0.3)

# Average reviews by room type
avg_reviews = df.groupby('room_type')['number_of_reviews'].mean().sort_values()
axes[1, 0].barh(avg_reviews.index, avg_reviews.values, color='steelblue')
axes[1, 0].set_xlabel('Average Number of Reviews')
axes[1, 0].set_title('Average Reviews by Room Type', fontsize=14, fontweight='bold')
axes[1, 0].grid(alpha=0.3)

# Review categories
review_categories = pd.cut(df['number_of_reviews'], bins=[0, 1, 10, 50, 100, 1000], 
                           labels=['0', '1-10', '11-50', '51-100', '100+'])
review_cat_counts = review_categories.value_counts().sort_index()
axes[1, 1].bar(range(len(review_cat_counts)), review_cat_counts.values, 
              tick_label=review_cat_counts.index, color='purple')
axes[1, 1].set_xlabel('Review Range')
axes[1, 1].set_ylabel('Count')
axes[1, 1].set_title('Listings by Review Count', fontsize=14, fontweight='bold')
axes[1, 1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('reports/figures/04_reviews_analysis.png', dpi=300, bbox_inches='tight')
plt.close()

# 5. Availability Analysis
print("  5/10: Availability analysis...")
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Availability distribution
axes[0, 0].hist(df['availability_365'], bins=50, edgecolor='black', alpha=0.7, color='skyblue')
axes[0, 0].set_xlabel('Availability (days/year)')
axes[0, 0].set_ylabel('Frequency')
axes[0, 0].set_title('Availability Distribution', fontsize=14, fontweight='bold')
axes[0, 0].grid(alpha=0.3)

# Availability by room type
if 'neighbourhood_group' in df.columns:
    avg_avail = df.groupby('neighbourhood_group')['availability_365'].mean().sort_values()
    axes[0, 1].barh(avg_avail.index, avg_avail.values, color='coral')
    axes[0, 1].set_xlabel('Average Availability (days)')
    axes[0, 1].set_title('Availability by Neighbourhood Group', fontsize=14, fontweight='bold')
    axes[0, 1].grid(alpha=0.3)

# Availability categories
avail_categories = pd.cut(df['availability_365'], bins=[0, 30, 90, 180, 300, 365], 
                          labels=['0-30', '31-90', '91-180', '181-300', '301-365'])
avail_cat_counts = avail_categories.value_counts().sort_index()
axes[1, 0].bar(range(len(avail_cat_counts)), avail_cat_counts.values, 
              tick_label=avail_cat_counts.index, color='mediumseagreen')
axes[1, 0].set_xlabel('Availability Range (days)')
axes[1, 0].set_ylabel('Count')
axes[1, 0].set_title('Listings by Availability', fontsize=14, fontweight='bold')
axes[1, 0].tick_params(axis='x', rotation=45)
axes[1, 0].grid(alpha=0.3)

# Price vs Availability
axes[1, 1].scatter(df['availability_365'], df['price'], alpha=0.3, s=10)
axes[1, 1].set_xlabel('Availability (days/year)')
axes[1, 1].set_ylabel('Price ($)')
axes[1, 1].set_title('Price vs Availability', fontsize=14, fontweight='bold')
axes[1, 1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('reports/figures/05_availability_analysis.png', dpi=300, bbox_inches='tight')
plt.close()

# 6. Host Analysis
print("  6/10: Host analysis...")
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Host listings distribution
if 'calculated_host_listings_count' in df.columns:
    axes[0, 0].hist(df['calculated_host_listings_count'], bins=50, edgecolor='black', alpha=0.7, color='purple')
    axes[0, 0].set_xlabel('Number of Listings per Host')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].set_title('Host Listings Distribution', fontsize=14, fontweight='bold')
    axes[0, 0].set_xlim(0, 50)
    axes[0, 0].grid(alpha=0.3)
    
    # Top hosts by listings
    host_listings = df.groupby('host_name')['id'].count().sort_values(ascending=False).head(15)
    axes[0, 1].barh(host_listings.index, host_listings.values, color='coral')
    axes[0, 1].set_xlabel('Number of Listings')
    axes[0, 1].set_title('Top 15 Hosts by Listings', fontsize=14, fontweight='bold')
    axes[0, 1].grid(alpha=0.3)

# Minimum nights distribution
axes[1, 0].hist(df['minimum_nights'][df['minimum_nights'] <= 30], bins=30, 
               edgecolor='black', alpha=0.7, color='steelblue')
axes[1, 0].set_xlabel('Minimum Nights')
axes[1, 0].set_ylabel('Frequency')
axes[1, 0].set_title('Minimum Nights Distribution (≤30)', fontsize=14, fontweight='bold')
axes[1, 0].grid(alpha=0.3)

# Price vs minimum nights
df_filtered = df[(df['minimum_nights'] <= 30) & (df['price'] <= 1000)]
axes[1, 1].scatter(df_filtered['minimum_nights'], df_filtered['price'], alpha=0.3, s=10)
axes[1, 1].set_xlabel('Minimum Nights')
axes[1, 1].set_ylabel('Price ($)')
axes[1, 1].set_title('Price vs Minimum Nights', fontsize=14, fontweight='bold')
axes[1, 1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('reports/figures/06_host_analysis.png', dpi=300, bbox_inches='tight')
plt.close()

# 7. Correlation Analysis
print("  7/10: Correlation analysis...")
numerical_cols = ['price', 'minimum_nights', 'number_of_reviews', 'reviews_per_month', 
                 'calculated_host_listings_count', 'availability_365']
numerical_cols = [col for col in numerical_cols if col in df.columns]

corr = df[numerical_cols].corr()

plt.figure(figsize=(10, 8))
sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', center=0, 
           square=True, linewidths=1, cbar_kws={"shrink": 0.8})
plt.title('Feature Correlation Heatmap', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig('reports/figures/07_correlation_heatmap.png', dpi=300, bbox_inches='tight')
plt.close()

# 8. Geographic Distribution (if neighbourhood_group exists)
if 'neighbourhood_group' in df.columns:
    print("  8/10: Geographic analysis...")
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Scatter plot by neighbourhood group
    for ng in df['neighbourhood_group'].unique():
        ng_data = df[df['neighbourhood_group'] == ng]
        axes[0].scatter(ng_data['longitude'], ng_data['latitude'], 
                       label=ng, alpha=0.3, s=5)
    axes[0].set_xlabel('Longitude')
    axes[0].set_ylabel('Latitude')
    axes[0].set_title('Listings by Location', fontsize=14, fontweight='bold')
    axes[0].legend()
    axes[0].grid(alpha=0.3)
    
    # Price heatmap
    scatter = axes[1].scatter(df['longitude'], df['latitude'], 
                            c=df['price'], cmap='viridis', alpha=0.5, s=5, vmax=500)
    axes[1].set_xlabel('Longitude')
    axes[1].set_ylabel('Latitude')
    axes[1].set_title('Price Distribution by Location', fontsize=14, fontweight='bold')
    plt.colorbar(scatter, ax=axes[1], label='Price ($)')
    axes[1].grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('reports/figures/08_geographic_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

# 9. Price vs Reviews Scatter
print("  9/10: Price vs reviews scatter...")
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

df_filtered = df[(df['price'] <= 1000) & (df['number_of_reviews'] <= 500)]
axes[0].scatter(df_filtered['number_of_reviews'], df_filtered['price'], 
               alpha=0.3, s=10, color='steelblue')
axes[0].set_xlabel('Number of Reviews')
axes[0].set_ylabel('Price ($)')
axes[0].set_title('Price vs Number of Reviews', fontsize=14, fontweight='bold')
axes[0].grid(alpha=0.3)

df_reviews_filtered = df[(df['reviews_per_month'].notna()) & (df['price'] <= 1000)]
axes[1].scatter(df_reviews_filtered['reviews_per_month'], df_reviews_filtered['price'], 
               alpha=0.3, s=10, color='coral')
axes[1].set_xlabel('Reviews per Month')
axes[1].set_ylabel('Price ($)')
axes[1].set_title('Price vs Reviews per Month', fontsize=14, fontweight='bold')
axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('reports/figures/09_price_vs_reviews.png', dpi=300, bbox_inches='tight')
plt.close()

# 10. Summary Dashboard
print("  10/10: Summary dashboard...")
fig = plt.figure(figsize=(20, 12))
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

# Key metrics
ax1 = fig.add_subplot(gs[0, 0])
metrics_text = f"""
KEY METRICS

Total Listings: {len(df):,}
Average Price: ${df['price'].mean():.2f}
Median Price: ${df['price'].median():.2f}
Total Reviews: {df['number_of_reviews'].sum():,}
Unique Hosts: {df['host_id'].nunique():,}
"""
ax1.text(0.1, 0.5, metrics_text, fontsize=14, verticalalignment='center', 
        family='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
ax1.axis('off')

# Price distribution
ax2 = fig.add_subplot(gs[0, 1:])
ax2.hist(df['price'], bins=50, edgecolor='black', alpha=0.7, color='skyblue')
ax2.set_xlabel('Price ($)')
ax2.set_ylabel('Frequency')
ax2.set_title('Price Distribution', fontweight='bold')
ax2.grid(alpha=0.3)

# Room type pie
ax3 = fig.add_subplot(gs[1, 0])
room_counts = df['room_type'].value_counts()
ax3.pie(room_counts.values, labels=room_counts.index, autopct='%1.1f%%')
ax3.set_title('Room Types', fontweight='bold')

# Neighbourhood groups
if 'neighbourhood_group' in df.columns:
    ax4 = fig.add_subplot(gs[1, 1])
    ng_counts = df['neighbourhood_group'].value_counts()
    ax4.bar(range(len(ng_counts)), ng_counts.values, tick_label=ng_counts.index)
    ax4.set_xlabel('Neighbourhood Group')
    ax4.set_ylabel('Count')
    ax4.set_title('Listings by Area', fontweight='bold')
    ax4.tick_params(axis='x', rotation=45)
    ax4.grid(alpha=0.3)

# Reviews
ax5 = fig.add_subplot(gs[1, 2])
ax5.hist(df['number_of_reviews'], bins=50, edgecolor='black', alpha=0.7, color='coral')
ax5.set_xlabel('Number of Reviews')
ax5.set_ylabel('Frequency')
ax5.set_title('Reviews Distribution', fontweight='bold')
ax5.grid(alpha=0.3)

# Availability
ax6 = fig.add_subplot(gs[2, 0])
ax6.hist(df['availability_365'], bins=50, edgecolor='black', alpha=0.7, color='mediumseagreen')
ax6.set_xlabel('Availability (days)')
ax6.set_ylabel('Frequency')
ax6.set_title('Availability Distribution', fontweight='bold')
ax6.grid(alpha=0.3)

# Price by room type
ax7 = fig.add_subplot(gs[2, 1])
price_by_room = df.groupby('room_type')['price'].mean().sort_values()
ax7.barh(price_by_room.index, price_by_room.values, color='steelblue')
ax7.set_xlabel('Average Price ($)')
ax7.set_title('Avg Price by Room Type', fontweight='bold')
ax7.grid(alpha=0.3)

# Geographic scatter
ax8 = fig.add_subplot(gs[2, 2])
ax8.scatter(df['longitude'], df['latitude'], alpha=0.2, s=1, c='blue')
ax8.set_xlabel('Longitude')
ax8.set_ylabel('Latitude')
ax8.set_title('Geographic Distribution', fontweight='bold')
ax8.grid(alpha=0.3)

plt.suptitle('Air BNB Analysis Dashboard', fontsize=20, fontweight='bold', y=0.995)
plt.savefig('reports/figures/10_summary_dashboard.png', dpi=300, bbox_inches='tight')
plt.close()

print("\n✅ All visualizations generated successfully!")
print("\nSaved files:")
for i in range(1, 11):
    filename = f"reports/figures/{i:02d}_*.png"
    print(f"  {filename}")

print("\n📊 View all images in: reports/figures/")
