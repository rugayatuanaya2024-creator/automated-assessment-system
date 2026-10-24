"""
repositories/database.py
Penyimpanan lokal SQLite untuk Automated Assessment System (AAS).
Mengelola profil guru, bank soal, riwayat analisis, versi revisi, dan inisialisasi data demonstrasi otomatis.
"""

import os
import json
import sqlite3
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "aas_database.sqlite")
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Membuat tabel-tabel SQLite bila belum ada."""
    conn = get_connection()
    cursor = conn.cursor()

    # Tabel Soal (versi asli dan versi revisi)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id TEXT PRIMARY KEY,
        materi TEXT NOT NULL,
        tp_id TEXT,
        tp_text TEXT NOT NULL,
        teks_soal TEXT NOT NULL,
        kunci_jawaban TEXT,
        langkah_penyelesaian TEXT,
        tingkat_tantangan TEXT,
        tipe_kualitas TEXT,
        catatan_kelemahan_demo TEXT,
        saran_perbaikan_demo TEXT,
        teks_soal_revisi_demo TEXT,
        versi INTEGER DEFAULT 1,
        parent_id TEXT,
        created_at TEXT,
        is_demo INTEGER DEFAULT 1
    )
    """)

    # Tabel Riwayat Hasil Analisis
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analysis_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id TEXT NOT NULL,
        versi INTEGER DEFAULT 1,
        waktu_analisis TEXT,
        materi TEXT,
        tp_text TEXT,
        teks_soal TEXT,
        kunci_jawaban TEXT,
        langkah_penyelesaian TEXT,
        skor_kurikuler REAL,
        skor_kognitif REAL,
        skor_bahasa REAL,
        ringkasan_kualitas TEXT,
        saran_revisi_utama TEXT,
        contoh_soal_revisi TEXT,
        keterbatasan_analisis TEXT,
        indicator_details TEXT,
        is_demo INTEGER DEFAULT 1
    )
    """)

    # Tabel Profil Guru Demonstrasi
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teacher_profile (
        id INTEGER PRIMARY KEY,
        nama_guru TEXT,
        kode_partisipan TEXT,
        sekolah TEXT,
        kelas TEXT,
        semester TEXT,
        mata_pelajaran TEXT,
        updated_at TEXT
    )
    """)

    conn.commit()
    conn.close()


