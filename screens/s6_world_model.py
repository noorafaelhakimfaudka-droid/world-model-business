"""
screens/s6_world_model.py
Babak 6: The World Model Simulator (Fitur Unggulan)
6A (Putuskan: 4 Kartu Pilihan & Vonis 'Uji Dulu') <-> 6B (Laboratorium Penuh: 3 Slider & Grid 462 Skenario)
"""

import streamlit as st
import plotly.graph_objects as go
from ui.components import render_top_bar, label_klaim, hero_number, so_what, callout, render_html
from core.simulate import sim_lookup

def render():
    sub_step = st.session_state.get("sub_step_6", "putuskan")
    
    # ==========================================
    # 6A. PUTUSKAN (Satu Layar, Satu Keputusan)
    # ==========================================
    if sub_step == "putuskan":
        render_top_bar("Babak 6: Uji Kebijakan", current_step=6, total_steps=7)
        
        st.markdown(label_klaim("PILIHAN STRATEGIS", "C"), unsafe_allow_html=True)
        render_html("""
        <div class="serif" style="font-size: 34px; line-height: 44px; margin-bottom: 24px;">
        Anggaran logistik kita terbatas.<br>Kebijakan mana yang ingin kamu ambil?
        </div>
        """)
        
        opsi_kebijakan = st.radio(
            "Pilih opsi kebijakan:",
            [
                "Sesuaikan Janji Pengiriman (+3 hari estimasi tiba di website · Biaya R$ 0)",
                "Bantu Penjual Menyiapkan Barang (Otomasi cetak resi & packing · Biaya rendah)",
                "Percepat Armada Kurir Fisik (Sewa jalur kilat & tambah kurir · Biaya sangat mahal)",
                "Biarkan Saja (Pertahankan kondisi saat ini)"
            ],
            index=0
        )
        
        render_html('<div style="height: 16px;"></div>')
        
        if "Sesuaikan Janji" in opsi_kebijakan:
            st.markdown(label_klaim("HASIL SIMULASI", "C"), unsafe_allow_html=True)
            hero_number("~2.600", unit="ulasan buruk dicegah", warna="var(--good)", subteks="Nilai kepuasan pelanggan yang terselamatkan: sekitar R$ 125.000 – R$ 240.000.")
            
            render_html("""
            <div class="card" style="border-left: 4px solid var(--good);">
            <div style="font-size: 13px; text-transform: uppercase; color: var(--ink2); font-weight: 600;">Saran dari Simulasi:</div>
            <div class="serif" style="font-size: 26px; color: var(--ink); margin: 4px 0;">Layak diuji coba.</div>
            <div style="font-size: 14px; color: var(--ink2); line-height: 22px;">
            Di simulasi, menambah 3 hari pada estimasi pengiriman berhasil menyelamatkan ribuan pembeli tanpa biaya operasional kurir sepeser pun. 
            Namun, janji tiba yang terlalu lama berisiko menurunkan minat orang di halaman checkout. 
            Karena itu, uji coba terbatas (A/B testing) tetap diperlukan sebelum diterapkan ke seluruh pengguna.
            </div>
            </div>
            """)
            
        elif "Kurir Fisik" in opsi_kebijakan:
            st.markdown(label_klaim("HASIL SIMULASI", "C"), unsafe_allow_html=True)
            hero_number("~1.200", unit="ulasan buruk dicegah", warna="var(--ink)", subteks="Biaya tambahan kurir melebihi R$ 600.000 (tidak efisien).")
            
            render_html("""
            <div class="card" style="border-left: 4px solid var(--bad);">
            <div style="font-size: 13px; text-transform: uppercase; color: var(--ink2); font-weight: 600;">Saran dari Simulasi:</div>
            <div class="serif" style="font-size: 26px; color: var(--bad); margin: 4px 0;">Kurang efisien.</div>
            <div style="font-size: 14px; color: var(--ink2); line-height: 22px;">
            Mempercepat waktu tempuh kurir hingga 20% membutuhkan biaya raksasa, namun hasilnya hanya mencegah separuh ulasan buruk dibanding memperbaiki estimasi janji tiba.
            </div>
            </div>
            """)
            
        else:
            hero_number("0", unit="ulasan buruk dicegah", warna="var(--ink2)", subteks="Platform tetap kehilangan 8,0% pelanggan akibat keterlambatan pengiriman.")

        col_b1, col_b2 = st.columns([1, 1.2])
        with col_b1:
            if st.button("Rancang Uji Lapangan (Babak 7)", type="primary", use_container_width=True):
                st.session_state["step"] = 7
                st.rerun()
        with col_b2:
            if st.button("Buka Laboratorium Bebas (Coba-coba Skenario)", type="secondary"):
                st.session_state["sub_step_6"] = "lab"
                st.rerun()

    # ==========================================
    # 6B. LABORATORIUM PENUH (What-If Engine)
    # ==========================================
    elif sub_step == "lab":
        render_top_bar("Babak 6: Uji Kebijakan", current_step=6, total_steps=7)
        
        st.markdown(label_klaim("SIMULASI MULTI-SKENARIO", "C"), unsafe_allow_html=True)
        render_html("""
        <div class="serif" style="font-size: 32px; line-height: 42px; margin-bottom: 8px;">
        Laboratorium Uji Skenario
        </div>
        """)
        st.caption("Coba kombinasikan tiga tuas kebijakan ini untuk melihat dampaknya ke angka keterlambatan dan biaya.")
        
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            b_val = st.select_slider("1. Tambah Hari Estimasi Janji Tiba (+Hari SLA):", options=[0, 1, 2, 3, 4, 5], value=3)
        with col_s2:
            s_val = st.select_slider("2. Percepat Waktu Penjual (%):", options=[0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50], value=0)
        with col_s3:
            k_val = st.select_slider("3. Percepat Waktu Tempuh Kurir (%):", options=[0, 5, 10, 15, 20, 25, 30], value=0)
            
        # Ambil hasil dari grid pra-hitung (< 50ms)
        res = sim_lookup(b_val, s_val, k_val)
        
        # Baris Metrik Real-Time
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric("Persentase Telat Baru", f"{res['late_rate']*100:.1f}%", delta=f"{(res['late_rate']-0.080)*100:.1f}%", delta_color="inverse")
        with col_m2:
            st.metric("Ulasan Dicegah", f"{int(res['bad_saved']):,}", delta="terselamatkan")
        with col_m3:
            st.metric("Biaya Tambahan", f"R$ {int(res['biaya']):,}")
        with col_m4:
            st.metric("Nilai Tertahan (Mid)", f"R$ {int(res['val_saved_mid']):,}")
            
        render_html('<div style="height: 16px;"></div>')
        
        # Tabel Komparasi Trade-Off Biaya
        st.markdown("**Tabel Perbandingan Skenario Kebijakan:**")
        comp_data = [
            {"Skenario": "Kondisi Saat Ini", "Persentase Telat": "8,0%", "Ulasan Dicegah": "0", "Biaya Tambahan": "R$ 0", "Biaya per Ulasan Selamat": "-"},
            {"Skenario": "Menyesuaikan Janji (+3 Hari)", "Persentase Telat": "2,0%", "Ulasan Dicegah": "2.608", "Biaya Tambahan": "R$ 0", "Biaya per Ulasan Selamat": "R$ 0 / ulasan"},
            {"Skenario": "Bantu Penjual (+30% Lebih Cepat)", "Persentase Telat": "7,5%", "Ulasan Dicegah": "234", "Biaya Tambahan": "R$ 64.712", "Biaya per Ulasan Selamat": "R$ 276 / ulasan"},
            {"Skenario": "Percepat Kurir (+20% Lebih Cepat)", "Persentase Telat": "7,4%", "Ulasan Dicegah": "278", "Biaya Tambahan": "R$ 431.415", "Biaya per Ulasan Selamat": "R$ 1.551 / ulasan"},
            {"Skenario": f"Pilihan Anda (+{b_val} Hari Janji, Penjual +{s_val}%, Kurir +{k_val}%)", "Persentase Telat": f"{res['late_rate']*100:.1f}%", "Ulasan Dicegah": f"{int(res['bad_saved']):,}", "Biaya Tambahan": f"R$ {int(res['biaya']):,}", "Biaya per Ulasan Selamat": f"R$ {res['cost_per_saved']} / ulasan"}
        ]
        st.dataframe(comp_data, hide_index=True, use_container_width=True)
        
        callout(
            "CATATAN RISIKO",
            "Estimasi tiba yang terlalu lama berpotensi membuat pembeli batal checkout.",
            "Dampak pembatalan checkout ini tidak tercatat di data historis. Karena itu, tingkat konversi checkout wajib dijadikan indikator keselamatan saat uji coba A/B."
        )
        
        col_nav1, col_nav2 = st.columns([1, 1.5])
        with col_nav1:
            if st.button("Lanjut ke Rencana Uji Lapangan", type="primary", use_container_width=True):
                st.session_state["step"] = 7
                st.rerun()
        with col_nav2:
            if st.button("Kembali ke Pilihan Kebijakan", type="secondary"):
                st.session_state["sub_step_6"] = "putuskan"
                st.rerun()
