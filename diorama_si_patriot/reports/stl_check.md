# Pemeriksaan STL (otomatis)

Dibuat oleh `src/build_all.py` (trimesh + manifold3d). Kolom: tertutup (watertight), arah muka konsisten, volume positif, jumlah badan terpisah, Z minimum, muat bed 220x220x250, ketebalan lokal persentil-1 (ray ke dalam dari 4000 titik acak), luas muka menghadap bawah >45° di atas bed.

| Berkas | Lolos | Tertutup | Volume (cm³) | Badan | Z min | Ukuran X×Y×Z (mm) | Tebal p1 (mm) | Overhang>45° (mm²) |
|---|---|---|---|---|---|---|---|---|
| `stl/figur/F01_rumput_pakan_hijauan.stl` | YA | ya | 38.01 | 1 | 0.0 | 70.6 × 56.6 × 26.4 | 1.0 | 0.0 |
| `stl/figur/F02_pakan_ternak.stl` | YA | ya | 20.58 | 1 | 0.0 | 42.3 × 34.6 × 30.6 | 1.66 | 106.5 |
| `stl/figur/F03_mesin_pencacah_rumput.stl` | YA | ya | 9.14 | 1 | 0.0 | 38.0 × 20.6 × 32.7 | 1.14 | 611.8 |
| `stl/figur/F04_kandang.stl` | YA | ya | 259.36 | 1 | 0.0 | 65.6 × 78.2 × 61.9 | 1.32 | 127.0 |
| `stl/figur/F05_sapi_perah_a.stl` | YA | ya | 12.71 | 1 | 0.0 | 56.4 × 20.0 × 39.3 | 1.9 | 418.6 |
| `stl/figur/F06_sapi_perah_b.stl` | YA | ya | 12.89 | 1 | 0.0 | 53.7 × 20.6 × 35.8 | 1.92 | 382.2 |
| `stl/figur/F07_peternak_badan.stl` | YA | ya | 1.24 | 1 | 0.0 | 16.6 × 12.9 × 35.3 | 1.47 | 20.1 |
| `stl/figur/F08_peternak_caping.stl` | YA | ya | 0.34 | 1 | 0.0 | 13.2 × 13.2 × 6.0 | 0.92 | 18.0 |
| `stl/figur/F09_botol_susu.stl` | YA | ya | 6.01 | 1 | 0.0 | 20.4 × 18.6 × 31.0 | 2.6 | 27.6 |
| `stl/figur/F10_kantong_uang_koin.stl` | YA | ya | 4.37 | 1 | 0.0 | 27.4 × 23.0 × 22.1 | 0.86 | 58.8 |
| `stl/figur/F11_limbah_ternak.stl` | YA | ya | 7.72 | 1 | 0.0 | 41.8 × 29.4 × 19.6 | 0.95 | 6.6 |
| `stl/figur/F12_biodigester.stl` | YA | ya | 62.54 | 1 | 0.0 | 80.3 × 59.5 × 39.0 | 1.6 | 2.1 |
| `stl/figur/F13_biogas.stl` | YA | ya | 1.52 | 1 | 0.0 | 16.0 × 16.0 × 21.8 | 2.17 | 0.6 |
| `stl/figur/F14_slurry.stl` | YA | ya | 3.25 | 1 | 0.0 | 17.0 × 11.5 × 22.5 | 0.82 | 62.0 |
| `stl/figur/F15_energi_dan_pupuk.stl` | YA | ya | 1.44 | 1 | 0.0 | 26.1 × 16.2 × 17.6 | 0.69 | 16.6 |
| `stl/figur/F16_limbah_padat.stl` | YA | ya | 16.63 | 1 | 0.0 | 45.8 × 32.9 × 12.7 | 3.5 | 93.1 |
| `stl/figur/F17_pupuk_organik.stl` | YA | ya | 10.19 | 1 | 0.0 | 25.3 × 22.2 × 35.8 | 1.32 | 79.9 |
| `stl/figur/F18_hp_si_patriot_dudukan.stl` | YA | ya | 13.37 | 1 | 0.0 | 39.0 × 36.0 × 50.0 | 1.72 | 69.5 |
| `stl/sapi_varian_belah/F05-1_sapi_A_belahan_kiri.stl` | YA | ya | 6.04 | 1 | 0.0 | 52.1 × 39.3 × 9.2 | 0.76 | 127.9 |
| `stl/sapi_varian_belah/F05-2_sapi_A_belahan_kanan.stl` | YA | ya | 6.6 | 1 | 0.0 | 56.4 × 39.3 × 10.8 | 1.09 | 147.5 |
| `stl/sapi_varian_belah/F06-1_sapi_B_belahan_kiri.stl` | YA | ya | 6.59 | 1 | 0.0 | 53.2 × 35.8 × 11.4 | 1.09 | 129.9 |
| `stl/sapi_varian_belah/F06-2_sapi_B_belahan_kanan.stl` | YA | ya | 6.22 | 1 | 0.0 | 53.0 × 35.8 × 9.2 | 0.57 | 158.0 |
| `stl/dudukan/D01_dudukan_pakan_hijauan.stl` | YA | ya | 78.28 | 1 | 0.0 | 94.0 × 86.0 × 10.8 | 1.28 | 36.3 |
| `stl/dudukan_varian_stiker/D01_dudukan_pakan_hijauan_stiker.stl` | YA | ya | 77.75 | 1 | 0.0 | 94.0 × 86.0 × 10.0 | 9.5 | 36.3 |
| `stl/dudukan/D02_dudukan_pakan_ternak_dan_mesin_pencacah.stl` | YA | ya | 178.56 | 1 | 0.0 | 112.0 × 76.5 × 22.8 | 1.02 | 34.8 |
| `stl/dudukan_varian_stiker/D02_dudukan_pakan_ternak_dan_mesin_pencacah_stiker.stl` | YA | ya | 177.71 | 1 | 0.0 | 112.0 × 76.5 × 22.0 | 21.5 | 34.8 |
| `stl/dudukan/D03_dudukan_produksi_ternak.stl` | YA | ya | 226.49 | 1 | 0.0 | 172.0 × 136.0 × 10.8 | 9.61 | 43.9 |
| `stl/dudukan_varian_stiker/D03_dudukan_produksi_ternak_stiker.stl` | YA | ya | 225.88 | 1 | 0.0 | 172.0 × 136.0 × 10.0 | 9.5 | 43.9 |
| `stl/dudukan/D04_dudukan_susu_sapi.stl` | YA | ya | 36.07 | 1 | 0.0 | 68.0 × 68.0 × 10.8 | 1.12 | 10.8 |
| `stl/dudukan_varian_stiker/D04_dudukan_susu_sapi_stiker.stl` | YA | ya | 35.77 | 1 | 0.0 | 68.0 × 68.0 × 10.0 | 9.5 | 10.8 |
| `stl/dudukan/D05_dudukan_pendapatan_peternak.stl` | YA | ya | 40.53 | 1 | 0.0 | 72.0 × 72.0 × 10.8 | 0.94 | 14.5 |
| `stl/dudukan_varian_stiker/D05_dudukan_pendapatan_peternak_stiker.stl` | YA | ya | 39.94 | 1 | 0.0 | 72.0 × 72.0 × 10.0 | 9.5 | 14.5 |
| `stl/dudukan/D06_dudukan_limbah_ternak.stl` | YA | ya | 59.37 | 1 | 0.0 | 92.0 × 74.0 × 10.8 | 1.13 | 33.4 |
| `stl/dudukan_varian_stiker/D06_dudukan_limbah_ternak_stiker.stl` | YA | ya | 58.91 | 1 | 0.0 | 92.0 × 74.0 × 10.0 | 9.5 | 33.4 |
| `stl/dudukan/D07_dudukan_biodigester.stl` | YA | ya | 112.39 | 1 | 0.0 | 124.0 × 104.0 × 10.8 | 9.35 | 52.5 |
| `stl/dudukan_varian_stiker/D07_dudukan_biodigester_stiker.stl` | YA | ya | 111.89 | 1 | 0.0 | 124.0 × 104.0 × 10.0 | 9.5 | 52.5 |
| `stl/dudukan/D08_dudukan_hasil_pengolahan_limbah.stl` | YA | ya | 135.56 | 1 | 0.0 | 144.0 × 105.0 × 10.8 | 1.01 | 52.9 |
| `stl/dudukan_varian_stiker/D08_dudukan_hasil_pengolahan_limbah_stiker.stl` | YA | ya | 134.33 | 1 | 0.0 | 144.0 × 105.0 × 10.0 | 9.5 | 52.9 |
| `stl/dudukan/D09_dudukan_pupuk_organik.stl` | YA | ya | 44.81 | 1 | 0.0 | 58.0 × 64.0 × 13.8 | 1.0 | 24.7 |
| `stl/dudukan_varian_stiker/D09_dudukan_pupuk_organik_stiker.stl` | YA | ya | 44.4 | 1 | 0.0 | 58.0 × 64.0 × 13.0 | 12.5 | 24.7 |
| `stl/dudukan/D10_dudukan_pencatatan_digital_si_patriot.stl` | YA | ya | 111.36 | 1 | 0.0 | 104.0 × 80.0 × 14.8 | 1.02 | 41.5 |
| `stl/dudukan_varian_stiker/D10_dudukan_pencatatan_digital_si_patriot_stiker.stl` | YA | ya | 110.47 | 1 | 0.0 | 104.0 × 80.0 × 14.0 | 13.5 | 41.5 |
| `stl/alas_cetak3d/T11_ubin_alas_depan_kiri.stl` | YA | ya | 276.09 | 1 | 0.0 | 200.0 × 180.0 × 8.0 | 3.8 | 661.9 |
| `stl/alas_cetak3d/T12_ubin_alas_depan_tengah.stl` | YA | ya | 273.36 | 1 | 0.0 | 200.0 × 180.0 × 8.0 | 3.8 | 992.9 |
| `stl/alas_cetak3d/T13_ubin_alas_depan_kanan.stl` | YA | ya | 278.91 | 1 | 0.0 | 200.0 × 180.0 × 8.0 | 3.8 | 661.9 |
| `stl/alas_cetak3d/T21_ubin_alas_belakang_kiri.stl` | YA | ya | 277.52 | 1 | 0.0 | 200.0 × 180.0 × 8.0 | 3.8 | 661.9 |
| `stl/alas_cetak3d/T22_ubin_alas_belakang_tengah.stl` | YA | ya | 270.73 | 1 | 0.0 | 200.0 × 180.0 × 8.0 | 3.2 | 992.9 |
| `stl/alas_cetak3d/T23_ubin_alas_belakang_kanan.stl` | YA | ya | 273.82 | 1 | 0.0 | 200.0 × 180.0 × 8.0 | 3.2 | 661.9 |
| `stl/alas_cetak3d/K01_kunci_sambungan_bowtie.stl` | YA | ya | 1.25 | 1 | 0.0 | 30.0 × 13.5 × 4.0 | 4.0 | 0.0 |

**49/49 berkas lolos semua syarat** (tertutup, volume > 0, satu badan, alas di Z = 0, valid sebagai manifold di manifold3d, muat bed).

Catatan pembersihan mesh (sebelum ekspor): serpihan degenerat nol-volume dan rongga internal kecil hasil marching-cubes dibuang; volume yang dibuang dicatat di `stl_check.json` (kolom `cleanup`). Tidak ada badan nyata (> 1 mm³) yang dibuang diam-diam.

Ketebalan persentil-1 di bawah 0,8 mm umumnya titik di tepi/sudut tajam (artefak metode ray), bukan dinding tipis; helai rumput dirancang >= 1,0 x 1,0 mm di ujung, huruf label >= 1,0 mm lebar garis.
