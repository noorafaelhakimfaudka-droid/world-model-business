"""
screens/s2_diagnosis.py
Babak 2: Diagnosis Operasional dan Geografi
1. Asimetri Geografi (SP vs RR)
2. Dekomposisi Waktu (Seller 3 hari vs Kurir 9 hari)
3. Hukum Pareto Kategori (20 kategori = 80% volume)
4. Peramalan Permintaan (WAPE 13,6%)
"""

import streamlit as st
import plotly.graph_objects as go
from ui.components import render_top_bar, label_klaim, so_what, callout, render_html
from core.load import load_agg

def render():
    render_top_bar("Babak 2: Diagnosis", current_step=2, total_steps=7)
    
    # -------------------------------------------------------------
    # 1. ASIMETRI GEOGRAFI
    # -------------------------------------------------------------
    st.markdown(label_klaim("DATA WILAYAH", "A"), unsafe_allow_html=True)
    render_html("""
    <div class="serif" style="font-size: 28px; line-height: 38px; margin-bottom: 8px;">
    1. Ketimpangan Durasi Antar Wilayah
    </div>
    """)
    
    df_geo = load_agg("agg_geo")
    
    col_g1, col_g2 = st.columns([1, 1])
    with col_g1:
        render_html("""
        <div style="font-size: 15px; color: var(--ink2); margin-bottom: 12px;">
        Pilih dua wilayah untuk melihat perbandingan waktu kirim:
        </div>
        """)
        st_state1 = st.selectbox("Wilayah Asal/Pusat:", ["SP (São Paulo)", "RJ (Rio de Janeiro)", "MG (Minas Gerais)"], index=0)
        st_state2 = st.selectbox("Wilayah Tujuan Terjauh:", ["RR (Roraima)", "AP (Amapá)", "AM (Amazonas)", "AC (Acre)"], index=0)
        
    with col_g2:
        render_html("""
        <div class="card" style="padding: 16px 20px;">
        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--line); padding-bottom: 8px; margin-bottom: 8px;">
        <span><b>São Paulo (SP)</b>: 41,8% pesanan</span>
        <span><b>8,3 hari</b> rata-rata</span>
        </div>
        <div style="display: flex; justify-content: space-between;">
        <span><b>Roraima (RR)</b>: 0,1% pesanan</span>
        <span style="color: var(--bad); font-weight: 600;">29,0 hari</span>
        </div>
        </div>
        """)
        
    so_what("São Paulo menyumbang 41,8% pesanan dan tiba dalam 8 hari, sementara paket ke Roraima butuh 29 hari. Menyamaratakan janji pengiriman untuk semua rute jelas tidak realistis.")
    
    render_html('<div style="height: 48px;"></div>')

    # -------------------------------------------------------------
    # 2. DEKOMPOSISI WAKTU
    # -------------------------------------------------------------
    st.markdown(label_klaim("ANALISIS WAKTU", "A"), unsafe_allow_html=True)
    render_html("""
    <div class="serif" style="font-size: 28px; line-height: 38px; margin-bottom: 8px;">
    2. Dari Mana Keterlambatan Sebenarnya Berasal?
    </div>
    """)
    
    fig_time = go.Figure()
    fig_time.add_trace(go.Bar(
        y=["Semua Pesanan", "São Paulo (Intra-SP)", "Roraima (Antar-Pulau)"],
        x=[3.0, 2.5, 3.5],
        name="Waktu di Penjual (Packing)",
        orientation="h",
        marker=dict(color="#14130F"),
        text=["3,0 hari (24%)", "2,5 hari (30%)", "3,5 hari (12%)"],
        textposition="inside"
    ))
    fig_time.add_trace(go.Bar(
        y=["Semua Pesanan", "São Paulo (Intra-SP)", "Roraima (Antar-Pulau)"],
        x=[9.5, 5.8, 25.5],
        name="Perjalanan Kurir",
        orientation="h",
        marker=dict(color="#8A8880"),
        text=["9,5 hari (76%)", "5,8 hari (70%)", "25,5 hari (88%)"],
        textposition="inside"
    ))
    
    fig_time.update_layout(
        barmode="stack",
        height=200,
        margin=dict(l=16, r=16, t=16, b=16),
        xaxis=dict(title="Hari", showgrid=True),
        yaxis=dict(title=None)
    )
    st.plotly_chart(fig_time, use_container_width=True, config={"displayModeBar": False})
    
    so_what("Sekitar 25% waktu pengiriman sebenarnya habis di tangan penjual sebelum paket diserahkan ke kurir. Membantu penjual memproses barang lebih cepat bisa memangkas waktu kirim tanpa harus menambah armada kurir.")
    
    render_html('<div style="height: 48px;"></div>')

    # -------------------------------------------------------------
    # 3. HUKUM PARETO KATEGORI & FORECAST
    # -------------------------------------------------------------
    st.markdown(label_klaim("PRIORITAS & PREDIKSI", "A"), unsafe_allow_html=True)
    render_html("""
    <div class="serif" style="font-size: 28px; line-height: 38px; margin-bottom: 8px;">
    3. Fokus Kategori Produk & Prediksi Pesanan
    </div>
    """)
    
    col_p1, col_p2 = st.columns([1, 1])
    with col_p1:
        render_html("""
        <div class="card">
        <div style="font-size: 13px; text-transform: uppercase; color: var(--ink2); font-weight: 600;">Fokus Kategori Produk</div>
        <div style="font-size: 24px; font-weight: 700; color: var(--ink); margin: 6px 0;">20 Kategori = 80% Pesanan</div>
        <div style="font-size: 14px; color: var(--ink2); line-height: 20px;">
        Dari total 71 kategori barang di Olist, kita cukup fokus memperbaiki 20 kategori utama untuk mengamankan 80% transaksi platform.
        </div>
        </div>
        """)
        
    with col_p2:
        render_html("""
        <div class="card">
        <div style="font-size: 13px; text-transform: uppercase; color: var(--ink2); font-weight: 600;">Prediksi Beban Pesanan</div>
        <div style="font-size: 24px; font-weight: 700; color: var(--good); margin: 6px 0;">Margin Error 13,6% (Mingguan)</div>
        <div style="font-size: 14px; color: var(--ink2); line-height: 20px;">
        Prediksi volume mingguan kami sangat akurat (selisih rata-rata hanya 13,6%, jauh di bawah batas toleransi bisnis 25%). Ini membuat persiapan kapasitas gudang dan kurir jauh lebih terencana.
        </div>
        </div>
        """)
        
    render_html('<div style="height: 36px;"></div>')
    
    if st.button("Lanjut ke Analisis Dampak", type="primary"):
        st.session_state["step"] = 3
        st.rerun()
