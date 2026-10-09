# Daftar objek, jumlah cetak, dan rencana cetak

Waktu & berat = estimasi PrusaSlicer 2.7 (nozzle 0,4; figur layer 0,12 mm, 3 perimeter, infill 15%; dudukan layer 0,2 mm; ubin 0,24 mm; PLA 1,24 g/cm³). Printer lain bisa berbeda ±30%.

## Figur & alat (semua dicetak 1×)

| ID | Objek | Jumlah | Dudukan | Ukuran (mm) | Support | Waktu | Gram | Filamen dasar | Ganti filamen | Cat / finishing |
|---|---|---|---|---|---|---|---|---|---|---|
| F01 | Rumput pakan hijauan | **1** | D01 | 71×57×26 | tidak | 9h 26m 56s | 28.8 | Cokelat -> hijau | ganti ke hijau di Z = 6,0 | dry-brush hijau tua di pangkal helai (opsional) |
| F02 | Pakan ternak (karung + wadah) | **1** | D02 | 42×35×31 | tidak | 1h 10m 51s | 9.7 | Krem/cokelat muda | - | biji pakan cokelat, toples hijau tua, tutup abu tua |
| F03 | Mesin pencacah rumput | **1** | D02 | 38×21×33 | tidak | 1h 26m 36s | 8.1 | Merah -> hijau | ganti ke hijau di Z = 11,6 (atas dek) | motor abu tua, tangki merah |
| F04 | Kandang | **1** | D03 | 66×78×62 | tidak | 6h 21m 46s | 74.9 | Hijau | - | atap hijau tua, list/pintu/jendela kuning gading, kaca jendela abu tua |
| F05 | Sapi perah A (berdiri, menoleh) | **1** | D03 | 56×20×39 | YA (24.38%) | 1h 32m 47s | 11.3 | Putih | - | corak hitam (lihat render), moncong & ambing merah muda, kuku abu, mata hitam |
| F06 | Sapi perah B (menunduk makan) | **1** | D03 | 54×21×36 | YA (24.01%) | 1h 33m 2s | 11.0 | Putih | - | sama dengan F05, pola corak dibuat berbeda |
| F07 | Peternak - badan | **1** | D03 | 17×13×35 | tidak | 29m 9s | 1.5 | Putih/abu (dasar cat) | - | kaos hijau, celana biru tua, sepatu bot hitam, kulit sawo matang |
| F08 | Peternak - caping | **1** | D03 | 13×13×6 | tidak | 6m 34s | 0.4 | Krem jerami / cokelat muda | - | tanpa cat (warna filamen) |
| F09 | Botol susu (3 botol menyatu) | **1** | D04 | 20×19×31 | tidak | 56m 29s | 4.9 | Putih | - | tutup botol hijau |
| F10 | Kantong uang + koin | **1** | D05 | 27×23×22 | tidak | 33m 14s | 3.2 | Krem/cokelat muda | - | koin & tali emas, huruf Rp emas |
| F11 | Limbah ternak | **1** | D06 | 42×29×20 | tidak | 31m 19s | 3.9 | Cokelat tua | - | dry-brush cokelat sedang |
| F12 | Biodigester | **1** | D07 | 80×60×39 | tidak | 2h 27m 54s | 22.5 | Zaitun/khaki -> hijau tua | ganti ke hijau tua di Z = 19,6 | pipa abu/hijau muda, bak inlet/outlet abu beton, isi bak cokelat |
| F13 | Biogas (api di tungku) | **1** | D08 | 16×16×22 | tidak | 20m 39s | 1.4 | Hijau tua -> oranye | ganti ke oranye di Z = 5,6 | inti api kuning |
| F14 | Slurry (jeriken) | **1** | D08 | 17×12×22 | tidak | 19m 9s | 2.0 | Hijau zaitun | - | panel label krem, ikon tetes cokelat tua, tutup abu tua |
| F15 | Energi & pupuk (lampu + tunas) | **1** | D08 | 26×16×18 | tidak | 22m 56s | 1.5 | Cokelat -> kuning muda | ganti ke kuning muda di Z = 3,0 | tunas hijau, ulir lampu perak |
| F16 | Limbah padat (blok berlapis) | **1** | D08 | 46×33×13 | tidak | 55m 42s | 7.4 | Cokelat | - | lapisan selang-seling cokelat muda (dry-brush) |
| F17 | Pupuk organik (karung kraft) | **1** | D09 | 25×22×36 | tidak | 39m 40s | 5.6 | Cokelat kraft | - | pita bawah hijau, gundukan butiran cokelat tua, tempel stiker label |
| F18 | HP SI PATRIOT + dudukan | **1** | D10 | 39×36×50 | tidak | 1h 23m 27s | 10.3 | Hitam | - | tempel stiker tangkapan layar App/Website SI PATRIOT |

