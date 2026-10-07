import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
import warnings
warnings.filterwarnings('ignore')

def get_propensity_scores(df, treatment_col, confounder_cols):
    X = df[confounder_cols]
    y = df[treatment_col]
    
    # Model sederhana untuk mencari probabilitas "ditakdirkan untuk telat"
    ps_model = make_pipeline(SimpleImputer(strategy='median'), StandardScaler(), LogisticRegression(max_iter=500))
    ps_model.fit(X, y)
    
    return ps_model.predict_proba(X)[:, 1]

def calculate_ate_with_psm(df, treatment_col, outcome_col, confounder_cols, caliper=0.05):
    """
    Melakukan Propensity Score Matching sederhana menggunakan NearestNeighbors.
    Mengembalikan ATE (Average Treatment Effect).
    """
    df_clean = df.dropna(subset=[treatment_col, outcome_col]).copy()
    
    # 1. Hitung Propensity Score (PS)
    df_clean['ps'] = get_propensity_scores(df_clean, treatment_col, confounder_cols)
    
    treated = df_clean[df_clean[treatment_col] == 1].reset_index()
    control = df_clean[df_clean[treatment_col] == 0].reset_index()
    
    if len(treated) == 0 or len(control) == 0:
        return np.nan, 0
        
    # 2. Cari kembaran (Matching) berdasarkan PS terdekat
    nn = NearestNeighbors(n_neighbors=1, algorithm='ball_tree')
    nn.fit(control[['ps']])
    
    distances, indices = nn.kneighbors(treated[['ps']])
    
    # Filter dengan caliper (buang kembaran yang terlalu beda)
    valid_matches = distances.flatten() <= caliper
    
    treated_matched = treated[valid_matches]
    control_matched = control.iloc[indices.flatten()[valid_matches]]
    
    # 3. Hitung ATE (Rata-rata selisih outcome antara yang telat dan kembaran tepat waktunya)
    if len(treated_matched) == 0:
        return np.nan, 0
        
    ate = treated_matched[outcome_col].mean() - control_matched[outcome_col].mean()
    
    return ate, len(treated_matched)

def run_placebo_test(df, treatment_col, confounder_cols):
    """
    Tes Placebo: Outcome diubah menjadi 'harga barang' yang tidak mungkin 
    disebabkan oleh keterlambatan (harga ditentukan SEBELUM telat).
    ATE seharusnya mendekati 0.
    """
    ate, matched_count = calculate_ate_with_psm(df, treatment_col, 'total_items_value', confounder_cols)
    return ate, matched_count
