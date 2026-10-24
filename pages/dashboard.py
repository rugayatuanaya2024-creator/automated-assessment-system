"""
pages/dashboard.py
Halaman Dashboard Utama untuk Automated Assessment System (AAS).
Menampilkan ringkasan metrik, grafik komparasi tiga dimensi, progres sebelum vs sesudah revisi,
dan linimasa aktivitas analisis terbaru.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from repositories.database import get_all_questions, get_all_analysis_results, get_teacher_profile
from components.ui_components import (
    render_metric_card, 
    create_radar_chart, 
    create_comparison_chart,
    DEMO_DISCLAIMER_LABEL
)


def render_dashboard_page():
    st.markdown("### 📊 Ringkasan Dashboard")
    st.caption("Pantauan otomatis terhadap seluruh soal yang telah dianalisis dan direvisi.")
    
    # Ambil data dari database
    questions = get_all_questions()
    analysis_list = get_all_analysis_results()
    profile = get_teacher_profile()
    
    # Filter soal asli vs revisi
    total_questions = len(questions)
    revised_questions = [q for q in questions if q.get("versi", 1) > 1 or q.get("parent_id") is not None]
    total_revised = len(revised_questions)
    
    # Hitung rata-rata skor per dimensi dari hasil analisis versi 1
    v1_analyses = [a for a in analysis_list if a.get("versi", 1) == 1]
    
    if v1_analyses:
        avg_kurikuler = sum(a.get("skor_kurikuler", 0.0) for a in v1_analyses) / len(v1_analyses)
        avg_kognitif = sum(a.get("skor_kognitif", 0.0) for a in v1_analyses) / len(v1_analyses)
        avg_bahasa = sum(a.get("skor_bahasa", 0.0) for a in v1_analyses) / len(v1_analyses)
    else:
        avg_kurikuler, avg_kognitif, avg_bahasa = 0.0, 0.0, 0.0

    # 1. Baris Kartu Metrik
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        render_metric_card("Total Soal", str(total_questions), "Bank soal aktif", "📝")
    with c2:
        render_metric_card("Soal Direvisi", str(total_revised), "Versi perbaikan", "🔄")
    with c3:
        render_metric_card("Keselarasan", f"{avg_kurikuler:.1f}", "Rerata kurikuler", "🎯")
    with c4:
        render_metric_card("Tuntutan HOTS", f"{avg_kognitif:.1f}", "Rerata kognitif", "🧠")
    with c5:
        render_metric_card("Kesesuaian Bahasa", f"{avg_bahasa:.1f}", "Rerata keterbacaan", "📖")

    st.markdown("---")

    # 2. Grafik Dua Kolom: Radar Profil Tiga Dimensi & Perbandingan Sebelum-Sesudah
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("#### 🎯 Profil Tiga Dimensi Rata-Rata")
        st.caption("Keseimbangan capaian kualitas soal cerita pada bank soal awal.")
        fig_radar = create_radar_chart(avg_kurikuler, avg_kognitif, avg_bahasa, "Rata-Rata 3 Dimensi Soal Awal")
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_chart2:
        st.markdown("#### 📈 Perbandingan Skor Sebelum vs Sesudah Revisi")
        st.caption("Simulasi dampak perbaikan konstruksi soal pada 4 contoh soal revisi.")
        
        # Cari soal yang memiliki versi 1 dan versi 2
        v2_analyses = [a for a in analysis_list if a.get("versi", 1) == 2]
        if v2_analyses:
            avg_v2_kur = sum(a.get("skor_kurikuler", 0.0) for a in v2_analyses) / len(v2_analyses)
            avg_v2_kog = sum(a.get("skor_kognitif", 0.0) for a in v2_analyses) / len(v2_analyses)
            avg_v2_bah = sum(a.get("skor_bahasa", 0.0) for a in v2_analyses) / len(v2_analyses)
            
            # Hitung rata-rata v1 dari soal yang sama
            matched_qids = set(a.get("question_id") for a in v2_analyses)
            v1_matched = [a for a in v1_analyses if a.get("question_id") in matched_qids]
            if v1_matched:
                avg_v1_kur = sum(a.get("skor_kurikuler", 0.0) for a in v1_matched) / len(v1_matched)
                avg_v1_kog = sum(a.get("skor_kognitif", 0.0) for a in v1_matched) / len(v1_matched)
                avg_v1_bah = sum(a.get("skor_bahasa", 0.0) for a in v1_matched) / len(v1_matched)
            else:
                avg_v1_kur, avg_v1_kog, avg_v1_bah = avg_kurikuler, avg_kognitif, avg_bahasa

            v1_dict = {"keselarasan_kurikuler": avg_v1_kur, "tuntutan_kognitif": avg_v1_kog, "kesesuaian_bahasa": avg_v1_bah}
            v2_dict = {"keselarasan_kurikuler": avg_v2_kur, "tuntutan_kognitif": avg_v2_kog, "kesesuaian_bahasa": avg_v2_bah}
            fig_comp = create_comparison_chart(v1_dict, v2_dict, "Versi Asli (v1)", "Versi Revisi (v2)")
            st.plotly_chart(fig_comp, use_container_width=True)
        else:
            st.info("Belum ada data revisi versi 2. Lakukan revisi pada menu 'Revisi Soal'.")

    st.markdown("---")

    # 3. Distribusi Kualitas Soal per Materi
    st.markdown("#### 📚 Distribusi Soal Berdasarkan Materi Matematika")
    if analysis_list:
        df_act = pd.DataFrame(analysis_list)
        materi_counts = df_act.groupby("materi").agg(
            Jumlah_Soal=("id", "count"),
            Rata_Kurikuler=("skor_kurikuler", "mean"),
            Rata_Kognitif=("skor_kognitif", "mean"),
            Rata_Bahasa=("skor_bahasa", "mean")
        ).reset_index()
        materi_counts["Rata_Kurikuler"] = materi_counts["Rata_Kurikuler"].round(1)
        materi_counts["Rata_Kognitif"] = materi_counts["Rata_Kognitif"].round(1)
        materi_counts["Rata_Bahasa"] = materi_counts["Rata_Bahasa"].round(1)
        st.dataframe(materi_counts, use_container_width=True, hide_index=True)

    # 4. Tabel Aktivitas Analisis Terbaru
    st.markdown("#### 🕒 Aktivitas Analisis Terbaru")
    if analysis_list:
        display_data = []
        for a in analysis_list[:8]:
            display_data.append({
                "Waktu": a.get("waktu_analisis", "-"),
                "ID Soal": a.get("question_id", "-"),
                "Versi": f"v{a.get('versi', 1)}",
                "Materi": a.get("materi", "-"),
                "Skor Kurikuler": f"{a.get('skor_kurikuler', 0):.1f}",
                "Skor Kognitif": f"{a.get('skor_kognitif', 0):.1f}",
                "Skor Bahasa": f"{a.get('skor_bahasa', 0):.1f}",
                "Ringkasan Kualitas": a.get("ringkasan_kualitas", "-")[:60] + "..."
            })
        st.dataframe(pd.DataFrame(display_data), use_container_width=True, hide_index=True)
    else:
        st.write("Belum ada aktivitas analisis.")
