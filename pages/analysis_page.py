"""
pages/analysis_page.py
Halaman Input dan Analisis Soal Cerita Matematika untuk Automated Assessment System (AAS).
Tata letak padat, ringkas satu layar, tanpa banyak scroll, dengan tab indikator per dimensi.
"""

import streamlit as st
import pandas as pd
from repositories.database import (
    get_curriculum_data, 
    get_all_questions, 
    save_question, 
    save_analysis_result,
    get_question_by_id
)
from services.feedback_engine import evaluate_question
from components.ui_components import (
    render_dimension_card, 
    create_radar_chart, 
    DEMO_DISCLAIMER_LABEL, 
    DEMO_NLP_LABEL
)


def render_analysis_page():
    st.markdown("### ✍️ Input dan Analisis Soal Cerita")
    
    curriculum = get_curriculum_data()
    all_questions = get_all_questions()
    
    default_materi = st.session_state.get("active_materi", curriculum[0]["materi"] if curriculum else "Bilangan Cacah dan Operasi Hitung")
    default_tp = st.session_state.get("active_tp_text", curriculum[0]["tujuan_pembelajaran"] if curriculum else "")
    default_question = st.session_state.get("active_question_text", "")
    default_kunci = st.session_state.get("active_kunci_jawaban", "")
    default_langkah = st.session_state.get("active_langkah", "")
    active_qid = st.session_state.get("active_question_id", "SOAL-BARU")

    materi_options = [c["materi"] for c in curriculum] if curriculum else ["Bilangan Cacah dan Operasi Hitung"]
    
    # Bagian Input Ringkas (2 Kolom)
    with st.container():
        col_in1, col_in2 = st.columns([1, 1])
        with col_in1:
            c_m1, c_m2 = st.columns([1, 1])
            with c_m1:
                try:
                    idx_mat = materi_options.index(default_materi)
                except ValueError:
                    idx_mat = 0
                materi_input = st.selectbox("Lingkup Materi:", materi_options, index=idx_mat)
            with c_m2:
                # Tombol Cepat
                if st.button("📥 Muat Contoh Demo", use_container_width=True):
                    if all_questions:
                        sample = all_questions[0]
                        st.session_state["active_question_id"] = sample["id"]
                        st.session_state["active_materi"] = sample["materi"]
                        st.session_state["active_tp_text"] = sample["tp_text"]
                        st.session_state["active_question_text"] = sample["teks_soal"]
                        st.session_state["active_kunci_jawaban"] = sample.get("kunci_jawaban", "")
                        st.session_state["active_langkah"] = sample.get("langkah_penyelesaian", "")
                        st.rerun()

            soal_input = st.text_area(
                "Teks Soal Cerita Matematika:",
                value=default_question,
                placeholder="Tuliskan teks soal cerita matematika di sini...",
                height=95
            )
            
        with col_in2:
            tp_matches = [c["tujuan_pembelajaran"] for c in curriculum if c["materi"] == materi_input]
            tp_default_val = tp_matches[0] if tp_matches else default_tp
            tp_input = st.text_area("Tujuan Pembelajaran (TP):", value=tp_default_val, height=55)
            
            c_k1, c_k2 = st.columns([1, 1])
            with c_k1:
                kunci_input = st.text_input("Kunci Jawaban (Opsional):", value=default_kunci, placeholder="Misal: 138 pensil")
            with c_k2:
                langkah_input = st.text_input("Langkah Singkat (Opsional):", value=default_langkah, placeholder="Misal: 12x24 - 150 = 138")
                
        btn_analyze = st.button("🚀 Jalankan Analisis Soal Sekarang", type="primary", use_container_width=True)

    # Eksekusi Analisis
    if btn_analyze:
        if not soal_input.strip():
            st.error("⚠️ Teks soal cerita tidak boleh kosong!")
        else:
            with st.spinner("Menganalisis..."):
                report = evaluate_question(
                    materi=materi_input,
                    tp_text=tp_input,
                    teks_soal=soal_input,
                    kunci_jawaban=kunci_input,
                    langkah_penyelesaian=langkah_input,
                    question_id=active_qid,
                    is_demo=True
                )
                
                q_record = {
                    "id": active_qid if active_qid != "SOAL-BARU" else f"SOAL-USR-{pd.Timestamp.now().strftime('%M%S')}",
                    "materi": materi_input,
                    "tp_id": "TP-CUSTOM",
                    "tp_text": tp_input,
                    "teks_soal": soal_input,
                    "kunci_jawaban": kunci_input,
                    "langkah_penyelesaian": langkah_input,
                    "tingkat_tantangan": "Evaluasi Guru",
                    "tipe_kualitas": "Input Pengguna",
                    "catatan_kelemahan_demo": "",
                    "saran_perbaikan_demo": report.saran_revisi_utama[0] if report.saran_revisi_utama else "",
                    "teks_soal_revisi_demo": report.contoh_soal_revisi,
                    "versi": 1,
                    "is_demo": 0
                }
                save_question(q_record)
                
                save_analysis_result({
                    "question_id": q_record["id"],
                    "versi": 1,
                    "waktu_analisis": report.waktu_analisis,
                    "materi": report.materi,
                    "tp_text": report.tp_text,
                    "teks_soal": report.teks_soal,
                    "kunci_jawaban": report.kunci_jawaban,
                    "langkah_penyelesaian": report.langkah_penyelesaian,
                    "skor_kurikuler": report.skor_kurikuler,
                    "skor_kognitif": report.skor_kognitif,
                    "skor_bahasa": report.skor_bahasa,
                    "ringkasan_kualitas": report.ringkasan_kualitas,
                    "saran_revisi_utama": report.saran_revisi_utama,
                    "contoh_soal_revisi": report.contoh_soal_revisi,
                    "keterbatasan_analisis": report.keterbatasan_analisis,
                    "indicator_details": {
                        dim_id: [
                            {
                                "id": ind.id,
                                "kode": ind.kode,
                                "nama": ind.nama,
                                "skor": ind.skor,
                                "skor_display": ind.skor_display,
                                "alasan": ind.alasan,
                                "bukti_teks": ind.bukti_teks,
                                "saran": ind.saran,
                                "is_evaluable": ind.is_evaluable
                            }
                            for ind in dim_res.indikator_results
                        ]
                        for dim_id, dim_res in report.dimensi_results.items()
                    },
                    "is_demo": 0
                })
                
                st.session_state["latest_report"] = report
                st.session_state["current_question_record"] = q_record
                st.success("✅ Analisis selesai!")

    # =========================================================================
    # LAPORAN HASIL PENILAIAN PADAT (KOMPAK 1 LAYAR)
    # =========================================================================
    report = st.session_state.get("latest_report")
    if report:
        st.markdown("---")
        
        # Baris Ringkasan Cepat
        st.info(f"💡 **Ringkasan:** {report.ringkasan_kualitas}")
        
        col_res1, col_res2 = st.columns([1, 1])
        
        # Kolom Kiri: Kartu Skor 3 Dimensi + Radar
        with col_res1:
            st.markdown("##### 🎯 Skor 3 Dimensi Penilaian")
            render_dimension_card(report.dimensi_results["keselarasan_kurikuler"])
            render_dimension_card(report.dimensi_results["tuntutan_kognitif"])
            render_dimension_card(report.dimensi_results["kesesuaian_bahasa"])
            
            radar_fig = create_radar_chart(report.skor_kurikuler, report.skor_kognitif, report.skor_bahasa, "Radar Mutu")
            st.plotly_chart(radar_fig, use_container_width=True)

        # Kolom Kanan: Rincian Indikator dalam Tab Kompak
        with col_res2:
            st.markdown("##### 📑 Rincian 12 Indikator Rubrik")
            
            tab_kk, tab_tk, tab_kb = st.tabs([
                "🎯 Kurikuler (KK)", 
                "🧠 HOTS (TK)", 
                "📖 Bahasa (KB)"
            ])
            
            # Helper render indikator list
            def render_compact_indicators(dim_key):
                dim_res = report.dimensi_results.get(dim_key)
                if not dim_res:
                    return
                for ind in dim_res.indikator_results:
                    badge_color = "#10B981" if (ind.skor or 0) >= 3 else ("#F59E0B" if (ind.skor or 0) == 2 else "#EF4444")
                    st.markdown(f"""
                    <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:6px; padding:8px 10px; margin-bottom:6px; font-size:12px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <strong>{ind.kode}: {ind.nama}</strong>
                            <span style="background:{badge_color}; color:white; padding:2px 8px; border-radius:10px; font-weight:700; font-size:11px;">Skor: {ind.skor_display}</span>
                        </div>
                        <div style="color:#475569; margin-top:3px;"><strong>Bukti:</strong> <em>{ind.bukti_teks}</em></div>
                        <div style="color:#2563EB; margin-top:2px;">💡 {ind.saran}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with tab_kk:
                render_compact_indicators("keselarasan_kurikuler")
            with tab_tk:
                render_compact_indicators("tuntutan_kognitif")
            with tab_kb:
                render_compact_indicators("kesesuaian_bahasa")

            st.markdown("##### 🔄 Draf Soal Revisi yang Disarankan:")
            st.success(f"💬 \"{report.contoh_soal_revisi}\"")
            
            if st.button("🛠️ Buka Soal Ini di Editor Revisi", type="primary", use_container_width=True):
                st.session_state["revision_source_id"] = report.question_id
                st.session_state["revision_orig_text"] = report.teks_soal
                st.session_state["revision_suggested_text"] = report.contoh_soal_revisi
                st.session_state["revision_orig_report"] = report
                st.session_state["nav_target"] = "🛠️ Fitur Revisi Soal"
                st.rerun()
