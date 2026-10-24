"""
pages/guided_demo.py
Modul Alur Demonstrasi Praktis Terpandu (3 Langkah Mudah)
Dirancang khusus untuk memandu presentasi/sidang disertasi secara terstruktur,
interaktif, dan ringkas dalam satu alur visual yang mudah dipahami.
"""

import streamlit as st
import pandas as pd
from repositories.database import get_question_by_id, get_all_questions
from services.feedback_engine import evaluate_question
from services.scoring import compute_score_delta
from components.ui_components import create_comparison_chart, create_radar_chart, DEMO_DISCLAIMER_LABEL


# 4 Skenario Kasus Siap Presentasi
DEMO_SCENARIOS = {
    "kasus_lots": {
        "id": "SOAL-002",
        "judul": "Kasus 1: Soal Tuntutan Kognitif Terlalu Rendah (LOTS)",
        "icon": "🔻",
        "materi": "Bilangan Cacah dan Operasi Hitung",
        "masalah_utama": "Tuntutan kognitif C1/C2 (hanya 1 operasi penjumlahan langsung 15+10 tanpa proses analisis).",
        "teks_awal": "Budi mempunyai 15 buah apel di dalam keranjang. Ibu memberi Budi 10 buah apel lagi. Berapa jumlah seluruh buah apel yang dimiliki Budi sekarang?",
        "teks_revisi": "Budi memetik 145 buah apel dari kebun paman. Ibu juga memetik 175 buah apel. Seluruh apel tersebut digabungkan lalu disortir. Sebanyak 20 apel ternyata busuk dan disisihkan. Apel yang bagus dimasukkan sama rata ke dalam 5 keranjang. Berapa buah apel pada setiap keranjang?",
        "fokus_perbaikan": "Meningkatkan alur pemikiran dari 1 langkah menjadi 3 langkah terurut (penjumlahan, pengurangan sortir, pembagian wadah)."
    },
    "kasus_konsep": {
        "id": "SOAL-004",
        "judul": "Kasus 2: Soal Cacat Konsep Matematika (Salah Satuan)",
        "icon": "❌",
        "materi": "Pengukuran (Panjang, Berat, dan Waktu)",
        "masalah_utama": "Miskonsepsi besaran: menanyakan satuan berat (kg) dalam satuan panjang (cm).",
        "teks_awal": "Sebuah karung berisi beras seberat 8 kg. Beras tersebut dipindahkan secara merata ke dalam 4 kantong plastik kecil. Berapa sentimeter (cm) berat beras dalam setiap kantong plastik kecil?",
        "teks_revisi": "Sebuah karung berisi beras seberat 8 kg. Beras tersebut dimasukkan secara merata ke dalam 4 kantong plastik kecil. Berapa gram berat beras dalam setiap kantong plastik kecil?",
        "fokus_perbaikan": "Memperbaiki satuan panjang (cm) menjadi satuan berat baku (gram) dan menguji konversi metrik kg ke gram."
    },
    "kasus_ambigu": {
        "id": "SOAL-003",
        "judul": "Kasus 3: Soal Ambigu dan Informasi Tidak Lengkap",
        "icon": "❓",
        "materi": "Pecahan Senilai dan Operasi Pecahan",
        "masalah_utama": "Data bagian adik dihilangkan sehingga soal mustahil diselesaikan secara matematis.",
        "teks_awal": "Ibu memotong kue bolu untuk anak-anaknya. Kakak mengambil 2/4 bagian. Adik juga mengambil kue itu. Berapa sisa kue bolu ibu sekarang?",
        "teks_revisi": "Ibu memotong sebuah kue bolu menjadi 4 bagian yang sama besar. Kakak mengambil 2/4 bagian untuk camilan, sedangkan Adik mengambil 1/4 bagian. Berapa bagian sisa kue bolu Ibu yang masih tersisa di piring?",
        "fokus_perbaikan": "Melengkapi besaran bagian kue yang diambil adik (1/4 bagian) dan menegaskan ukuran kue utuh."
    },
    "kasus_jargon": {
        "id": "SOAL-009",
        "judul": "Kasus 4: Soal dengan Kosakata Rumit / Jargon Dewasa",
        "icon": "📖",
        "materi": "Pengukuran (Panjang, Berat, dan Waktu)",
        "masalah_utama": "Kosakata tidak ramah anak SD (fluktuasi komoditas, amortisasi penyusutan logistik).",
        "teks_awal": "Berdasarkan fluktuasi komoditas pangan grosir, seorang distributor mengangkut 3 kuintal beras medium dengan estimasi penyusutan logistik seberat 15.000 gram akibat faktor dehidrasi selama distribusi. Hitunglah neraca neto riil bobot komoditas beras tersebut dalam satuan kilogram!",
        "teks_revisi": "Sebuah toko beras menerima kiriman 3 karung besar beras seberat 300 kg. Saat diperiksa, sebanyak 15.000 gram beras tumpah karena salah satu karung robek kecil. Berapa kilogram sisa beras yang masih utuh di toko tersebut?",
        "fokus_perbaikan": "Mengubah jargon korporat menjadi narasi belanja sehari-hari yang ramah pemahaman anak kelas IV SD."
    }
}


