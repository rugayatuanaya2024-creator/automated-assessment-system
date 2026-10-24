
__pycache__/
*.py[cod]
*$py.class
.venv/
venv/
*.sqlite
.pytest_cache/
.DS_Store

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

[pytest]
pythonpath = .
testpaths = tests

# Automated Assessment System (AAS)
**Asisten Cerdas Guru dalam Merancang Soal Cerita Matematika Kelas IV SD**

> **Prototipe Demonstrasi untuk Penelitian Disertasi:**  
> *"Pengembangan Automated Assessment System Berbasis Kecerdasan Artifisial untuk Meningkatkan Literasi Asesmen Guru dan Kualitas Soal Cerita Matematika Kelas IV SD"*

---

## 📌 1. Gambaran Umum

Aplikasi **Automated Assessment System (AAS)** adalah perangkat lunak berbasis web lokal yang dirancang untuk membantu guru kelas IV SD (Fase B) dalam menganalisis, mengevaluasi, dan merevisi soal cerita matematika. 

Aplikasi ini menggunakan pendekatan **penilaian hybrid demonstratif**:
1. **Komponen A (Mesin Aturan / Rule-Based):** Memeriksa kelengkapan sintaksis, keberadaan tanda tanya, deteksi angka/satuan, konsistensi matematis, dan penghitungan skor rubrik.
2. **Komponen B (Simulasi NLP/AI):** Menganalisis kemiripan semantik soal dengan Tujuan Pembelajaran (TP), menganalisis keterbacaan leksikal ramah anak usia 9–10 tahun, mendeteksi jargon dewasa, serta mengestimasi kedalaman proses berpikir kognitif (LOTS vs HOTS).

### 🏷️ Catatan Penting & Etika Data
- Seluruh data awal (profil guru, bank soal, rubrik, tujuan pembelajaran, dan data penelitian 30 guru) dibuat secara **otomatis oleh sistem**.
- Berlabel resmi: **"DATA DEMONSTRASI, BUKAN DATA PENELITIAN NYATA"**.
- Analisis diberi label: **"SIMULASI ANALISIS NLP/AI"**. Penilaian ini merupakan alat bantu reflektif demonstratif, bukan vonis mutlak atau hasil pengujian empiris tervalidasi psikometri.
- **100% Berjalan Lokal:** Tidak membutuhkan API key eksternal, akun berbayar, atau koneksi internet.

---

## 🚀 2. Cara Cepat Menjalankan Aplikasi

Aplikasi telah disiapkan lengkap dengan lingkungan Python virtual environment (`.venv`) di dalam folder kerja.

### Cara 1: Menggunakan Tombol Batch (Paling Mudah)
Cukup **klik ganda (double-click)** pada berkas:
```text
run_app.bat
```
Jendela terminal akan terbuka otomatis dan menjalankan server Streamlit, lalu peramban (browser) akan otomatis membuka alamat:
```
http://localhost:8501
```

### Cara 2: Melalui Terminal / PowerShell
Buka PowerShell pada folder proyek ini, lalu jalankan:
```powershell
& ".\.venv\Scripts\streamlit.exe" run app.py
```

---

## 🧩 3. Fitur Utama Halaman Aplikasi

