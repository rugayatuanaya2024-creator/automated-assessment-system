"""
pages/revision_page.py
Halaman Fitur Revisi Soal untuk Automated Assessment System (AAS).
Memungkinkan guru membandingkan versi asli vs revisi, mengedit draf revisi,
menganalisis ulang versi baru, dan menyimpan riwayat revisi sebagai versi terpisah.
"""

import streamlit as st
import pandas as pd
from repositories.database import (
    get_all_questions, 
    get_question_by_id, 
    save_question, 
    save_analysis_result,
    get_analysis_by_question_id
)
from services.feedback_engine import evaluate_question
from services.scoring import compute_score_delta
from components.ui_components import create_comparison_chart, DEMO_DISCLAIMER_LABEL


def render_revision_page():
    st.markdown("### 🛠️ Fitur Revisi Soal & Perbandingan Versi")
    st.caption("Perbaiki konstruksi soal cerita matematika, lakukan analisis ulang, dan bandingkan peningkatan kualitas antarsi.")
    
    questions = get_all_questions()
    
    # Pilih soal yang akan direvisi
    source_qid = st.session_state.get("revision_source_id")
    q_ids = [q["id"] for q in questions]
    
    col_sel1, col_sel2 = st.columns([1, 2])
    with col_sel1:
        selected_qid = st.selectbox(
            "Pilih Soal yang Ingin Direvisi:",
            q_ids,
            index=q_ids.index(source_qid) if source_qid in q_ids else 0
        )
        
    current_q = get_question_by_id(selected_qid)
    if not current_q:
        st.warning("Pilih soal terlebih dahulu.")
        return

    # Ambil riwayat analisis soal ini (versi 1)
    analysis_hist = get_analysis_by_question_id(selected_qid)
    v1_analysis = analysis_hist[0] if analysis_hist else None
    
    # Ambil teks saran awal
    default_revision_draft = st.session_state.get("revision_suggested_text")
    if not default_revision_draft:
        default_revision_draft = current_q.get("teks_soal_revisi_demo") or current_q.get("teks_soal")

    st.markdown("---")
    
    # Tampilan Dua Kolom: Soal Asli vs Editor Revisi
    col_orig, col_edit = st.columns(2)
    
    with col_orig:
        st.markdown("#### 📄 Versi Asli (Sebelum Revisi)")
        st.info(f"💬 \"{current_q.get('teks_soal')}\"")
        
        if v1_analysis:
            st.markdown(f"**Skor Versi Awal:**")
            st.write(f"- 🎯 Keselarasan Kurikuler: **{v1_analysis.get('skor_kurikuler', 0):.1f}**")
            st.write(f"- 🧠 Tuntutan Kognitif / HOTS: **{v1_analysis.get('skor_kognitif', 0):.1f}**")
            st.write(f"- 📖 Kesesuaian Bahasa: **{v1_analysis.get('skor_bahasa', 0):.1f}**")
            
            if v1_analysis.get("saran_revisi_utama"):
                st.markdown("**Catatan Rekomendasi Sistem:**")
                for s in v1_analysis.get("saran_revisi_utama")[:2]:
                    st.caption(f"• {s}")
        else:
            st.write("Belum ada skor awal tersimpan.")

    with col_edit:
        st.markdown("#### ✏️ Editor Teks Revisi (Versi Baru)")
        revised_text = st.text_area(
            "Sesuaikan atau sunting teks revisi di bawah ini:",
            value=default_revision_draft,
            height=160,
            key="txt_area_revision"
        )
        
        btn_reanalyze = st.button("🚀 Simpan & Analisis Ulang Versi Revisi", type="primary", use_container_width=True)

    # Eksekusi Analisis Ulang Versi Revisi
    if btn_reanalyze:
        if not revised_text.strip():
            st.error("Teks revisi tidak boleh kosong!")
        else:
            with st.spinner("Menganalisis versi revisi baru..."):
                rev_report = evaluate_question(
                    materi=current_q["materi"],
                    tp_text=current_q["tp_text"],
                    teks_soal=revised_text,
                    kunci_jawaban=current_q.get("kunci_jawaban", ""),
                    langkah_penyelesaian="Penyelesaian versi revisi.",
                    question_id=current_q["id"],
                    is_demo=False
                )
                
                # Simpan versi revisi sebagai record terpisah di SQLite (tanpa menimpa versi asli)
                rev_qid = f"{current_q['id']}-REV{len(analysis_hist) + 1}"
                new_version_num = len(analysis_hist) + 1
                
                save_question({
                    "id": rev_qid,
                    "materi": current_q["materi"],
                    "tp_id": current_q.get("tp_id"),
                    "tp_text": current_q["tp_text"],
                    "teks_soal": revised_text,
                    "kunci_jawaban": current_q.get("kunci_jawaban", ""),
                    "langkah_penyelesaian": "Penyelesaian revisi guru.",
                    "tingkat_tantangan": "Revisi Teruji",
                    "tipe_kualitas": f"Versi Revisi ({new_version_num})",
                    "catatan_kelemahan_demo": "Hasil perbaikan mandiri.",
                    "saran_perbaikan_demo": "",
                    "teks_soal_revisi_demo": "",
                    "versi": new_version_num,
                    "parent_id": current_q["id"],
                    "is_demo": 0
                })
                
                save_analysis_result({
                    "question_id": current_q["id"],
                    "versi": new_version_num,
                    "waktu_analisis": rev_report.waktu_analisis,
                    "materi": rev_report.materi,
                    "tp_text": rev_report.tp_text,
                    "teks_soal": revised_text,
                    "kunci_jawaban": rev_report.kunci_jawaban,
                    "langkah_penyelesaian": "Penyelesaian revisi guru.",
                    "skor_kurikuler": rev_report.skor_kurikuler,
                    "skor_kognitif": rev_report.skor_kognitif,
                    "skor_bahasa": rev_report.skor_bahasa,
                    "ringkasan_kualitas": rev_report.ringkasan_kualitas,
                    "saran_revisi_utama": rev_report.saran_revisi_utama,
                    "contoh_soal_revisi": rev_report.contoh_soal_revisi,
                    "keterbatasan_analisis": rev_report.keterbatasan_analisis,
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
                        for dim_id, dim_res in rev_report.dimensi_results.items()
                    },
                    "is_demo": 0
                })
                
                st.session_state["active_rev_report"] = rev_report
                st.success("✅ Versi revisi berhasil dianalisis dan disimpan sebagai versi terpisah!")
                st.rerun()

    # =========================================================================
    # PERBANDINGAN SEBELUM DAN SESUDAH REVISI
    # =========================================================================
    st.markdown("---")
    st.markdown("### 📊 Perbandingan Hasil Sebelum dan Sesudah Revisi")
    
    # Muat ulang riwayat versi terkini untuk soal ini
    updated_hist = get_analysis_by_question_id(selected_qid)
    if len(updated_hist) >= 2:
        v_awal = updated_hist[0]
        v_akhir = updated_hist[-1]
        
        v1_scores = {
            "keselarasan_kurikuler": v_awal.get("skor_kurikuler", 0.0),
            "tuntutan_kognitif": v_awal.get("skor_kognitif", 0.0),
            "kesesuaian_bahasa": v_awal.get("skor_bahasa", 0.0)
        }
        v2_scores = {
            "keselarasan_kurikuler": v_akhir.get("skor_kurikuler", 0.0),
            "tuntutan_kognitif": v_akhir.get("skor_kognitif", 0.0),
            "kesesuaian_bahasa": v_akhir.get("skor_bahasa", 0.0)
        }
        deltas = compute_score_delta(v1_scores, v2_scores)
        
        c_del1, c_del2, c_del3 = st.columns(3)
        with c_del1:
            d = deltas["keselarasan_kurikuler"]
            st.metric("Keselarasan Kurikuler", f"{d['v2']:.1f}", delta=f"{d['status_text']} poin")
        with c_del2:
            d = deltas["tuntutan_kognitif"]
            st.metric("Tuntutan Kognitif / HOTS", f"{d['v2']:.1f}", delta=f"{d['status_text']} poin")
        with c_del3:
            d = deltas["kesesuaian_bahasa"]
            st.metric("Kesesuaian Bahasa", f"{d['v2']:.1f}", delta=f"{d['status_text']} poin")
            
        fig_diff = create_comparison_chart(v1_scores, v2_scores, f"Versi {v_awal.get('versi', 1)}", f"Versi {v_akhir.get('versi', 2)}")
        st.plotly_chart(fig_diff, use_container_width=True)
        
        st.info(
            "📌 **Keterangan Peneliti:** Peningkatan skor pada mode simulasi membuktikan berfungsinya alur deteksi aturan dan evaluasi NLP, "
            "tetapi belum membuktikan efektivitas sistem di dunia nyata tanpa uji eksperimen empiris terhadap guru di sekolah."
        )
    else:
        st.write("Silakan simpan versi revisi untuk melihat komparasi perubahan skor.")
