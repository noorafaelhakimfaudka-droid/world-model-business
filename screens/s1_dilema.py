"""
screens/s1_dilema.py
Babak 1: Dilema Logistik dan Reputasi
1A (Tebak) -> 1B (Ungkap & Tebing Kepuasan) -> 1C (Konteks 4 KPI)
"""

import streamlit as st
import plotly.graph_objects as go
from ui.components import render_top_bar, label_klaim, hero_number, so_what, callout, render_html
from core.load import load_agg

def render():
    sub_step = st.session_state.get("sub_step_1", "tebak")
    
    # ==========================================
    # 1A. TEBAK
    # ==========================================
    if sub_step == "tebak":
        render_top_bar("Babak 1: Dilema", current_step=1, total_steps=7)
        
        st.markdown(label_klaim("PERTANYAAN", "A"), unsafe_allow_html=True)
        render_html("""
        <div class="serif" style="font-size: 38px; line-height: 48px; margin: 16px 0 32px 0;">
        Pesanan yang datang terlambat,<br>berapa bintang rata-rata ulasannya?
        </div>
        """)
        
        st.caption("Sebagai pembanding: pesanan yang tiba tepat waktu mendapat rata-rata 4,3 bintang.")
        
        tebakan = st.radio(
            "Pilih tebakanmu:",
            ["1,0 – 1,9", "2,0 – 2,9", "3,0 – 3,9", "4,0 – 4,9", "5,0"],
            index=2,
            horizontal=True
        )
        
        render_html('<div style="height: 32px;"></div>')
        if st.button("Kunci tebakan", type="primary"):
            st.session_state["tebakan"] = tebakan
            st.session_state["sub_step_1"] = "ungkap"
            st.rerun()

    # ==========================================
    # 1B. UNGKAP & TEBING KEPUASAN
    # ==========================================
    elif sub_step == "ungkap":
        render_top_bar("Babak 1: Ungkap Kausalitas", current_step=1, total_steps=7)
        
        st.markdown(label_klaim("TEMUAN UTAMA", "B"), unsafe_allow_html=True)
        hero_number("−1,86", unit="bintang", warna="var(--bad)", subteks="Penurunan rating murni (ATE kausal) pada 6.740 pasang pesanan kembar identik yang disetarakan.")
        
        tebakan_user = st.session_state.get("tebakan", "3,0 – 3,9")
        if tebakan_user == "2,0 – 2,9":
            render_html('<div style="font-size: 15px; color: var(--good); font-weight: 500; margin-bottom: 24px;">Tepat sekali! Tebakanmu masuk di rentang 2,0 – 2,9. Angka riil di data adalah 2,4 bintang:</div>')
        else:
            render_html(f'<div style="font-size: 15px; color: var(--bad); font-weight: 500; margin-bottom: 24px;">Kamu menebak {tebakan_user}. Di kenyataan aslinya, rating pesanan telat langsung anjlok ke 2,4 bintang:</div>')
            
        # Grafik Tebing Kepuasan (Plotly)
        fig = go.Figure()
        x_pts = ["Tepat waktu", "Telat 1–3 hari", "Telat >7 hari"]
        y_pts = [4.3, 2.4, 1.2]
        
        fig.add_trace(go.Scatter(
            x=x_pts,
            y=y_pts,
            mode="lines+markers+text",
            line=dict(color="#14130F", width=2.5, shape="spline"),
            marker=dict(size=9, color=["#1F7A5A", "#C2432B", "#C2432B"]),
            text=["4,3 ★", "2,4 ★", "1,2 ★"],
            textposition=["top center", "top right", "top right"],
            textfont=dict(family="Instrument Sans", size=14, color="#14130F")
        ))
        
        fig.update_layout(
            height=280,
            yaxis=dict(range=[0.8, 5.0], title=None, dtick=1),
            xaxis=dict(title=None),
            margin=dict(l=16, r=24, t=24, b=24)
        )
        
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.caption("Ulasan buruk (bintang 1–2): Saat tepat waktu hanya 9,8%, tapi kalau telat lebih dari seminggu melonjak jadi 54,3% (naik 5,5 kali lipat).")
        
        callout("POIN PENTING", "Ekspektasi pembeli runtuh seketika saat tanggal janji terlewati.", "Pembeli tidak terlalu mempermasalahkan paket datang cepat atau biasa saja, tapi mereka sangat kecewa jika paket melewati tanggal estimasi di aplikasi.")
        
        col_btn1, col_btn2 = st.columns([1, 2])
        with col_btn1:
            if st.button("Lanjut ke Konteks Bisnis", type="primary", use_container_width=True):
                st.session_state["sub_step_1"] = "konteks"
                st.rerun()
        with col_btn2:
            with st.expander("Dari mana angka −1,86 bintang ini?"):
                st.write(
                    "Analisis ini membandingkan 6.740 pasang pesanan kembar identik (Propensity Score Matching) yang kondisinya serupa — rute pengiriman, biaya ongkir, "
                    "kategori produk, berat barang, dan harganya sama persis. Satu-satunya perbedaan: yang satu tiba tepat waktu, "
                    "dan yang satu lagi terlambat. Selisih kepuasan murni akibat keterlambatan ini terbukti sebesar −1,86 bintang (dibandingkan gap naif −1,83 bintang)."
                )

    # ==========================================
    # 1C. KONTEKS 4 KPI & PROBLEM STATEMENT
    # ==========================================
    elif sub_step == "konteks":
        render_top_bar("Babak 1: Konteks Bisnis", current_step=1, total_steps=7)
        
        st.markdown(label_klaim("DATA RIIL", "A"), unsafe_allow_html=True)
        render_html("""
        <div class="serif" style="font-size: 32px; line-height: 42px; margin-bottom: 24px;">
        Kondisi operasional Olist saat ini.
        </div>
        """)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Pesanan", "99.084", help="86.283 data pengembangan + 12.801 data uji terkunci")
        with col2:
            st.metric("Persentase Telat", "8,0%", delta="- target perbaikan", delta_color="inverse")
        with col3:
            st.metric("Ulasan Buruk", "14,8%", delta="- pemicu churn", delta_color="inverse")
        with col4:
            st.metric("Rata-rata Transaksi", "R$ 137,75", help="Nilai barang rata-rata per transaksi")
            
        render_html('<div style="height: 1px; background: var(--line); margin: 24px 0;"></div>')
        
        render_html("""
        <div style="font-size: 16px; line-height: 26px; color: var(--ink); margin-bottom: 24px;">
        <b>Di Olist, hanya 3,0% pembeli yang pernah berbelanja lebih dari satu kali.</b><br>
        Hampir semua transaksi berasal dari pelanggan baru. Artinya, pesanan pertama adalah penentu segalanya. 
        Satu ulasan buruk di pesanan pertama sering kali membuat pembeli pergi selamanya.
        </div>
        """)
        
        pilihan = st.radio(
            "Mulai investigasi dari mana?",
            [
                "Cari Tahu Masalah Pengiriman (Wilayah & Operasional)",
                "Lihat Dampak ke Pembeli & Penjual UMKM",
                "Langsung Uji Solusi di Simulator Kebijakan"
            ],
            index=0
        )
        
        render_html('<div style="height: 24px;"></div>')
        if st.button("Lanjut", type="primary"):
            if "Pengiriman" in pilihan:
                st.session_state["step"] = 2
            elif "Pembeli" in pilihan:
                st.session_state["step"] = 3
            else:
                st.session_state["step"] = 6
                st.session_state["sub_step_6"] = "putuskan"
            st.rerun()
