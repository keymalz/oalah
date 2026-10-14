"""Tata letak diorama: alas utama 600 x 360 mm, dudukan (pulau) krem berlabel,
dan posisi setiap figur. Origin = pusat permukaan atas alas utama.
+X = kanan (dilihat dari depan meja), +Y = ke belakang, +Z = atas.

Susunan mengikuti "Gambar 3. Skema Circular Smart Farming":
pakan kiri/atas, kandang kanan/atas, susu & pendapatan kanan, limbah
kanan/bawah, biodigester bawah, keluaran biogas/slurry/pupuk kiri/bawah,
pupuk organik kiri, pencatatan digital di tengah. Tanpa panah atau jalur.
"""
import math
import numpy as np

BASE_W, BASE_D, BASE_T = 600.0, 360.0, 12.0   # papan fisik (MDF/plywood) 12 mm
MIN_EDGE_MARGIN = 12.0
ISLAND_TOP_FILLET = 2.5
LABEL_RAISE = 0.8          # tinggi huruf timbul (4 layer @0,2 mm)
STICKER_DEPTH = 0.5        # varian stiker: cekungan 0,5 mm


# ---------------------------------------------------------------- bentuk 2D
def sd_rrect(p, c, w, d, r, rot=0.0):
    q = p - np.asarray(c)
    if rot:
        a = math.radians(rot)
        R = np.array([[math.cos(a), math.sin(a)], [-math.sin(a), math.cos(a)]])
        q = q @ R.T
    hx, hy = w / 2 - r, d / 2 - r
    qx, qy = np.abs(q[:, 0]) - hx, np.abs(q[:, 1]) - hy
    out = np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2)
    return out + np.minimum(np.maximum(qx, qy), 0) - r


def sd_circle(p, c, r):
    return np.linalg.norm(p - np.asarray(c), axis=1) - r


def sd_trap(p, c, w_front, w_back, d, r):
    """Trapesium membulat (depan lebih lebar), -Y = depan."""
    q = p - np.asarray(c)
    # poligon lalu offset r
    hy = d / 2 - r
    a = w_front / 2 - r
    b = w_back / 2 - r
    pts = np.array([(-a, -hy), (a, -hy), (b, hy), (-b, hy)])
    return _sd_poly(q, pts) - r


def _sd_poly(p, v):
    n = len(v)
    d = np.full(len(p), np.inf)
    s = np.ones(len(p))
    for i in range(n):
        a, b = v[i], v[(i + 1) % n]
        e = b - a
        w = p - a
        t = np.clip((w @ e) / (e @ e), 0, 1)
        bvec = w - np.outer(t, e)
        d = np.minimum(d, np.einsum("ij,ij->i", bvec, bvec))
        c1 = p[:, 1] >= a[1]
        c2 = p[:, 1] < b[1]
        c3 = e[0] * w[:, 1] > e[1] * w[:, 0]
        flip = (c1 & c2 & c3) | (~c1 & ~c2 & ~c3)
        s = np.where(flip, -s, s)
    return s * np.sqrt(d)


def smin(a, b, k):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b * (1 - h) + a * h - k * h * (1 - h)


class Shape2D:
    """Gabungan halus beberapa primitif 2D (koordinat lokal dudukan)."""

    def __init__(self, prims, k=10.0):
        self.prims = prims
        self.k = k

    def d(self, p):
        r = None
        for kind, args in self.prims:
            if kind == "rrect":
                v = sd_rrect(p, *args)
            elif kind == "circle":
                v = sd_circle(p, *args)
            elif kind == "trap":
                v = sd_trap(p, *args)
            r = v if r is None else smin(r, v, self.k)
        return r

    def outline(self, n=720, extent=200, res=0.5):
        """Kontur (untuk gambar & template) via marching squares."""
        from skimage.measure import find_contours
        xs = np.arange(-extent, extent, res)
        X, Y = np.meshgrid(xs, xs, indexing="ij")
        D = self.d(np.stack([X.ravel(), Y.ravel()], 1)).reshape(X.shape)
        cs = find_contours(D, 0.0)
        c = max(cs, key=len)
        return np.stack([xs[0] + c[:, 0] * res, xs[0] + c[:, 1] * res], 1)


