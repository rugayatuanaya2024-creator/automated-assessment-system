"""
services/demo_nlp.py
Komponen B: Simulasi Analisis NLP/AI untuk Automated Assessment System.
Melakukan pemrosesan teks, estimasi keselarasan leksikal/konseptual dengan TP,
analisis kompleksitas kosakata anak SD, dan penalaran semantik kontekstual.
Diberi label eksplisit: [SIMULASI ANALISIS NLP/AI].
"""

import re
from typing import Dict, Any, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Daftar kata berkarakter jargon/istilah dewasa yang kurang ramah untuk siswa kelas IV SD (usia 9-10 tahun)
ADULT_JARGON_WORDS = [
    "fluktuasi", "komoditas", "distributor", "amortisasi", "dehidrasi", 
    "neto", "bruto", "tara", "kuintal", "inflasi", "logistik", "penyusutan",
    "akselerasi", "rekapitulasi", "spesifikasi", "diversifikasi", "estimasi"
]

# Kata kunci operasi/konsep per materi untuk evaluasi kecocokan kurikuler
MATERI_CONCEPT_MAP = {
    "Bilangan Cacah dan Operasi Hitung": [
        "tambah", "kurang", "kali", "bagi", "pensil", "buku", "apel", "koperasi", 
        "butir", "keranjang", "kotak", "kantong", "sisa", "jumlah", "seluruh"
    ],
    "Pecahan Senilai dan Operasi Pecahan": [
        "pecahan", "senilai", "potong", "bagian", "loyang", "pizza", "kue", "martabak", 
        "pita", "setengah", "per", "/", "seperempat"
    ],
    "Pengukuran (Panjang, Berat, dan Waktu)": [
        "meter", "sentimeter", "cm", "m", "kg", "gram", "jam", "menit", "detik", 
        "durasi", "waktu", "berat", "panjang", "jarak"
    ],
    "Keliling dan Luas Bangun Datar": [
        "persegi", "panjang", "lebar", "sisi", "keliling", "luas", "taman", "lantai", 
        "ubin", "pagar", "kawat", "kolam", "cm²", "m²"
    ],
    "Data dan Penyajian Data": [
        "data", "tabel", "diagram", "batang", "peminjaman", "nilai", "frekuensi", 
        "terbanyak", "tersedikit", "selisih", "grafik", "catatan"
    ]
}


def compute_tp_similarity(tp_text: str, question_text: str) -> float:
    """
    Simulasi NLP: Mengukur kedekatan konsep soal dengan tujuan pembelajaran
    menggunakan representasi TF-IDF dan Cosine Similarity.
    """
    if not tp_text.strip() or not question_text.strip():
        return 0.0
    try:
        corpus = [tp_text, question_text]
        vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b")
        tfidf_matrix = vectorizer.fit_transform(corpus)
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return float(similarity)
    except Exception:
        # Fallback penghitungan overlap token sederhana
        tp_tokens = set(re.findall(r"\w+", tp_text.lower()))
        q_tokens = set(re.findall(r"\w+", question_text.lower()))
        if not tp_tokens:
            return 0.0
        return len(tp_tokens.intersection(q_tokens)) / len(tp_tokens)


def analyze_lexical_readability(text: str) -> Dict[str, Any]:
    """
    Simulasi NLP: Analisis keterbacaan leksikal ramah anak SD kelas IV.
    Mendeteksi jargon dewasa, rerata panjang kata, dan panjang kalimat.
    """
    clean_text = text.strip()
    words = re.findall(r"\b\w+\b", clean_text.lower())
    sentences = [s.strip() for s in re.split(r"[.!?]+", clean_text) if s.strip()]
    
    if not words:
        return {
            "avg_word_length": 0.0,
            "avg_sentence_length": 0.0,
            "detected_jargon": [],
            "readability_score": "Belum Cukup Bukti"
        }
        
    avg_word_len = sum(len(w) for w in words) / len(words)
    avg_sentence_len = len(words) / max(1, len(sentences))
    
    # Deteksi kata-kata jargon dewasa
    detected_jargon = [w for w in words if w in ADULT_JARGON_WORDS]
    
    # Evaluasi keterbacaan untuk anak kelas IV (9-10 tahun)
    # Standar ramah anak SD: rata-rata panjang kalimat 10-18 kata, minim jargon dewasa
    if detected_jargon:
        readability_status = "Kurang Sesuai untuk Kelas IV SD (Terdapat istilah teknis/jargon dewasa)"
    elif avg_sentence_len > 25:
        readability_status = "Perlu Penyederhanaan (Kalimat terlalu panjang/kompleks)"
    else:
        readability_status = "Sesuai untuk Kelas IV SD (Kosakata wajar dan kalimat mengalir)"
        
    return {
        "avg_word_length": round(avg_word_len, 1),
        "avg_sentence_length": round(avg_sentence_len, 1),
        "detected_jargon": list(set(detected_jargon)),
        "readability_status": readability_status
    }


def analyze_cognitive_demand(text: str, rule_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulasi NLP: Mengestimasi tingkat tuntutan kognitif (LOTS vs HOTS).
    Memeriksa keberadaan pertanyaan evaluatif, pemilahan informasi, dan multi-langkah.
    """
    clean_text = text.lower()
    
    # Indikator evaluasi/penalaran (HOTS)
    evaluative_markers = ["apakah cukup", "jelaskan", "mengapa", "simpulkan", "bandingkan", "buktikan", "alasan"]
    has_evaluative = any(m in clean_text for m in evaluative_markers)
    
    # Indikator analisis (memilah informasi)
    analysis_markers = ["selisih", "terbanyak", "tersedikit", "sisanya", "masing-masing", "wadah", "keranjang"]
    has_analysis = any(m in clean_text for m in analysis_markers)
    
    # Indikator satu langkah langsung (LOTS)
    direct_single_step = (
        rule_info.get("number_count", 0) <= 2 and 
        len(rule_info.get("detected_multistep", [])) == 0 and 
        not has_evaluative
    )
    
    if has_evaluative and len(rule_info.get("detected_multistep", [])) > 0:
        level = "Tinggi (HOTS: Analisis & Evaluasi Kondisi)"
        estimated_c_level = "C4 - C5 (Menganalisis & Mengevaluasi)"
    elif len(rule_info.get("detected_multistep", [])) > 0 or has_analysis:
        level = "Sedang (Penerapan Kontekstual Multi-Tahap)"
        estimated_c_level = "C3 - C4 (Menerapkan & Menguraikan)"
    elif direct_single_step:
        level = "Rendah (LOTS: Perhitungan Langsung Tunggal / Ingatan)"
        estimated_c_level = "C1 - C2 (Mengingat / Memahami Dasar)"
    else:
        level = "Sedang-Rendah"
        estimated_c_level = "C2 - C3"
        
    return {
        "level": level,
        "estimated_c_level": estimated_c_level,
        "has_evaluative": has_evaluative,
        "has_analysis": has_analysis
    }
