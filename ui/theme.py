"""
ui/theme.py
Design System: CSS kustom "Executive Modern" dan Template Plotly "janji"
"""

import streamlit as st
import plotly.io as pio
import plotly.graph_objects as go

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;1,6..72,400&family=Instrument+Sans:wght@400;500;600&display=swap');

:root {
  --bg: #F7F5F0;
  --surface: #FFFFFF;
  --ink: #14130F;
  --ink2: #5E5C55;
  --line: #E4E0D6;
  --good: #1F7A5A;
  --bad: #C2432B;
  --gray: #8A8880;
}

[data-theme="dark"] {
  --bg: #111110;
  --surface: #1A1A18;
  --ink: #F2F0EA;
  --ink2: #A9A69D;
  --line: #2B2A26;
  --good: #4DB58F;
  --bad: #E8735C;
  --gray: #7C7A72;
}

html, body, .stApp {
  background: var(--bg) !important;
  color: var(--ink) !important;
  font-family: 'Instrument Sans', system-ui, sans-serif !important;
  font-variant-numeric: tabular-nums !important;
}

/* Sembunyikan chrome default Streamlit agar tampilan murni seperti web app independen */
header[data-testid="stHeader"], footer, #MainMenu, [data-testid="stSidebar"], [data-testid="stToolbar"] {
  display: none !important;
}

/* Hilangkan flicker skeleton loader yang membuat tampilan patah-patah */
[data-testid="stSkeleton"] {
  display: none !important;
}

/* Animasi Masuk Halus (Fade & Gentle Slide) */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.block-container {
  max-width: 960px !important;
  padding-top: 36px !important;
  padding-bottom: 96px !important;
  margin: 0 auto !important;
  animation: fadeInUp 0.22s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  will-change: opacity, transform;
}

.serif { font-family: 'Newsreader', Georgia, serif; font-weight: 400; }
.display { font-family: 'Newsreader', Georgia, serif; font-size: 64px; line-height: 1.08; letter-spacing: -0.01em; }
.giant { font-family: 'Newsreader', Georgia, serif; font-size: 130px; line-height: 1; letter-spacing: -0.02em; }
.label { font-size: 13px; letter-spacing: 0.1em; text-transform: uppercase; color: var(--ink2); font-weight: 600; }
.so-what { font-family: 'Newsreader', Georgia, serif; font-size: 30px; line-height: 38px; max-width: 720px; color: var(--ink); }

.card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 16px;
  transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
}
.card:hover {
  border-color: rgba(20, 19, 15, 0.22);
}
.card.on {
  border: 2px solid var(--ink) !important;
}
.hatch {
  background: repeating-linear-gradient(45deg, transparent 0 6px, rgba(138,136,128,0.2) 6px 7px);
}

/* Tombol Utama: Pil Tinta 56px */
.stButton > button[kind="primary"] {
  height: 56px !important;
  padding: 0 44px !important;
  border-radius: 999px !important;
  background: var(--ink) !important;
  color: var(--bg) !important;
  border: 0 !important;
  font-family: 'Instrument Sans', sans-serif !important;
  font-size: 17px !important;
  font-weight: 500 !important;
  cursor: pointer !important;
  transition: transform 0.15s ease, opacity 0.15s ease !important;
}
.stButton > button[kind="primary"]:hover {
  opacity: 0.9 !important;
  transform: translateY(-1px) !important;
}
.stButton > button[kind="secondary"] {
  background: transparent !important;
  border: 0 !important;
  text-decoration: underline !important;
  text-underline-offset: 4px !important;
  color: var(--ink) !important;
  font-size: 15px !important;
  padding: 0 !important;
}

/* Callout Box Status */
.callout {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 16px 20px;
  margin: 16px 0;
}
.callout-label {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-bottom: 6px;
}
.callout-insight { color: var(--ink); }
.callout-perhatian { color: var(--bad); }
.callout-hasil { color: var(--good); }
.callout-batasan { color: var(--gray); }

@media (max-width: 640px) {
  .display { font-size: 40px !important; }
  .giant { font-size: 88px !important; }
  .so-what { font-size: 22px !important; line-height: 30px !important; }
  .block-container { padding-top: 24px !important; padding-bottom: 64px !important; }
}
</style>
"""

def inject_theme():
    """Menyisipkan CSS kustom ke dalam Streamlit."""
    st.markdown(CSS, unsafe_allow_html=True)

def setup_plotly_template():
    """Mengonfigurasi template Plotly 'janji' tanpa legenda dan dengan warna aksen minimalis."""
    pio.templates["janji"] = go.layout.Template(
        layout=dict(
            font=dict(family="Instrument Sans", size=13, color="#14130F"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, zeroline=False, linecolor="#E4E0D6", tickcolor="#E4E0D6"),
            yaxis=dict(showgrid=True, gridcolor="#E4E0D6", griddash="dot", zeroline=False),
            margin=dict(l=24, r=24, t=24, b=24),
            showlegend=False,
            colorway=["#14130F", "#C2432B", "#1F7A5A", "#8A8880"]
        )
    )
    pio.templates.default = "janji"
