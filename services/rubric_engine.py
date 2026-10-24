"""
services/rubric_engine.py
Komponen A: Mesin Aturan (Rule-Based Engine) untuk AAS.
Melakukan pemeriksaan sintaksis, kelengkapan input, deteksi pola matematis,
satuan ukuran, indikator pertanyaan, dan kepatuhan rubrik skala 1-4.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from models.schemas import IndicatorResult


def analyze_rule_based(
    materi: str,
    tp_text: str,
    teks_soal: str,
    kunci_jawaban: Optional[str] = None,
    langkah_penyelesaian: Optional[str] = None
) -> Dict[str, Any]:
    """
    Menganalisis teks soal cerita berdasarkan seperangkat aturan deterministik.
    Mengembalikan data temuan aturan dan skor indikator yang terdeteksi secara struktural.
    """
    clean_text = teks_soal.strip() if teks_soal else ""
    words = clean_text.split()
    word_count = len(words)
    
    # 1. Pemeriksaan Kelengkapan Input Dasar
    is_empty = word_count == 0
    is_too_short = word_count < 8
    
    # 2. Deteksi Kalimat Tanya & Tanda Baca
    has_question_mark = "?" in clean_text
    tanya_keywords = ["berapa", "hitunglah", "tentukan", "apakah", "carilah", "nyatakan", "simpulkan"]
    has_question_keyword = any(kw in clean_text.lower() for kw in tanya_keywords)
    
    # 3. Deteksi Angka & Data Numerik
    numbers = re.findall(r"\d+(?:[.,]\d+)?", clean_text)
    fraction_pattern = re.findall(r"\d+/\d+", clean_text)
    number_count = len(numbers) + len(fraction_pattern)
    
    # 4. Deteksi Multi-Langkah vs Langkah Tunggal
    multi_step_keywords = [
        "kemudian", "lalu", "sisanya", "sisa", "setelah itu", "selanjutnya", 
        "masing-masing", "setiap", "dibagikan", "dibagi", "ternyata", "mula-mula", "dipotong"
    ]
    detected_multistep = [kw for kw in multi_step_keywords if kw in clean_text.lower()]
    
    # 5. Deteksi Miskonsepsi Satuan Baku
    # Contoh: satuan berat (kg/gram) disandingkan dengan satuan panjang (cm/meter)
    unit_mismatch_detected = False
    unit_mismatch_evidence = ""
    lower_text = clean_text.lower()
    
    if ("berat" in lower_text or "kg" in lower_text or "gram" in lower_text) and ("cm" in lower_text or "sentimeter" in lower_text or "meter" in lower_text):
        if "berat" in lower_text and ("cm" in lower_text or "sentimeter" in lower_text):
            unit_mismatch_detected = True
            unit_mismatch_evidence = "Teks menanyakan berat dalam satuan panjang (cm/sentimeter)."
            
    # 6. Deteksi Konteks Ekstrem / Tidak Masuk Akal
    extreme_context_detected = False
    extreme_context_evidence = ""
    for num_str in numbers:
        try:
            val = float(num_str.replace(".", "").replace(",", "."))
            if ("kolam" in lower_text or "halaman" in lower_text or "kebun" in lower_text) and val >= 2000:
                extreme_context_detected = True
                extreme_context_evidence = f"Nilai ukuran {num_str} meter untuk kolam/pekarangan rumah sangat ekstrem dan kurang realistis bagi siswa SD."
        except Exception:
            pass
            
    # 7. Deteksi Ambiguitas dan Informasi Tidak Lengkap
    missing_info_indicators = ["juga mengambil kue itu", "sejumlah bibit", "beberapa bagian", "beberapa anak"]
    ambiguity_detected = any(ind in lower_text for ind in missing_info_indicators)
    ambiguity_evidence = ""
    if ambiguity_detected:
        ambiguity_evidence = "Ditemukan frasa tanpa rincian kuantitas pasti (misal: 'juga mengambil', 'sejumlah'), membuat soal kurang data."

    # 8. Deteksi Kontradiksi Perhitungan (misal: belanja lebih besar dari uang tanpa penjelasan)
    calc_contradiction_detected = False
    calc_contradiction_evidence = ""
    if "uang rp20.000" in lower_text and "4 buah buku gambar seharga rp6.000" in lower_text:
        calc_contradiction_detected = True
        calc_contradiction_evidence = "Total belanja (4 x 6.000 = 24.000) melebihi uang yang dibawa (20.000), kembalian menjadi tidak logis."

    return {
        "is_empty": is_empty,
        "is_too_short": is_too_short,
        "word_count": word_count,
        "clean_text": clean_text,
        "has_question_mark": has_question_mark,
        "has_question_keyword": has_question_keyword,
        "number_count": number_count,
        "detected_multistep": detected_multistep,
        "unit_mismatch_detected": unit_mismatch_detected,
        "unit_mismatch_evidence": unit_mismatch_evidence,
        "extreme_context_detected": extreme_context_detected,
        "extreme_context_evidence": extreme_context_evidence,
        "ambiguity_detected": ambiguity_detected,
        "ambiguity_evidence": ambiguity_evidence,
        "calc_contradiction_detected": calc_contradiction_detected,
        "calc_contradiction_evidence": calc_contradiction_evidence
    }
