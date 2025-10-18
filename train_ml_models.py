"""
Machine Learning Models for Real Air BNB Data
Price prediction using your actual dataset columns
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import os

warnings.filterwarnings('ignore')
os.makedirs('reports/models', exist_ok=True)

print("="*80)
print("MACHINE LEARNING - PRICE PREDICTION")
print("="*80)

# Load data
print("\n### Loading Data ###")
df = pd.read_csv('Airbnb_dataset.csv')
print(f"✓ Loaded {len(df):,} records")

# Data Preparation
print("\n### Data Preparation ###")
df_ml = df.copy()

# Handle missing values
df_ml['reviews_per_month'].fillna(0, inplace=True)
df_ml = df_ml.dropna(subset=['host_name'])

# Remove extreme outliers (price > $1000)
df_ml = df_ml[df_ml['price'] <= 1000]
df_ml = df_ml[df_ml['price'] > 0]

print(f"After cleaning: {len(df_ml):,} records")

# Feature Engineering
print("\n### Feature Engineering ###")

# 1. Reviews features
df_ml['has_reviews'] = (df_ml['number_of_reviews'] > 0).astype(int)
df_ml['review_score'] = df_ml['reviews_per_month'] * df_ml['number_of_reviews']
df_ml['is_popular'] = (df_ml['number_of_reviews'] > df_ml['number_of_reviews'].median()).astype(int)

# 2. Host features
df_ml['is_multi_host'] = (df_ml['calculated_host_listings_count'] > 1).astype(int)
df_ml['host_experience'] = np.where(df_ml['calculated_host_listings_count'] > 5, 'High',
                                     np.where(df_ml['calculated_host_listings_count'] > 1, 'Medium', 'Low'))

# 3. Availability features
df_ml['is_full_time'] = (df_ml['availability_365'] >= 300).astype(int)
df_ml['availability_category'] = pd.cut(df_ml['availability_365'], 
                                          bins=[0, 90, 180, 300, 365],
                                          labels=['Low', 'Medium', 'High', 'Full'])

# 4. Location features (using lat/long)
df_ml['distance_from_center'] = np.sqrt((df_ml['latitude'] - df_ml['latitude'].mean())**2 + 
                                         (df_ml['longitude'] - df_ml['longitude'].mean())**2)

# 5. Booking features
df_ml['is_flexible'] = (df_ml['minimum_nights'] <= 3).astype(int)
df_ml['min_nights_category'] = pd.cut(df_ml['minimum_nights'],
                                       bins=[0, 1, 7, 30, 1000],
                                       labels=['1_night', '2-7_nights', '8-30_nights', '30+_nights'])

print("Created features:")
print("  - has_reviews, review_score, is_popular")
print("  - is_multi_host, host_experience")
print("  - is_full_time, availability_category")
print("  - distance_from_center")
print("  - is_flexible, min_nights_category")

# Encode categorical variables
print("\n### Encoding Categorical Variables ###")
le_dict = {}

categorical_features = ['neighbourhood_group', 'neighbourhood', 'room_type', 
                       'host_experience', 'availability_category', 'min_nights_category']

for col in categorical_features:
    le = LabelEncoder()
    df_ml[f'{col}_encoded'] = le.fit_transform(df_ml[col].astype(str))
    le_dict[col] = le
    print(f"  Encoded {col}: {len(le.classes_)} categories")

# Select features for modeling
feature_cols = [
    'neighbourhood_group_encoded',
    'neighbourhood_encoded',
    'room_type_encoded',
    'latitude',
    'longitude',
    'minimum_nights',
    'number_of_reviews',
    'reviews_per_month',
    'calculated_host_listings_count',
    'availability_365',
    'has_reviews',
    'review_score',
    'is_popular',
    'is_multi_host',
    'host_experience_encoded',
    'is_full_time',
    'availability_category_encoded',
    'distance_from_center',
    'is_flexible',
    'min_nights_category_encoded'
]

X = df_ml[feature_cols]
y = df_ml['price']

print(f"\n### Final Dataset ###")
print(f"Features: {X.shape[1]}")
print(f"Samples: {X.shape[0]:,}")
print(f"\nTarget variable (price):")
print(f"  Mean: ${y.mean():.2f}")
print(f"  Median: ${y.median():.2f}")
print(f"  Std: ${y.std():.2f}")

# Train-test split
print("\n### Train-Test Split ###")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"Training set: {len(X_train):,} samples")
print(f"Test set: {len(X_test):,} samples")

# Train Models
print("\n" + "="*80)
print("TRAINING MODELS")
print("="*80)

models = {
    'Linear Regression': LinearRegression(),
    'Random Forest': RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1),
    'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42)
}

results = {}

for name, model in models.items():
    print(f"\n### {name} ###")
    print("Training...")
    model.fit(X_train, y_train)
    
    # Predictions
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    # Metrics
    train_mae = mean_absolute_error(y_train, y_pred_train)
    test_mae = mean_absolute_error(y_test, y_pred_test)
    train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
    test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
    train_r2 = r2_score(y_train, y_pred_train)
    test_r2 = r2_score(y_test, y_pred_test)
    
    results[name] = {
        'model': model,
        'train_mae': train_mae,
        'test_mae': test_mae,
        'train_rmse': train_rmse,
        'test_rmse': test_rmse,
        'train_r2': train_r2,
        'test_r2': test_r2,
        'predictions': y_pred_test
    }
    
    print(f"Training MAE: ${train_mae:.2f}")
    print(f"Test MAE: ${test_mae:.2f}")
    print(f"Training RMSE: ${train_rmse:.2f}")
    print(f"Test RMSE: ${test_rmse:.2f}")
    print(f"Training R²: {train_r2:.4f}")
    print(f"Test R²: {test_r2:.4f}")

# Best Model
print("\n" + "="*80)
print("BEST MODEL")
print("="*80)
best_model_name = min(results.keys(), key=lambda k: results[k]['test_mae'])
best_model = results[best_model_name]['model']
print(f"\n🏆 Best Model: {best_model_name}")
print(f"Test MAE: ${results[best_model_name]['test_mae']:.2f}")
print(f"Test R²: {results[best_model_name]['test_r2']:.4f}")

# Feature Importance (for tree-based models)
if best_model_name in ['Random Forest', 'Gradient Boosting']:
    print("\n### Top 10 Most Important Features ###")
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': best_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    for idx, row in feature_importance.head(10).iterrows():
        feature_name = row['feature'].replace('_encoded', '')
        print(f"  {feature_name}: {row['importance']:.4f}")

# Visualizations
print("\n### Generating Visualizations ###")

# 1. Model Comparison
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

model_names = list(results.keys())
test_maes = [results[m]['test_mae'] for m in model_names]
test_rmses = [results[m]['test_rmse'] for m in model_names]
test_r2s = [results[m]['test_r2'] for m in model_names]

axes[0].bar(model_names, test_maes, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
axes[0].set_ylabel('MAE ($)')
axes[0].set_title('Mean Absolute Error (Lower is Better)', fontweight='bold')
axes[0].tick_params(axis='x', rotation=45)
axes[0].grid(alpha=0.3)

axes[1].bar(model_names, test_rmses, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
axes[1].set_ylabel('RMSE ($)')
axes[1].set_title('Root Mean Squared Error (Lower is Better)', fontweight='bold')
axes[1].tick_params(axis='x', rotation=45)
axes[1].grid(alpha=0.3)

axes[2].bar(model_names, test_r2s, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
axes[2].set_ylabel('R² Score')
axes[2].set_title('R² Score (Higher is Better)', fontweight='bold')
axes[2].tick_params(axis='x', rotation=45)
axes[2].axhline(0, color='red', linestyle='--', alpha=0.5)
axes[2].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('reports/models/model_comparison.png', dpi=300, bbox_inches='tight')
plt.close()
print("  ✓ Saved: reports/models/model_comparison.png")

# 2. Predictions vs Actual (Best Model)
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

y_pred_best = results[best_model_name]['predictions']

# Scatter plot
axes[0].scatter(y_test, y_pred_best, alpha=0.5, s=20)
axes[0].plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
axes[0].set_xlabel('Actual Price ($)')
axes[0].set_ylabel('Predicted Price ($)')
axes[0].set_title(f'{best_model_name}: Predictions vs Actual', fontweight='bold')
axes[0].grid(alpha=0.3)

# Residuals
residuals = y_test - y_pred_best
axes[1].scatter(y_pred_best, residuals, alpha=0.5, s=20)
axes[1].axhline(0, color='red', linestyle='--', lw=2)
axes[1].set_xlabel('Predicted Price ($)')
axes[1].set_ylabel('Residuals ($)')
axes[1].set_title('Residual Plot', fontweight='bold')
axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('reports/models/predictions_analysis.png', dpi=300, bbox_inches='tight')
plt.close()
print("  ✓ Saved: reports/models/predictions_analysis.png")

# 3. Feature Importance (if available)
if best_model_name in ['Random Forest', 'Gradient Boosting']:
    fig, ax = plt.subplots(figsize=(10, 8))
    
    top_features = feature_importance.head(15)
    top_features['feature_clean'] = top_features['feature'].str.replace('_encoded', '')
    
    ax.barh(range(len(top_features)), top_features['importance'], color='steelblue')
    ax.set_yticks(range(len(top_features)))
    ax.set_yticklabels(top_features['feature_clean'])
    ax.set_xlabel('Importance')
    ax.set_title(f'{best_model_name}: Top 15 Feature Importances', fontweight='bold', fontsize=14)
    ax.grid(alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.savefig('reports/models/feature_importance.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: reports/models/feature_importance.png")

# 4. Error Distribution
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

errors = np.abs(y_test - y_pred_best)

axes[0].hist(errors, bins=50, edgecolor='black', alpha=0.7, color='coral')
axes[0].axvline(errors.mean(), color='red', linestyle='--', label=f'Mean: ${errors.mean():.2f}')
axes[0].axvline(errors.median(), color='green', linestyle='--', label=f'Median: ${errors.median():.2f}')
axes[0].set_xlabel('Absolute Error ($)')
axes[0].set_ylabel('Frequency')
axes[0].set_title('Distribution of Prediction Errors', fontweight='bold')
axes[0].legend()
axes[0].grid(alpha=0.3)

axes[1].hist(residuals, bins=50, edgecolor='black', alpha=0.7, color='skyblue')
axes[1].axvline(0, color='red', linestyle='--', lw=2)
axes[1].set_xlabel('Residual ($)')
axes[1].set_ylabel('Frequency')
axes[1].set_title('Distribution of Residuals', fontweight='bold')
axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('reports/models/error_distribution.png', dpi=300, bbox_inches='tight')
plt.close()
print("  ✓ Saved: reports/models/error_distribution.png")

# Summary Report
print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"\n✅ Trained {len(models)} models")
print(f"✅ Best model: {best_model_name}")
print(f"✅ Test MAE: ${results[best_model_name]['test_mae']:.2f}")
print(f"✅ Test R²: {results[best_model_name]['test_r2']:.4f}")
print(f"✅ Average prediction error: ${errors.mean():.2f}")
print(f"✅ Median prediction error: ${errors.median():.2f}")
print(f"\n✅ Generated 4 visualization files in reports/models/")

# Save results
results_df = pd.DataFrame({
    'Model': model_names,
    'Test MAE': [results[m]['test_mae'] for m in model_names],
    'Test RMSE': [results[m]['test_rmse'] for m in model_names],
    'Test R²': [results[m]['test_r2'] for m in model_names]
})

results_df.to_csv('reports/models/model_results.csv', index=False)
print("✅ Saved: reports/models/model_results.csv")

print("\n" + "="*80)
print("COMPLETE!")
print("="*80)
print("\nTo use the model:")
print("  1. View visualizations in: reports/models/")
print("  2. Best model for deployment: " + best_model_name)
print("  3. Expected error: ~$" + f"{results[best_model_name]['test_mae']:.2f} per prediction")
print("="*80)
