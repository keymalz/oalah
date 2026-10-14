"""Palet warna diorama SI PATRIOT.

Setiap kunci warna dipakai untuk material render (Blender) dan untuk panduan
cat/filamen. Nilai hex diambil mendekati warna pada "Gambar 3. Skema Circular
Smart Farming" (hijau - putih/krem - cokelat yang terkontrol).
"""

PALETTE = {
    # key            hex        roughness  keterangan cat / filamen
    "cream":        ("#EFEADC", 0.55, "PLA krem/putih tulang (dudukan)"),
    "label":        ("#1E4D2B", 0.50, "PLA hijau tua (huruf label, ganti filamen)"),
    "base_brown":   ("#6B4A2F", 0.80, "Cat akrilik cokelat tanah (alas utama)"),
    "soil":         ("#7A5434", 0.90, "Cokelat tanah"),
    "grass":        ("#5FA03A", 0.70, "PLA hijau rumput"),
    "grass_dark":   ("#3E7E2B", 0.70, "Hijau rumput gelap (cat dry-brush)"),
    "burlap":       ("#B8935F", 0.85, "Cokelat karung goni"),
    "feed":         ("#9A7442", 0.90, "Cokelat pakan/konsentrat"),
    "jar_green":    ("#2F6B3A", 0.45, "Hijau tua wadah pakan"),
    "lid":          ("#D9C9A3", 0.50, "Krem tutup"),
    "machine_green":("#2E8B3E", 0.40, "Hijau mesin pencacah"),
    "machine_red":  ("#C62828", 0.40, "Merah rangka mesin pencacah"),
    "metal":        ("#8C9297", 0.35, "Abu-abu metal"),
    "dark_metal":   ("#3A3D40", 0.40, "Abu-abu gelap (motor)"),
    "barn_wall":    ("#3E8A4D", 0.60, "Hijau dinding kandang"),
    "barn_roof":    ("#1F5A35", 0.55, "Hijau tua atap kandang"),
    "trim_white":   ("#F4F4EF", 0.50, "Putih list kandang"),
    "barn_trim":    ("#D6B24A", 0.55, "Kuning gading list pintu/jendela kandang"),
    "door_dark":    ("#2B6A3B", 0.60, "Hijau pintu kandang"),
    "window":       ("#2A3B44", 0.30, "Abu kebiruan jendela"),
    "cow_white":    ("#F7F6F1", 0.60, "Putih sapi"),
    "cow_black":    ("#1C1C1C", 0.60, "Hitam corak sapi"),
    "cow_pink":     ("#E3A39A", 0.60, "Merah muda moncong & ambing"),
    "hoof":         ("#4A4440", 0.60, "Abu-cokelat kuku"),
    "skin":         ("#B97D52", 0.65, "Kulit peternak"),
    "shirt":        ("#2F7D46", 0.70, "Kaos hijau peternak"),
    "pants":        ("#33414E", 0.70, "Celana biru gelap"),
    "boots":        ("#1D1D1D", 0.50, "Sepatu bot hitam"),
    "straw":        ("#D7B56D", 0.80, "Caping anyaman"),
    "milk":         ("#FBFBF7", 0.20, "Putih susu"),
    "cap_green":    ("#2E7D32", 0.40, "Hijau tutup botol"),
    "money_bag":    ("#C9A35C", 0.80, "Krem kantong uang"),
    "gold":         ("#D9A926", 0.30, "Emas koin"),
    "manure":       ("#4A2F1B", 0.55, "Cokelat tua limbah"),
    "manure_light": ("#5E3C22", 0.65, "Cokelat limbah (sorotan)"),
    "digester":     ("#1F5A35", 0.45, "Hijau tua biodigester"),
    "digester_band":("#4E9A5B", 0.45, "Hijau muda sabuk biodigester"),
    "pipe":         ("#9AA1A6", 0.35, "Abu pipa"),
    "bag_white":    ("#B9BCB8", 0.75, "Abu muda kantong biodigester (terpal) - kontras dgn dudukan krem"),
    "pvc_white":    ("#E2E2DE", 0.40, "Putih pipa PVC"),
    "brass":        ("#9C7A3C", 0.35, "Kuningan katup gas"),
    "hose_red":     ("#B8322A", 0.45, "Merah selang gas"),
    "concrete":     ("#B9B6AE", 0.85, "Abu beton"),
    "flame":        ("#F39C1F", 0.40, "Oranye api"),
    "flame_core":   ("#FFD54A", 0.40, "Kuning inti api"),
    "slurry":       ("#3B2A1E", 0.25, "Cokelat kehitaman slurry (mengilap)"),
    "jerrycan":     ("#9C8A2E", 0.50, "Hijau zaitun jeriken slurry"),
    "digester_low": ("#8E7B32", 0.50, "Zaitun/khaki badan biodigester"),
    "bucket":       ("#5E7F8C", 0.50, "Abu kebiruan ember"),
    "bulb":         ("#FFF1A8", 0.15, "Kuning lampu"),
    "compost":      ("#6E4B2E", 0.90, "Cokelat limbah padat"),
    "compost_light":("#8A6340", 0.90, "Cokelat muda limbah padat"),
    "kraft":        ("#B98D58", 0.80, "Cokelat kraft karung pupuk"),
    "sticker":      ("#F6F3E8", 0.40, "Area stiker"),
    "granule":      ("#4B3420", 0.85, "Butiran pupuk"),
    "phone":        ("#1B1D20", 0.30, "Hitam HP"),
    "screen":       ("#DCEFE0", 0.20, "Area stiker layar"),
    "table":        ("#C9C2B5", 0.60, "Meja pameran"),
    "tile_brown":   ("#6B4A2F", 0.80, "PLA cokelat (ubin alas)"),
}

COLOR_KEYS = list(PALETTE.keys())
COLOR_INDEX = {k: i for i, k in enumerate(COLOR_KEYS)}


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
