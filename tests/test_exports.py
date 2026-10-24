"""
tests/test_exports.py
Pengujian unit untuk integritas data demonstrasi dan ekspor:
- Verifikasi keberadaan dan struktur berkas JSON kurikulum (5 materi)
- Verifikasi struktur rubrik demonstratif (3 dimensi, 12 indikator)
- Verifikasi dataset simulasi penelitian (30 partisipan fiktif, rentang skor 0-100)
- Verifikasi pemisahan variabel literasi asesmen dan kualitas soal
"""

import pytest
import pandas as pd
from repositories.database import get_curriculum_data, get_rubric_data, get_research_data


def test_curriculum_data_integrity():
    """Menguji bahwa bank TP memuat 5 materi matematika kelas IV SD pokok."""
    curr = get_curriculum_data()
    assert len(curr) == 5
    materi_names = [c["materi"] for c in curr]
    assert "Bilangan Cacah dan Operasi Hitung" in materi_names
    assert "Pecahan Senilai dan Operasi Pecahan" in materi_names
    assert "Pengukuran (Panjang, Berat, dan Waktu)" in materi_names
    assert "Keliling dan Luas Bangun Datar" in materi_names
    assert "Data dan Penyajian Data" in materi_names
    
    for c in curr:
        assert "tujuan_pembelajaran" in c
        assert "konsep_matematika" in c
        assert len(c["indikator_ketercapaian"]) >= 2
        assert "contoh_soal" in c


def test_rubric_data_integrity():
    """Menguji bahwa rubrik memuat tepat 3 dimensi dan 12 indikator."""
    rubric = get_rubric_data()
    assert "dimensi" in rubric
    dims = rubric["dimensi"]
    assert len(dims) == 3
    
    total_indicators = sum(len(d["indikator"]) for d in dims)
    assert total_indicators == 12
    
    for d in dims:
        assert d["id"] in ["keselarasan_kurikuler", "tuntutan_kognitif", "kesesuaian_bahasa"]
        assert len(d["indikator"]) == 4
        for ind in d["indikator"]:
            assert set(ind["kriteria"].keys()) == {"1", "2", "3", "4"}


def test_research_data_integrity():
    """Menguji dataset sintetis pretest-posttest 30 guru fiktif."""
    df = get_research_data()
    assert not df.empty
    assert len(df) == 30
    
    # Verifikasi kolom-kolom pokok
    expected_cols = [
        "id_partisipan", "nama_guru", "sekolah", "kelas",
        "skor_pretest_literasi", "skor_posttest_literasi", "gain_literasi",
        "skor_pretest_kualitas_soal", "skor_posttest_kualitas_soal", "gain_kualitas_soal"
    ]
    for col in expected_cols:
        assert col in df.columns
        
    # Rentang skor valid 0 - 100
    assert (df["skor_pretest_literasi"] >= 0).all() and (df["skor_pretest_literasi"] <= 100).all()
    assert (df["skor_posttest_literasi"] >= 0).all() and (df["skor_posttest_literasi"] <= 100).all()
    assert (df["skor_pretest_kualitas_soal"] >= 0).all() and (df["skor_pretest_kualitas_soal"] <= 100).all()
    assert (df["skor_posttest_kualitas_soal"] >= 0).all() and (df["skor_posttest_kualitas_soal"] <= 100).all()
    
    # Verifikasi bahwa literasi dan kualitas soal memiliki skor yang bervariasi dan tidak identik
    assert not df["skor_pretest_literasi"].equals(df["skor_pretest_kualitas_soal"])
    assert df["gain_literasi"].std() > 0.5
    assert df["gain_kualitas_soal"].std() > 0.5