def render_guided_demo_page():
    # Header Khusus Alur Panduan
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%); padding: 18px 24px; border-radius: 12px; color: white; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div>
                <h2 style="margin: 0; font-size: 22px; font-weight: 700;">🚀 Alur Panduan Demonstrasi Praktis (3 Langkah)</h2>
                <p style="margin: 4px 0 0 0; font-size: 14px; opacity: 0.9;">Gunakan alur ini untuk mendemonstrasikan cara kerja sistem secara terstruktur dan cepat saat presentasi.</p>
            </div>
            <span style="background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">MODE PRESENTASI</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Inisialisasi Step Wizard
    if "demo_step" not in st.session_state:
        st.session_state["demo_step"] = 1
    if "selected_scenario_key" not in st.session_state:
        st.session_state["selected_scenario_key"] = "kasus_lots"

    current_step = st.session_state["demo_step"]

    # Bar Indikator Visual 3 Langkah
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        if current_step == 1:
            st.markdown("🔵 **Langkah 1: Pilih Kasus Soal**")
        elif current_step > 1:
            st.markdown("✅ *Langkah 1: Kasus Dipilih*")
        else:
            st.markdown("⚪ Langkah 1: Pilih Kasus")
    with col_s2:
        if current_step == 2:
            st.markdown("🔵 **Langkah 2: Analisis Cerdas (Hybrid AI)**")
        elif current_step > 2:
            st.markdown("✅ *Langkah 2: Selesai Dianalisis*")
        else:
            st.markdown("⚪ Langkah 2: Analisis Cerdas")
    with col_s3:
        if current_step == 3:
            st.markdown("🔵 **Langkah 3: Transformasi Revisi & Peningkatan**")
        else:
            st.markdown("⚪ Langkah 3: Transformasi Revisi")

    st.markdown("---")

    # =========================================================================
    # LANGKAH 1: PILIH KASUS SOAL BERMASALAH
    # =========================================================================
    if current_step == 1:
        st.markdown("### 📌 Langkah 1: Pilih Contoh Kasus Butir Soal yang Bermasalah")
        st.caption("Pilih salah satu dari 4 kasus nyata yang mencerminkan tantangan guru SD dalam merancang soal cerita:")

        cols = st.columns(2)
        scenario_keys = list(DEMO_SCENARIOS.keys())
        for idx, s_key in enumerate(scenario_keys):
            sc = DEMO_SCENARIOS[s_key]
            with cols[idx % 2]:
                with st.container():
                    st.markdown(f"""
                    <div style="background: #FFFFFF; border: 2px solid {'#3B82F6' if st.session_state['selected_scenario_key'] == s_key else '#E2E8F0'}; border-radius: 10px; padding: 14px; margin-bottom: 12px;">
                        <div style="font-weight: 700; font-size: 15px; color: #1E293B; margin-bottom: 4px;">{sc['icon']} {sc['judul']}</div>
                        <div style="font-size: 12px; color: #2563EB; font-weight: 600; margin-bottom: 6px;">Materi: {sc['materi']}</div>
                        <div style="font-size: 12.5px; color: #475569; background: #F8FAFC; padding: 8px; border-radius: 6px; font-style: italic; margin-bottom: 8px;">"{sc['teks_awal']}"</div>
                        <div style="font-size: 12px; color: #DC2626; margin-bottom: 10px;">⚠️ <strong>Kelemahan:</strong> {sc['masalah_utama']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"👉 Pilih & Analisis Kasus Ini", key=f"btn_pilih_{s_key}", use_container_width=True):
                        st.session_state["selected_scenario_key"] = s_key
                        st.session_state["demo_step"] = 2
                        st.rerun()

    # =========================================================================
    # LANGKAH 2: MESIN ANALISIS CERDAS
    # =========================================================================
    elif current_step == 2:
        sc = DEMO_SCENARIOS[st.session_state["selected_scenario_key"]]
        st.markdown(f"### 🔍 Langkah 2: Hasil Pemeriksaan Mesin Analisis AAS terhadap {sc['icon']} {sc['id']}")
        st.caption(f"Kasus Terpilih: **{sc['judul']}**")

        # Evaluasi secara nyata
        report_v1 = evaluate_question(
            materi=sc["materi"],
            tp_text=f"Peserta didik dapat menyelesaikan masalah kontekstual pada materi {sc['materi']}",
            teks_soal=sc["teks_awal"],
            question_id=sc["id"],
            is_demo=True
        )

        col_left, col_right = st.columns([1, 1])
        with col_left:
            st.markdown("##### 📄 Teks Soal yang Dianalisis:")
            st.info(f"💬 \"{sc['teks_awal']}\"")
            st.markdown(f"**Temuan Kelemahan Soal:**")
            st.error(f"⚠️ {sc['masalah_utama']}")

        with col_right:
            st.markdown("##### 🎯 Skor 3 Dimensi Hasil Evaluasi:")
            
            # Kartu Mini 3 Dimensi
            c_m1, c_m2, c_m3 = st.columns(3)
            with c_m1:
                st.metric("Keselarasan", f"{report_v1.skor_kurikuler:.0f}/100")
            with c_m2:
                st.metric("Tuntutan HOTS", f"{report_v1.skor_kognitif:.0f}/100")
            with c_m3:
                st.metric("Bahasa", f"{report_v1.skor_bahasa:.0f}/100")

            st.markdown("##### 💡 Rekomendasi Perbaikan Sistem:")
            for s in report_v1.saran_revisi_utama[:2]:
                st.warning(f"• {s}")

        st.markdown("---")
        col_nav1, col_nav2 = st.columns([1, 1])
        with col_nav1:
            if st.button("⬅️ Kembali Pilih Kasus Lain", use_container_width=True):
                st.session_state["demo_step"] = 1
                st.rerun()
        with col_nav2:
            if st.button("🚀 Lanjut ke Langkah 3: Eksekusi Revisi & Lihat Peningkatan", type="primary", use_container_width=True):
                st.session_state["demo_step"] = 3
                st.rerun()

    # =========================================================================
    # LANGKAH 3: TRANSFORMASI REVISI DAN BUKTI PENINGKATAN
    # =========================================================================
    elif current_step == 3:
        sc = DEMO_SCENARIOS[st.session_state["selected_scenario_key"]]
        st.markdown(f"### ✨ Langkah 3: Transformasi Revisi & Bukti Peningkatan Mutu Soal")
        st.caption(f"Hasil Perbaikan untuk: **{sc['judul']}**")

        # Analisis naskah awal dan naskah revisi secara nyata
        report_v1 = evaluate_question(sc["materi"], "TP Sasaran", sc["teks_awal"], question_id=sc["id"])
        report_v2 = evaluate_question(sc["materi"], "TP Sasaran", sc["teks_revisi"], question_id=sc["id"] + "-REV")

        v1_scores = {"keselarasan_kurikuler": report_v1.skor_kurikuler, "tuntutan_kognitif": report_v1.skor_kognitif, "kesesuaian_bahasa": report_v1.skor_bahasa}
        v2_scores = {"keselarasan_kurikuler": report_v2.skor_kurikuler, "tuntutan_kognitif": report_v2.skor_kognitif, "kesesuaian_bahasa": report_v2.skor_bahasa}
        deltas = compute_score_delta(v1_scores, v2_scores)

        # Baris Metrik Peningkatan Delta
        c_d1, c_d2, c_d3 = st.columns(3)
        with c_d1:
            st.metric("Keselarasan Kurikuler", f"{v2_scores['keselarasan_kurikuler']:.1f}", delta=f"{deltas['keselarasan_kurikuler']['status_text']} poin")
        with c_d2:
            st.metric("Tuntutan Kognitif / HOTS", f"{v2_scores['tuntutan_kognitif']:.1f}", delta=f"{deltas['tuntutan_kognitif']['status_text']} poin")
        with c_d3:
            st.metric("Kesesuaian Bahasa", f"{v2_scores['kesesuaian_bahasa']:.1f}", delta=f"{deltas['kesesuaian_bahasa']['status_text']} poin")

        st.markdown("---")

        # Perbandingan Berdampingan Naskah Asli vs Naskah Revisi
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            st.markdown("#### ❌ Naskah Soal Sebelum Revisi (Versi 1)")
            st.error(f"💬 \"{sc['teks_awal']}\"")
            st.caption(f"Catatan: {sc['masalah_utama']}")

        with col_v2:
            st.markdown("#### ✅ Naskah Soal Sesudah Revisi (Versi 2 Disempurnakan)")
            st.success(f"💬 \"{sc['teks_revisi']}\"")
            st.caption(f"Transformasi: {sc['fokus_perbaikan']}")

        # Grafik Komparasi Batang
        st.markdown("##### 📊 Visualisasi Perubahan Skor Mutu:")
        fig_cmp = create_comparison_chart(v1_scores, v2_scores, "Sebelum Revisi (v1)", "Setelah Revisi (v2)")
        st.plotly_chart(fig_cmp, use_container_width=True)

        st.success(
            "🎉 **Kesimpulan Demonstrasi Disertasi:** "
            "Sistem AAS berhasil memandu guru mengidentifikasi kelemahan spesifik pada butir soal cerita matematika SD, "
            "memberikan saran pedagogis konkret, dan mendokumentasikan peningkatan kualitas soal secara transparan."
        )

        col_end1, col_end2 = st.columns(2)
        with col_end1:
            if st.button("🔄 Coba Demonstrasi Kasus Lain", use_container_width=True):
                st.session_state["demo_step"] = 1
                st.rerun()
        with col_end2:
            if st.button("✍️ Beralih ke Menu Analisis Soal Bebas", type="primary", use_container_width=True):
                st.session_state["nav_target"] = "✍️ Analisis Soal"
                st.rerun()
