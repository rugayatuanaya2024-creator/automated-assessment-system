"""
pages/question_bank.py
Halaman Bank Soal Cerita Demonstrasi untuk Automated Assessment System (AAS).
Menyediakan minimal 15 soal cerita matematika dengan variasi kelemahan dan karakteristik demonstratif.
"""

import streamlit as st
import pandas as pd
from repositories.database import get_all_questions
from components.ui_components import DEMO_DISCLAIMER_LABEL


def render_question_bank_page():
    st.markdown("### 📦 Bank Soal Cerita Matematika Demonstrasi")
    st.caption("Koleksi 15 soal sintetis kelas IV SD dengan variasi karakteristik, kekuatan, dan kelemahan yang sengaja dirancang.")
    
    st.info(f"🏷️ **{DEMO_DISCLAIMER_LABEL}:** Soal-soal ini dirancang untuk demonstrasi fungsi analisis sistem dan belum divalidasi oleh ahli.")
    
    questions = get_all_questions()
    
    # Filter dan Pencarian
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        materi_list = sorted(list(set(q.get("materi", "") for q in questions if q.get("materi"))))
        selected_materi = st.selectbox("Filter Materi Matematika:", ["Semua Materi"] + materi_list)
    with col_f2:
        kualitas_list = sorted(list(set(q.get("tipe_kualitas", "") for q in questions if q.get("tipe_kualitas"))))
        selected_kualitas = st.selectbox("Filter Tipe / Kelemahan Soal:", ["Semua Tipe Kualitas"] + kualitas_list)
        
    filtered = questions
    if selected_materi != "Semua Materi":
        filtered = [q for q in filtered if q.get("materi") == selected_materi]
    if selected_kualitas != "Semua Tipe Kualitas":
        filtered = [q for q in filtered if q.get("tipe_kualitas") == selected_kualitas]
        
    st.markdown(f"Menampilkan **{len(filtered)}** soal:")
    
    for q in filtered:
        q_id = q.get("id")
        materi = q.get("materi")
        tipe = q.get("tipe_kualitas", "Umum")
        tantangan = q.get("tingkat_tantangan", "Sedang")
        
        with st.expander(f"📝 {q_id} — {materi} [{tipe}]", expanded=False):
            st.markdown(f"**Teks Soal Cerita:**")
            st.info(f"💬 \"{q.get('teks_soal')}\"")
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Tujuan Pembelajaran Sasaran:**\n> {q.get('tp_text')}")
                st.markdown(f"**Kunci Jawaban:** `{q.get('kunci_jawaban')}`")
                st.markdown(f"**Langkah Penyelesaian:**\n{q.get('langkah_penyelesaian')}")
                
            with c2:
                st.markdown(f"**Tingkat Tantangan Kognitif:** `{tantangan}`")
                st.markdown(f"**Karakteristik / Kelemahan Demonstrasi:**\n⚠️ {q.get('catatan_kelemahan_demo')}")
                st.markdown(f"**Saran Awal Perbaikan:**\n💡 {q.get('saran_perbaikan_demo')}")
                
                st.markdown("---")
                if st.button(f"🔍 Analisis Soal {q_id}", key=f"btn_analyze_{q_id}", use_container_width=True):
                    st.session_state["active_question_id"] = q_id
                    st.session_state["active_materi"] = materi
                    st.session_state["active_tp_text"] = q.get("tp_text")
                    st.session_state["active_question_text"] = q.get("teks_soal")
                    st.session_state["active_kunci_jawaban"] = q.get("kunci_jawaban", "")
                    st.session_state["active_langkah"] = q.get("langkah_penyelesaian", "")
                    st.session_state["nav_target"] = "Input dan Analisis Soal"
                    st.rerun()
