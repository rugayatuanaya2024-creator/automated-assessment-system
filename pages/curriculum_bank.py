"""
pages/curriculum_bank.py
Bank Tujuan Pembelajaran Demonstratif untuk Kelas IV SD pada Automated Assessment System (AAS).
Menyediakan bank TP untuk 5 materi pokok matematika disertai konsep inti dan contoh indikator ketercapaian.
"""

import streamlit as st
from repositories.database import get_curriculum_data


def render_curriculum_bank_page():
    st.markdown("### 🎯 Bank Tujuan Pembelajaran (TP) Demonstratif")
    st.caption("Pilihan acuan capaian pembelajaran matematika Fase B (Kelas IV SD).")
    
    st.warning("⚠️ **PERHATIAN:** TUJUAN PEMBELAJARAN DEMONSTRATIF, PERLU VERIFIKASI TERHADAP DOKUMEN KURIKULUM RESMI.")
    
    curriculum = get_curriculum_data()
    if not curriculum:
        st.error("Data kurikulum demonstrasi tidak ditemukan.")
        return

    # Filter Materi
    materi_list = [item["materi"] for item in curriculum]
    selected_materi_filter = st.selectbox("Pilih Lingkup Materi untuk Dilihat:", ["Semua Materi"] + materi_list)
    
    displayed_items = curriculum if selected_materi_filter == "Semua Materi" else [c for c in curriculum if c["materi"] == selected_materi_filter]
    
    for item in displayed_items:
        with st.expander(f"📌 {item['id']} — {item['materi']}", expanded=True):
            st.markdown(f"**Tujuan Pembelajaran:**\n> *\"{item['tujuan_pembelajaran']}\"*")
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Konsep Matematika Inti:**")
                st.write(item["konsep_matematika"])
                
                st.markdown("**Contoh Indikator Ketercapaian:**")
                for ind in item["indikator_ketercapaian"]:
                    st.markdown(f"- {ind}")
                    
            with c2:
                st.markdown("**Contoh Soal Cerita Relevan:**")
                st.info(f"💬 {item['contoh_soal']}")
                
                if st.button(f"🚀 Gunakan TP Ini untuk Analisis Soal", key=f"btn_use_{item['id']}"):
                    st.session_state["active_materi"] = item["materi"]
                    st.session_state["active_tp_text"] = item["tujuan_pembelajaran"]
                    st.session_state["active_question_text"] = item["contoh_soal"]
                    st.session_state["nav_target"] = "Input dan Analisis Soal"
                    st.success(f"Tujuan pembelajaran '{item['materi']}' telah dipilih! Silakan beralih ke menu 'Input dan Analisis Soal'.")
                    st.rerun()
