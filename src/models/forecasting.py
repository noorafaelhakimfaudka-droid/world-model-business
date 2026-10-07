import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import warnings
warnings.filterwarnings('ignore')

def aggregate_weekly_data(df, top_n_categories=6):
    # Pilih top kategori berdasarkan volume
    top_cats = df['primary_category'].value_counts().head(top_n_categories).index.tolist()
    
    df_top = df[df['primary_category'].isin(top_cats)].copy()
    
    # Pastikan datetime
    df_top['order_purchase_timestamp'] = pd.to_datetime(df_top['order_purchase_timestamp'])
    
    # Resample per minggu (mulai Senin)
    df_top.set_index('order_purchase_timestamp', inplace=True)
    
    weekly = df_top.groupby('primary_category').resample('W-MON').agg(
        unit_sold=('order_id', 'count'),
        avg_price=('total_items_value', 'mean')
    ).reset_index()
    
    return weekly

def build_lag_features(weekly_df):
    df = weekly_df.sort_values(['primary_category', 'order_purchase_timestamp']).copy()
    
    # Tambahkan fitur kalender
    df['month'] = df['order_purchase_timestamp'].dt.month
    df['week_of_year'] = df['order_purchase_timestamp'].dt.isocalendar().week.astype(int)
    
    # Lag 1 sampai 4 minggu ke belakang
    for lag in [1, 2, 3, 4]:
        df[f'unit_lag_{lag}'] = df.groupby('primary_category')['unit_sold'].shift(lag)
        
    df.dropna(inplace=True)
    return df

def calculate_wape(y_true, y_pred):
    return np.sum(np.abs(y_true - y_pred)) / np.sum(y_true)

def rolling_validation(df, model, features, target='unit_sold', n_splits=5):
    # Rolling window sederhana karena data kita sedikit (~75 minggu)
    # Kita latih di data lama, tes di 4 minggu ke depan. Geser.
    categories = df['primary_category'].unique()
    
    wapes = []
    
    for cat in categories:
        df_c = df[df['primary_category'] == cat].sort_values('order_purchase_timestamp').reset_index(drop=True)
        if len(df_c) < 30:
            continue
            
        n = len(df_c)
        test_size = 4
        
        cat_wapes = []
        for i in range(n_splits):
            train_end = n - test_size * (i + 1)
            if train_end < 10:
                break
                
            train = df_c.iloc[:train_end]
            test = df_c.iloc[train_end:train_end+test_size]
            
            X_train, y_train = train[features], train[target]
            X_test, y_test = test[features], test[target]
            
            # Khusus Baseline (nilai lag 1)
            if model == 'baseline':
                preds = X_test['unit_lag_1']
            else:
                model.fit(X_train, y_train)
                preds = model.predict(X_test)
                
            wape = calculate_wape(y_test.values, preds)
            cat_wapes.append(wape)
            
        if cat_wapes:
            wapes.append(np.mean(cat_wapes))
            
    return np.mean(wapes) if wapes else np.nan

def evaluate_models(df):
    features = ['avg_price', 'month', 'week_of_year', 'unit_lag_1', 'unit_lag_2', 'unit_lag_3', 'unit_lag_4']
    
    # 1. Baseline
    baseline_wape = rolling_validation(df, 'baseline', features)
    
    # 2. Ridge (Linier)
    ridge_model = make_pipeline(SimpleImputer(), StandardScaler(), Ridge())
    ridge_wape = rolling_validation(df, ridge_model, features)
    
    # 3. Random Forest (Bisa diganti LightGBM, tapi RF lebih mudah tanpa dependensi ekstra untuk sekarang)
    rf_model = make_pipeline(SimpleImputer(), RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42))
    rf_wape = rolling_validation(df, rf_model, features)
    
    return {
        'Baseline (Lag 1)': baseline_wape,
        'Statistik (Ridge)': ridge_wape,
        'Machine Learning (RF)': rf_wape
    }
