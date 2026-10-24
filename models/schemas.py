"""
models/schemas.py
Definisi skema data dan tipe model untuk Automated Assessment System (AAS).
Semua data demonstrasi diberi penanda jelas.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime

DEMO_DISCLAIMER_LABEL = "DATA DEMONSTRASI, BUKAN DATA PENELITIAN NYATA"
DEMO_NLP_LABEL = "SIMULASI ANALISIS NLP/AI"


@dataclass
class TeacherProfile:
    nama_guru: str = "Guru Demonstrasi"
    kode_partisipan: str = "DEMO-001"
    sekolah: str = "SD Demonstrasi Nusantara"
    kelas: str = "IV (Fase B)"
    semester: str = "Ganjil"
    mata_pelajaran: str = "Matematika"
    catatan: str = DEMO_DISCLAIMER_LABEL

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class IndicatorResult:
    id: str  # misal 'KK1'
    kode: str  # misal 'KK-1'
    nama: str  # 'Kesesuaian dengan Tujuan Pembelajaran'
    dimensi_id: str  # 'keselarasan_kurikuler'
    skor: Optional[int]  # 1-4 atau None bila tidak cukup bukti
    alasan: str
    bukti_teks: str
    saran: str
    is_evaluable: bool = True  # False jika "Belum cukup bukti"

    @property
    def skor_display(self) -> str:
        if self.skor is None or not self.is_evaluable:
            return "Belum cukup bukti"
        return f"{self.skor} / 4"


@dataclass
class DimensionResult:
    id: str
    nama: str
    skor: float  # 0 - 100
    indikator_results: List[IndicatorResult] = field(default_factory=list)
    indikator_dievaluasi: int = 0
    total_indikator: int = 4

    @property
    def kategori_label(self) -> str:
        if self.skor >= 75.0:
            return "Memenuhi dengan Baik (Tinggi)"
        elif self.skor >= 50.0:
            return "Cukup Memenuhi (Sedang)"
        elif self.skor > 0.0:
            return "Perlu Perbaikan (Rendah)"
        return "Belum Cukup Bukti"

    @property
    def warna_badge(self) -> str:
        if self.skor >= 75.0:
            return "#10B981"  # Emerald green
        elif self.skor >= 50.0:
            return "#F59E0B"  # Amber yellow
        return "#EF4444"  # Red


@dataclass
class AssessmentReport:
    question_id: str
    materi: str
    tp_text: str
    teks_soal: str
    kunci_jawaban: Optional[str]
    langkah_penyelesaian: Optional[str]
    dimensi_results: Dict[str, DimensionResult]
    ringkasan_kualitas: str
    saran_revisi_utama: List[str]
    contoh_soal_revisi: str
    keterbatasan_analisis: str
    waktu_analisis: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    versi: int = 1
    label_status: str = DEMO_DISCLAIMER_LABEL

    @property
    def skor_kurikuler(self) -> float:
        return self.dimensi_results.get("keselarasan_kurikuler", DimensionResult("keselarasan_kurikuler", "Keselarasan Kurikuler", 0.0)).skor

    @property
    def skor_kognitif(self) -> float:
        return self.dimensi_results.get("tuntutan_kognitif", DimensionResult("tuntutan_kognitif", "Tuntutan Kognitif dan HOTS", 0.0)).skor

    @property
    def skor_bahasa(self) -> float:
        return self.dimensi_results.get("kesesuaian_bahasa", DimensionResult("kesesuaian_bahasa", "Kesesuaian Bahasa dan Keterbacaan", 0.0)).skor


@dataclass
class QuestionItem:
    id: str
    materi: str
    tp_id: str
    tp_text: str
    teks_soal: str
    kunci_jawaban: str
    langkah_penyelesaian: str
    tingkat_tantangan: str
    tipe_kualitas: str
    catatan_kelemahan_demo: str
    saran_perbaikan_demo: str
    teks_soal_revisi_demo: str
    versi: int = 1
    parent_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    is_demo: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
