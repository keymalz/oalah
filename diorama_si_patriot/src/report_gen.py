"""Tulis laporan Markdown: pemeriksaan STL, daftar objek (BOM) & rencana cetak."""
import os, sys, json, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
REP = os.path.join(ROOT, "reports")
DOCS = os.path.join(ROOT, "docs")
MAN = json.load(open(os.path.join(REP, "manifest.json")))
CHK = json.load(open(os.path.join(REP, "stl_check.json")))
SL = {r["file"]: r for r in json.load(open(os.path.join(REP, "slicing.json")))}

# warna filamen dasar, ganti filamen (Z mm), dan cat
COLOR_PLAN = {
    "F01": ("Cokelat -> hijau", "ganti ke hijau di Z = 6,0", "dry-brush hijau tua di pangkal helai (opsional)"),
    "F02": ("Krem/cokelat muda", "-", "biji pakan cokelat, toples hijau tua, tutup abu tua"),
    "F03": ("Merah -> hijau", "ganti ke hijau di Z = 11,6 (atas dek)", "motor abu tua, tangki merah"),
    "F04": ("Hijau", "-", "atap hijau tua, list/pintu/jendela kuning gading, kaca jendela abu tua"),
    "F05": ("Putih", "-", "corak hitam (lihat render), moncong & ambing merah muda, kuku abu, mata hitam"),
    "F06": ("Putih", "-", "sama dengan F05, pola corak dibuat berbeda"),
    "F07": ("Putih/abu (dasar cat)", "-", "kaos hijau, celana biru tua, sepatu bot hitam, kulit sawo matang"),
    "F08": ("Krem jerami / cokelat muda", "-", "tanpa cat (warna filamen)"),
    "F09": ("Putih", "-", "tutup botol hijau"),
    "F10": ("Krem/cokelat muda", "-", "koin & tali emas, huruf Rp emas"),
    "F11": ("Cokelat tua", "-", "dry-brush cokelat sedang"),
    "F12": ("Zaitun/khaki -> hijau tua", "ganti ke hijau tua di Z = 19,6", "pipa abu/hijau muda, bak inlet/outlet abu beton, isi bak cokelat"),
    "F13": ("Hijau tua -> oranye", "ganti ke oranye di Z = 5,6", "inti api kuning"),
    "F14": ("Hijau zaitun", "-", "panel label krem, ikon tetes cokelat tua, tutup abu tua"),
    "F15": ("Cokelat -> kuning muda", "ganti ke kuning muda di Z = 3,0", "tunas hijau, ulir lampu perak"),
    "F16": ("Cokelat", "-", "lapisan selang-seling cokelat muda (dry-brush)"),
    "F17": ("Cokelat kraft", "-", "pita bawah hijau, gundukan butiran cokelat tua, tempel stiker label"),
    "F18": ("Hitam", "-", "tempel stiker tangkapan layar App/Website SI PATRIOT"),
}


def secs(t):
    s = 0
    for v, u in re.findall(r"(\d+)([dhms])", t or ""):
        s += int(v) * {"d": 86400, "h": 3600, "m": 60, "s": 1}[u]
    return s


def hm(s):
    return f"{s // 3600}j {(s % 3600) // 60}m"


def stl_check_md():
    lines = ["# Pemeriksaan STL (otomatis)", "",
             "Dibuat oleh `src/build_all.py` (trimesh + manifold3d). Kolom: tertutup (watertight), arah muka konsisten, "
             "volume positif, jumlah badan terpisah, Z minimum, muat bed 220x220x250, ketebalan lokal persentil-1 "
             "(ray ke dalam dari 4000 titik acak), luas muka menghadap bawah >45° di atas bed.", "",
             "| Berkas | Lolos | Tertutup | Volume (cm³) | Badan | Z min | Ukuran X×Y×Z (mm) | Tebal p1 (mm) | Overhang>45° (mm²) |",
             "|---|---|---|---|---|---|---|---|---|"]
    for r in CHK:
        lines.append(f"| `{r['file']}` | {'YA' if r['PASS'] else 'TIDAK'} | {'ya' if r['watertight'] else 'tidak'} | "
                     f"{r['volume_cm3']} | {r['bodies']} | {r['min_z']} | {' × '.join(str(x) for x in r['size_mm'])} | "
                     f"{r['thick_p1_mm']} | {r['overhang45_mm2']} |")
    n = sum(r["PASS"] for r in CHK)
    lines += ["", f"**{n}/{len(CHK)} berkas lolos semua syarat** (tertutup, volume > 0, satu badan, alas di Z = 0, "
              "valid sebagai manifold di manifold3d, muat bed).", "",
              "Catatan pembersihan mesh (sebelum ekspor): serpihan degenerat nol-volume dan rongga internal kecil hasil "
              "marching-cubes dibuang; volume yang dibuang dicatat di `stl_check.json` (kolom `cleanup`). Tidak ada badan "
              "nyata (> 1 mm³) yang dibuang diam-diam.", "",
              "Ketebalan persentil-1 di bawah 0,8 mm umumnya titik di tepi/sudut tajam (artefak metode ray), bukan dinding "
              "tipis; helai rumput dirancang >= 1,0 x 1,0 mm di ujung, huruf label >= 1,0 mm lebar garis."]
    open(os.path.join(REP, "stl_check.md"), "w").write("\n".join(lines) + "\n")


