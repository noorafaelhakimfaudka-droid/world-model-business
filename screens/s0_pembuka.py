"""
screens/s0_pembuka.py
Layar Pembuka: World Model for Business — Simulator Keputusan Logistik & Pengalaman Pelanggan
Menyajikan 4 KPI Utama Olist, Latar Belakang Proyek, dan Segel Holdout SHA-256
"""

import streamlit as st
from ui.components import render_segel_holdout, render_html

def render():
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        render_html("""
        <div style="font-family: 'Newsreader', serif; font-size: 24px; font-weight: 600; letter-spacing: -0.02em; color: var(--ink);">
            World Model for Business
        </div>
        """)
    with col_t2:
        render_segel_holdout()
        
    render_html('<div style="height: 32px;"></div>')
    
    render_html("""
    <div style="display: inline-block; background: var(--surface); border: 1px solid var(--line); border-radius: 999px; padding: 4px 14px; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: var(--ink2); margin-bottom: 16px;">
        Simulator Keputusan Logistik & Pengalaman Pelanggan
    </div>
    <div class="display" style="max-width: 860px; margin-bottom: 20px;">
        Jangan buru-buru beli armada truk fisik.<br>
        <i>Uji dulu aturan janjinya di komputer.</i>
    </div>
    """)
    
    # 4 Kartu KPI Eksekutif (Persis Slide 1 HTML)
    render_html("""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin-bottom: 28px;">
        <div class="card" style="margin-bottom: 0; padding: 18px 20px;">
            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; color: var(--ink2); font-weight: 600; margin-bottom: 4px;">Transaksi Nyata</div>
            <div style="font-family: 'Newsreader', serif; font-size: 32px; font-weight: 600; color: var(--ink); line-height: 1.1;">99.084</div>
            <div style="font-size: 12px; color: var(--ink2); margin-top: 4px;">Ekosistem Olist 2016–2018</div>
        </div>
        <div class="card" style="margin-bottom: 0; padding: 18px 20px;">
            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; color: var(--ink2); font-weight: 600; margin-bottom: 4px;">Cakupan Wilayah</div>
            <div style="font-family: 'Newsreader', serif; font-size: 32px; font-weight: 600; color: var(--ink); line-height: 1.1;">8,5 Juta km²</div>
            <div style="font-size: 12px; color: var(--ink2); margin-top: 4px;">Pengiriman Seluas Benua</div>
        </div>
        <div class="card" style="margin-bottom: 0; padding: 18px 20px;">
            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; color: var(--ink2); font-weight: 600; margin-bottom: 4px;">Merchant Mitra</div>
            <div style="font-family: 'Newsreader', serif; font-size: 32px; font-weight: 600; color: var(--ink); line-height: 1.1;">3.095</div>
            <div style="font-size: 12px; color: var(--ink2); margin-top: 4px;">Tersebar di 4.119 Kota</div>
        </div>
        <div class="card" style="margin-bottom: 0; padding: 18px 20px;">
            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; color: var(--ink2); font-weight: 600; margin-bottom: 4px;">Kurir Eksternal</div>
            <div style="font-family: 'Newsreader', serif; font-size: 32px; font-weight: 600; color: var(--bad); line-height: 1.1;">100%</div>
            <div style="font-size: 12px; color: var(--ink2); margin-top: 4px;">Tanpa Truk & Gudang Sendiri</div>
        </div>
    </div>
    """)
    
    # Narasi: Kenapa Memilih Ini Sebagai Proyek
    render_html("""
    <div class="card" style="border-left: 3px solid var(--ink); padding: 22px 24px; margin-bottom: 32px; background: #FFFFFF;">
        <div style="font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--ink2); margin-bottom: 8px;">
            Kenapa Memilih Masalah Ini Sebagai Proyek?
        </div>
        <div style="font-size: 16px; line-height: 26px; color: var(--ink); margin-bottom: 12px;">
            Di industri e-commerce, keterlambatan pengiriman adalah titik paling rapuh yang langsung merusak reputasi platform. 
            Olist di Brasil adalah studi kasus operasional yang nyata: mengelola hampir 100 ribu pesanan di wilayah seluas benua (8,5 juta km²) 
            tanpa memiliki satu pun gudang atau truk pengiriman sendiri—seratus persen bergantung pada kurir pos pihak ketiga.
        </div>
        <div style="font-size: 15px; line-height: 25px; color: var(--ink2);">
            Ketika keterlambatan terjadi, coba-coba mengubah janji tiba langsung di aplikasi bisa membuat pembeli kabur, 
            sementara berinvestasi armada fisik butuh modal ratusan miliar yang sangat berisiko. 
            Karena itulah dibangun <b>World Model for Business</b>: simulator keputusan digital untuk menguji berbagai skenario kebijakan 
            secara aman di komputer sebelum modal nyata dipertaruhkan di lapangan.
        </div>
    </div>
    """)
    
    col_b1, col_b2 = st.columns([1, 2])
    with col_b1:
        if st.button("Mulai Navigasi Keputusan →", type="primary", use_container_width=True):
            st.session_state["step"] = 1
            st.session_state["sub_step_1"] = "tebak"
            st.rerun()
            
    render_html("""
    <div style="font-size: 13px; color: var(--ink2); margin-top: 14px;">
        Data holdout: 12.801 pesanan terkunci segel SHA-256 untuk audit objektif · Waktu simulasi: ~3–5 menit
    </div>
    """)