Ringkas jumlah wajib: **2 sapi** (F05, F06 - pose berbeda), **1 peternak** (F07 badan + F08 caping), **1 mesin pencacah** (F03), **1 biodigester** (F12), **1 HP** (F18). Tidak ada sapi ketiga, HP kedua, laptop, monitor, tablet, atau panah.

Alternatif sapi tanpa support di perut/ambing: `stl/sapi_varian_belah/` (2 belahan per sapi + 2 pin potongan filamen 1,75 mm × 12 mm). Masih perlu support kecil di bawah kaki (sisi dalam, tidak terlihat).

## Dudukan krem berlabel (semua 1×)

| ID | Label | Jumlah | Ukuran (mm) | Pusat dari pojok kiri-depan alas (mm) | Waktu | Gram | Ganti filamen |
|---|---|---|---|---|---|---|---|
| D01 | PAKAN HIJAUAN | **1** | 94×86×10.8 | (130; 288) | 2h 39m 36s | 30.1 | krem -> hijau tua di Z = 10.0 |
| D02 | MESIN PENCACAH / PAKAN TERNAK | **1** | 112×76×22.8 | (258; 306) | 3h 39m 39s | 51.3 | krem -> hijau tua di Z = 22.0 |
| D03 | PRODUKSI TERNAK | **1** | 172×136×10.8 | (410; 279) | 7h 18m 38s | 82.5 | krem -> hijau tua di Z = 10.0 |
| D04 | SUSU SAPI | **1** | 68×68×10.8 | (542; 256) | 1h 16m 6s | 14.6 | krem -> hijau tua di Z = 10.0 |
| D05 | PENDAPATAN PETERNAK | **1** | 72×72×10.8 | (550; 166) | 1h 26m 54s | 16.3 | krem -> hijau tua di Z = 10.0 |
| D06 | LIMBAH TERNAK | **1** | 92×74×10.8 | (445; 106) | 2h 2m 16s | 23.2 | krem -> hijau tua di Z = 10.0 |
| D07 | BIODIGESTER | **1** | 124×104×10.8 | (304; 67) | 3h 44m 32s | 42.3 | krem -> hijau tua di Z = 10.0 |
| D08 | BIOGAS / SLURRY / ENERGI & PUPUK / LIMBAH PADAT | **1** | 144×105×10.8 | (128; 92) | 4h 29m 50s | 50.6 | krem -> hijau tua di Z = 10.0 |
| D09 | PUPUK ORGANIK | **1** | 58×64×13.8 | (44; 210) | 1h 20m 45s | 16.5 | krem -> hijau tua di Z = 13.0 |
| D10 | PENCATATAN DIGITAL SI PATRIOT | **1** | 104×80×14.8 | (280; 168) | 3h 0m 23s | 37.2 | krem -> hijau tua di Z = 14.0 |

Varian stiker (tanpa ganti filamen): `stl/dudukan_varian_stiker/` + `docs/stiker_label_A4_skala_1-1.pdf`.

## Alas utama

**Disarankan:** papan MDF/plywood 600 × 360 × 12 mm, tepi atas di-chamfer/diamplas, cat akrilik cokelat tanah (doff). Biaya & waktu jauh lebih kecil daripada mencetak.

Opsional cetak 3D (PLA cokelat):

| ID | Berkas | Jumlah | Waktu | Gram |
|---|---|---|---|---|
| T11 | `stl/alas_cetak3d/T11_ubin_alas_depan_kiri.stl` | 1 | 8h 11m 2s | 98.0 |
| T12 | `stl/alas_cetak3d/T12_ubin_alas_depan_tengah.stl` | 1 | 7h 43m 11s | 98.9 |
| T13 | `stl/alas_cetak3d/T13_ubin_alas_depan_kanan.stl` | 1 | 8h 11m 11s | 98.3 |
| T21 | `stl/alas_cetak3d/T21_ubin_alas_belakang_kiri.stl` | 1 | 7h 49m 57s | 98.7 |
| T22 | `stl/alas_cetak3d/T22_ubin_alas_belakang_tengah.stl` | 1 | 8h 13m 44s | 98.2 |
| T23 | `stl/alas_cetak3d/T23_ubin_alas_belakang_kanan.stl` | 1 | 8h 1m 2s | 98.2 |
| K01 | `stl/alas_cetak3d/K01_kunci_sambungan_bowtie.stl` | 14 | 1j 12m total | 13 total |

## Total estimasi

- Figur & alat: **30j 38m**, ±208 g
- Dudukan: **30j 58m**, ±365 g
- (Opsional) alas cetak 3D: **49j 22m**, ±603 g
- Total tanpa alas cetak: **61j 36m** (≈ 31 jam bila 2 printer jalan paralel)

