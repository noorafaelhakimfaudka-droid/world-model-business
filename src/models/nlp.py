import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF

def get_past_seller_reviews(df, order_date, seller_id, review_dict):
    """
    Mengambil teks ulasan masa lalu dari seller sebelum order_date
    review_dict: dict {seller_id: [(review_creation_date, review_message), ...]}
    """
    if seller_id not in review_dict:
        return ""
    
    past_reviews = [
        msg for date, msg in review_dict[seller_id]
        if date < order_date and isinstance(msg, str)
    ]
    return " ".join(past_reviews)

def extract_topics(texts, n_topics=3):
    if not texts or len(texts) == 0:
        return []
        
    tfidf = TfidfVectorizer(max_features=1000, stop_words='english') # portuguese stop words usually require nltk, keep simple
    try:
        X = tfidf.fit_transform(texts)
    except ValueError: # Empty vocabulary
        return []
        
    if X.shape[1] < n_topics:
        return []
        
    nmf = NMF(n_components=n_topics, random_state=42)
    nmf.fit(X)
    
    feature_names = tfidf.get_feature_names_out()
    topics = []
    for topic_idx, topic in enumerate(nmf.components_):
        top_words = [feature_names[i] for i in topic.argsort()[:-5 - 1:-1]]
        topics.append(" ".join(top_words))
        
    return topics
