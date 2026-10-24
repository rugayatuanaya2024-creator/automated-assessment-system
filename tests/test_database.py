"""
tests/test_database.py
Pengujian unit untuk lapisan repositori basis data SQLite:
- Inisialisasi tabel SQLite
- Seeding data demonstrasi otomatis
- Penyimpanan dan pemanggilan kembali butir soal
- Pembuatan dan pemanggilan versi revisi
- Penyimpanan profil guru
- Fungsi reset demonstrasi
"""

import pytest
import os
from repositories.database import (
    init_database,
    seed_demo_data,
    get_all_questions,
    get_question_by_id,
    save_question,
    save_analysis_result,
    get_all_analysis_results,
    get_analysis_by_question_id,
    get_teacher_profile,
    save_teacher_profile
)


def test_database_init_and_seed():
    """Menguji inisialisasi basis data dan seeding otomatis."""
    init_database()
    seed_demo_data(force_reset=True)
    
    questions = get_all_questions()
    # Harus memuat minimal 15 soal demo asli plus versi revisi demo
    assert len(questions) >= 15
    
    # Cek profil awal guru demonstrasi
    prof = get_teacher_profile()
    assert prof["nama_guru"] == "Guru Demonstrasi"
    assert prof["kode_partisipan"] == "DEMO-001"
    assert prof["sekolah"] == "SD Demonstrasi Nusantara"


def test_save_and_retrieve_question():
    """Menguji penyimpanan soal baru buatan pengguna."""
    test_q = {
        "id": "SOAL-UNIT-TEST",
        "materi": "Pecahan Senilai dan Operasi Pecahan",
        "tp_id": "TP-02",
        "tp_text": "Tujuan Pembelajaran Uji Unit",
        "teks_soal": "Sebuah pizza dipotong menjadi 6 bagian sama rata. Berapa sisa pizza jika 2 potong dimakan?",
        "kunci_jawaban": "4/6 bagian",
        "langkah_penyelesaian": "6/6 - 2/6 = 4/6",
        "tingkat_tantangan": "Sedang",
        "tipe_kualitas": "Uji Unit",
        "versi": 1,
        "is_demo": 0
    }
    save_question(test_q)
    
    retrieved = get_question_by_id("SOAL-UNIT-TEST")
    assert retrieved is not None
    assert retrieved["id"] == "SOAL-UNIT-TEST"
    assert "pizza dipotong" in retrieved["teks_soal"]
    assert retrieved["versi"] == 1


def test_revision_versioning_preserves_original():
    """Menguji bahwa pembuatan versi revisi tidak menimpa versi asli."""
    # Simpan versi 1
    orig_q = {
        "id": "SOAL-VERSI-ASLI",
        "materi": "Pengukuran",
        "tp_text": "TP Pengukuran",
        "teks_soal": "Soal versi asli sebelum revisi.",
        "versi": 1,
        "is_demo": 0
    }
    save_question(orig_q)
    
    # Simpan versi revisi (versi 2) dengan parent_id
    rev_q = {
        "id": "SOAL-VERSI-REVISI-1",
        "parent_id": "SOAL-VERSI-ASLI",
        "materi": "Pengukuran",
        "tp_text": "TP Pengukuran",
        "teks_soal": "Soal versi revisi yang disempurnakan.",
        "versi": 2,
        "is_demo": 0
    }
    save_question(rev_q)
    
    # Verifikasi kedua versi tetap ada
    q1 = get_question_by_id("SOAL-VERSI-ASLI")
    q2 = get_question_by_id("SOAL-VERSI-REVISI-1")
    
    assert q1 is not None
    assert q2 is not None
    assert q1["versi"] == 1
    assert q2["versi"] == 2
    assert q2["parent_id"] == "SOAL-VERSI-ASLI"
    assert q1["teks_soal"] == "Soal versi asli sebelum revisi."
    assert q2["teks_soal"] == "Soal versi revisi yang disempurnakan."


def test_update_teacher_profile():
    """Menguji pembaruan data profil guru fiktif."""
    save_teacher_profile({
        "nama_guru": "Ibu Siti Rahmawati S.Pd.",
        "kode_partisipan": "GURU-004",
        "sekolah": "SD Tunas Cendekia",
        "kelas": "IV B",
        "semester": "Genap",
        "mata_pelajaran": "Matematika"
    })
    
    prof = get_teacher_profile()
    assert prof["nama_guru"] == "Ibu Siti Rahmawati S.Pd."
    assert prof["kode_partisipan"] == "GURU-004"
    assert prof["sekolah"] == "SD Tunas Cendekia"