| Halaman | Deskripsi Fitur |
|---|---|
| **📊 Dashboard** | Ringkasan metrik total soal, soal direvisi, rata-rata skor 3 dimensi, grafik radar keseimbangan mutu, komparasi sebelum-sesudah revisi, dan log aktivitas analisis terbaru. |
| **👤 Profil & Pengaturan Demo** | Formulir profil guru fiktif (Guru Demonstrasi, DEMO-001, SD Demonstrasi Nusantara) dan tombol **Reset Demo** untuk mengembalikan seluruh data awal pabrikan kapan saja. |
| **🎯 Bank Tujuan Pembelajaran** | 5 materi matematika pokok kelas IV SD (Bilangan Cacah, Pecahan Senilai, Pengukuran, Bangun Datar, Data) lengkap dengan konsep inti, indikator ketercapaian, dan tombol kirim ke form analisis. |
| **📦 Bank Soal Demonstrasi** | 15 butir soal cerita matematika sintetis dengan variasi kelemahan yang sengaja dirancang (soal baik, kognitif rendah, ambigu, salah satuan, konteks ekstrem, jargon berlebih, dsb.). |
| **✍️ Input & Analisis Soal** | Formulir interaktif untuk menganalisis soal cerita apa pun. Menghasilkan laporan skor 3 dimensi terpisah (skala 0–100), tabel rincian 12 indikator rubrik (skala 1–4), bukti kutipan teks, alasan evaluasi, saran perbaikan, dan contoh draf perbaikan otomatis. |
| **🛠️ Fitur Revisi Soal** | Editor teks interaktif berdampingan (side-by-side) dengan soal asli. Memungkinkan guru mengedit, menganalisis ulang, dan menyimpan versi revisi tanpa menimpa soal asli. Dilengkapi tabel delta perubahan skor. |
| **🔬 Simulasi Penelitian Pre-Post** | Visualisasi demonstratif desain eksperimen disertasi dengan 30 guru fiktif. Membedakan secara tegas variabel **Literasi Asesmen Guru** dan **Kualitas Soal Cerita**, dilengkapi grafik sebaran, box plot, dan rata-rata gain. |
| **📂 Riwayat & Ekspor Data** | Penelusuran arsip evaluasi, fitur komparasi dua versi sembarang, unduh berkas CSV terpisah (bank soal, skor dimensi, skor 12 indikator, data penelitian), dan format pratinjau cetak ramah peramban. |

---

## 📐 4. Tiga Dimensi dan 12 Indikator Rubrik

Penilaian menggunakan rubrik demonstratif skala 1 sampai 4:
- `1 = Belum memenuhi`
- `2 = Perlu perbaikan besar`
- `3 = Cukup memenuhi`
- `4 = Memenuhi dengan baik`
- *(Atau "Belum cukup bukti" jika input terlalu minim/kosong)*

### Rumus Baku Perhitungan Skor Dimensi:
$$\text{Skor Dimensi} = \frac{\sum \text{Skor Indikator yang Dinilai}}{4 \times \text{Jumlah Indikator yang Dinilai}} \times 100$$

Ketiga dimensi disajikan secara terpisah tanpa pembobotan total semena-mena:
1. **Keselarasan Kurikuler:**
   - `KK-1`: Kesesuaian dengan Tujuan Pembelajaran
   - `KK-2`: Ketepatan Konsep Matematika
   - `KK-3`: Kesesuaian Tuntutan Soal dengan Kompetensi
   - `KK-4`: Kesesuaian Konteks Cerita dengan Tujuan
2. **Tuntutan Kognitif dan HOTS:**
   - `TK-1`: Proses Berpikir yang Diperlukan (C1–C5)
   - `TK-2`: Kebutuhan Menganalisis Informasi
   - `TK-3`: Kebutuhan Menghubungkan Konsep
   - `TK-4`: Kebutuhan Mengevaluasi Strategi atau Menyusun Solusi
3. **Kesesuaian Bahasa dan Keterbacaan:**
   - `KB-1`: Kejelasan Instruksi dan Kalimat Tanya
   - `KB-2`: Struktur Kalimat dan Keterbacaan
   - `KB-3`: Kesesuaian Kosakata untuk Siswa Kelas IV SD
   - `KB-4`: Kejelasan Informasi dan Ketiadaan Ambiguitas

---

## 🧪 5. Menjalankan Pengujian Otomatis (pytest)

Seluruh fungsi penting telah diuji menggunakan paket `pytest` otomatis (19 uji unit lulus 100%).

Untuk menjalankan kembali pengujian unit:
```powershell
& ".\.venv\Scripts\python.exe" -m pytest -v
```