# ---------------------------------------------------------------- dudukan
# figur: (id_figur, dx, dy, rot_z_derajat) relatif pusat dudukan
# label: (teks, tinggi_huruf_kapital, x, y)
ISLANDS = [
    dict(id="D01", name="PAKAN HIJAUAN", pos=(-170.0, 108.0), H=10.0,
         shape=Shape2D([("rrect", ((0, 0), 94, 86, 16))]),
         labels=[("PAKAN HIJAUAN", 6.0, 0, -33.0)],
         figures=[("F01", 0.0, 9.0, 0.0)]),
    dict(id="D02", name="PAKAN TERNAK & MESIN PENCACAH", pos=(-42.0, 126.0), H=22.0,
         shape=Shape2D([("rrect", ((0, 0), 112, 72, 18)), ("rrect", ((0, 8), 92, 64, 20))], k=8),
         labels=[("MESIN\nPENCACAH", 5.0, -27.0, -22.5), ("PAKAN\nTERNAK", 5.0, 28.0, -22.5)],
         figures=[("F03", -27.0, 10.0, 180.0), ("F02", 22.0, 9.0, 0.0)]),
    dict(id="D03", name="PRODUKSI TERNAK", pos=(110.0, 99.0), H=10.0,
         shape=Shape2D([("rrect", ((0, 0), 172, 136, 28))]),
         labels=[("PRODUKSI TERNAK", 6.0, -30.0, -56.0)],
         figures=[("F04", 12.0, 16.0, -15.0), ("F05", -56.0, 13.0, 232.0), ("F06", 41.0, -48.5, -14.0),
                  ("F07", -12.0, -35.0, -15.0)]),
    dict(id="D04", name="SUSU SAPI", pos=(242.0, 76.0), H=10.0,
         shape=Shape2D([("circle", ((0, 0), 34.0))]),
         labels=[("SUSU SAPI", 5.5, 0, -16.5)],
         figures=[("F09", 0.0, 9.0, 0.0)]),
    dict(id="D05", name="PENDAPATAN PETERNAK", pos=(250.0, -14.0), H=10.0,
         shape=Shape2D([("circle", ((0, 0), 36.0))]),
         labels=[("PENDAPATAN\nPETERNAK", 5.0, 0, -15.0)],
         figures=[("F10", -5.0, 12.5, 0.0)]),
    dict(id="D06", name="LIMBAH TERNAK", pos=(145.0, -74.0), H=10.0,
         shape=Shape2D([("trap", ((0, 0), 92, 76, 74, 18))]),
         labels=[("LIMBAH TERNAK", 5.5, 0, -25.0)],
         figures=[("F11", 0.0, 9.0, 0.0)]),
    dict(id="D07", name="BIODIGESTER", pos=(4.0, -113.0), H=10.0,
         shape=Shape2D([("trap", ((0, 0), 124, 112, 104, 22))]),
         labels=[("BIODIGESTER", 6.5, 0, -40.0)],
         figures=[("F12", 2.5, 7.0, 0.0)]),
    dict(id="D08", name="HASIL PENGOLAHAN LIMBAH", pos=(-172.0, -88.0), H=10.0,
         shape=Shape2D([("rrect", ((0, 4), 136, 84, 28)), ("rrect", ((10, -30), 104, 58, 22)),
                        ("circle", ((-48, -24), 27))], k=14),
         labels=[("BIOGAS", 5.0, -20.0, 15.0), ("SLURRY", 5.0, 50.0, 13.0),
                 ("ENERGI &\nPUPUK", 5.0, -46.0, -36.0), ("LIMBAH PADAT", 5.5, 14.0, -50.0)],
         figures=[("F13", -20.0, 31.0, 0.0), ("F14", 50.0, 28.0, -8.0), ("F15", -46.0, -15.0, 0.0),
                  ("F16", 14.0, -24.0, 0.0)]),
    dict(id="D09", name="PUPUK ORGANIK", pos=(-256.0, 30.0), H=13.0,
         shape=Shape2D([("rrect", ((0, 0), 58, 64, 17))]),
         labels=[("PUPUK\nORGANIK", 5.0, 0, -19.5)],
         figures=[("F17", 0.0, 13.5, 0.0)]),
    dict(id="D10", name="PENCATATAN DIGITAL SI PATRIOT", pos=(-20.0, -12.0), H=14.0,
         shape=Shape2D([("rrect", ((0, 0), 104, 80, 20))]),
         labels=[("PENCATATAN DIGITAL\nSI PATRIOT", 5.0, 0, -23.0)],
         figures=[("F18", 0.0, 6.0, 0.0)]),
]

# ---------------------------------------------------------------- figur
# id: (nama, modul:fungsi, jumlah cetak, keterangan)
FIGURES = {
    "F01": ("Rumput pakan hijauan", "fig_feed:build_grass"),
    "F02": ("Pakan ternak (karung + wadah)", "fig_feed:build_feed_group"),
    "F03": ("Mesin pencacah rumput", "fig_feed:build_chopper"),
    "F04": ("Kandang", "fig_barn:build_barn"),
    "F05": ("Sapi perah A (berdiri, menoleh)", "fig_cow:build_cow:A"),
    "F06": ("Sapi perah B (menunduk makan)", "fig_cow:build_cow:B"),
    "F07": ("Peternak - badan", "fig_farmer:build_farmer_body"),
    "F08": ("Peternak - caping", "fig_farmer:build_caping"),
    "F09": ("Botol susu (3 botol menyatu)", "fig_misc:build_milk"),
    "F10": ("Kantong uang + koin", "fig_misc:build_money"),
    "F11": ("Limbah ternak", "fig_misc:build_manure"),
    "F12": ("Biodigester kantong (balon)", "fig_misc:build_biodigester_kantong"),
    "F13": ("Biogas (api di tungku)", "fig_misc:build_biogas"),
    "F14": ("Slurry (jeriken)", "fig_misc:build_jerrycan"),
    "F15": ("Energi & pupuk (lampu + tunas)", "fig_misc:build_energy"),
    "F16": ("Limbah padat (blok berlapis)", "fig_misc:build_compost"),
    "F17": ("Pupuk organik (karung kraft)", "fig_misc:build_fertilizer"),
    "F18": ("HP SI PATRIOT + dudukan", "fig_misc:build_phone"),
}
# caping dipasang di atas kepala peternak (F07)
ATTACH = {"F08": ("F07", (0.0, 0.0, (38.4 - 0.8) * 0.92))}


def island_by_id(i):
    return next(d for d in ISLANDS if d["id"] == i)
