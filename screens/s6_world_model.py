"""
screens/s6_world_model.py
Babak 6: The World Model Simulator (Operational Reality Lab)
Fitur Unggulan DSS: Simulasi Kontrafaktual Keputusan Bisnis Nyata
Memadukan:
1. Pilihan Lingkup Kebijakan (Blanket vs Rute Kritis >800km vs 6% Seller Lelet)
2. Visualisasi Pergeseran Gelombang SLA & Garis Janji Tiba (Plotly Real-Time)
3. Neraca Keuangan Kebijakan (P&L Capex/Opex vs Nilai Retensi)
4. Uji Stres Risiko Batal Beli di Halaman Checkout (Checkout Drop-off Sensitivity)
5. Inspektur 4 Studi Kasus Pesanan Nyata Olist
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from ui.components import render_top_bar, label_klaim, hero_number, so_what, callout, render_html
from core.load import load_agg
from core.simulate import sim_lookup

def render():
    render_top_bar("Babak 6: World Model Simulator", current_step=6, total_steps=7)
    
    st.markdown(label_klaim("SIMULATOR SISTEM OPERASIONAL", "A"), unsafe_allow_html=True)
    
    render_html("""
    <div class="serif" style="font-size: 36px; line-height: 46px; margin-bottom: 8px;">
    Laboratorium Keputusan Bisnis: Uji Sebelum Keluar Modal
    </div>
    <div style="font-size: 16px; color: var(--ink2); line-height: 26px; max-width: 820px; margin-bottom: 24px;">
    Jangan jadikan operasional fisik sebagai kelinci percobaan. Di laboratorium ini, kita menghubungkan rantai kausal nyata: 
    <b>waktu penanganan seller + durasi kurir → pemenuhan janji tiba → reaksi ulasan bintang → neraca laba-rugi platform</b>.
    </div>
    """)
    
    # Mode Tab: Kokpit Kebijakan Makro vs Inspektur Pesanan Satuan
    tab_sim1, tab_sim2 = st.tabs([
        "Kokpit Kebijakan Makro & Simulasi SLA",
        "Inspektur Kasus Pesanan Nyata (Order Inspector)"
    ])
    
    # =========================================================================
    # TAB 1: KOKPIT KEBIJAKAN MAKRO
    # =========================================================================
    with tab_sim1:
        render_html("""
        <div style="font-size: 13px; font-weight: 600; text-transform: uppercase; color: var(--ink2); letter-spacing: 0.08em; margin-bottom: 12px;">
        1. Tuas Intervensi Manajemen
        </div>
        """)
        
        # Lingkup Intervensi
        col_scope, col_dummy = st.columns([2, 1])
        with col_scope:
            lingkup_pilihan = st.selectbox(
                "Pilih Lingkup Penerapan Kebijakan:",
                [
                    "Seluruh Pesanan Platform (Blanket Policy — 86.283 Pesanan)",
                    "Fokus Rute Jarak Jauh Kritis (Interstate >800 km — Penyumbang 68% Telat)",
                    "Fokus Penjual Bermasalah (6% Seller Lelet — Penyumbang 34% Telat)"
                ],
                index=0
            )
        
        col_ctl1, col_ctl2, col_ctl3 = st.columns(3)
        with col_ctl1:
            buffer_val = st.select_slider(
                "Buffer Janji Tiba (+Hari SLA):",
                options=[0, 1, 2, 3, 4, 5],
                value=3,
                help="Menambah hari janji tiba di halaman website/checkout untuk menyerap variabilitas logistik."
            )
        with col_ctl2:
            seller_val = st.select_slider(
                "Percepat Penanganan Seller (%):",
                options=[0, 10, 20, 30, 40, 50],
                value=0,
                help="Intervensi automasi cetak resi dan sanksi SLA pengemasan seller."
            )
        with col_ctl3:
            kurir_val = st.select_slider(
                "Sewa Armada Kurir Kilat (%):",
                options=[0, 10, 20, 30],
                value=0,
                help="Menyewa jalur logistik prioritas ekspres pihak ketiga (capex mahal)."
            )
            
        # Perhitungan lookup dinamis
        res = sim_lookup(buffer_val, seller_val, kurir_val)
        
        # Penyesuaian jika memilih lingkup khusus
        factor_scope = 1.0
        if "Rute Jarak Jauh" in lingkup_pilihan:
            factor_scope = 0.68
        elif "Fokus Penjual" in lingkup_pilihan:
            factor_scope = 0.52
            
        late_rate_disp = res['late_rate']
        bad_saved_disp = int(round(res['bad_saved'] * factor_scope))
        biaya_disp = int(round(res['biaya'] * factor_scope))
        val_saved_disp = int(round(res['val_saved_mid'] * factor_scope))
        net_roi_disp = val_saved_disp - biaya_disp
        
        render_html('<div style="height: 16px;"></div>')
        
        # 4 Metrik Dial Real-time
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric(
                "Tingkat Telat Baru",
                f"{late_rate_disp*100:.1f}%",
                delta=f"{(late_rate_disp - 0.080)*100:.1f}% (dari 8,0%)",
                delta_color="inverse"
            )
        with col_m2:
            st.metric(
                "Ulasan Buruk Dicegah",
                f"{bad_saved_disp:,} ulasan",
                delta=f"+{bad_saved_disp:,} pembeli puas",
                delta_color="normal"
            )
        with col_m3:
            st.metric(
                "Biaya Ekstra Logistik",
                f"R$ {biaya_disp:,}",
                delta="Capex R$ 0" if biaya_disp == 0 else f"-R$ {biaya_disp:,}",
                delta_color="off" if biaya_disp == 0 else "inverse"
            )
        with col_m4:
            st.metric(
                "Dampak Bersih (Net Value)",
                f"R$ {net_roi_disp:,}",
                delta="Untung Murni" if net_roi_disp > 0 and biaya_disp == 0 else f"{'Surplus' if net_roi_disp > 0 else 'Defisit'}",
                delta_color="normal" if net_roi_disp >= 0 else "inverse"
            )
            
        render_html('<div style="height: 24px;"></div>')
        
        # =====================================================================
        # VISUALISASI PERGESERAN GELOMBANG SLA
        # =====================================================================
        st.markdown("**Visualisasi Gelombang Paket & Pergeseran Garis Janji Tiba:**")
        st.caption("Amati bagaimana penambahan buffer menggeser garis batas janji ke kanan, menyapu paket yang tadinya terlambat menjadi tepat waktu.")
        
        df_dist = load_agg("agg_delay_dist")
        if not df_dist.empty:
            sub_dist = df_dist[df_dist['bin'].between(-7, 12)].copy()
            
            # Warnai batang berdasarkan status
            bar_colors = []
            bar_hover = []
            for b in sub_dist['bin']:
                cnt = int(sub_dist.loc[sub_dist['bin'] == b, 'order_count'].values[0])
                bad_pct = float(sub_dist.loc[sub_dist['bin'] == b, 'bad_review_pct'].values[0])
                stars = float(sub_dist.loc[sub_dist['bin'] == b, 'avg_stars'].values[0])
                
                if b < 0:
                    bar_colors.append("#1F7A5A") # Hijau: Tepat Waktu Asli
                    status_lbl = "[Tepat Waktu] Alami"
                elif b < buffer_val:
                    bar_colors.append("#D97706") # Amber/Emas: Terselamatkan oleh Buffer!
                    status_lbl = "[Terselamatkan] Oleh Buffer"
                else:
                    bar_colors.append("#C2432B") # Merah: Tetap Terlambat
                    status_lbl = "[Terlambat] Melewati Buffer"
                    
                bar_hover.append(
                    f"<b>Selisih Tiba: {b} Hari</b><br>"
                    f"Status: {status_lbl}<br>"
                    f"Jumlah Pesanan: {cnt:,}<br>"
                    f"Tingkat Ulasan Buruk: {bad_pct}%<br>"
                    f"Rata-rata Rating: {stars}★"
                )
                
            fig_hist = go.Figure()
            fig_hist.add_trace(go.Bar(
                x=sub_dist['bin'],
                y=sub_dist['order_count'],
                marker_color=bar_colors,
                hovertext=bar_hover,
                hoverinfo="text",
                name="Distribusi Pesanan"
            ))
            
            # Tambahkan Garis Janji Baru
            fig_hist.add_vline(
                x=buffer_val - 0.5,
                line_width=3,
                line_dash="dash",
                line_color="#14130F",
                annotation_text=f"Batas Janji Baru (+{buffer_val} Hari)",
                annotation_position="top right",
                annotation_font=dict(size=12, color="#14130F", family="Instrument Sans")
            )
            
            # Garis Janji Awal (0)
            if buffer_val > 0:
                fig_hist.add_vline(
                    x=-0.5,
                    line_width=1.5,
                    line_dash="dot",
                    line_color="#8A8880",
                    annotation_text="Janji Awal (0 Hari)",
                    annotation_position="top left",
                    annotation_font=dict(size=11, color="#8A8880", family="Instrument Sans")
                )
                
            fig_hist.update_layout(
                height=320,
                xaxis=dict(
                    title="Selisih Waktu Tiba vs Janji Awal (Hari) — [< 0: Tiba Cepat | > 0: Telat]",
                    tickmode='linear',
                    tick0=-7,
                    dtick=1
                ),
                yaxis=dict(title="Volume Pesanan"),
                margin=dict(l=20, r=20, t=30, b=30),
                showlegend=False
            )
            st.plotly_chart(fig_hist, use_container_width=True)
            
            # Legenda visual
            render_html("""
            <div style="display: flex; gap: 24px; font-size: 13px; color: var(--ink2); margin-top: -8px; margin-bottom: 20px;">
                <div style="display: flex; align-items: center; gap: 6px;">
                    <span style="width: 12px; height: 12px; background: #1F7A5A; border-radius: 2px; display: inline-block;"></span>
                    <span>Tepat Waktu Alami (Bintang 4.1★ – 4.3★)</span>
                </div>
                <div style="display: flex; align-items: center; gap: 6px;">
                    <span style="width: 12px; height: 12px; background: #D97706; border-radius: 2px; display: inline-block;"></span>
                    <span><b>Terselamatkan oleh Buffer</b> (Batal Bintang 1)</span>
                </div>
                <div style="display: flex; align-items: center; gap: 6px;">
                    <span style="width: 12px; height: 12px; background: #C2432B; border-radius: 2px; display: inline-block;"></span>
                    <span>Tetap Terlambat (Kendala Fisik Kurir)</span>
                </div>
            </div>
            """)
            
        render_html('<div style="height: 16px;"></div>')
        
        # =====================================================================
        # NERACA KEUANGAN KEBIJAKAN (P&L BREAKDOWN)
        # =====================================================================
        st.markdown("**Neraca Finansial Kebijakan (P&L Impact Breakdown):**")
        
        col_pnl1, col_pnl2 = st.columns([1.2, 1])
        with col_pnl1:
            # Pilihan Valuasi Nilai Ulasan
            val_scenario = st.radio(
                "Asumsi Nilai Satu Ulasan Buruk Terselamatkan (PRD §3.4 Lapis Nilai):",
                [
                    "Konservatif (R$ 14,06) — Hanya menghitung selisih repeat order empiris 3,05%",
                    "Moderat (R$ 70,00) — Memperhitungkan efek nilai belanja seumur hidup (CLV)",
                    "Optimis (R$ 92,00) — Memperhitungkan proteksi reputasi platform jangka panjang"
                ],
                index=1
            )
            val_per_review = 70.0
            if "Konservatif" in val_scenario: val_per_review = 14.06
            elif "Optimis" in val_scenario: val_per_review = 92.0
            
            total_saved_revenue = int(round(bad_saved_disp * val_per_review))
            net_profit_calc = total_saved_revenue - biaya_disp
            roi_pct = (net_profit_calc / biaya_disp * 100) if biaya_disp > 0 else 9999.0
            
        with col_pnl2:
            render_html(f"""
            <div class="card" style="background: var(--surface); padding: 18px;">
                <div style="font-size: 12px; text-transform: uppercase; color: var(--ink2); font-weight: 600;">Ringkasan Nilai Finansial:</div>
                <div style="display: flex; justify-content: space-between; margin-top: 10px; font-size: 14px;">
                    <span>Nilai Retensi Diselamatkan:</span>
                    <b>+R$ {total_saved_revenue:,}</b>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 6px; font-size: 14px; color: var(--bad);">
                    <span>Biaya Capex/Opex Logistik:</span>
                    <b>-R$ {biaya_disp:,}</b>
                </div>
                <div style="height: 1px; background: var(--line); margin: 10px 0;"></div>
                <div style="display: flex; justify-content: space-between; font-size: 16px;">
                    <span><b>Laba Bersih Kebijakan:</b></span>
                    <b style="color: {'var(--good)' if net_profit_calc >= 0 else 'var(--bad)'};">R$ {net_profit_calc:,}</b>
                </div>
                <div style="font-size: 12px; color: var(--ink2); margin-top: 6px;">
                    {'Status: Efisiensi Maksimal (Biaya R$ 0)' if biaya_disp == 0 else f'ROI Bersih: {roi_pct:.1f}%'}
                </div>
            </div>
            """)
            
        render_html('<div style="height: 16px;"></div>')
        
        # =====================================================================
        # UJI STRES RISIKO CHECKOUT (DROP-OFF SENSITIVITY)
        # =====================================================================
        st.markdown("**Uji Stres Risiko: Toleransi Penurunan Konversi Checkout (Abandonment Risk)**")
        st.caption("Kekhawatiran direksi: Jika estimasi tiba ditambah, apakah ada pembeli yang batal bayar di website?")
        
        col_stress_ctl, col_stress_box = st.columns([1.2, 1])
        with col_stress_ctl:
            checkout_drop_pct = st.slider(
                "Asumsi Penurunan Conversion Rate di Halaman Checkout (%):",
                min_value=0.0,
                max_value=3.0,
                value=0.5,
                step=0.1,
                help="Berapa persen calon pembeli yang diasumsikan batal checkout karena melihat janji tiba lebih lama."
            )
            
            # Hitungan titik impas toleransi batal beli:
            # Rata-rata margin per pesanan = R$ 137 * 15% (take-rate marketplace) = R$ 20.55
            # Kerugian omset = 86.283 * (checkout_drop_pct / 100) * R$ 20.55
            take_rate_margin = 20.55
            lost_margin = int(round(86283 * (checkout_drop_pct / 100.0) * take_rate_margin))
            net_stress_impact = total_saved_revenue - biaya_disp - lost_margin
            
            # Break-even drop rate
            if take_rate_margin * 86283 > 0:
                breakeven_drop_pct = max(0.0, (total_saved_revenue - biaya_disp) / (86283 * take_rate_margin) * 100)
            else:
                breakeven_drop_pct = 0.0
                
        with col_stress_box:
            is_surplus = net_stress_impact >= 0
            callout(
                "HASIL UJI STRES" if is_surplus else "PERHATIAN DEFISIT",
                f"Dengan asumsi pembeli batal {checkout_drop_pct:.1f}%, platform kehilangan margin R$ {lost_margin:,}.",
                f"<b>Batas Aman (Titik Impas):</b> Kebijakan buffer tetap menguntungkan selama pembeli yang kabur <b>kurang dari {breakeven_drop_pct:.2f}%</b>."
            )
            
    # =========================================================================
    # TAB 2: INSPEKTUR PESANAN NYATA (ORDER INSPECTOR)
    # =========================================================================
    with tab_sim2:
        render_html("""
        <div style="font-size: 13px; font-weight: 600; text-transform: uppercase; color: var(--ink2); letter-spacing: 0.08em; margin-bottom: 8px;">
        Uji Coba pada 4 Kasus Pesanan Nyata dari Database Olist
        </div>
        <div style="font-size: 15px; color: var(--ink2); margin-bottom: 20px;">
        Pilih salah satu pesanan historis untuk membuktikan bagaimana kebijakan bekerja di tingkat paket satuan.
        </div>
        """)
        
        df_cases = load_agg("sample_orders")
        if not df_cases.empty:
            case_options = [f"{row['title']} (Order #{row['order_id'][:8]}...)" for _, row in df_cases.iterrows()]
            selected_case_title = st.selectbox("Pilih Kasus Pesanan:", case_options, index=0)
            selected_idx = case_options.index(selected_case_title)
            c = df_cases.iloc[selected_idx]
            
            col_c_left, col_c_right = st.columns([1.1, 1.2])
            
            with col_c_left:
                render_html(f"""
                <div class="card">
                    <div style="font-size: 12px; text-transform: uppercase; color: var(--ink2); font-weight: 600; margin-bottom: 12px;">Profil Pesanan Asli</div>
                    <div style="font-size: 18px; font-weight: 600; color: var(--ink);">{c['title']}</div>
                    <div style="font-size: 13px; color: var(--ink2); margin-top: 4px;">Kategori: {c['category']} · Nilai: R$ {c['item_value']}</div>
                    <div style="height: 1px; background: var(--line); margin: 12px 0;"></div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 13px;">
                        <div>Rute: <b>{c['seller_state']} → {c['customer_state']}</b></div>
                        <div>Janji Awal SLA: <b>{c['estimated_days']} Hari</b></div>
                        <div>Waktu Seller: <b>{c['seller_days']} Hari</b></div>
                        <div>Waktu Kurir: <b>{c['carrier_days']} Hari</b></div>
                        <div>Waktu Tiba Total: <b>{c['actual_days']} Hari</b></div>
                        <div>Selisih Keterlambatan: <b style="color: {'var(--bad)' if c['delay_days'] > 0 else 'var(--good)'};">{c['delay_days']:+.1f} Hari</b></div>
                    </div>
                    <div style="height: 1px; background: var(--line); margin: 12px 0;"></div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 13px;">Ulasan Bintang Nyata:</span>
                        <span style="font-size: 20px; font-weight: 700; color: {'var(--bad)' if c['actual_stars'] <= 2 else 'var(--good)'};">{c['actual_stars']} ★</span>
                    </div>
                    <div style="font-size: 12px; color: var(--ink2); margin-top: 8px; font-style: italic;">"{c['diagnosa']}"</div>
                </div>
                """)
                
            with col_c_right:
                # Simulasi interaktif pada pesanan ini
                st.markdown("**Simulasikan Kebijakan pada Paket Ini:**")
                c_buffer = st.slider("Tambah Buffer Janji (+Hari SLA):", 0, 5, 3, key=f"buf_{c['case_id']}")
                c_seller_speed = st.slider("Percepat Waktu Seller (%):", 0, 50, 0, step=10, key=f"sel_{c['case_id']}")
                
                # Hitung kondisi baru paket ini
                new_seller_days = max(1.0, c['seller_days'] * (1.0 - c_seller_speed / 100.0))
                new_actual_days = round(new_seller_days + c['carrier_days'], 1)
                new_estimated_days = round(c['estimated_days'] + c_buffer, 1)
                new_delay_days = round(new_actual_days - new_estimated_days, 1)
                
                is_now_ontime = new_delay_days <= 0
                
                if is_now_ontime:
                    pred_stars = "4.2 ★"
                    verdict_box = f"""
                    <div class="card" style="border-left: 4px solid var(--good); background: #F0FDF4;">
                        <div style="font-size: 12px; text-transform: uppercase; color: var(--good); font-weight: 600;">Status Baru: TERSELAMATKAN!</div>
                        <div class="serif" style="font-size: 24px; color: var(--good); margin: 4px 0;">Paket Tiba Tepat Waktu</div>
                        <div style="font-size: 14px; color: var(--ink); line-height: 22px;">
                            Dengan janji baru <b>{new_estimated_days} hari</b>, paket tiba di hari ke-<b>{new_actual_days}</b>. 
                            Pelanggan tidak merasa dikhianati karena tiba sebelum tanggal yang dijanjikan.
                            Estimasi ulasan melonjak dari <b>{c['actual_stars']}★ → {pred_stars}</b>.
                        </div>
                    </div>
                    """
                else:
                    pred_stars = "1.2 ★" if new_delay_days > 5 else "2.3 ★"
                    verdict_box = f"""
                    <div class="card" style="border-left: 4px solid var(--bad); background: #FEF2F2;">
                        <div style="font-size: 12px; text-transform: uppercase; color: var(--bad); font-weight: 600;">Status Baru: TETAP TERLAMBAT</div>
                        <div class="serif" style="font-size: 24px; color: var(--bad); margin: 4px 0;">Masih Telat {new_delay_days:+.1f} Hari</div>
                        <div style="font-size: 14px; color: var(--ink); line-height: 22px;">
                            Keterlambatan paket ini terlalu parah (+{new_delay_days} hari melampaui janji). 
                            Buffer SLA wajar (+{c_buffer} hari) tidak cukup menyelamatkan kurir yang tersesat atau tertahan parah.
                        </div>
                    </div>
                    """
                render_html(verdict_box)
                
                # Timeline visual mini
                st.caption(f"Dekomposisi Waktu Baru: Seller ({new_seller_days:.1f} hari) + Kurir ({c['carrier_days']:.1f} hari) = Total {new_actual_days:.1f} hari vs Janji {new_estimated_days:.1f} hari.")
                
    render_html('<div style="height: 32px;"></div>')
    
    # Navigasi Lanjut
    col_nav1, col_nav2 = st.columns([1, 1.2])
    with col_nav1:
        if st.button("Lanjut ke Rencana Uji Lapangan & A/B Test (Babak 7)", type="primary", use_container_width=True):
            st.session_state["step"] = 7
            st.rerun()
    with col_nav2:
        if st.button("← Kembali ke Babak 5 (Uji Kausalitas)", type="secondary"):
            st.session_state["step"] = 5
            st.rerun()

