"""
screens/s4_early_warning.py
Babak 4: Sistem Peringatan Dini CS (T0 dan T1)
Prediksi Risiko Point-in-Time, Meteran Horizontal 3 Zona, dan Kejujuran Presisi 8,0%
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from ui.components import render_top_bar, label_klaim, hero_number, so_what, callout, render_html

def render():
    render_top_bar("Babak 4: Deteksi Dini", current_step=4, total_steps=7)
    
    st.markdown(label_klaim("SISTEM DETEKSI DINI", "B"), unsafe_allow_html=True)
    render_html("""
    <div class="serif" style="font-size: 32px; line-height: 42px; margin-bottom: 8px;">
        Peringatan Dini Risiko Keterlambatan
    </div>
    """)
    st.caption("Model ini hanya membaca informasi saat transaksi dibuat — tanpa mengintip apa yang terjadi di masa depan.")
    
    stage = st.radio(
        "Kapan kita cek risikonya?",
        ["Saat Checkout (Pembeli baru bayar)", "Saat Serah Kurir (Setelah paket dikirim penjual)"],
        horizontal=True
    )
    
    col_form, col_res = st.columns([1, 1.2])
    
    with col_form:
        with st.form("risk_form", border=True):
            c_state = st.selectbox("Provinsi Pembeli:", ["SP", "RJ", "MG", "BA", "RS", "PR", "PE", "CE", "PA", "AM", "RR"], index=0)
            s_state = st.selectbox("Provinsi Penjual:", ["SP", "PR", "MG", "RJ", "SC"], index=0)
            est_days = st.number_input("Estimasi Tiba di Aplikasi (Hari):", min_value=5, max_value=50, value=22, step=1)
            weight_kg = st.number_input("Berat Paket (kg):", min_value=0.1, max_value=30.0, value=1.2, step=0.5)
            price = st.number_input("Nilai Belanja (R$):", min_value=10.0, max_value=5000.0, value=130.0, step=10.0)
            
            seller_h = 3.0
            if "Serah Kurir" in stage:
                seller_h = st.number_input("Lama Penjual Menyiapkan Barang (Hari):", min_value=0.5, max_value=15.0, value=3.0, step=0.5)
                
            btn_calc = st.form_submit_button("Periksa Risiko", type="primary", use_container_width=True)

    with col_res:
        # Perhitungan probabilitas heuristik berkalibrasi model Random Forest Fase 6
        base_p = 0.04
        if c_state in ["AM", "RR", "PA"]:
            base_p += 0.16
        elif c_state in ["RJ", "BA", "CE"]:
            base_p += 0.06
            
        if s_state != c_state:
            base_p += 0.04
        if weight_kg > 5.0:
            base_p += 0.03
        if est_days < 12:
            base_p += 0.07
        elif est_days > 28:
            base_p -= 0.02
            
        if "Serah Kurir" in stage and seller_h > 3.5:
            base_p += 0.08 * (seller_h - 3.0)
            
        prob = np.clip(base_p, 0.02, 0.82)
        lift = prob / 0.080
        
        # Zona Aksi
        if prob < 0.08:
            zona = "Aman"
            zona_color = "var(--good)"
            aksi_text = "Paket diperkirakan tiba sesuai jadwal. Tidak perlu tindakan khusus."
        elif prob < 0.18:
            zona = "Perlu Dipantau"
            zona_color = "var(--ink2)"
            aksi_text = "Amati saat serah terima kurir. Belum perlu menghubungi pembeli."
        else:
            zona = "Beri Tahu Pembeli"
            zona_color = "var(--bad)"
            aksi_text = "Informasikan lebih awal bahwa paket berpotensi butuh waktu lebih lama. Jangan berikan voucher di tahap ini."
            
        stage_label = "Saat Checkout" if "Checkout" in stage else "Saat Serah Kurir"
        render_html(f"""
        <div class="card">
        <div style="font-size: 13px; text-transform: uppercase; color: var(--ink2); font-weight: 600;">Potensi Keterlambatan ({stage_label})</div>
        <div class="giant" style="font-size: 64px; line-height: 1.1; color: {zona_color};">{prob*100:.1f}%</div>
        <div style="font-size: 14px; color: var(--ink2); margin-top: 4px;">
        Risiko ini <b>{lift:.1f}x lebih tinggi</b> dibanding rata-rata normal platform (8,0%).
        </div>
        </div>
        """)
        
        # Meteran Risiko 3 Zona via Plotly (Bebas Potong Teks & Bebas Tooltip Mengganggu)
        fig_meter = go.Figure()
        fig_meter.add_trace(go.Bar(
            y=["Risiko"], x=[8], orientation="h", name="Zona Aman (<8%)",
            marker=dict(color="#4DB58F"), hoverinfo="none"
        ))
        fig_meter.add_trace(go.Bar(
            y=["Risiko"], x=[10], orientation="h", name="Perlu Dipantau (8-18%)",
            marker=dict(color="#A9A69D"), hoverinfo="none"
        ))
        fig_meter.add_trace(go.Bar(
            y=["Risiko"], x=[82], orientation="h", name="Risiko Tinggi (>18%)",
            marker=dict(color="#E8735C"), hoverinfo="none"
        ))
        
        # Posisi anotasi dinamis agar tidak terpotong tepi layar
        ann_x = prob * 100
        if ann_x < 15:
            ann_pos = "top right"
        elif ann_x > 85:
            ann_pos = "top left"
        else:
            ann_pos = "top"
            
        fig_meter.add_vline(
            x=ann_x, line_width=4, line_color="#14130F",
            annotation_text=f"Skor: {ann_x:.1f}%", annotation_position=ann_pos,
            annotation_font=dict(family="Instrument Sans", size=13, color="#14130F")
        )
        fig_meter.update_layout(
            barmode="stack",
            height=70,
            margin=dict(l=15, r=15, t=32, b=4),
            xaxis=dict(range=[0, 100], showgrid=False, showticklabels=False),
            yaxis=dict(showticklabels=False),
            showlegend=False
        )
        st.plotly_chart(fig_meter, use_container_width=True, config={"displayModeBar": False})
        
        render_html(f"""
        <div style="display: flex; justify-content: space-between; font-size: 11px; color: var(--ink2); margin-bottom: 16px;">
        <span>Aman (&lt;8%)</span>
        <span>Perlu Dipantau (8-18%)</span>
        <span>Risiko Tinggi (&gt;18%)</span>
        </div>
        <div class="card" style="padding: 16px 20px;">
        <div style="font-size: 12px; text-transform: uppercase; font-weight: 600; color: var(--ink2);">Langkah yang Disarankan:</div>
        <div style="font-size: 15px; font-weight: 600; color: var(--ink); margin-top: 2px;">{zona}: {aksi_text}</div>
        </div>
        """)
        
    callout(
        "CATATAN STRATEGIS",
        "Mengapa jangan langsung membagikan voucher diskon saat checkout?",
        "Dari pesanan yang terdeteksi berisiko tinggi saat checkout, sebagian besar sebenarnya masih bisa tiba tepat waktu. Jika kita membagikan voucher di awal, anggaran kompensasi akan habis sia-sia. Langkah yang tepat: gunakan deteksi awal untuk memantau paket, lalu berikan kompensasi hanya jika paket memang terbukti tertahan lama di penjual."
    )
    
    render_html('<div style="height: 24px;"></div>')
    if st.button("Lanjut ke Pembuktian Sebab-Akibat", type="primary"):
        st.session_state["step"] = 5
        st.rerun()
