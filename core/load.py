"""
core/load.py
Pemuatan artefak ringan dan agregat data dengan st.cache_data / st.cache_resource
"""

import os
import pandas as pd
import streamlit as st

@st.cache_data(show_spinner=False)
def load_agg(name: str) -> pd.DataFrame:
    """Memuat data agregat parquet dari folder data/."""
    path = os.path.join("data", f"{name}.parquet")
    if os.path.exists(path):
        return pd.read_parquet(path)
    # Fallback dummy jika berkas belum ada
    return pd.DataFrame()

@st.cache_data(show_spinner=False)
def get_seal_hash() -> str:
    """Membaca hash SHA-256 resmi dari data/SEAL.txt."""
    path = os.path.join("data", "SEAL.txt")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return "SHA-256: dfa121510c806f39cf24b894ae470a7e512af2a987c5ba7cf40dd871dd3ff84e"
