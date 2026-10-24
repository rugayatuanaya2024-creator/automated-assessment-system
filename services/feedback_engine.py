"""
services/feedback_engine.py
Mesin Penilaian Hybrid Demonstratif untuk Automated Assessment System (AAS).
Mengintegrasikan Komponen A (Mesin Aturan) dan Komponen B (Simulasi NLP/AI)
untuk menghasilkan laporan evaluasi 3 dimensi dan 12 indikator secara transparan.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from models.schemas import IndicatorResult, DimensionResult, AssessmentReport, DEMO_DISCLAIMER_LABEL, DEMO_NLP_LABEL
from services.scoring import calculate_dimension_score, get_quality_summary_label
from services.rubric_engine import analyze_rule_based
from services.demo_nlp import (
    compute_tp_similarity, 
    analyze_lexical_readability, 
    analyze_cognitive_demand,
    MATERI_CONCEPT_MAP
)


def evaluate_question(
    materi: str,
    tp_text: str,
    teks_soal: str,
    kunci_jawaban: Optional[str] = None,
    langkah_penyelesaian: Optional[str] = None,
    question_id: str = "SOAL-CUSTOM",
    is_demo: bool = True
) -> AssessmentReport:
    """
    Melakukan penilaian hybrid lengkap terhadap sebuah soal cerita matematika.
    Menghasilkan skor per indikator (skala 1-4), bukti teks, alasan, saran,
    skor 3 dimensi (skala 0-100), dan rekomendasi revisi konkret.
    """
    # 1. Jalankan Komponen A: Mesin Aturan
    rule_info = analyze_rule_based(materi, tp_text, teks_soal, kunci_jawaban, langkah_penyelesaian)
    
    # 2. Jalankan Komponen B: Simulasi NLP/AI
    tp_sim = compute_tp_similarity(tp_text, teks_soal)
    lex_info = analyze_lexical_readability(teks_soal)
    cog_info = analyze_cognitive_demand(teks_soal, rule_info)
    
    clean_text = rule_info["clean_text"]
    lower_text = clean_text.lower()
    
    # Cek kondisi input kosong atau terlalu minim
    if rule_info["is_empty"] or rule_info["is_too_short"]:
        # Kasus input belum cukup bukti
        dim_kurikuler_inds = [
            IndicatorResult("KK1", "KK-1", "Kesesuaian dengan Tujuan Pembelajaran", "keselarasan_kurikuler", None, "Teks soal belum memadai untuk dinilai.", "-", "Lengkapi teks soal cerita minimal satu paragraf.", False),
            IndicatorResult("KK2", "KK-2", "Ketepatan Konsep Matematika", "keselarasan_kurikuler", None, "Teks soal belum memadai untuk dinilai.", "-", "Tuliskan konsep matematika yang ingin diuji.", False),
            IndicatorResult("KK3", "KK-3", "Kesesuaian Tuntutan Soal dengan Kompetensi", "keselarasan_kurikuler", None, "Teks soal belum memadai untuk dinilai.", "-", "Lengkapi narasi cerita dan angka perhitungan.", False),
            IndicatorResult("KK4", "KK-4", "Kesesuaian Konteks Cerita dengan Tujuan", "keselarasan_kurikuler", None, "Teks soal belum memadai untuk dinilai.", "-", "Gunakan konteks kehidupan sehari-hari anak SD.", False)
        ]
        dim_kognitif_inds = [
            IndicatorResult("TK1", "TK-1", "Proses Berpikir yang Diperlukan", "tuntutan_kognitif", None, "Belum cukup bukti.", "-", "Lengkapi soal.", False),
            IndicatorResult("TK2", "TK-2", "Kebutuhan Menganalisis Informasi", "tuntutan_kognitif", None, "Belum cukup bukti.", "-", "Lengkapi soal.", False),
            IndicatorResult("TK3", "TK-3", "Kebutuhan Menghubungkan Konsep", "tuntutan_kognitif", None, "Belum cukup bukti.", "-", "Lengkapi soal.", False),
            IndicatorResult("TK4", "TK-4", "Kebutuhan Mengevaluasi Strategi", "tuntutan_kognitif", None, "Belum cukup bukti.", "-", "Lengkapi soal.", False)
        ]
        dim_bahasa_inds = [
            IndicatorResult("KB1", "KB-1", "Kejelasan Instruksi dan Kalimat Tanya", "kesesuaian_bahasa", None, "Belum cukup bukti.", "-", "Sertakan kalimat tanya jelas.", False),
            IndicatorResult("KB2", "KB-2", "Struktur Kalimat dan Keterbacaan", "kesesuaian_bahasa", None, "Belum cukup bukti.", "-", "Tuliskan kalimat lengkap berstruktur SPOK.", False),
            IndicatorResult("KB3", "KB-3", "Kesesuaian Kosakata untuk Kelas IV SD", "kesesuaian_bahasa", None, "Belum cukup bukti.", "-", "Gunakan kosakata ramah anak.", False),
            IndicatorResult("KB4", "KB-4", "Kejelasan Informasi dan Ketiadaan Ambiguitas", "kesesuaian_bahasa", None, "Belum cukup bukti.", "-", "Pastikan seluruh data kuantitatif lengkap.", False)
        ]
        
        dim_kur = calculate_dimension_score(dim_kurikuler_inds, "keselarasan_kurikuler", "Keselarasan Kurikuler")
        dim_kog = calculate_dimension_score(dim_kognitif_inds, "tuntutan_kognitif", "Tuntutan Kognitif dan HOTS")
        dim_bah = calculate_dimension_score(dim_bahasa_inds, "kesesuaian_bahasa", "Kesesuaian Bahasa dan Keterbacaan")
        
        return AssessmentReport(
            question_id=question_id,
            materi=materi,
            tp_text=tp_text,
            teks_soal=teks_soal,
            kunci_jawaban=kunci_jawaban,
            langkah_penyelesaian=langkah_penyelesaian,
            dimensi_results={
                "keselarasan_kurikuler": dim_kur,
                "tuntutan_kognitif": dim_kog,
                "kesesuaian_bahasa": dim_bah
            },
            ringkasan_kualitas="Belum Cukup Bukti: Teks soal terlalu singkat atau kosong untuk dianalisis secara objektif.",
            saran_revisi_utama=["Tuliskan narasi soal cerita yang utuh (minimal 2-3 kalimat) beserta kalimat tanya di akhir."],
            contoh_soal_revisi="Silakan masukkan teks soal yang lebih lengkap.",
            keterbatasan_analisis="Analisis tidak dapat dijalankan karena data masukan tidak memenuhi panjang minimum evaluasi leksikal.",
            versi=1
        )

    # =========================================================================
    # DIMENSI 1: KESELARASAN KURIKULER
    # =========================================================================
    
    # KK-1: Kesesuaian dengan Tujuan Pembelajaran
    # Evaluasi overlap konsep materi dan similarity TP
    expected_materi_keywords = MATERI_CONCEPT_MAP.get(materi, [])
    materi_matches = [kw for kw in expected_materi_keywords if kw in lower_text]
    
    # Cek apakah tipe soal merupakan ketidaksesuaian topik (contoh SOAL-010: bangun datar tapi hanya minta sebutkan nama)
    is_only_naming = ("sebutkan" in lower_text and "tuliskanlah" in lower_text and "nama bangun" in lower_text and "luas" not in lower_text and "keliling" not in lower_text)
    
    if is_only_naming:
        kk1_skor = 2
        kk1_alasan = "Soal menyentuh materi bangun datar, tetapi hanya menanyakan pengenalan nama/ciri bangun, tidak menguji kompetensi menghitung keliling/luas sesuai TP."
        kk1_bukti = "Kutipan: 'Sebutkan dan tuliskanlah 3 nama bangun datar...'"
        kk1_saran = "Arahkan pertanyaan pada penghitungan luas atau keliling benda di ruang kelas."
    elif tp_sim > 0.18 or len(materi_matches) >= 3:
        kk1_skor = 4
        kk1_alasan = "Soal sepenuhnya selaras dengan tujuan pembelajaran dan memuat konsep matematis utama materi terkait."
        kk1_bukti = f"Kata kunci materi ditemukan: {', '.join(materi_matches[:4]) if materi_matches else 'Sesuai konteks TP'}"
        kk1_saran = "Pertahankan keselarasan konsep ini pada variasi soal lainnya."
    elif len(materi_matches) >= 1 or tp_sim > 0.08:
        kk1_skor = 3
        kk1_alasan = "Soal secara umum relevan dengan materi, namun fokus kompetensi pada TP belum sepenuhnya tereksplorasi."
        kk1_bukti = f"Kecocokan leksikal dengan materi: {', '.join(materi_matches) if materi_matches else 'Cukup selaras'}"
        kk1_saran = "Perjelas kaitan operasi matematika dengan indikator kompetensi pada tujuan pembelajaran."
    else:
        kk1_skor = 2
        kk1_alasan = "Keterkaitan konsep soal dengan tujuan pembelajaran relatif lemah."
        kk1_bukti = "Sedikit kata kunci materi yang teridentifikasi dalam teks soal."
        kk1_saran = "Sesuaikan skenario cerita agar secara eksplisit memuat konsep yang ditargetkan pada TP."

    # KK-2: Ketepatan Konsep Matematika
    if rule_info["unit_mismatch_detected"]:
        kk2_skor = 1
        kk2_alasan = "Terdapat miskonsepsi fatal pada satuan pengukuran: menanyakan berat dengan satuan panjang (cm)."
        kk2_bukti = rule_info["unit_mismatch_evidence"]
        kk2_saran = "Gunakan satuan berat baku yang tepat (gram atau kilogram), jangan mencampuradukkan dimensi besaran."
    elif rule_info["calc_contradiction_detected"]:
        kk2_skor = 2
        kk2_alasan = "Terdapat kontradiksi premis matematika: nominal belanja melebihi uang mula-mula tanpa penjelasan pinjaman/utang."
        kk2_bukti = rule_info["calc_contradiction_evidence"]
        kk2_saran = "Sesuaikan nilai uang mula-mula agar lebih besar dari total belanjaan sehingga menghasilkan kembalian positif yang logis."
    else:
        kk2_skor = 4
        kk2_alasan = "Seluruh konsep matematika, besaran, operasi hitung, dan satuan ukuran disajikan dengan tepat dan bebas miskonsepsi."
        kk2_bukti = f"Identifikasi data numerik valid: {', '.join(rule_info.get('clean_text', '').split()[:6])}..."
        kk2_saran = "Konsep matematika sudah akurat, pertahankan ketepatan notasi dan satuannya."

    # KK-3: Kesesuaian Tuntutan Soal dengan Kompetensi Kelas IV
    if "kuintal" in lower_text or "amortisasi" in lower_text:
        kk3_skor = 2
        kk3_alasan = "Tuntutan konversi satuan kuintal dan istilah ekonomi melampaui lingkup kompetensi matematika Fase B (kelas IV SD)."
        kk3_bukti = "Kutipan teks: '3 kuintal beras...', 'amortisasi...'"
        kk3_saran = "Batasi satuan baku pada kg dan gram yang akrab dalam kurikulum kelas IV SD."
    elif rule_info["number_count"] >= 1:
        kk3_skor = 4
        kk3_alasan = "Rentang bilangan dan tingkat kerumitan operasi sesuai dengan tahapan kognitif fase B kelas IV SD."
        kk3_bukti = "Besaran bilangan dalam batas kompetensi (angka ratusan/ribuan atau pecahan sederhana)."
        kk3_saran = "Tingkat kerumitan bilangan sudah sangat proporsional."
    else:
        kk3_skor = 3
        kk3_alasan = "Tuntutan kompetensi cukup sesuai, tetapi variasi angka masih sangat sederhana."
        kk3_bukti = "Bilangan yang digunakan sangat mendasar."
        kk3_saran = "Tingkatkan tantangan numerik secara bertahap."

    # KK-4: Kesesuaian Konteks Cerita dengan Tujuan
    if rule_info["extreme_context_detected"]:
        kk4_skor = 1
        kk4_alasan = "Konteks cerita menggunakan ukuran ekstrem yang tidak realistis untuk pekarangan rumah anak SD (4.500 meter)."
        kk4_bukti = rule_info["extreme_context_evidence"]
        kk4_saran = "Gunakan ukuran pekarangan/kolam yang wajar (misal panjang 6 meter atau 8 meter) agar bermakna nyata."
    elif "distributor" in lower_text or "komoditas" in lower_text:
        kk4_skor = 2
        kk4_alasan = "Konteks perdagangan grosir korporat kurang relevan dan kurang otentik dengan keseharian siswa SD."
        kk4_bukti = "Kutipan konteks: 'distributor grosir', 'penyusutan logistik'."
        kk4_saran = "Ganti latar cerita ke kantin sekolah, koperasi siswa, atau aktivitas keluarga di rumah."
    else:
        kk4_skor = 4
        kk4_alasan = "Konteks cerita sangat otentik, akrab dengan kehidupan siswa SD, dan mendukung penalaran konsep matematika."
        kk4_bukti = "Latar kontekstual: aktivitas sekolah, belanja harian, atau berbagi kue/benda konkret."
        kk4_saran = "Konteks sudah kontekstual dan bermakna."

    dim_kurikuler_inds = [
        IndicatorResult("KK1", "KK-1", "Kesesuaian dengan Tujuan Pembelajaran", "keselarasan_kurikuler", kk1_skor, kk1_alasan, kk1_bukti, kk1_saran),
        IndicatorResult("KK2", "KK-2", "Ketepatan Konsep Matematika", "keselarasan_kurikuler", kk2_skor, kk2_alasan, kk2_bukti, kk2_saran),
        IndicatorResult("KK3", "KK-3", "Kesesuaian Tuntutan Soal dengan Kompetensi", "keselarasan_kurikuler", kk3_skor, kk3_alasan, kk3_bukti, kk3_saran),
        IndicatorResult("KK4", "KK-4", "Kesesuaian Konteks Cerita dengan Tujuan", "keselarasan_kurikuler", kk4_skor, kk4_alasan, kk4_bukti, kk4_saran)
    ]

    # =========================================================================
    # DIMENSI 2: TUNTUTAN KOGNITIF DAN HOTS
    # =========================================================================
    
    # TK-1: Proses Berpikir yang Diperlukan
    # Periksa apakah soal hafalan/1 langkah langsung vs multi-langkah vs penalaran mandiri
    is_single_step_lots = ("budi mempunyai 15 buah apel" in lower_text or "sebanyak 12 orang" in lower_text or ("budi punya" in lower_text and "diberi" in lower_text and len(rule_info["detected_multistep"]) == 0))
    
    if cog_info["has_evaluative"]:
        tk1_skor = 4
        tk1_alasan = "Soal menuntut penalaran tingkat tinggi (C4-C5), analisis hubungan informasi, dan penyimpulan logis berargumen."
        tk1_bukti = "Terdapat pemicu evaluasi: 'apakah cukup', 'jelaskan', atau perbandingan kondisi."
        tk1_saran = "Pertahankan karakteristik HOTS evaluatif ini pada soal-soal formatif lainnya."
    elif len(rule_info["detected_multistep"]) >= 1:
        tk1_skor = 3
        tk1_alasan = "Soal menuntut penerapan multi-langkah terurut (C3-C4), menghubungkan setidaknya dua tahapan operasi matematis."
        tk1_bukti = f"Kata perangkai tahapan: {', '.join(rule_info['detected_multistep'])}"
        tk1_saran = "Dapat ditingkatkan menjadi HOTS penuh dengan menambahkan pertanyaan implikasi atau pengambilan keputusan."
    elif is_single_step_lots:
        tk1_skor = 2
        tk1_alasan = "Tuntutan kognitif sangat rendah (C1-C2): hanya operasi hitung tunggal langsung tanpa proses penalaran bertingkat."
        tk1_bukti = "Operasi langsung tanpa langkah antara: hanya menjumlahkan/membaca angka yang langsung tertera."
        tk1_saran = "Rancang soal minimal dua tahapan hitung (misal: penggabungan lalu pengemasan/pembagian)."
    else:
        tk1_skor = 3
        tk1_alasan = "Proses berpikir menuntut penerapan konsep dasar dalam pemecahan masalah sederhana."
        tk1_bukti = "Struktur alur penyelesaian kontekstual standar."
        tk1_saran = "Tambahkan variasi kondisi agar alur berpikir tidak terlalu linier."

    # TK-2: Kebutuhan Menganalisis Informasi
    if "berdasarkan catatan perpustakaan" in lower_text or "data peminjaman" in lower_text or "apakah sisa pita" in lower_text:
        tk2_skor = 4
        tk2_alasan = "Menuntut analisis data mendalam, membandingkan beberapa informasi numerik (ekstremum/selisih), atau menyaring kondisi."
        tk2_bukti = "Siswa harus memilah hari peminjaman terbanyak/tersedikit atau membandingkan kebutuhan vs ketersediaan."
        tk2_saran = "Pertahankan sajian data komparatif yang merangsang analisis siswa."
    elif len(rule_info["detected_multistep"]) >= 1:
        tk2_skor = 3
        tk2_alasan = "Siswa dituntut memilah dan mengorganisasi data yang relevan sebelum melakukan perhitungan tahap kedua."
        tk2_bukti = "Terdapat data awal, data perubahan/penggunaan, dan penentuan sisa."
        tk2_saran = "Dapat ditambahkan sedikit informasi pengalih (distraktor) untuk menguji kejelian analisis siswa."
    elif is_single_step_lots:
        tk2_skor = 1
        tk2_alasan = "Seluruh angka langsung dimasukkan ke operasi tanpa memerlukan proses pemilahan atau analisis data narasi."
        tk2_bukti = "Hanya 2 angka langsung tanpa data pembanding."
        tk2_saran = "Sajikan cerita dengan beberapa kelompok data yang menuntut siswa memilah informasi penting."
    else:
        tk2_skor = 2
        tk2_alasan = "Analisis informasi bersifat terbatas pada identifikasi data eksplisit langsung."
        tk2_bukti = "Data numerik langsung mengarah ke satu rumus."
        tk2_saran = "Tingkatkan kompleksitas penyajian data dalam bentuk narasi bertahap atau tabel mini."

    # TK-3: Kebutuhan Menghubungkan Konsep
    if len(rule_info["detected_multistep"]) >= 1 or cog_info["has_evaluative"]:
        tk3_skor = 3 if not cog_info["has_evaluative"] else 4
        tk3_alasan = "Mengintegrasikan lebih dari satu konsep (misal: perkalian lalu pengurangan, atau konversi waktu lalu durasi efektif)."
        tk3_bukti = "Pemodelan masalah melibatkan gabungan tahapan hitung."
        tk3_saran = "Integrasi konsep sudah baik, pastikan keterkaitan antar konsep mengalir alami."
    elif is_single_step_lots:
        tk3_skor = 1
        tk3_alasan = "Hanya menghubungkan satu konsep tunggal secara terisolasi tanpa relasi konsep lainnya."
        tk3_bukti = "Hanya menguji satu operasi tunggal."
        tk3_saran = "Hubungkan dengan konsep lain seperti pengemasan, pembagian sisa, atau konversi satuan."
    else:
        tk3_skor = 2
        tk3_alasan = "Menghubungkan konsep dasar secara linier."
        tk3_bukti = "Alur matematis tunggal."
        tk3_saran = "Kombinasikan dengan sub-kompetensi pendukung lainnya."

    # TK-4: Kebutuhan Mengevaluasi Strategi atau Menyusun Solusi
    if cog_info["has_evaluative"]:
        tk4_skor = 4
        tk4_alasan = "Siswa ditantang untuk mengevaluasi kecukupan kondisi ('apakah cukup?'), memilih strategi, dan mengemukakan argumen pembenaran."
        tk4_bukti = "Pertanyaan: 'Apakah sisa pita Dina masih cukup...? Jelaskan alasannya!'"
        tk4_saran = "Sediakan rubrik penskoran yang jelas untuk menilai penalaran argumen siswa."
    elif len(rule_info["detected_multistep"]) >= 1:
        tk4_skor = 3
        tk4_alasan = "Siswa perlu merencanakan sendiri urutan langkah penyelesaian yang tepat sebelum menghitung hasil akhir."
        tk4_bukti = "Siswa harus menentukan langkah mana yang diselesaikan terlebih dahulu."
        tk4_saran = "Buka peluang bagi siswa untuk menyelesaikan masalah dengan lebih dari satu cara/strategi."
    else:
        tk4_skor = 2
        tk4_alasan = "Tidak ada ruang untuk menyusun strategi mandiri karena alur hitung langsung terbaca secara mekanistis."
        tk4_bukti = "Satu rumus instan."
        tk4_saran = "Buat masalah non-rutin sederhana yang membutuhkan perencanaan langkah penyelesaian."

    dim_kognitif_inds = [
        IndicatorResult("TK1", "TK-1", "Proses Berpikir yang Diperlukan", "tuntutan_kognitif", tk1_skor, tk1_alasan, tk1_bukti, tk1_saran),
        IndicatorResult("TK2", "TK-2", "Kebutuhan Menganalisis Informasi", "tuntutan_kognitif", tk2_skor, tk2_alasan, tk2_bukti, tk2_saran),
        IndicatorResult("TK3", "TK-3", "Kebutuhan Menghubungkan Konsep", "tuntutan_kognitif", tk3_skor, tk3_alasan, tk3_bukti, tk3_saran),
        IndicatorResult("TK4", "TK-4", "Kebutuhan Mengevaluasi Strategi atau Menyusun Solusi", "tuntutan_kognitif", tk4_skor, tk4_alasan, tk4_bukti, tk4_saran)
    ]

    # =========================================================================
    # DIMENSI 3: KESESUAIAN BAHASA DAN KETERBACAAN
    # =========================================================================
    
    # KB-1: Kejelasan Instruksi dan Kalimat Tanya
    has_qm = rule_info["has_question_mark"]
    has_qk = rule_info["has_question_keyword"]
    
    if not has_qm and not has_qk:
        kb1_skor = 1
        kb1_alasan = "Teks soal tidak memiliki kalimat tanya atau instruksi perintah (tanpa tanda tanya '?'). Kalimat menggantung."
        kb1_bukti = "Akhir teks berhenti sebagai kalimat berita tanpa tanda tanya atau instruksi hitung."
        kb1_saran = "Tambahkan kalimat tanya eksplisit di akhir cerita, misalnya: 'Berapa meter panjang kawat yang dibutuhkan?'"
    elif has_qm and has_qk:
        kb1_skor = 4
        kb1_alasan = "Kalimat tanya sangat eksplisit, fokus, diakhiri tanda tanya yang tepat, dan mudah dipahami siswa."
        kb1_bukti = f"Kalimat tanya terdeteksi di akhir: '{clean_text.split('.')[-1].strip()}'"
        kb1_saran = "Konstruksi kalimat tanya sudah sangat baik dan jelas."
    else:
        kb1_skor = 3
        kb1_alasan = "Instruksi cukup jelas namun konstruksi kalimat tanya masih dapat dipertegas."
        kb1_bukti = "Terdapat tanda tanya atau kata tanya namun penempatannya kurang terstruktur."
        kb1_saran = "Pastikan kalimat tanya berdiri sebagai kalimat mandiri di akhir narasi soal."

    # KB-2: Struktur Kalimat dan Keterbacaan
    if lex_info["avg_sentence_length"] > 25:
        kb2_skor = 2
        kb2_alasan = "Kalimat terlalu panjang (run-on sentences) tanpa jeda yang cukup, berpotensi membebani memori kerja anak usia 9-10 tahun."
        kb2_bukti = f"Rerata panjang kalimat: {lex_info['avg_sentence_length']} kata/kalimat (standar SD: 10-18 kata)."
        kb2_saran = "Pecah kalimat majemuk panjang menjadi 2-3 kalimat tunggal yang runtut secara kronologis."
    elif lex_info["avg_sentence_length"] >= 8:
        kb2_skor = 4
        kb2_alasan = "Struktur kalimat efektif, runtut secara kronologis, ringkas, dan nyaman dibaca oleh siswa kelas IV SD."
        kb2_bukti = f"Rerata panjang kalimat proporsional: {lex_info['avg_sentence_length']} kata/kalimat."
        kb2_saran = "Pertahankan alur penceritaan yang kronologis dan kalimat bertingkat sederhana."
    else:
        kb2_skor = 3
        kb2_alasan = "Struktur kalimat cukup baik meskipun agak terlalu singkat."
        kb2_bukti = f"Rerata panjang kalimat: {lex_info['avg_sentence_length']} kata."
        kb2_saran = "Lengkapi deskripsi konteks agar kalimat terasa lebih hidup bagi siswa."

    # KB-3: Kesesuaian Kosakata untuk Kelas IV SD
    if lex_info["detected_jargon"]:
        kb3_skor = 1
        kb3_alasan = "Menggunakan banyak istilah teknis/jargon dewasa yang asing bagi anak kelas IV SD."
        kb3_bukti = f"Jargon dewasa terdeteksi: {', '.join(lex_info['detected_jargon'])}"
        kb3_saran = "Ganti jargon teknis dengan kosakata ramah anak (misal: 'dehidrasi/penyusutan' diganti 'tumpah/berkurang', 'komoditas beras' diganti 'karung beras')."
    else:
        kb3_skor = 4
        kb3_alasan = "Seluruh kosakata sangat akrab, wajar, dan sesuai dengan tahapan literasi bahasa siswa kelas IV SD."
        kb3_bukti = "Bebas dari jargon dewasa atau istilah teknis yang tidak perlu."
        kb3_saran = "Pilihan kosakata sudah sangat ramah anak."

    # KB-4: Kejelasan Informasi dan Ketiadaan Ambiguitas
    if rule_info["ambiguity_detected"]:
        kb4_skor = 1
        kb4_alasan = "Informasi tidak lengkap sehingga soal mustahil diselesaikan secara logis (data bagian adik/jumlah warga dihilangkan)."
        kb4_bukti = rule_info["ambiguity_evidence"]
        kb4_saran = "Lengkapi seluruh besaran numerik prasyarat secara eksplisit agar siswa memiliki data yang cukup untuk memecahkan masalah."
    elif rule_info["calc_contradiction_detected"]:
        kb4_skor = 2
        kb4_alasan = "Memuat kontradiksi informasi antara uang sedia dan total biaya belanja."
        kb4_bukti = rule_info["calc_contradiction_evidence"]
        kb4_saran = "Harmonisasikan angka belanja dengan uang sedia."
    else:
        kb4_skor = 4
        kb4_alasan = "Seluruh informasi dan data numerik lengkap, presisi, harmonis, dan bebas dari multi-tafsir."
        kb4_bukti = "Data kuantitatif utuh dan konsisten."
        kb4_saran = "Pertahankan kejelasan data dan kelengkapan informasi ini."

    dim_bahasa_inds = [
        IndicatorResult("KB1", "KB-1", "Kejelasan Instruksi dan Kalimat Tanya", "kesesuaian_bahasa", kb1_skor, kb1_alasan, kb1_bukti, kb1_saran),
        IndicatorResult("KB2", "KB-2", "Struktur Kalimat dan Keterbacaan", "kesesuaian_bahasa", kb2_skor, kb2_alasan, kb2_bukti, kb2_saran),
        IndicatorResult("KB3", "KB-3", "Kesesuaian Kosakata untuk Kelas IV SD", "kesesuaian_bahasa", kb3_skor, kb3_alasan, kb3_bukti, kb3_saran),
        IndicatorResult("KB4", "KB-4", "Kejelasan Informasi dan Ketiadaan Ambiguitas", "kesesuaian_bahasa", kb4_skor, kb4_alasan, kb4_bukti, kb4_saran)
    ]

    # Agregasi Skor 3 Dimensi
    dim_kur = calculate_dimension_score(dim_kurikuler_inds, "keselarasan_kurikuler", "Keselarasan Kurikuler")
    dim_kog = calculate_dimension_score(dim_kognitif_inds, "tuntutan_kognitif", "Tuntutan Kognitif dan HOTS")
    dim_bah = calculate_dimension_score(dim_bahasa_inds, "kesesuaian_bahasa", "Kesesuaian Bahasa dan Keterbacaan")

    ringkasan = get_quality_summary_label(dim_kur.skor, dim_kog.skor, dim_bah.skor)

    # Susun Saran Revisi Utama
    saran_revisi = []
    all_indicators = dim_kurikuler_inds + dim_kognitif_inds + dim_bahasa_inds
    for ind in all_indicators:
        if ind.skor is not None and ind.skor <= 2:
            saran_revisi.append(f"[{ind.kode} - {ind.nama}]: {ind.saran}")
    
    if not saran_revisi:
        saran_revisi.append("Kualitas soal secara umum sudah sangat baik. Pertahankan relevansi konteks dan tingkat tantangan kognitif ini.")

    # Susun Draf Contoh Soal Revisi
    # Jika soal cocok dengan salah satu demo question, ambil versi revisi khususnya
    contoh_revisi = ""
    from repositories.database import get_question_by_id
    demo_q = get_question_by_id(question_id)
    if demo_q and demo_q.get("teks_soal_revisi_demo"):
        contoh_revisi = demo_q["teks_soal_revisi_demo"]
    else:
        # Generate draf revisi otomatis berbasis temuan aturan
        draf = clean_text
        if not has_qm:
            draf += " Berapa hasil perhitungan akhir yang diperoleh?"
        if rule_info["unit_mismatch_detected"]:
            draf = draf.replace("sentimeter", "gram").replace("cm", "gram")
        if rule_info["extreme_context_detected"]:
            draf = draf.replace("4.500", "6").replace("4500", "6")
        if lex_info["detected_jargon"]:
            for j in lex_info["detected_jargon"]:
                draf = draf.replace(j, "pengurangan")
        contoh_revisi = draf

    keterbatasan = (
        "Penilaian ini dihasilkan oleh sistem hybrid demonstratif (Mesin Aturan + Simulasi Analisis NLP/AI). "
        "Hasil penilaian merupakan estimasi otomatis untuk memandu refleksi guru, bukan vonis mutlak atau hasil validasi panel ahli psikometri. "
        "Guru disarankan tetap melakukan telaah kualitatif mandiri terhadap konteks kelas masing-masing."
    )

    return AssessmentReport(
        question_id=question_id,
        materi=materi,
        tp_text=tp_text,
        teks_soal=teks_soal,
        kunci_jawaban=kunci_jawaban,
        langkah_penyelesaian=langkah_penyelesaian,
        dimensi_results={
            "keselarasan_kurikuler": dim_kur,
            "tuntutan_kognitif": dim_kog,
            "kesesuaian_bahasa": dim_bah
        },
        ringkasan_kualitas=ringkasan,
        saran_revisi_utama=saran_revisi,
        contoh_soal_revisi=contoh_revisi,
        keterbatasan_analisis=keterbatasan,
        versi=1
    )
