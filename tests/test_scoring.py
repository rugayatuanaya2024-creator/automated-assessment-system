"""
tests/test_scoring.py
Pengujian unit untuk modul scoring.py:
- Perhitungan formula skor dimensi
- Penanganan indikator tanpa bukti yang cukup (is_evaluable=False)
- Penanganan list indikator kosong
- Label kualitas soal
- Kalkulasi selisih delta antarsi
"""

import pytest
from models.schemas import IndicatorResult, DimensionResult
from services.scoring import calculate_dimension_score, get_quality_summary_label, compute_score_delta


def test_calculate_dimension_score_all_valid():
    """Menguji perhitungan skor ketika semua 4 indikator valid."""
    inds = [
        IndicatorResult("KK1", "KK-1", "Indikator 1", "keselarasan_kurikuler", 4, "Alasan 1", "Bukti 1", "Saran 1", True),
        IndicatorResult("KK2", "KK-2", "Indikator 2", "keselarasan_kurikuler", 3, "Alasan 2", "Bukti 2", "Saran 2", True),
        IndicatorResult("KK3", "KK-3", "Indikator 3", "keselarasan_kurikuler", 4, "Alasan 3", "Bukti 3", "Saran 3", True),
        IndicatorResult("KK4", "KK-4", "Indikator 4", "keselarasan_kurikuler", 3, "Alasan 4", "Bukti 4", "Saran 4", True),
    ]
    # Total skor: 4 + 3 + 4 + 3 = 14
    # Max possible: 4 * 4 = 16
    # Persentase: 14 / 16 * 100 = 87.5
    dim_res = calculate_dimension_score(inds, "keselarasan_kurikuler", "Keselarasan Kurikuler")
    assert dim_res.skor == 87.5
    assert dim_res.indikator_dievaluasi == 4
    assert dim_res.total_indikator == 4
    assert dim_res.kategori_label == "Memenuhi dengan Baik (Tinggi)"


def test_calculate_dimension_score_with_insufficient_evidence():
    """
    Menguji bahwa indikator 'Belum cukup bukti' (skor=None / is_evaluable=False)
    tidak dimasukkan ke pembagi sehingga tidak merugikan perhitungan.
    """
    inds = [
        IndicatorResult("KK1", "KK-1", "Indikator 1", "keselarasan_kurikuler", 3, "Alasan 1", "Bukti 1", "Saran 1", True),
        IndicatorResult("KK2", "KK-2", "Indikator 2", "keselarasan_kurikuler", 3, "Alasan 2", "Bukti 2", "Saran 2", True),
        IndicatorResult("KK3", "KK-3", "Indikator 3", "keselarasan_kurikuler", None, "Belum cukup bukti", "-", "Saran", False),
        IndicatorResult("KK4", "KK-4", "Indikator 4", "keselarasan_kurikuler", None, "Belum cukup bukti", "-", "Saran", False),
    ]
    # Total skor: 3 + 3 = 6
    # Indikator dinilai: 2
    # Max possible: 4 * 2 = 8
    # Persentase: 6 / 8 * 100 = 75.0
    dim_res = calculate_dimension_score(inds, "keselarasan_kurikuler", "Keselarasan Kurikuler")
    assert dim_res.skor == 75.0
    assert dim_res.indikator_dievaluasi == 2
    assert dim_res.total_indikator == 4


def test_calculate_dimension_score_empty_or_zero_evaluable():
    """Menguji penanganan ketika tidak ada indikator yang bisa dievaluasi."""
    inds = [
        IndicatorResult("KK1", "KK-1", "Indikator 1", "keselarasan_kurikuler", None, "Belum cukup bukti", "-", "-", False),
        IndicatorResult("KK2", "KK-2", "Indikator 2", "keselarasan_kurikuler", None, "Belum cukup bukti", "-", "-", False),
    ]
    dim_res = calculate_dimension_score(inds, "keselarasan_kurikuler", "Keselarasan Kurikuler")
    assert dim_res.skor == 0.0
    assert dim_res.indikator_dievaluasi == 0
    assert dim_res.kategori_label == "Belum Cukup Bukti"


def test_quality_summary_label():
    """Menguji pelabelan deskriptif kualitas soal."""
    lbl_high = get_quality_summary_label(85.0, 80.0, 90.0)
    assert "Sangat Baik" in lbl_high
    
    lbl_mid = get_quality_summary_label(60.0, 70.0, 65.0)
    assert "Cukup Baik" in lbl_mid
    
    lbl_low = get_quality_summary_label(45.0, 80.0, 75.0)
    assert "Perlu Perbaikan Signifikan" in lbl_low
    assert "Keselarasan Kurikuler" in lbl_low


def test_compute_score_delta():
    """Menguji penghitungan selisih skor antar versi."""
    v1 = {"keselarasan_kurikuler": 50.0, "tuntutan_kognitif": 40.0, "kesesuaian_bahasa": 60.0}
    v2 = {"keselarasan_kurikuler": 75.0, "tuntutan_kognitif": 70.0, "kesesuaian_bahasa": 85.0}
    deltas = compute_score_delta(v1, v2)
    assert deltas["keselarasan_kurikuler"]["diff"] == 25.0
    assert deltas["keselarasan_kurikuler"]["is_improved"] is True
    assert deltas["tuntutan_kognitif"]["diff"] == 30.0
    assert deltas["kesesuaian_bahasa"]["diff"] == 25.0
