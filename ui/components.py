"""
ui/components.py
Komponen antarmuka yang dapat digunakan ulang: label klaim, callout, angka raksasa, dan vonis
Dilengkapi textwrap.dedent agar kebal terhadap galat pemformatan indentasi Markdown (raw div)
"""

import textwrap
import streamlit as st
from core.load import get_seal_hash

def render_html(html_str: str):
    """Render HTML secara aman tanpa memicu format kode <pre><code> akibat indentasi Python."""
    cleaned = textwrap.dedent(html_str).strip()
    st.markdown(cleaned, unsafe_allow_html=True)

def render_top_bar(step_title: str = "", current_step: int = 0, total_steps: int = 7):
    """Menampilkan penanda progres minimalis di bagian paling atas."""
    col_l, col_r = st.columns([2, 1])
    with col_l:
        render_html(f'<div style="font-family: \'Newsreader\', serif; font-size: 20px; font-weight: 600; letter-spacing: -0.02em;">Janji <span style="font-family: \'Instrument Sans\', sans-serif; font-size: 13px; font-weight: 400; color: var(--ink2); margin-left: 12px;">{step_title}</span></div>')
    with col_r:
        if current_step > 0:
            render_html(f'<div style="text-align: right; font-size: 13px; color: var(--ink2); font-weight: 500;">Babak {current_step} dari {total_steps}</div>')
    render_html('<div style="height: 1px; background: var(--line); margin: 16px 0 32px 0;"></div>')

def label_klaim(jenis: str, tingkat: str = "B"):
    """
    Menampilkan label epistemik klaim (DATA, ASOSIASI, ESTIMASI, PREDIKSI, SKENARIO)
    dan lencana tingkat bukti (A, B, C).
    """
    jenis = jenis.upper()
    return f"""<div style="display: inline-flex; align-items: center; gap: 8px; margin-bottom: 8px;"><span class="label" style="background: var(--surface); border: 1px solid var(--line); padding: 3px 8px; border-radius: 4px;">{jenis}</span><span style="font-size: 11px; font-weight: 600; color: var(--ink2); border-radius: 50%; border: 1px solid var(--line); width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center;">{tingkat}</span></div>"""

def hero_number(angka: str, unit: str = "", warna: str = "var(--ink)", subteks: str = "", unit_str: str = "", **kwargs):
    """Menampilkan angka raksasa editorial Newsreader dengan satuan."""
    u = unit_str if unit_str else unit
    sub = f'<div style="font-size: 15px; color: var(--ink2); margin-top: 6px;">{subteks}</div>' if subteks else ''
    render_html(f"""
    <div style="margin: 20px 0;">
    <div style="display: flex; align-items: baseline; gap: 12px;">
    <span class="giant" style="color: {warna};">{angka}</span>
    <span class="serif" style="font-size: 28px; color: var(--ink2);">{u}</span>
    </div>
    {sub}
    </div>
    """)

def so_what(kalimat: str):
    """Menampilkan kalimat vonis 'jadi apa' bergaya editorial Newsreader."""
    render_html(f"""
    <div class="so-what" style="margin: 24px 0 32px 0;">
    {kalimat}
    </div>
    """)

def callout(jenis: str, teks: str, subteks: str = ""):
    """
    Menampilkan status alert sesuai aturan desain:
    Label huruf kapital + latar permukaan + garis tipis (tanpa garis kiri tebal).
    """
    jenis_upper = jenis.upper()
    color_map = {
        "INSIGHT": "callout-insight",
        "PERHATIAN": "callout-perhatian",
        "HASIL": "callout-hasil",
        "BATASAN": "callout-batasan"
    }
    cls = color_map.get(jenis_upper, "callout-insight")
    hatch_cls = "hatch" if jenis_upper == "BATASAN" else ""
    sub = f'<div style="font-size: 13px; color: var(--ink2); margin-top: 6px;">{subteks}</div>' if subteks else ''
    
    render_html(f"""
    <div class="callout {hatch_cls}">
    <div class="callout-label {cls}">{jenis_upper}</div>
    <div style="font-size: 15px; line-height: 22px; color: var(--ink);">{teks}</div>
    {sub}
    </div>
    """)

def render_segel_holdout():
    """Menampilkan tombol segel popover holdout di pojok layar."""
    with st.popover("Data Uji Terkunci [SHA-256]", use_container_width=False):
        st.markdown("**Bukti Keaslian Data Uji (SHA-256)**")
        st.code(get_seal_hash(), language="text")
        st.caption(
            "Sebanyak 12.801 pesanan dipisahkan sebagai data uji murni sejak awal. "
            "Kunci digital ini membuktikan data uji tidak pernah diintip atau dimanipulasi selama pembuatan model."
        )
