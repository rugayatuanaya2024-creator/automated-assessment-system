"""
tests/test_engines.py
Pengujian unit untuk Mesin Aturan, Simulasi NLP, dan Feedback Engine:
- Validasi penanganan input kosong atau terlalu pendek
- Deteksi anomali satuan (miskonsepsi konsep matematika)
- Deteksi ketiadaan tanda tanya / kalimat instruksi
- Deteksi konteks ekstrem tidak realistis
- Evaluasi hybrid lengkap terhadap butir soal
"""

import pytest
from services.rubric_engine import analyze_rule_based
from services.demo_nlp import compute_tp_similarity, analyze_lexical_readability, analyze_cognitive_demand
from services.feedback_engine import evaluate_question


def test_rule_based_empty_and_short_input():
    """Menguji bahwa input kosong atau terlalu pendek terdeteksi dengan tepat."""
    res_empty = analyze_rule_based("Bilangan Cacah", "TP", "")
    assert res_empty["is_empty"] is True
    assert res_empty["word_count"] == 0

    res_short = analyze_rule_based("Bilangan Cacah", "TP", "Budi punya tiga apel.")
    assert res_short["is_too_short"] is True


def test_rule_based_unit_mismatch_detection():
    """Menguji deteksi miskonsepsi ketika berat dinyatakan dalam cm."""
    text_error = "Sebuah karung berisi beras seberat 8 kg. Berapa sentimeter (cm) berat tiap kantong?"
    res = analyze_rule_based("Pengukuran", "TP", text_error)
    assert res["unit_mismatch_detected"] is True
    assert "sentimeter" in res["unit_mismatch_evidence"].lower()


def test_rule_based_missing_question_mark():
    """Menguji deteksi soal yang menggantung tanpa tanda tanya."""
    text_hanging = "Kebun sayur kakek berbentuk persegi panjang berukuran 15 meter dan 10 meter."
    res = analyze_rule_based("Bangun Datar", "TP", text_hanging)
    assert res["has_question_mark"] is False
    assert res["has_question_keyword"] is False


def test_rule_based_extreme_context():
    """Menguji deteksi ukuran ekstrem kolam pekarangan ribuan meter."""
    text_extreme = "Pak Budi membuat kolam ikan lele persegi dengan panjang sisi 4.500 meter. Berapa kelilingnya?"
    res = analyze_rule_based("Bangun Datar", "TP", text_extreme)
    assert res["extreme_context_detected"] is True


def test_demo_nlp_readability_jargon():
    """Menguji deteksi istilah dewasa/jargon ekonomi yang kurang ramah untuk kelas IV SD."""
    text_jargon = "Distributor mengangkut beras dengan faktor amortisasi dehidrasi fluktuasi komoditas."
    lex = analyze_lexical_readability(text_jargon)
    assert len(lex["detected_jargon"]) >= 3
    assert "Kurang Sesuai" in lex["readability_status"]


def test_feedback_engine_empty_input_handling():
    """Menguji bahwa input kosong menghasilkan status 'Belum Cukup Bukti' tanpa error."""
    report = evaluate_question("Bilangan Cacah", "TP", "", question_id="EMPTY-TEST")
    assert "Belum Cukup Bukti" in report.ringkasan_kualitas
    assert report.skor_kurikuler == 0.0
    assert report.skor_kognitif == 0.0
    assert report.skor_bahasa == 0.0
    # Seluruh indikator harus is_evaluable=False
    for dim_res in report.dimensi_results.values():
        for ind in dim_res.indikator_results:
            assert ind.is_evaluable is False
            assert ind.skor_display == "Belum cukup bukti"


def test_feedback_engine_valid_question():
    """Menguji penilaian hybrid lengkap terhadap soal multi-langkah yang baik."""
    good_text = (
        "Koperasi SD Nusantara membeli 12 kotak pensil. Setiap kotak berisi 24 pensil. "
        "Sebanyak 150 pensil dibagikan kepada siswa berprestasi. Berapa batang sisa pensil yang masih ada di koperasi?"
    )
    report = evaluate_question(
        materi="Bilangan Cacah dan Operasi Hitung",
        tp_text="Peserta didik dapat menyelesaikan masalah kontekstual dua langkah...",
        teks_soal=good_text,
        question_id="TEST-001"
    )
    assert report.skor_kurikuler >= 75.0
    assert report.skor_kognitif >= 60.0
    assert report.skor_bahasa >= 75.0
    assert len(report.dimensi_results) == 3
    assert len(report.saran_revisi_utama) >= 1
    assert report.contoh_soal_revisi != ""
