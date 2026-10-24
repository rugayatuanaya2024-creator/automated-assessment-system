"""
services/scoring.py
Modul perhitungan skor dan agregasi dimensi sesuai rubrik skala 1-4.
Rumus baku:
Skor dimensi = (jumlah skor indikator dinilai) / (4 * jumlah indikator dinilai) * 100.
Menangani kondisi 'Belum cukup bukti' secara transparan tanpa memaksakan skor.
"""

from typing import List, Dict, Any, Tuple, Optional
from models.schemas import IndicatorResult, DimensionResult


def calculate_dimension_score(indikator_results: List[IndicatorResult], dimensi_id: str, dimensi_nama: str) -> DimensionResult:
    """
    Menghitung skor satu dimensi berdasarkan daftar hasil indikator.
    Jika ada indikator dengan is_evaluable=False atau skor=None, indikator tersebut
    dikecualikan dari perhitungan dan tidak membebani pembagi (denominator).
    """
    evaluable_indicators = [
        ind for ind in indikator_results 
        if ind.is_evaluable and ind.skor is not None
    ]
    
    total_evaluated = len(evaluable_indicators)
    total_indicators = len(indikator_results)
    
    if total_evaluated == 0:
        return DimensionResult(
            id=dimensi_id,
            nama=dimensi_nama,
            skor=0.0,
            indikator_results=indikator_results,
            indikator_dievaluasi=0,
            total_indikator=total_indicators
        )
    
    sum_scores = sum(ind.skor for ind in evaluable_indicators)
    max_possible = 4.0 * total_evaluated
    percentage_score = (sum_scores / max_possible) * 100.0
    percentage_score = round(min(100.0, max(0.0, percentage_score)), 1)
    
    return DimensionResult(
        id=dimensi_id,
        nama=dimensi_nama,
        skor=percentage_score,
        indikator_results=indikator_results,
        indikator_dievaluasi=total_evaluated,
        total_indikator=total_indicators
    )


def get_quality_summary_label(skor_kurikuler: float, skor_kognitif: float, skor_bahasa: float) -> str:
    """
    Menghasilkan ringkasan deskriptif kualitas soal tanpa memadukan ketiga dimensi
    menjadi skor tunggal yang semena-mena.
    """
    scores = [skor_kurikuler, skor_kognitif, skor_bahasa]
    min_score = min(scores)
    avg_score = sum(scores) / 3.0
    
    if min_score >= 75.0:
        return "Sangat Baik: Selaras kurikulum, berpotensi HOTS, dan konstruksi bahasa efektif."
    elif min_score >= 50.0 and avg_score >= 65.0:
        return "Cukup Baik: Soal dapat digunakan, namun memerlukan penyempurnaan pada dimensi tertentu."
    elif any(s < 50.0 for s in scores):
        weak_dims = []
        if skor_kurikuler < 50.0:
            weak_dims.append("Keselarasan Kurikuler")
        if skor_kognitif < 50.0:
            weak_dims.append("Tuntutan Kognitif")
        if skor_bahasa < 50.0:
            weak_dims.append("Kesesuaian Bahasa")
        return f"Perlu Perbaikan Signifikan: Terdapat catatan kritis pada aspek {', '.join(weak_dims)}."
    return "Perlu Review Ulang: Data teks belum memadai untuk kesimpulan komprehensif."


def compute_score_delta(v1_scores: Dict[str, float], v2_scores: Dict[str, float]) -> Dict[str, Dict[str, Any]]:
    """
    Menghitung selisih (delta) skor antara dua versi soal.
    """
    deltas = {}
    for dim_key in ["keselarasan_kurikuler", "tuntutan_kognitif", "kesesuaian_bahasa"]:
        s1 = v1_scores.get(dim_key, 0.0)
        s2 = v2_scores.get(dim_key, 0.0)
        diff = round(s2 - s1, 1)
        deltas[dim_key] = {
            "v1": s1,
            "v2": s2,
            "diff": diff,
            "is_improved": diff > 0,
            "status_text": f"+{diff}" if diff > 0 else f"{diff}"
        }
    return deltas
