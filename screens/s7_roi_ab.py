"""
screens/s7_roi_ab.py
Babak 7: Kalkulator ROI Finansial & Protokol Uji Coba A/B Testing
Kalkulator Titik Impas Voucher CS dan Desain Sampel Eksperimen Acak (~1.560 per kelompok)
"""

import streamlit as st
from ui.components import render_top_bar, label_klaim, hero_number, so_what, callout, render_html
from core.finance import calc_voucher_roi, calc_ab_sample

def render():
    render_top_bar("Babak 7: Uji Lapangan", current_step=7, total_steps=7)
    
    st.markdown(label_klaim("ANALISIS BIAYA & EKSPERIMEN", "B"), unsafe_allow_html=True)
    render_html("""
    <div class="serif" style="font-size: 32px; line-height: 42px; margin-bottom: 24px;">
    Perhitungan Finansial & Rencana Uji Coba Lapangan
    </div>
    """)
    
    # -------------------------------------------------------------
    # 1. KALKULATOR TITIK IMPAS VOUCHER CS
    # -------------------------------------------------------------
    render_html("""
    <div class="serif" style="font-size: 24px; margin-bottom: 8px;">
    1. Kapan Pemberian Kompensasi Voucher Masuk Akal?
    </div>
    """)
    
    col_v1, col_v2 = st.columns([1, 1.2])
    with col_v1:
        v_cost = st.number_input("Nilai Voucher Goodwill (R$):", min_value=5.0, max_value=50.0, value=15.0, step=1.0)
        v_clv = st.number_input("Rata-rata Nilai Belanja Pembeli (R$):", min_value=50.0, max_value=300.0, value=137.75, step=5.0)
        p_precision = st.selectbox("Kapan Voucher Diberikan:", ["Saat Checkout (Baru Terdeteksi Potensi Telat)", "Saat Tertahan di Penjual (Keterlambatan Terkonfirmasi)"])
        r_save = st.slider("Perkiraan Pembeli yang Mau Belanja Ulang (%):", min_value=5, max_value=50, value=15, step=1)
        
        p_val = 8.0 if "Checkout" in p_precision else 35.0
        roi_res = calc_voucher_roi(v_cost, v_clv, r_save, p_val)
        
    with col_v2:
        render_html(f"""
        <div class="card">
        <div style="font-size: 13px; text-transform: uppercase; color: var(--ink2); font-weight: 600;">Hasil Evaluasi Voucher</div>
        <div style="margin: 12px 0; border-bottom: 1px solid var(--line); padding-bottom: 12px;">
        <div style="font-size: 13px; color: var(--ink2);">Titik Impas (Per Pembeli yang Benar-benar Telat):</div>
        <div style="font-size: 22px; font-weight: 700; color: var(--good);">{roi_res['impas_per_telat_pct']}% pembeli harus terselamatkan</div>
        <div style="font-size: 13px; color: var(--ink2); margin-top: 2px;">
        Dengan voucher R$ {v_cost:.0f} dan belanja R$ {v_clv:.2f}, minimal {roi_res['impas_per_telat_pct']}% pembeli harus mau belanja lagi agar biaya voucher balik modal.
        </div>
        </div>
        <div>
        <div style="font-size: 13px; color: var(--ink2);">Dampak Finansial Per Pesanan yang Diberi Voucher:</div>
        <div style="font-size: 24px; font-weight: 700; color: {'var(--good)' if roi_res['untung_per_ditandai'] > 0 else 'var(--bad)'};">
        R$ {roi_res['untung_per_ditandai']} {'(Untung Bersih)' if roi_res['untung_per_ditandai'] > 0 else '(Rugi Bersih)'}
        </div>
        <div style="font-size: 13px; color: var(--ink2); margin-top: 4px;">
        {'Menguntungkan: Memberikan voucher saat paket terbukti tertahan di penjual menghasilkan profit bersih.' if roi_res['untung_per_ditandai'] > 0 else 'Merugikan: Memberikan voucher massal saat checkout justru membuang anggaran karena sebagian besar paket sebenarnya selamat.'}
        </div>
        </div>
        </div>
        """)
        
    render_html('<div style="height: 36px; border-bottom: 1px solid var(--line); margin-bottom: 36px;"></div>')

    # -------------------------------------------------------------
    # 2. KALKULATOR A/B TESTING
    # -------------------------------------------------------------
    render_html("""
    <div class="serif" style="font-size: 24px; margin-bottom: 8px;">
    2. Rencana Uji Coba Lapangan (A/B Testing)
    </div>
    """)
    st.caption("Sebelum kebijakan penyesuaian estimasi diterapkan ke seluruh pengguna, uji coba terkontrol ini memastikan dampaknya benar-benar nyata.")
    
    col_ab1, col_ab2 = st.columns([1, 1.2])
    with col_ab1:
        p_base = st.number_input("Persentase Keterlambatan Saat Ini:", min_value=0.05, max_value=0.20, value=0.080, step=0.005, format="%.3f")
        p_target = st.number_input("Target Persentase Keterlambatan Baru:", min_value=0.02, max_value=0.10, value=0.055, step=0.005, format="%.3f")
        ab_res = calc_ab_sample(p_base, p_target, alpha=0.05, power=0.80, weekly_orders=1200)
        
    with col_ab2:
        hero_number(f"~{ab_res['n_per_group']:,}", unit="pesanan / kelompok", warna="var(--ink)", subteks=f"Total: {ab_res['total_n']:,} pesanan (butuh sekitar {ab_res['weeks']} minggu pengujian lalu lintas belanja normal).")
        
    render_html("""
    <div class="card" style="margin-top: 16px;">
    <div style="font-size: 13px; text-transform: uppercase; color: var(--ink2); font-weight: 600; margin-bottom: 8px;">Rencana Pengujian:</div>
    <ul style="font-size: 14px; color: var(--ink); line-height: 22px; padding-left: 20px; margin: 0;">
    <li><b>Kelompok Kontrol (A)</b>: Tampilkan estimasi tanggal tiba standar seperti biasa.</li>
    <li><b>Kelompok Uji Coba (B)</b>: Tambahkan +3 hari pada estimasi tanggal tiba (strategi penyesuaian janji).</li>
    <li><b>Metrik Utama</b>: Penurunan ulasan buruk (target: turun dari 14,8% ke &le;12,0%).</li>
    <li><b>Batas Pengaman (Guardrail)</b>: Tingkat konversi di halaman checkout (pastikan tidak turun lebih dari 0,5%).</li>
    </ul>
    </div>
    """)
    
    render_html('<div style="height: 36px;"></div>')
    
    col_fin1, col_fin2 = st.columns([1, 2])
    with col_fin1:
        if st.button("Ulangi dari Pembuka", type="primary", use_container_width=True):
            st.session_state["step"] = 0
            st.rerun()
    with col_fin2:
        st.download_button(
            label="Unduh Ringkasan Eksekutif (.md)",
            data="""# Ringkasan Eksekutif: World Model for Business (Olist Logistics)

## 1. Inti Masalah
Olist tidak memiliki armada kurir dan gudang sendiri. Keterlambatan pengiriman (8,0% pesanan) menjadi pemicu utama anjloknya rating pembeli dari 4,3 bintang menjadi 2,4 bintang. Mengingat 73,8% pembeli hanya belanja satu kali, pesanan pertama yang mengecewakan berarti kehilangan pelanggan selamanya.

## 2. Bukti Nyata
Dengan membandingkan 6.740 pasang pesanan kembar identik yang berkarakteristik serupa (rute, berat, ongkir, dan harga), keterlambatan terbukti secara langsung memotong 1,86 bintang kepuasan pelanggan (Average Treatment Effect murni). Uji kendali mutu placebo membuktikan model analisis ini jujur dan kebal dari korelasi palsu (efek semu hanya R$ 1,60 terhadap rata-rata harga produk R$ 137).

## 3. Solusi Terpilih
Daripada menambah armada kurir fisik yang menelan biaya sangat mahal, simulator menunjukkan bahwa menambahkan 3 hari pada estimasi janji pengiriman berhasil mencegah 2.608 ulasan buruk (memangkas angka telat dari 8,0% ke 2,0%) dengan biaya modal logistik R$ 0.

## 4. Langkah Berikutnya (Uji Lapangan)
Lakukan A/B testing terkontrol dengan ~1.560 pesanan per kelompok (~3 minggu) untuk memvalidasi kebijakan ini dan memastikan penambahan estimasi tidak menurunkan tingkat konversi di halaman checkout (toleransi drop-off < 0,5%).
""",
            file_name="ringkasan_eksekutif_wmfb.md",
            mime="text/markdown"
        )
