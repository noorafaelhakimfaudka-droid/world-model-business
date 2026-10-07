import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression

class WorldModelSimulator:
    def __init__(self):
        # Menyimpan model-model blok
        self.late_model = None
        self.review_model = None
        
    def train_late_model(self, X, y):
        # Abstraksi dari Random Forest Fase 6
        self.late_model = LogisticRegression(class_weight='balanced')
        self.late_model.fit(X, y)
        
    def train_review_model(self, X, y):
        # Abstraksi dari prediksi ulasan
        self.review_model = LogisticRegression(class_weight='balanced')
        self.review_model.fit(X, y)
        
    def simulate(self, X_future):
        """
        Rantai B1 -> B2 -> B3
        Input: Data fitur masa depan
        Output: Prediksi keterlambatan dan probabilitas ulasan buruk
        """
        if self.late_model is None or self.review_model is None:
            raise ValueError("Model belum dilatih!")
            
        # Blok 1: Prediksi Keterlambatan
        late_probs = self.late_model.predict_proba(X_future)[:, 1]
        
        # Simulasi stokastik (undian)
        simulated_late = (np.random.rand(len(late_probs)) < late_probs).astype(int)
        
        # Tambahkan hasil simulasi keterlambatan ke fitur untuk masuk ke Blok 2
        X_review = X_future.copy()
        X_review['simulated_is_late'] = simulated_late
        
        # Blok 2: Prediksi Ulasan Buruk (karena telat)
        review_probs = self.review_model.predict_proba(X_review)[:, 1]
        simulated_bad_review = (np.random.rand(len(review_probs)) < review_probs).astype(int)
        
        return simulated_late, simulated_bad_review


def run_u2_known_answer_test():
    """
    Tes U2: Jawaban Diketahui
    Sengaja membuat data palsu di mana 'telat' MENYEBABKAN 'ulasan buruk' 
    naik tepat 0.40 poin secara matematis.
    """
    np.random.seed(42)
    n = 10000
    
    # Fitur acak
    jarak = np.random.normal(50, 20, n)
    harga = np.random.normal(100, 30, n)
    
    # Peluang telat murni dipengaruhi jarak
    prob_late = 1 / (1 + np.exp(-(jarak - 50) / 10))
    is_late = (np.random.rand(n) < prob_late).astype(int)
    
    # Peluang ulasan buruk: Dasar 10%. Jika telat, tambah persis 40% (0.40)
    # Ini adalah 'Ground Truth' atau Jawaban Diketahui
    base_bad_review_prob = 0.10 + (is_late * 0.40) 
    is_bad_review = (np.random.rand(n) < base_bad_review_prob).astype(int)
    
    df_dummy = pd.DataFrame({
        'jarak': jarak,
        'harga': harga,
        'simulated_is_late': is_late,
        'is_bad_review': is_bad_review
    })
    
    # Latih model penilai
    X = df_dummy[['jarak', 'harga', 'simulated_is_late']]
    y = df_dummy['is_bad_review']
    
    model = LogisticRegression()
    model.fit(X, y)
    
    # Hitung efek menurut mesin (Partial Dependence / ATE)
    X_false = X.copy()
    X_false['simulated_is_late'] = 0
    prob_if_not_late = model.predict_proba(X_false)[:, 1].mean()
    
    X_true = X.copy()
    X_true['simulated_is_late'] = 1
    prob_if_late = model.predict_proba(X_true)[:, 1].mean()
    
    mesin_effect = prob_if_late - prob_if_not_late
    ground_truth = 0.40
    galat = abs(mesin_effect - ground_truth) / ground_truth
    
    return ground_truth, mesin_effect, galat