def get_teacher_profile() -> Dict[str, Any]:
    init_database()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM teacher_profile WHERE id = 1")
    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return {
        "nama_guru": "Guru Demonstrasi",
        "kode_partisipan": "DEMO-001",
        "sekolah": "SD Demonstrasi Nusantara",
        "kelas": "IV",
        "semester": "Ganjil",
        "mata_pelajaran": "Matematika",
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def save_teacher_profile(profile: Dict[str, Any]):
    init_database()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO teacher_profile (id, nama_guru, kode_partisipan, sekolah, kelas, semester, mata_pelajaran, updated_at)
    VALUES (1, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
        nama_guru=excluded.nama_guru,
        kode_partisipan=excluded.kode_partisipan,
        sekolah=excluded.sekolah,
        kelas=excluded.kelas,
        semester=excluded.semester,
        mata_pelajaran=excluded.mata_pelajaran,
        updated_at=excluded.updated_at
    """, (
        profile.get("nama_guru", "Guru Demonstrasi"),
        profile.get("kode_partisipan", "DEMO-001"),
        profile.get("sekolah", "SD Demonstrasi Nusantara"),
        profile.get("kelas", "IV"),
        profile.get("semester", "Ganjil"),
        profile.get("mata_pelajaran", "Matematika"),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()


def get_all_questions() -> List[Dict[str, Any]]:
    init_database()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_question_by_id(question_id: str) -> Optional[Dict[str, Any]]:
    init_database()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions WHERE id = ?", (question_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def save_question(q: Dict[str, Any]):
    init_database()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO questions (
        id, materi, tp_id, tp_text, teks_soal, kunci_jawaban, langkah_penyelesaian,
        tingkat_tantangan, tipe_kualitas, catatan_kelemahan_demo, saran_perbaikan_demo,
        teks_soal_revisi_demo, versi, parent_id, created_at, is_demo
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
        materi=excluded.materi,
        tp_id=excluded.tp_id,
        tp_text=excluded.tp_text,
        teks_soal=excluded.teks_soal,
        kunci_jawaban=excluded.kunci_jawaban,
        langkah_penyelesaian=excluded.langkah_penyelesaian,
        tingkat_tantangan=excluded.tingkat_tantangan,
        tipe_kualitas=excluded.tipe_kualitas,
        catatan_kelemahan_demo=excluded.catatan_kelemahan_demo,
        saran_perbaikan_demo=excluded.saran_perbaikan_demo,
        teks_soal_revisi_demo=excluded.teks_soal_revisi_demo,
        versi=excluded.versi,
        parent_id=excluded.parent_id,
        is_demo=excluded.is_demo
    """, (
        q.get("id"),
        q.get("materi"),
        q.get("tp_id"),
        q.get("tp_text"),
        q.get("teks_soal"),
        q.get("kunci_jawaban", ""),
        q.get("langkah_penyelesaian", ""),
        q.get("tingkat_tantangan", "Sedang"),
        q.get("tipe_kualitas", "Buatan Pengguna"),
        q.get("catatan_kelemahan_demo", ""),
        q.get("saran_perbaikan_demo", ""),
        q.get("teks_soal_revisi_demo", ""),
        q.get("versi", 1),
        q.get("parent_id"),
        q.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        q.get("is_demo", 0)
    ))
    conn.commit()
    conn.close()


def save_analysis_result(res: Dict[str, Any]) -> int:
    init_database()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO analysis_results (
        question_id, versi, waktu_analisis, materi, tp_text, teks_soal, kunci_jawaban,
        langkah_penyelesaian, skor_kurikuler, skor_kognitif, skor_bahasa, ringkasan_kualitas,
        saran_revisi_utama, contoh_soal_revisi, keterbatasan_analisis, indicator_details, is_demo
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        res.get("question_id"),
        res.get("versi", 1),
        res.get("waktu_analisis", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        res.get("materi", ""),
        res.get("tp_text", ""),
        res.get("teks_soal", ""),
        res.get("kunci_jawaban", ""),
        res.get("langkah_penyelesaian", ""),
        res.get("skor_kurikuler", 0.0),
        res.get("skor_kognitif", 0.0),
        res.get("skor_bahasa", 0.0),
        res.get("ringkasan_kualitas", ""),
        json.dumps(res.get("saran_revisi_utama", []), ensure_ascii=False),
        res.get("contoh_soal_revisi", ""),
        res.get("keterbatasan_analisis", ""),
        json.dumps(res.get("indicator_details", {}), ensure_ascii=False),
        res.get("is_demo", 0)
    ))
    inserted_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return inserted_id


def get_all_analysis_results() -> List[Dict[str, Any]]:
    init_database()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analysis_results ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    results = []
    for r in rows:
        d = dict(r)
        try:
            d["saran_revisi_utama"] = json.loads(d["saran_revisi_utama"])
        except Exception:
            d["saran_revisi_utama"] = []
        try:
            d["indicator_details"] = json.loads(d["indicator_details"])
        except Exception:
            d["indicator_details"] = {}
        results.append(d)
    return results


def get_analysis_by_question_id(question_id: str) -> List[Dict[str, Any]]:
    init_database()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analysis_results WHERE question_id = ? ORDER BY versi ASC, id ASC", (question_id,))
    rows = cursor.fetchall()
    conn.close()

    results = []
    for r in rows:
        d = dict(r)
        try:
            d["saran_revisi_utama"] = json.loads(d["saran_revisi_utama"])
        except Exception:
            d["saran_revisi_utama"] = []
        try:
            d["indicator_details"] = json.loads(d["indicator_details"])
        except Exception:
            d["indicator_details"] = {}
        results.append(d)
    return results


def get_curriculum_data() -> List[Dict[str, Any]]:
    curriculum_path = os.path.join(DATA_DIR, "demo_curriculum.json")
    if os.path.exists(curriculum_path):
        with open(curriculum_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def get_rubric_data() -> Dict[str, Any]:
    rubric_path = os.path.join(DATA_DIR, "demo_rubric.json")
    if os.path.exists(rubric_path):
        with open(rubric_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def get_research_data() -> pd.DataFrame:
    research_path = os.path.join(DATA_DIR, "demo_research_data.csv")
    if os.path.exists(research_path):
        return pd.read_csv(research_path)
    return pd.DataFrame()


def seed_demo_data(force_reset: bool = False):
    """
    Mengisi database lokal dengan data awal demonstrasi secara otomatis.
    Jika force_reset=True, menghapus data lama dan mengisi ulang dari berkas demo.
    """
    init_database()
    conn = get_connection()
    cursor = conn.cursor()

    if force_reset:
        cursor.execute("DELETE FROM questions")
        cursor.execute("DELETE FROM analysis_results")
        cursor.execute("DELETE FROM teacher_profile")
        conn.commit()

    # Periksa apakah tabel questions sudah terisi
    cursor.execute("SELECT COUNT(*) as cnt FROM questions")
    count_q = cursor.fetchone()["cnt"]
    conn.close()

    if count_q == 0 or force_reset:
        # Isi profil guru awal
        save_teacher_profile({
            "nama_guru": "Guru Demonstrasi",
            "kode_partisipan": "DEMO-001",
            "sekolah": "SD Demonstrasi Nusantara",
            "kelas": "IV",
            "semester": "Ganjil",
            "mata_pelajaran": "Matematika"
        })

        # Muat 15 soal demo dari JSON
        questions_path = os.path.join(DATA_DIR, "demo_questions.json")
        if os.path.exists(questions_path):
            with open(questions_path, "r", encoding="utf-8") as f:
                questions_list = json.load(f)
            for q in questions_list:
                q["versi"] = 1
                q["parent_id"] = None
                q["is_demo"] = 1
                save_question(q)

        # Impor feedback engine untuk menjalankan analisis otomatis pada soal awal
        try:
            from services.feedback_engine import evaluate_question
            for q in questions_list:
                report = evaluate_question(
                    materi=q["materi"],
                    tp_text=q["tp_text"],
                    teks_soal=q["teks_soal"],
                    kunci_jawaban=q.get("kunci_jawaban", ""),
                    langkah_penyelesaian=q.get("langkah_penyelesaian", ""),
                    question_id=q["id"],
                    is_demo=True
                )
                # Simpan hasil analisis versi 1
                save_analysis_result({
                    "question_id": q["id"],
                    "versi": 1,
                    "waktu_analisis": report.waktu_analisis,
                    "materi": report.materi,
                    "tp_text": report.tp_text,
                    "teks_soal": report.teks_soal,
                    "kunci_jawaban": report.kunci_jawaban,
                    "langkah_penyelesaian": report.langkah_penyelesaian,
                    "skor_kurikuler": report.skor_kurikuler,
                    "skor_kognitif": report.skor_kognitif,
                    "skor_bahasa": report.skor_bahasa,
                    "ringkasan_kualitas": report.ringkasan_kualitas,
                    "saran_revisi_utama": report.saran_revisi_utama,
                    "contoh_soal_revisi": report.contoh_soal_revisi,
                    "keterbatasan_analisis": report.keterbatasan_analisis,
                    "indicator_details": {
                        dim_id: [
                            {
                                "id": ind.id,
                                "kode": ind.kode,
                                "nama": ind.nama,
                                "skor": ind.skor,
                                "skor_display": ind.skor_display,
                                "alasan": ind.alasan,
                                "bukti_teks": ind.bukti_teks,
                                "saran": ind.saran,
                                "is_evaluable": ind.is_evaluable
                            }
                            for ind in dim_res.indikator_results
                        ]
                        for dim_id, dim_res in report.dimensi_results.items()
                    },
                    "is_demo": 1
                })

            # Buat beberapa contoh versi revisi (versi 2) untuk SOAL-001, SOAL-002, SOAL-004, SOAL-005
            demo_revisions = [
                ("SOAL-001", "SOAL-001-REV1", "Koperasi SD Nusantara membeli 12 kotak pensil untuk persediaan. Setiap kotak berisi 24 batang pensil. Sebanyak 150 pensil dibagikan kepada siswa penerima bantuan. Sisanya akan dimasukkan ke dalam wadah kecil yang masing-masing memuat 6 pensil. Berapa wadah kecil yang dibutuhkan koperasi?"),
                ("SOAL-002", "SOAL-002-REV1", "Budi memetik 145 buah apel dari kebun paman. Ibu juga memetik 175 buah apel. Seluruh apel tersebut digabungkan lalu disortir. Sebanyak 20 apel ternyata busuk dan disisihkan. Apel yang bagus dimasukkan sama rata ke dalam 5 keranjang. Berapa buah apel pada setiap keranjang?"),
                ("SOAL-004", "SOAL-004-REV1", "Sebuah karung berisi beras seberat 8 kg. Beras tersebut dimasukkan secara merata ke dalam 4 kantong plastik kecil. Berapa gram berat beras dalam setiap kantong plastik kecil?"),
                ("SOAL-005", "SOAL-005-REV1", "Pak Budi berencana membuat kolam ikan lele berbentuk persegi di pekarangan rumahnya. Panjang sisi kolam adalah 6 meter. Di sekeliling kolam dipasangi pagar bambu. Berapa meter panjang pagar bambu yang dibutuhkan?")
            ]

            for orig_id, rev_id, rev_text in demo_revisions:
                orig_q = get_question_by_id(orig_id)
                if orig_q:
                    # Simpan pertanyaan revisi
                    rev_q = dict(orig_q)
                    rev_q["id"] = rev_id
                    rev_q["parent_id"] = orig_id
                    rev_q["versi"] = 2
                    rev_q["teks_soal"] = rev_text
                    rev_q["tipe_kualitas"] = "Hasil Revisi Demonstrasi (Versi 2)"
                    save_question(rev_q)

                    # Analisis pertanyaan revisi
                    rev_report = evaluate_question(
                        materi=orig_q["materi"],
                        tp_text=orig_q["tp_text"],
                        teks_soal=rev_text,
                        kunci_jawaban=orig_q.get("kunci_jawaban", ""),
                        langkah_penyelesaian="Penyelesaian versi revisi.",
                        question_id=orig_id,  # Kaitkan dengan question_id asli untuk perbandingan
                        is_demo=True
                    )
                    save_analysis_result({
                        "question_id": orig_id,
                        "versi": 2,
                        "waktu_analisis": rev_report.waktu_analisis,
                        "materi": rev_report.materi,
                        "tp_text": rev_report.tp_text,
                        "teks_soal": rev_text,
                        "kunci_jawaban": rev_report.kunci_jawaban,
                        "langkah_penyelesaian": "Penyelesaian versi revisi.",
                        "skor_kurikuler": rev_report.skor_kurikuler,
                        "skor_kognitif": rev_report.skor_kognitif,
                        "skor_bahasa": rev_report.skor_bahasa,
                        "ringkasan_kualitas": "Versi perbaikan simulasi dengan struktur informasi yang lebih lengkap dan tuntutan kognitif yang disempurnakan.",
                        "saran_revisi_utama": ["Versi revisi telah mengatasi cacat instruksi dan/atau meningkatkan kedalaman proses berpikir siswa."],
                        "contoh_soal_revisi": rev_text,
                        "keterbatasan_analisis": rev_report.keterbatasan_analisis,
                        "indicator_details": {
                            dim_id: [
                                {
                                    "id": ind.id,
                                    "kode": ind.kode,
                                    "nama": ind.nama,
                                    "skor": ind.skor,
                                    "skor_display": ind.skor_display,
                                    "alasan": ind.alasan,
                                    "bukti_teks": ind.bukti_teks,
                                    "saran": ind.saran,
                                    "is_evaluable": ind.is_evaluable
                                }
                                for ind in dim_res.indikator_results
                            ]
                            for dim_id, dim_res in rev_report.dimensi_results.items()
                        },
                        "is_demo": 1
                    })
        except Exception as e:
            # Fallback jika terjadi kesalahan saat seeding
            print(f"Peringatan seeding: {e}")