def bom_md():
    rows = []
    tot = {"figur": [0, 0.0], "dudukan": [0, 0.0], "alas": [0, 0.0]}
    for o in MAN["objects"]:
        r = SL.get(o["stl"], {})
        need = r.get("needs_support")
        t = r.get("time_support" if need else "time_nosupport", "")
        g = r.get("filament_g_support" if need else "filament_g_nosupport", 0) or 0
        tot["figur"][0] += secs(t); tot["figur"][1] += g
        cp = COLOR_PLAN.get(o["id"], ("", "", ""))
        rows.append(f"| {o['id']} | {o['name']} | **1** | {o['island']} | {o['size'][0]:.0f}×{o['size'][1]:.0f}×{o['size'][2]:.0f} | "
                    f"{'YA (' + str(r.get('support_pct_support')) + '%)' if need else 'tidak'} | {t} | {g} | {cp[0]} | {cp[1]} | {cp[2]} |")
    drows = []
    for i in MAN["islands"]:
        r = SL.get(i["stl"], {})
        t = r.get("time_nosupport", "")
        g = r.get("filament_g_nosupport", 0) or 0
        tot["dudukan"][0] += secs(t); tot["dudukan"][1] += g
        lab = " / ".join(l["text"].replace("\n", " ") for l in i["labels"])
        drows.append(f"| {i['id']} | {lab} | **1** | {i['size'][0]:.0f}×{i['size'][1]:.0f}×{i['size'][2]:.1f} | "
                     f"({i['center_from_front_left'][0]:.0f}; {i['center_from_front_left'][1]:.0f}) | {t} | {g} | "
                     f"krem -> hijau tua di Z = {i['color_change_z']:.1f} |")
    trows = []
    for tl in MAN.get("tiles", []):
        r = SL.get(tl["stl"], {})
        t = r.get("time_nosupport", "")
        g = r.get("filament_g_nosupport", 0) or 0
        tot["alas"][0] += secs(t); tot["alas"][1] += g
        trows.append(f"| {tl['id']} | `{tl['stl']}` | 1 | {t} | {g} |")
    kr = SL.get(MAN["tile_keys"]["stl"], {})
    nk = MAN["tile_keys"]["count"]
    kt = secs(kr.get("time_nosupport", "")) * nk
    kg = (kr.get("filament_g_nosupport", 0) or 0) * nk
    tot["alas"][0] += kt; tot["alas"][1] += kg
    out = ["# Daftar objek, jumlah cetak, dan rencana cetak", "",
           "Waktu & berat = estimasi PrusaSlicer 2.7 (nozzle 0,4; figur layer 0,12 mm, 3 perimeter, infill 15%; "
           "dudukan layer 0,2 mm; ubin 0,24 mm; PLA 1,24 g/cm³). Printer lain bisa berbeda ±30%.", "",
           "## Figur & alat (semua dicetak 1×)", "",
           "| ID | Objek | Jumlah | Dudukan | Ukuran (mm) | Support | Waktu | Gram | Filamen dasar | Ganti filamen | Cat / finishing |",
           "|---|---|---|---|---|---|---|---|---|---|---|"] + rows + [
           "", "Ringkas jumlah wajib: **2 sapi** (F05, F06 - pose berbeda), **1 peternak** (F07 badan + F08 caping), "
           "**1 mesin pencacah** (F03), **1 biodigester** (F12), **1 HP** (F18). Tidak ada sapi ketiga, HP kedua, laptop, "
           "monitor, tablet, atau panah.", "",
           "Alternatif sapi tanpa support di perut/ambing: `stl/sapi_varian_belah/` (2 belahan per sapi + 2 pin "
           "potongan filamen 1,75 mm × 12 mm). Masih perlu support kecil di bawah kaki (sisi dalam, tidak terlihat).", "",
           "## Dudukan krem berlabel (semua 1×)", "",
           "| ID | Label | Jumlah | Ukuran (mm) | Pusat dari pojok kiri-depan alas (mm) | Waktu | Gram | Ganti filamen |",
           "|---|---|---|---|---|---|---|---|"] + drows + [
           "", "Varian stiker (tanpa ganti filamen): `stl/dudukan_varian_stiker/` + `docs/stiker_label_A4_skala_1-1.pdf`.", "",
           "## Alas utama", "",
           "**Disarankan:** papan MDF/plywood 600 × 360 × 12 mm, tepi atas di-chamfer/diamplas, cat akrilik cokelat tanah "
           "(doff). Biaya & waktu jauh lebih kecil daripada mencetak.", "",
           "Opsional cetak 3D (PLA cokelat):", "", "| ID | Berkas | Jumlah | Waktu | Gram |", "|---|---|---|---|---|"] + trows + [
           f"| K01 | `{MAN['tile_keys']['stl']}` | {nk} | {hm(kt)} total | {kg:.0f} total |", "",
           "## Total estimasi", "",
           f"- Figur & alat: **{hm(tot['figur'][0])}**, ±{tot['figur'][1]:.0f} g",
           f"- Dudukan: **{hm(tot['dudukan'][0])}**, ±{tot['dudukan'][1]:.0f} g",
           f"- (Opsional) alas cetak 3D: **{hm(tot['alas'][0])}**, ±{tot['alas'][1]:.0f} g",
           f"- Total tanpa alas cetak: **{hm(tot['figur'][0] + tot['dudukan'][0])}** "
           f"(≈ {(tot['figur'][0] + tot['dudukan'][0]) / 3600 / 2:.0f} jam bila 2 printer jalan paralel)", ""]
    open(os.path.join(DOCS, "daftar_objek_dan_rencana_cetak.md"), "w").write("\n".join(out) + "\n")
    return tot


if __name__ == "__main__":
    stl_check_md()
    t = bom_md()
    print({k: (hm(v[0]), round(v[1])) for k, v in t.items()})