Cakupan pengujian mencakup:
- Formula kalkulasi skor dimensi dan pembagian proporsional.
- Pengecualian indikator "Belum cukup bukti" dari denominator.
- Validasi input kosong dan masukan terlalu pendek.
- Deteksi anomali leksikal, satuan ukuran salah, dan konteks ekstrem.
- Penyimpanan dan versioning SQLite tanpa menimpa data asli.
- Pemutakhiran profil guru dan integritas ekspor dataset.

---

## 📁 6. Struktur Direktori Proyek

```text
RISET BU SITA/
├── app.py                     # Entry point aplikasi Streamlit
├── run_app.bat                # Skrip peluncur instan Windows
├── requirements.txt           # Daftar dependensi pustaka Python
├── pytest.ini                 # Konfigurasi pengujian pytest
├── README.md                  # Dokumentasi panduan operasional
├── aas_database.sqlite        # Basis data lokal SQLite otomatis
├── pages/                     # Modul antarmuka halaman
│   ├── dashboard.py           # Halaman ringkasan dashboard
│   ├── profile.py             # Halaman profil guru & reset demo
│   ├── curriculum_bank.py     # Halaman bank tujuan pembelajaran
│   ├── question_bank.py       # Halaman bank 15 soal demonstrasi
│   ├── analysis_page.py       # Halaman input & analisis hybrid
│   ├── revision_page.py       # Halaman editor revisi & komparasi
│   ├── research_simulation.py # Halaman simulasi pretest-posttest 30 guru
│   └── history_export.py      # Halaman riwayat & pusat unduh CSV
├── components/                # Komponen visual & grafik Plotly
│   └── ui_components.py       # Desain kartu, styling CSS, dan radar chart
├── services/                  # Logika bisnis & mesin penilaian
│   ├── scoring.py             # Formula perhitungan & agregasi skor
│   ├── rubric_engine.py       # Komponen A: Mesin aturan deterministik
│   ├── demo_nlp.py            # Komponen B: Simulasi NLP semantik & leksikal
│   └── feedback_engine.py     # Hybrid assessment engine
├── repositories/              # Akses basis data SQLite lokal
│   └── database.py            # CRUD soal, analisis, profil, dan auto-seeding
├── models/                    # Definisi model data & dataclass
│   └── schemas.py             # Schema laporan, indikator, dan profil
├── data/                      # Berkas data awal demonstratif otomatis
│   ├── demo_curriculum.json   # 5 materi & TP kelas IV SD
│   ├── demo_rubric.json       # Rubrik 3 dimensi & 12 indikator
│   ├── demo_questions.json    # 15 butir soal dengan variasi kelemahan
│   └── demo_research_data.csv # Data sintetis 30 partisipan penelitian
└── tests/                     # Berkas pengujian unit otomatis
    ├── test_scoring.py        # Pengujian perhitungan skor
    ├── test_engines.py        # Pengujian mesin aturan & simulasi NLP
    ├── test_database.py       # Pengujian operasi SQLite & versioning
    └── test_exports.py        # Pengujian integritas berkas data
```

---

## 💡 7. Keterbatasan Prototipe

Prototipe ini dikembangkan untuk keperluan demonstrasi akademik tahap awal disertasi:
- Penilaian pada aplikasi memanfaatkan mesin aturan lokal dan representasi leksikal/TF-IDF tanpa mengirim data ke model bahasa besar komersial daring.
- Nilai gain pada simulasi penelitian merupakan angka sintetis acak terkontrol (fixed seed) untuk mendemonstrasikan visualisasi data, bukan hasil empiris di lapangan.
- Revisi otomatis merupakan saran draf rekonstruksi, guru tetap memegang kendali pedagogis penuh dalam menyetujui atau menyunting butir soal.

streamlit>=1.30.0
pandas>=2.0.0
plotly>=5.18.0
pytest>=8.0.0
scikit-learn>=1.4.0
