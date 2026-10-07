"""
app.py
Router Utama Aplikasi "Janji: World Model for Business (Olist Edition)"
Mengatur alur satu keputusan per layar dan Mode Eksplorasi (?m=x)
"""

import sys
import os

# Pastikan modul internal lokal selalu dimuat segar dari disk
for mod in list(sys.modules.keys()):
    if any(mod.startswith(pkg) for pkg in ["ui", "screens", "core"]):
        del sys.modules[mod]

import streamlit as st
from ui.theme import inject_theme, setup_plotly_template
from ui.components import render_html

# 1. Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Janji: World Model for Business",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Injeksi Tema & Plotly Template
inject_theme()
setup_plotly_template()

# Inisialisasi State Sesi
if "step" not in st.session_state:
    st.session_state["step"] = 0

# Cek Mode Eksplorasi lewat URL Query Parameter (?m=x)
is_exploration_mode = st.query_params.get("m") == "x"

# 3. Router Berdasarkan Mode
if is_exploration_mode:
    # Mode Eksplorasi: Navigasi Bebas dengan Tabs
    tab_titles = [
        "Pembuka",
        "1. Dilema",
        "2. Diagnosis",
        "3. Penyelamatan",
        "4. Early Warning",
        "5. Kausalitas",
        "6. Simulator",
        "7. ROI & A/B"
    ]
    tabs = st.tabs(tab_titles)
    
    import screens.s0_pembuka as s0
    import screens.s1_dilema as s1
    import screens.s2_diagnosis as s2
    import screens.s3_penyelamatan as s3
    import screens.s4_early_warning as s4
    import screens.s5_psm_lab as s5
    import screens.s6_world_model as s6
    import screens.s7_roi_ab as s7
    
    with tabs[0]: s0.render()
    with tabs[1]: s1.render()
    with tabs[2]: s2.render()
    with tabs[3]: s3.render()
    with tabs[4]: s4.render()
    with tabs[5]: s5.render()
    with tabs[6]: s6.render()
    with tabs[7]: s7.render()

else:
    # Alur Terpandu (Satu Layar, Satu Keputusan)
    curr_step = st.session_state["step"]
    
    if curr_step == 0:
        import screens.s0_pembuka as s0
        s0.render()
        
    elif curr_step == 1:
        import screens.s1_dilema as s1
        s1.render()
        
    elif curr_step == 2:
        import screens.s2_diagnosis as s2
        s2.render()
        
    elif curr_step == 3:
        import screens.s3_penyelamatan as s3
        s3.render()
        
    elif curr_step == 4:
        import screens.s4_early_warning as s4
        s4.render()
        
    elif curr_step == 5:
        import screens.s5_psm_lab as s5
        s5.render()
        
    elif curr_step == 6:
        import screens.s6_world_model as s6
        s6.render()
        
    elif curr_step == 7:
        import screens.s7_roi_ab as s7
        s7.render()
        
    # Navigasi Sekunder untuk Kembali
    if curr_step > 0:
        render_html('<div style="height: 32px;"></div>')
        col_prev, col_mode = st.columns([1, 1])
        with col_prev:
            if st.button("← Kembali ke babak sebelumnya", type="secondary"):
                st.session_state["step"] = max(0, curr_step - 1)
                st.rerun()
        with col_mode:
            render_html('<div style="text-align: right;"><a href="?m=x" target="_self" style="font-size: 13px; color: var(--ink2); text-decoration: underline;">Buka Mode Eksplorasi (Semua Tab)</a></div>')
