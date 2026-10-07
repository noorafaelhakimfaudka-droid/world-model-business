import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_recall_curve, auc

def build_classification_pipeline(cat_cols, num_cols, model_type='logistic'):
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, num_cols),
            ('cat', categorical_transformer, cat_cols)
        ])
    
    if model_type == 'logistic':
        clf = LogisticRegression(class_weight='balanced', max_iter=500, random_state=42)
    elif model_type == 'rf':
        clf = RandomForestClassifier(n_estimators=100, max_depth=8, class_weight='balanced', random_state=42)
    elif model_type == 'rule_based':
        clf = None # Aturan sederhana tidak butuh model
    else:
        raise ValueError("Model tidak dikenali")
        
    if clf is not None:
        return Pipeline(steps=[('preprocessor', preprocessor), ('classifier', clf)])
    return None

def evaluate_top_k(y_true, y_probs, k_fraction=0.1):
    # Urutkan berdasarkan probabilitas keterlambatan tertinggi
    n_top = int(len(y_true) * k_fraction)
    
    # argsort secara ascending, jadi ambil n_top dari belakang
    top_indices = np.argsort(y_probs)[-n_top:]
    
    y_true_top = np.array(y_true)[top_indices]
    
    # Presisi = (Benar terlambat di top K) / (Jumlah top K)
    precision_at_k = np.mean(y_true_top)
    
    # Recall = (Benar terlambat di top K) / (Total semua yang terlambat di data uji)
    total_late = np.sum(y_true)
    recall_at_k = np.sum(y_true_top) / total_late if total_late > 0 else 0
    
    # PR-AUC
    precision, recall, _ = precision_recall_curve(y_true, y_probs)
    pr_auc = auc(recall, precision)
    
    return precision_at_k, recall_at_k, pr_auc
