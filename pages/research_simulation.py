"""
pages/research_simulation.py
Halaman Simulasi Penelitian Pretest-Posttest untuk Automated Assessment System (AAS).
Menggambarkan alur desain eksperimen penelitian disertasi dengan data sintetis 30 guru fiktif.
Membedakan dengan tegas antara Literasi Asesmen Guru dan Kualitas Soal Cerita Matematika.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from repositories.database import get_research_data
from components.ui_components import render_metric_card, DEMO_DISCLAIMER_LABEL


def render_research_simulation_page():
    st.markdown("### 🔬 Simulasi Desain Penelitian Eksperimen (Pretest - Posttest)")
    st.caption("Visualisasi demonstratif alur intervensi sistem terhadap Literasi Asesmen Guru dan Kualitas Soal Cerita Matematika.")
    
    # Banner Peringatan Kritis
    st.error(
        f"🚨 **LABEL RESMI:** {DEMO_DISCLAIMER_LABEL}.<br>"
        "Seluruh visualisasi dan angka statistik di halaman ini adalah simulasi buatan (dummy data) untuk mendemonstrasikan "
        "rencana analisis data pada disertasi. Data ini <strong>BUKAN bukti empiris</strong> dan <strong>TIDAK boleh digunakan "
        "untuk mengklaim efektivitas sistem di dunia nyata</strong>.",
        icon="⚠️"
    )
    
    df = get_research_data()
    if df.empty:
        st.warning("Data simulasi penelitian tidak ditemukan.")
        return

    # Penjelasan Pemisahan Dua Variabel Utama
    st.info(
        "📌 **Kaidah Metodologis:** Dalam penelitian ini, **Literasi Asesmen Guru** (pengetahuan & keterampilan merancang asesmen) "
        "dan **Kualitas Soal Cerita Matematika** (karakteristik fisik butir soal) diperlakukan sebagai **dua variabel hasil yang terpisah**, "
        "tidak digabungkan menjadi satu variabel komposit tunggal."
    )

    # Ringkasan Statistik Deskriptif
    st.markdown("#### 📊 Ringkasan Statistik Rata-Rata (N = 30 Guru Fiktif)")
    
    mean_pre_lit = df["skor_pretest_literasi"].mean()
    mean_post_lit = df["skor_posttest_literasi"].mean()
    mean_gain_lit = df["gain_literasi"].mean()
    
    mean_pre_q = df["skor_pretest_kualitas_soal"].mean()
    mean_post_q = df["skor_posttest_kualitas_soal"].mean()
    mean_gain_q = df["gain_kualitas_soal"].mean()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Pretest Literasi", f"{mean_pre_lit:.1f}", "Skala 0-100", "📝")
    with c2:
        render_metric_card("Posttest Literasi", f"{mean_post_lit:.1f}", f"Rata-rata gain: +{mean_gain_lit:.1f}", "📈")
    with c3:
        render_metric_card("Kualitas Soal Pre", f"{mean_pre_q:.1f}", "Skala 0-100", "📋")
    with c4:
        render_metric_card("Kualitas Soal Post", f"{mean_post_q:.1f}", f"Rata-rata gain: +{mean_gain_q:.1f}", "⭐")

    st.markdown("---")

    # Visualisasi Komparasi Pretest vs Posttest
    tab_lit, tab_soal, tab_dist = st.tabs([
        "📚 Variabel 1: Literasi Asesmen Guru", 
        "📝 Variabel 2: Kualitas Soal Cerita", 
        "📊 Distribusi & Boxplot Skor"
    ])
    
    with tab_lit:
        st.markdown("##### Perubahan Skor Literasi Asesmen Setiap Guru (Pretest vs Posttest)")
        fig_lit = go.Figure()
        
        # Garis pasangan untuk setiap guru
        for _, row in df.iterrows():
            fig_lit.add_trace(go.Scatter(
                x=["Pretest Literasi", "Posttest Literasi"],
                y=[row["skor_pretest_literasi"], row["skor_posttest_literasi"]],
                mode="lines+markers",
                line=dict(color="rgba(59, 130, 246, 0.4)", width=1.5),
                marker=dict(size=6),
                showlegend=False,
                hoverinfo="text",
                text=f"{row['nama_guru']} ({row['id_partisipan']}): Pre {row['skor_pretest_literasi']} -> Post {row['skor_posttest_literasi']} (Gain: +{row['gain_literasi']})"
            ))
            
        # Garis rata-rata
        fig_lit.add_trace(go.Scatter(
            x=["Pretest Literasi", "Posttest Literasi"],
            y=[mean_pre_lit, mean_post_lit],
            mode="lines+markers+text",
            line=dict(color="#1E3A8A", width=4),
            marker=dict(size=12, color="#1E3A8A"),
            text=[f"Rerata Pre: {mean_pre_lit:.1f}", f"Rerata Post: {mean_post_lit:.1f}"],
            textposition="top center",
            name="Rata-rata Kelompok"
        ))
        
        fig_lit.update_layout(
            yaxis=dict(range=[30, 100], title="Skor Literasi Asesmen (0 - 100)", gridcolor="#F1F5F9"),
            margin=dict(l=20, r=20, t=30, b=20),
            height=380
        )
        st.plotly_chart(fig_lit, use_container_width=True)

    with tab_soal:
        st.markdown("##### Perubahan Kualitas Soal Cerita Matematika Guru (Sebelum vs Sesudah Intervensi)")
        fig_q = go.Figure()
        
        for _, row in df.iterrows():
            fig_q.add_trace(go.Scatter(
                x=["Kualitas Pre", "Kualitas Post"],
                y=[row["skor_pretest_kualitas_soal"], row["skor_posttest_kualitas_soal"]],
                mode="lines+markers",
                line=dict(color="rgba(16, 185, 129, 0.4)", width=1.5),
                marker=dict(size=6),
                showlegend=False,
                hoverinfo="text",
                text=f"{row['nama_guru']}: Pre {row['skor_pretest_kualitas_soal']} -> Post {row['skor_posttest_kualitas_soal']} (Gain: +{row['gain_kualitas_soal']})"
            ))
            
        fig_q.add_trace(go.Scatter(
            x=["Kualitas Pre", "Kualitas Post"],
            y=[mean_pre_q, mean_post_q],
            mode="lines+markers+text",
            line=dict(color="#065F46", width=4),
            marker=dict(size=12, color="#065F46"),
            text=[f"Rerata Pre: {mean_pre_q:.1f}", f"Rerata Post: {mean_post_q:.1f}"],
            textposition="top center",
            name="Rata-rata Kelompok"
        ))
        
        fig_q.update_layout(
            yaxis=dict(range=[30, 100], title="Skor Kualitas Soal Cerita (0 - 100)", gridcolor="#F1F5F9"),
            margin=dict(l=20, r=20, t=30, b=20),
            height=380
        )
        st.plotly_chart(fig_q, use_container_width=True)

    with tab_dist:
        st.markdown("##### Sebaran Skor Pretest dan Posttest")
        col_box1, col_box2 = st.columns(2)
        with col_box1:
            fig_box_lit = go.Figure()
            fig_box_lit.add_trace(go.Box(y=df["skor_pretest_literasi"], name="Pretest Literasi", marker_color="#93C5FD"))
            fig_box_lit.add_trace(go.Box(y=df["skor_posttest_literasi"], name="Posttest Literasi", marker_color="#3B82F6"))
            fig_box_lit.update_layout(yaxis=dict(range=[30, 100], title="Skor"), margin=dict(l=20, r=20, t=20, b=20), height=320)
            st.plotly_chart(fig_box_lit, use_container_width=True)
        with col_box2:
            fig_box_q = go.Figure()
            fig_box_q.add_trace(go.Box(y=df["skor_pretest_kualitas_soal"], name="Pre Kualitas Soal", marker_color="#A7F3D0"))
            fig_box_q.add_trace(go.Box(y=df["skor_posttest_kualitas_soal"], name="Post Kualitas Soal", marker_color="#10B981"))
            fig_box_q.update_layout(yaxis=dict(range=[30, 100], title="Skor"), margin=dict(l=20, r=20, t=20, b=20), height=320)
            st.plotly_chart(fig_box_q, use_container_width=True)

    st.markdown("---")

    # Tabel Rincian Data Partisipan & Ekspor
    st.markdown("#### 📋 Data Lengkap 30 Partisipan Guru Fiktif")
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Unduh Data Sintetis Penelitian (CSV)",
        data=csv_bytes,
        file_name="demo_research_data_synthetic.csv",
        mime="text/csv",
        type="primary"
    )
