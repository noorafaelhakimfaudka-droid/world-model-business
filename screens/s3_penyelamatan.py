"""
screens/s3_penyelamatan.py
Babak 3: Matriks Penyelamatan Pelanggan dan Penjual UMKM
Pilihan: Tab Pelanggan (RFM) & Tab Seller
"""

import streamlit as st
import plotly.graph_objects as go
from ui.components import render_top_bar, label_klaim, so_what, callout, render_html
from core.load import load_agg

def render():
    render_top_bar("Babak 3: Dampak Nyata", current_step=3, total_steps=7)
    
    view_mode = st.radio(
        "Pilih Sudut Pandang:",
        ["Dampak ke Pembeli (Retensi)", "Dampak ke Penjual UMKM (Pendampingan)"],
        horizontal=True
    )
    
    render_html('<div style="height: 16px;"></div>')
    
    # ==========================================
    # 1. TAB PELANGGAN
    # ==========================================
    if "Pembeli" in view_mode:
        st.markdown(label_klaim("DATA PEMBELI", "A"), unsafe_allow_html=True)
        render_html("""
        <div class="serif" style="font-size: 32px; line-height: 42px; margin-bottom: 12px;">
        73,8% pembeli tidak pernah belanja lagi.<br>Pesanan pertama adalah satu-satunya kesempatan.
        </div>
        """)
        
        df_rfm = load_agg("agg_rfm")
        
        fig_rfm = go.Figure()
        fig_rfm.add_trace(go.Bar(
            x=df_rfm["pct"],
            y=df_rfm["segment"],
            orientation="h",
            marker=dict(color=["#14130F", "#14130F", "#5E5C55", "#8A8880", "#C2432B"]),
            text=[f"{p}%" for p in df_rfm["pct"]],
            textposition="inside",
            textfont=dict(color="white", size=13)
        ))
        fig_rfm.update_layout(
            height=240,
            margin=dict(l=16, r=16, t=16, b=16),
            xaxis=dict(title="% dari Total Pelanggan", range=[0, 80]),
            yaxis=dict(title=None, autorange="reversed")
        )
        st.plotly_chart(fig_rfm, use_container_width=True, config={"displayModeBar": False})
        
        callout(
            "RISIKO BISNIS",
            "Jika pesanan pertama telat dan pembeli kecewa, mereka hampir pasti tidak akan kembali.",
            "Biaya promosi dan iklan untuk mendatangkan pelanggan baru terbuang sia-sia jika pengalaman belanja pertama mereka mengecewakan."
        )
        
        so_what("Menjaga agar pesanan pertama tiba tepat waktu adalah strategi retensi pelanggan yang paling murah dan berdampak langsung.")

    # ==========================================
    # 2. TAB SELLER
    # ==========================================
    else:
        st.markdown(label_klaim("DATA PENJUAL", "A"), unsafe_allow_html=True)
        render_html("""
        <div class="serif" style="font-size: 32px; line-height: 42px; margin-bottom: 12px;">
        Hanya 6% penjual yang menyumbang sepertiga keterlambatan.<br>Solusinya mendampingi mereka, bukan menghukum.
        </div>
        """)
        
        df_seller = load_agg("agg_seller")
        
        st.dataframe(
            df_seller[["tier", "handling_days", "share_orders", "late_rate", "action"]],
            column_config={
                "tier": "Kelompok Penjual",
                "handling_days": "Waktu Packing & Serah",
                "share_orders": "Porsi Pesanan",
                "late_rate": "Persentase Telat",
                "action": "Solusi Pendampingan"
            },
            hide_index=True,
            use_container_width=True
        )
        
        callout(
            "TEMUAN LAPANGAN",
            "Penjual yang lambat sebagian besar adalah pelaku UMKM rumahan dengan proses serba manual.",
            "Alih-alih memberi penalti denda yang mematikan usaha mereka, menyediakan fitur cetak label resi otomatis terbukti memangkas waktu pemrosesan hingga 1,2 hari kerja."
        )
        
        so_what("Membantu 6% penjual ini memproses paket lebih cepat langsung melindungi sepertiga pembeli dari risiko keterlambatan.")
        
    render_html('<div style="height: 36px;"></div>')
    if st.button("Lanjut ke Sistem Peringatan Dini", type="primary"):
        st.session_state["step"] = 4
        st.rerun()
