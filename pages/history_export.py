"""
pages/history_export.py
Halaman Riwayat Analisis, Perbandingan Antar Versi, dan Ekspor Data untuk AAS.
Menyediakan fitur pencarian riwayat, perbandingan dua versi sembarang,
ekspor data ke berbagai format CSV terpisah, dan laporan siap cetak browser.
"""

import streamlit as st
import pandas as pd
import json
from repositories.database import (
    get_all_questions, 
    get_all_analysis_results, 
    get_research_data, 
    get_connection
)
from services.scoring import compute_score_delta
from components.ui_components import create_comparison_chart, DEMO_DISCLAIMER_LABEL


def render_history_export_page():
    st.markdown("### 📂 Riwayat Analisis dan Ekspor Data")
    st.caption("Telusuri arsip evaluasi butir soal, bandingkan versi revisi, dan unduh data ke berkas CSV.")
    
    analysis_list = get_all_analysis_results()
    questions = get_all_questions()
    
    if not analysis_list:
        st.info("Belum ada riwayat analisis yang tersimpan di basis data.")
        return

    tab_history, tab_compare, tab_export, tab_print = st.tabs([
        "📜 Riwayat Analisis", 
        "⚖️ Komparasi Dua Versi", 
        "📥 Pusat Ekspor CSV",
        "🖨️ Laporan Siap Cetak"
    ])

    # 1. Tab Riwayat Analisis
    with tab_history:
        st.markdown("##### Seluruh Riwayat Analisis Tersimpan")
        
        # Opsi Pencarian
        search_kw = st.text_input("Cari berdasarkan ID Soal atau Teks:", "")
        filtered_list = analysis_list
        if search_kw:
            filtered_list = [
                a for a in analysis_list 
                if search_kw.lower() in a.get("question_id", "").lower() or search_kw.lower() in a.get("teks_soal", "").lower()
            ]
            
        st.write(f"Ditemukan **{len(filtered_list)}** entri analisis:")
        
        rows = []
        for a in filtered_list:
            rows.append({
                "ID Analisis": a.get("id"),
                "ID Soal": a.get("question_id"),
                "Versi": f"v{a.get('versi', 1)}",
                "Waktu": a.get("waktu_analisis"),
                "Materi": a.get("materi"),
                "Kurikuler": f"{a.get('skor_kurikuler', 0):.1f}",
                "Kognitif": f"{a.get('skor_kognitif', 0):.1f}",
                "Bahasa": f"{a.get('skor_bahasa', 0):.1f}",
                "Tipe": "Demo" if a.get("is_demo") == 1 else "Pengguna"
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # 2. Tab Komparasi Dua Versi
    with tab_compare:
        st.markdown("##### Bandingkan Dua Hasil Analisis Sembarang")
        st.caption("Pilih dua entri analisis untuk melihat perbandingan skor dimensi dan selisihnya.")
        
        entry_labels = [f"#{a['id']} - {a['question_id']} (v{a['versi']}) - {a['waktu_analisis']}" for a in analysis_list]
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            sel_entry1 = st.selectbox("Pilih Versi Pertama (Baseline):", entry_labels, index=min(len(entry_labels)-1, 1))
        with col_c2:
            sel_entry2 = st.selectbox("Pilih Versi Kedua (Pembanding):", entry_labels, index=0)
            
        id1 = int(sel_entry1.split(" - ")[0].replace("#", ""))
        id2 = int(sel_entry2.split(" - ")[0].replace("#", ""))
        
        entry1 = next((a for a in analysis_list if a["id"] == id1), None)
        entry2 = next((a for a in analysis_list if a["id"] == id2), None)
        
        if entry1 and entry2:
            s1_dict = {"keselarasan_kurikuler": entry1["skor_kurikuler"], "tuntutan_kognitif": entry1["skor_kognitif"], "kesesuaian_bahasa": entry1["skor_bahasa"]}
            s2_dict = {"keselarasan_kurikuler": entry2["skor_kurikuler"], "tuntutan_kognitif": entry2["skor_kognitif"], "kesesuaian_bahasa": entry2["skor_bahasa"]}
            deltas = compute_score_delta(s1_dict, s2_dict)
            
            c_d1, c_d2, c_d3 = st.columns(3)
            with c_d1:
                st.metric("Keselarasan Kurikuler", f"{s2_dict['keselarasan_kurikuler']:.1f}", delta=f"{deltas['keselarasan_kurikuler']['status_text']}")
            with c_d2:
                st.metric("Tuntutan Kognitif / HOTS", f"{s2_dict['tuntutan_kognitif']:.1f}", delta=f"{deltas['tuntutan_kognitif']['status_text']}")
            with c_d3:
                st.metric("Kesesuaian Bahasa", f"{s2_dict['kesesuaian_bahasa']:.1f}", delta=f"{deltas['kesesuaian_bahasa']['status_text']}")
                
            fig_cmp = create_comparison_chart(s1_dict, s2_dict, f"Entri #{id1}", f"Entri #{id2}")
            st.plotly_chart(fig_cmp, use_container_width=True)
            
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                st.markdown(f"**Teks Soal Entri #{id1}:**")
                st.info(f"💬 \"{entry1['teks_soal']}\"")
            with col_t2:
                st.markdown(f"**Teks Soal Entri #{id2}:**")
                st.success(f"💬 \"{entry2['teks_soal']}\"")

    # 3. Tab Pusat Ekspor CSV Terpisah
    with tab_export:
        st.markdown("##### Unduh Dataset Analisis dalam Format CSV Terpisah")
        st.caption("Seluruh berkas ekspor membedakan dengan jelas antara data demonstrasi dan data pengguna.")
        
        # Ekspor 1: Bank Soal & Versi Revisi
        df_soal = pd.DataFrame(questions)
        csv_soal = df_soal.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 1. Unduh Data Soal dan Versi Revisi (CSV)",
            data=csv_soal,
            file_name="aas_bank_soal_dan_revisi.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        # Ekspor 2: Skor Tiga Dimensi
        dim_rows = []
        for a in analysis_list:
            dim_rows.append({
                "id_analisis": a["id"],
                "id_soal": a["question_id"],
                "versi": a["versi"],
                "waktu": a["waktu_analisis"],
                "materi": a["materi"],
                "skor_keselarasan_kurikuler": a["skor_kurikuler"],
                "skor_tuntutan_kognitif": a["skor_kognitif"],
                "skor_kesesuaian_bahasa": a["skor_bahasa"],
                "ringkasan_kualitas": a["ringkasan_kualitas"],
                "status_data": "DATA DEMONSTRASI" if a.get("is_demo") == 1 else "DATA PENGGUNA"
            })
        df_dim = pd.DataFrame(dim_rows)
        csv_dim = df_dim.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 2. Unduh Hasil Skor Tiga Dimensi (CSV)",
            data=csv_dim,
            file_name="aas_skor_tiga_dimensi.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        # Ekspor 3: Rincian 12 Indikator Rubrik
        ind_rows = []
        for a in analysis_list:
            details = a.get("indicator_details", {})
            if isinstance(details, dict):
                for dim_name, ind_list in details.items():
                    if isinstance(ind_list, list):
                        for ind in ind_list:
                            ind_rows.append({
                                "id_analisis": a["id"],
                                "id_soal": a["question_id"],
                                "versi": a["versi"],
                                "dimensi": dim_name,
                                "kode_indikator": ind.get("kode"),
                                "nama_indikator": ind.get("nama"),
                                "skor": ind.get("skor"),
                                "skor_display": ind.get("skor_display"),
                                "alasan": ind.get("alasan"),
                                "bukti_teks": ind.get("bukti_teks"),
                                "saran": ind.get("saran"),
                                "status_data": "DATA DEMONSTRASI" if a.get("is_demo") == 1 else "DATA PENGGUNA"
                            })
        df_ind = pd.DataFrame(ind_rows)
        csv_ind = df_ind.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 3. Unduh Rincian Skor 12 Indikator Rubrik (CSV)",
            data=csv_ind,
            file_name="aas_skor_12_indikator.csv",
            mime="text/csv",
            use_container_width=True
        )

        # Ekspor 4: Data Simulasi Pretest-Posttest Penelitian
        df_res = get_research_data()
        csv_res = df_res.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 4. Unduh Data Simulasi Pretest-Posttest (CSV)",
            data=csv_res,
            file_name="aas_simulasi_penelitian_pretest_posttest.csv",
            mime="text/csv",
            use_container_width=True
        )

    # 4. Tab Laporan Siap Cetak Browser
    with tab_print:
        st.markdown("##### Pratinjau Laporan Siap Cetak (Print-Friendly)")
        st.caption("Gunakan fitur cetak browser Anda (Ctrl+P / Command+P) untuk menyimpan dokumen ini sebagai PDF.")
        
        sel_print_entry = st.selectbox(
            "Pilih Soal untuk Pratinjau Cetak:",
            entry_labels,
            key="sel_print_report"
        )
        print_id = int(sel_print_entry.split(" - ")[0].replace("#", ""))
        print_item = next((a for a in analysis_list if a["id"] == print_id), None)
        
        if print_item:
            st.markdown(f"""
            <div style="background-color: #FFFFFF; border: 2px solid #E2E8F0; border-radius: 8px; padding: 24px; color: #1E293B;">
                <div style="text-align: center; border-bottom: 2px solid #334155; padding-bottom: 12px; margin-bottom: 16px;">
                    <h2 style="margin: 0; color: #0F172A;">LEMBAR LAPORAN ANALISIS SOAL CERITA MATEMATIKA</h2>
                    <p style="margin: 4px 0 0 0; font-size: 13px; color: #64748B;">Automated Assessment System (AAS) — Kelas IV SD Fase B</p>
                    <span style="font-size: 11px; background: #FEF3C7; color: #92400E; padding: 2px 8px; border-radius: 4px; font-weight: bold;">
                        {DEMO_DISCLAIMER_LABEL}
                    </span>
                </div>
                
                <table style="width: 100%; font-size: 13px; margin-bottom: 16px;">
                    <tr><td style="width: 25%; font-weight: bold;">ID Butir Soal:</td><td>{print_item['question_id']} (Versi {print_item['versi']})</td></tr>
                    <tr><td style="font-weight: bold;">Waktu Analisis:</td><td>{print_item['waktu_analisis']}</td></tr>
                    <tr><td style="font-weight: bold;">Lingkup Materi:</td><td>{print_item['materi']}</td></tr>
                    <tr><td style="font-weight: bold;">Tujuan Pembelajaran:</td><td>{print_item['tp_text']}</td></tr>
                </table>
                
                <div style="background: #F8FAFC; border-left: 4px solid #2563EB; padding: 12px; margin-bottom: 16px;">
                    <strong>Teks Soal Cerita:</strong><br>
                    <em>"{print_item['teks_soal']}"</em>
                </div>
                
                <h4 style="margin: 16px 0 8px 0; color: #0F172A;">Hasil Skor Tiga Dimensi</h4>
                <table style="width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 16px;">
                    <tr style="background: #F1F5F9; border-bottom: 1px solid #CBD5E1;">
                        <th style="padding: 8px; text-align: left;">Dimensi Penilaian</th>
                        <th style="padding: 8px; text-align: center;">Skor (0 - 100)</th>
                        <th style="padding: 8px; text-align: left;">Kategori Kualitas</th>
                    </tr>
                    <tr style="border-bottom: 1px solid #E2E8F0;">
                        <td style="padding: 8px;">1. Keselarasan Kurikuler</td>
                        <td style="padding: 8px; text-align: center; font-weight: bold;">{print_item['skor_kurikuler']:.1f}</td>
                        <td style="padding: 8px;">{'Memenuhi dengan Baik' if print_item['skor_kurikuler']>=75 else ('Cukup' if print_item['skor_kurikuler']>=50 else 'Perlu Perbaikan')}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #E2E8F0;">
                        <td style="padding: 8px;">2. Tuntutan Kognitif dan HOTS</td>
                        <td style="padding: 8px; text-align: center; font-weight: bold;">{print_item['skor_kognitif']:.1f}</td>
                        <td style="padding: 8px;">{'Memenuhi dengan Baik' if print_item['skor_kognitif']>=75 else ('Cukup' if print_item['skor_kognitif']>=50 else 'Perlu Perbaikan')}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #E2E8F0;">
                        <td style="padding: 8px;">3. Kesesuaian Bahasa & Keterbacaan</td>
                        <td style="padding: 8px; text-align: center; font-weight: bold;">{print_item['skor_bahasa']:.1f}</td>
                        <td style="padding: 8px;">{'Memenuhi dengan Baik' if print_item['skor_bahasa']>=75 else ('Cukup' if print_item['skor_bahasa']>=50 else 'Perlu Perbaikan')}</td>
                    </tr>
                </table>
                
                <h4 style="margin: 16px 0 8px 0; color: #0F172A;">Rekomendasi Revisi Soal</h4>
                <div style="font-size: 13px; line-height: 1.6; color: #334155;">
                    <strong>Contoh Draf Revisi:</strong><br>
                    <em>"{print_item['contoh_soal_revisi']}"</em>
                </div>
            </div>
            """, unsafe_allow_html=True)
