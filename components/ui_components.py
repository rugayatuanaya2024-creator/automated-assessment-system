"""
components/ui_components.py
Komponen antarmuka modern, lembut, dan akademis untuk Automated Assessment System (AAS).
Warna biru lembut akademis, kartu putih bersih, kontras teks optimal, dan tata letak ringkas.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, Any, List, Optional
from models.schemas import DimensionResult, IndicatorResult, DEMO_DISCLAIMER_LABEL, DEMO_NLP_LABEL


def inject_custom_css():
    """Menyuntikkan stylesheet CSS bernuansa akademis resmi, bersih, dan lembut."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Header Card Akademis Lembut */
    .hero-banner {
        background: linear-gradient(135deg, #1E40AF 0%, #2563EB 60%, #3B82F6 100%);
        border: 1px solid #1D4ED8;
        border-radius: 12px;
        padding: 20px 24px;
        color: #FFFFFF;
        margin-bottom: 18px;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.15);
    }
    
    .hero-title {
        font-size: 24px;
        font-weight: 700;
        margin: 0;
        color: #FFFFFF;
        letter-spacing: -0.4px;
    }
    
    .hero-subtitle {
        font-size: 14.5px;
        color: #DBEAFE;
        margin-top: 4px;
        font-weight: 400;
    }
    
    /* Disclaimer Tag */
    .demo-badge {
        display: inline-block;
        background-color: #FEF3C7;
        color: #92400E;
        font-size: 11px;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 6px;
        border: 1px solid #FDE68A;
        letter-spacing: 0.3px;
    }

    .demo-nlp-badge {
        display: inline-block;
        background-color: #EFF6FF;
        color: #1E40AF;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 6px;
        border: 1px solid #BFDBFE;
    }
    
    /* Metric Cards */
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 14px 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(0,0,0,0.06);
    }
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: #0F172A;
        margin: 2px 0;
    }
    .metric-label {
        font-size: 12px;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }
    .metric-desc {
        font-size: 11.5px;
        color: #94A3B8;
    }

    /* Score Indicator Badges */
    .score-badge-green {
        background-color: #DCFCE7;
        color: #166534;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
        display: inline-block;
        font-size: 12px;
    }
    .score-badge-yellow {
        background-color: #FEF9C3;
        color: #854D0E;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
        display: inline-block;
        font-size: 12px;
    }
    .score-badge-red {
        background-color: #FEE2E2;
        color: #991B1B;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
        display: inline-block;
        font-size: 12px;
    }

    /* Dimension Box Ringkas */
    .dimension-box {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 8px;
    }
    </style>
    """, unsafe_allow_html=True)


def render_header():
    """Merender banner judul aplikasi bergaya akademis lembut."""
    inject_custom_css()
    st.markdown(f"""
    <div class="hero-banner">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px;">
            <div>
                <h1 class="hero-title">Automated Assessment System (AAS)</h1>
                <p class="hero-subtitle">Asisten Cerdas Guru dalam Merancang & Mengevaluasi Soal Cerita Matematika Kelas IV SD</p>
            </div>
            <span class="demo-badge">{DEMO_DISCLAIMER_LABEL}</span>
        </div>
        <div style="margin-top: 10px; font-size: 12px; color: #EFF6FF; line-height: 1.5; border-top: 1px solid rgba(255,255,255,0.25); padding-top: 8px;">
            🎓 <strong>Proyek Disertasi:</strong> <em>"Pengembangan Automated Assessment System Berbasis AI untuk Meningkatkan Literasi Asesmen Guru dan Kualitas Soal Cerita Matematika SD."</em>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_metric_card(label: str, value: str, desc: str = "", icon: str = "📊"):
    """Merender kartu metrik visual bersih dan ringkas."""
    st.markdown(f"""
    <div class="metric-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span class="metric-label">{label}</span>
            <span style="font-size: 18px;">{icon}</span>
        </div>
        <div class="metric-value">{value}</div>
        <div class="metric-desc">{desc}</div>
    </div>
    """, unsafe_allow_html=True)


def render_dimension_card(dim: DimensionResult):
    """Merender kartu skor satu dimensi dengan progress bar padat."""
    if dim.skor >= 75.0:
        badge_class = "score-badge-green"
    elif dim.skor >= 50.0:
        badge_class = "score-badge-yellow"
    else:
        badge_class = "score-badge-red"

    st.markdown(f"""
    <div class="dimension-box">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <strong style="font-size: 14px; color: #1E293B;">{dim.nama}</strong>
            <span class="{badge_class}">{dim.skor:.1f} / 100</span>
        </div>
        <div style="font-size: 11.5px; color: #64748B; margin-top: 4px;">
            Status: <strong>{dim.kategori_label}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.progress(min(1.0, max(0.0, dim.skor / 100.0)))


def create_radar_chart(skor_kurikuler: float, skor_kognitif: float, skor_bahasa: float, title: str = "Profil 3 Dimensi") -> go.Figure:
    """Membuat radar chart Plotly ringkas untuk visualisasi tiga dimensi soal."""
    categories = ["Keselarasan Kurikuler", "Tuntutan Kognitif / HOTS", "Kesesuaian Bahasa"]
    values = [skor_kurikuler, skor_kognitif, skor_bahasa]
    
    categories_closed = categories + [categories[0]]
    values_closed = values + [values[0]]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=categories_closed,
        fill='toself',
        fillcolor='rgba(59, 130, 246, 0.25)',
        line=dict(color='#2563EB', width=2),
        name='Skor Dimensi'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=9), color="#64748B"),
            angularaxis=dict(tickfont=dict(size=10.5, color="#1E293B"))
        ),
        showlegend=False,
        margin=dict(l=30, r=30, t=25, b=25),
        height=260,
        title=dict(text=title, font=dict(size=13, color="#1E293B"), x=0.5)
    )
    return fig


def create_comparison_chart(v1_scores: Dict[str, float], v2_scores: Dict[str, float], label1: str = "Sebelum", label2: str = "Sesudah") -> go.Figure:
    """Membuat bar chart Plotly perbandingan ringkas skor sebelum dan sesudah revisi."""
    dims = ["Kurikuler", "Kognitif/HOTS", "Bahasa"]
    keys = ["keselarasan_kurikuler", "tuntutan_kognitif", "kesesuaian_bahasa"]
    
    s1 = [v1_scores.get(k, 0.0) for k in keys]
    s2 = [v2_scores.get(k, 0.0) for k in keys]
    
    fig = go.Figure(data=[
        go.Bar(name=label1, x=dims, y=s1, marker_color='#94A3B8'),
        go.Bar(name=label2, x=dims, y=s2, marker_color='#10B981')
    ])
    
    fig.update_layout(
        barmode='group',
        yaxis=dict(range=[0, 105], title="Skor (0-100)", gridcolor="#F1F5F9", tickfont=dict(size=10)),
        xaxis=dict(tickfont=dict(size=11)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)),
        margin=dict(l=20, r=20, t=25, b=20),
        height=260
    )
    return fig
