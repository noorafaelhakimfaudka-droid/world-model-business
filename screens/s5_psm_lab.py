"""
screens/s5_psm_lab.py
Babak 5: Laboratorium Bukti Kausalitas (PSM Lab)
5A (Jebakan Korelasi) -> 5B (Love Plot Kembaran) -> 5C (Hasil ATE -1,86) -> 5D (Uji Placebo)
"""

import streamlit as st
import plotly.graph_objects as go
from ui.components import render_top_bar, label_klaim, hero_number, so_what, callout, render_html
from core.load import load_agg

def render():
    render_top_bar("Babak 5: Bukti Nyata", current_step=5, total_steps=7)
    
    st.markdown(label_klaim("ANALISIS SEBAB-AKIBAT", "B"), unsafe_allow_html=True)
    render_html("""
    <div class="serif" style="font-size: 32px; line-height: 42px; margin-bottom: 8px;">
    Korelasi sering kali menipu.<br>Ini bukti bahwa keterlambatan memang penyebab utamanya.
    </div>
    """)
    
    tab_a, tab_b, tab_c = st.tabs([
        "1. Mengapa Perlu Dicocokkan?",
        "2. Hasil Perbandingan Murni (−1,86★)",
        "3. Uji Kejujuran Analisis"
    ])
    
    with tab_a:
        render_html("""
        <div style="font-size: 15px; color: var(--ink); margin: 12px 0 16px 0;">
        Pesanan yang telat sering kali barangnya memang lebih berat, harganya lebih mahal, atau dikirim antarpulau. 
        Apakah pembeli marah karena keterlambatan pengiriman, atau karena faktor barang itu sendiri?<br>
        Agar perbandingannya adil, metode Propensity Score Matching memasangkan 6.740 pesanan telat dengan pesanan tepat waktu yang 'kembar identik' — rute, berat barang, kategori produk, dan harganya sama persis.
        </div>
        """)
        
        df_love = load_agg("agg_psm_love")
        fig_love = go.Figure()
        
        fig_love.add_trace(go.Scatter(
            x=df_love["before_match"],
            y=df_love["covariate"],
            mode="markers",
            name="Sebelum Dicocokkan (Profil Berbeda)",
            marker=dict(size=10, color="#8A8880")
        ))
        fig_love.add_trace(go.Scatter(
            x=df_love["after_match"],
            y=df_love["covariate"],
            mode="markers",
            name="Setelah Dicocokkan (Kondisi Setara)",
            marker=dict(size=12, color="#14130F", symbol="diamond")
        ))
        
        fig_love.add_vline(x=0.05, line_width=1, line_dash="dot", line_color="#C2432B")
        
        fig_love.update_layout(
            height=260,
            margin=dict(l=16, r=16, t=16, b=16),
            xaxis=dict(title="Tingkat Perbedaan Karakteristik (Makin ke kiri = makin seimbang)", range=[-0.05, 0.50]),
            yaxis=dict(title=None, autorange="reversed"),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_love, use_container_width=True, config={"displayModeBar": False})
        st.caption("Hasil Pencocokan: Titik hitam berlian yang berkumpul di sebelah kiri (SMD < 0,05) membuktikan kedua kelompok pesanan kini sudah setara dan adil untuk dibandingkan.")

    with tab_b:
        hero_number("−1,86", unit="bintang", warna="var(--bad)", subteks="Selisih kepuasan nyata (ATE kausal) antara pesanan telat vs tepat waktu pada 6.740 pasang kembar identik.")
        
        render_html("""
        <div class="card">
        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--line); padding-bottom: 10px; margin-bottom: 10px;">
        <span><b>Pesanan Tepat Waktu (Kontrol Kembaran)</b></span>
        <span style="font-size: 18px; font-weight: 700; color: var(--good);">4,31 ★</span>
        </div>
        <div style="display: flex; justify-content: space-between;">
        <span><b>Pesanan Terlambat (Treatment Kembaran)</b></span>
        <span style="font-size: 18px; font-weight: 700; color: var(--bad);">2,45 ★</span>
        </div>
        </div>
        """)
        so_what("Setelah faktor jarak, harga, ongkir, dan berat disetarakan secara ketat, keterlambatan terbukti langsung memotong 1,86 bintang kepuasan pelanggan (dibandingkan gap naif −1,83 bintang: 4,28★ vs 2,45★).")

    with tab_c:
        render_html("""
        <div class="card">
        <div style="font-size: 13px; text-transform: uppercase; color: var(--ink2); font-weight: 600;">Uji Kejujuran Analisis (Kendali Mutu Placebo)</div>
        <div class="display" style="font-size: 42px; margin: 8px 0; color: var(--ink);">Efek Palsu = R$ 1,60</div>
        <div style="font-size: 14px; color: var(--ink2); line-height: 22px;">
        <i>"Jika metode analisis ini menemukan dampak di tempat yang mustahil ada dampaknya, berarti model ini cacat."</i><br>
        Uji plasebo menguji apakah paket telat memengaruhi harga barang (yang sudah pasti mustahil, karena harga ditentukan di awal transaksi).<br>
        Hasil uji membuktikan dampaknya hanya <b>R$ 1,60</b> (relatif nol terhadap rata-rata harga produk R$ 137, jauh di bawah batas toleransi R$ 20,00). Ini menegaskan metode estimasi kausal ini sehat, objektif, dan tidak mendeteksi pola palsu.
        </div>
        </div>
        """)

    callout(
        "CATATAN LAPANGAN",
        "Analisis ini telah mengontrol faktor jarak rute, berat paket, harga, dan kategori barang.",
        "Namun, kendala di lapangan seperti cuaca ekstrem atau masalah teknis kurir tetap bisa terjadi. Karena itu, uji coba terbatas (A/B testing) tetap wajib sebelum kebijakan diterapkan ke seluruh pengguna."
    )

    render_html('<div style="height: 24px;"></div>')
    if st.button("Lanjut ke Simulator Kebijakan", type="primary"):
        st.session_state["step"] = 6
        st.session_state["sub_step_6"] = "putuskan"
        st.rerun()
