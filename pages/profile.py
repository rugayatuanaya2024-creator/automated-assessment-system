"""
pages/profile.py
Halaman Profil Guru dan Pengaturan Demonstrasi untuk Automated Assessment System (AAS).
Memungkinkan guru mengubah profil fiktif dan menyediakan tombol reset data demo.
"""

import streamlit as st
from repositories.database import get_teacher_profile, save_teacher_profile, seed_demo_data
from components.ui_components import DEMO_DISCLAIMER_LABEL


def render_profile_page():
    st.markdown("### 👤 Profil Guru dan Pengaturan Demonstrasi")
    st.caption("Kelola data partisipan guru fiktif dan setelan lingkungan demonstrasi lokal.")
    
    profile = get_teacher_profile()
    
    st.info(
        f"🔒 **Catatan Demonstrasi & Privasi:** Seluruh identitas di bawah ini adalah data demonstrasi fiktif. "
        f"Aplikasi tidak mengumpulkan atau mengirim data pribadi ke internet. Seluruh data tersimpan secara lokal."
    )
    
    with st.form("form_profil_guru"):
        col1, col2 = st.columns(2)
        with col1:
            nama_guru = st.text_input("Nama Guru:", value=profile.get("nama_guru", "Guru Demonstrasi"))
            kode_partisipan = st.text_input("Kode Partisipan:", value=profile.get("kode_partisipan", "DEMO-001"))
            sekolah = st.text_input("Nama Sekolah:", value=profile.get("sekolah", "SD Demonstrasi Nusantara"))
        with col2:
            kelas = st.selectbox("Tingkat Kelas:", ["IV", "IV A", "IV B", "Kelas IV Fase B"], index=0)
            semester = st.selectbox("Semester:", ["Ganjil", "Genap"], index=0 if profile.get("semester") == "Ganjil" else 1)
            mapel = st.text_input("Mata Pelajaran:", value=profile.get("mata_pelajaran", "Matematika"), disabled=True)
            
        submitted = st.form_submit_button("💾 Simpan Perubahan Profil", use_container_width=True)
        if submitted:
            save_teacher_profile({
                "nama_guru": nama_guru,
                "kode_partisipan": kode_partisipan,
                "sekolah": sekolah,
                "kelas": kelas,
                "semester": semester,
                "mata_pelajaran": mapel
            })
            st.success("✅ Profil guru berhasil diperbarui!")
            st.rerun()

    st.markdown("---")
    
    # Pengaturan Reset Demonstrasi
    st.markdown("### 🔄 Pemulihan Data Demonstrasi (Reset Demo)")
    st.caption("Gunakan tombol di bawah ini untuk mengembalikan seluruh basis data demonstrasi ke kondisi awal pabrikan.")
    
    st.warning("⚠️ **Peringatan:** Reset Demo akan menghapus riwayat analisis dan soal revisi buatan pengguna, lalu mengisi ulang 15 bank soal demonstrasi awal.")
    
    col_reset1, col_reset2 = st.columns([1, 2])
    with col_reset1:
        if st.button("🚨 Reset Seluruh Data Demo", type="secondary", use_container_width=True):
            with st.spinner("Mengembalikan seluruh data demonstrasi ke kondisi awal..."):
                seed_demo_data(force_reset=True)
            st.success("✅ Data demonstrasi berhasil direset ke kondisi awal!")
            st.rerun()
    with col_reset2:
        st.caption("Tindakan ini aman dan memastikan seluruh 15 soal dan 4 simulasi revisi terisi kembali.")
