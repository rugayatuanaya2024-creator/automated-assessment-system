"""
app.py
Aplikasi Utama: Automated Assessment System (AAS)
Asisten Cerdas Guru dalam Merancang Soal Cerita Matematika Kelas IV SD.
Prototipe Demonstrasi untuk Disertasi Doktoral.
Dilengkapi Navigasi Horizontal Atas dan Mode Alur Panduan Demonstrasi 3 Langkah.
"""

import streamlit as st
from repositories.database import seed_demo_data, init_database
from components.ui_components import render_header, DEMO_DISCLAIMER_LABEL

# Halaman-halaman aplikasi
from pages.guided_demo import render_guided_demo_page
from pages.dashboard import render_dashboard_page
from pages.profile import render_profile_page
from pages.curriculum_bank import render_curriculum_bank_page
from pages.question_bank import render_question_bank_page
from pages.analysis_page import render_analysis_page
from pages.revision_page import render_revision_page
from pages.research_simulation import render_research_simulation_page
from pages.history_export import render_history_export_page

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Automated Assessment System (AAS)",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="collapsed"  # Tutup sidebar secara default agar ruang layar luas dan fokus ke tab atas
)

# Inisialisasi Otomatis Data Demonstrasi Saat Pertama Kali Dibuka
if "initialized" not in st.session_state:
    init_database()
    seed_demo_data(force_reset=False)
    st.session_state["initialized"] = True

# Daftar Halaman Aplikasi
PAGES = {
    "🚀 Panduan Demonstrasi (3 Langkah)": render_guided_demo_page,
    "📊 Dashboard Utama": render_dashboard_page,
    "🎯 Bank Tujuan Pembelajaran": render_curriculum_bank_page,
    "📦 Bank Soal Demonstrasi": render_question_bank_page,
    "✍️ Input & Analisis Soal": render_analysis_page,
    "🛠️ Fitur Revisi Soal": render_revision_page,
    "🔬 Simulasi Riset Pre-Post": render_research_simulation_page,
    "📂 Riwayat & Ekspor Data": render_history_export_page,
    "👤 Profil & Reset": render_profile_page
}

# Sinkronisasi Navigasi Aktif
if "nav_target" not in st.session_state:
    st.session_state["nav_target"] = "🚀 Panduan Demonstrasi (3 Langkah)"

# Validasi target navigasi
page_keys = list(PAGES.keys())
if st.session_state["nav_target"] not in page_keys:
    # Coba pencocokan parsial kata kunci
    matched = next((k for k in page_keys if any(part in k for part in st.session_state["nav_target"].split())), "🚀 Panduan Demonstrasi (3 Langkah)")
    st.session_state["nav_target"] = matched

# Render Header Bersama
render_header()

# =============================================================================
# NAVIGASI HORIZONTAL ATAS (TAMPIL DI ATAS HALAMAN UTAMA)
# =============================================================================
current_idx = page_keys.index(st.session_state["nav_target"])

st.markdown("""
<style>
div[data-testid="stHorizontalBlock"] button {
    border-radius: 8px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# Menu Tab Horizontal Menggunakan Segmented Control / Radio Horizontal Modern
selected_page = st.radio(
    "Pilih Menu Navigasi:",
    page_keys,
    index=current_idx,
    horizontal=True,
    label_visibility="collapsed"
)

if selected_page != st.session_state["nav_target"]:
    st.session_state["nav_target"] = selected_page
    st.rerun()

st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

# Render Halaman yang Aktif
render_func = PAGES.get(st.session_state["nav_target"], render_guided_demo_page)
render_func()

# Sidebar Opsional (Hanya untuk Reset Cepat & Info Partisipan)
with st.sidebar:
    st.markdown("### ⚙️ Pengaturan Cepat")
    from repositories.database import get_teacher_profile
    profile = get_teacher_profile()
    st.markdown(f"**Partisipan:** {profile.get('nama_guru', 'Guru Demonstrasi')}")
    st.caption(f"{profile.get('sekolah', 'SDN Nusantara')} • {profile.get('kelas', 'Kelas IV')}")
    st.markdown("---")
    if st.button("🔄 Reset Seluruh Data Demo", use_container_width=True):
        seed_demo_data(force_reset=True)
        st.session_state["nav_target"] = "🚀 Panduan Demonstrasi (3 Langkah)"
        st.session_state["demo_step"] = 1
        st.success("Data demonstrasi dipulihkan!")
        st.rerun()
