"""
screens/s0_pembuka.py
Layar Pembuka: "Jangan perbaiki kurirnya dulu. Uji janjinya."
"""

import streamlit as st
from ui.components import render_segel_holdout, render_html

def render():
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        render_html('<div style="font-family: \'Newsreader\', serif; font-size: 24px; font-weight: 600; letter-spacing: -0.02em;">Janji</div>')
    with col_t2:
        render_segel_holdout()
        
    render_html('<div style="height: 64px;"></div>')
    
    render_html("""
    <div class="display" style="max-width: 820px; margin-bottom: 24px;">
    Jangan buru-buru perbaiki kurir.<br>
    <i>Uji dulu janjinya.</i>
    </div>
    """)
    
    render_html("""
    <div style="font-size: 18px; line-height: 28px; color: var(--ink2); max-width: 680px; margin-bottom: 48px;">
    Berdasarkan analisis 99.084 pesanan riil Olist di Brasil. Sebanyak 12.801 pesanan kami pisahkan sebagai data uji murni sejak awal, 
    agar simulasi ini mencerminkan kenyataan di lapangan dan bebas dari bias.
    </div>
    """)
    
    col_b1, col_b2 = st.columns([1, 2])
    with col_b1:
        if st.button("Mulai Simulasi", type="primary", use_container_width=True):
            st.session_state["step"] = 1
            st.session_state["sub_step_1"] = "tebak"
            st.rerun()
            
    render_html("""
    <div style="font-size: 13px; color: var(--ink2); margin-top: 16px;">
    Waktu eksplorasi: sekitar 3–5 menit
    </div>
    """)
