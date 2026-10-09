"""Dudukan (pulau) krem dengan fillet atas, chamfer bawah, dan label.

Varian "timbul": huruf timbul 0,8 mm di atas bidang atas (ganti filamen ke
hijau tua tepat di Z = tebal dudukan -> huruf berwarna tanpa dicat).
Varian "stiker": cekungan 0,5 mm untuk stiker label (file stiker disediakan).
"""
import math
import numpy as np
from manifold3d import Manifold, CrossSection, JoinType
import geo
from geo import tag
import layout as L
from sdf import Func, mesh_sdf


def island_sdf(isl):
    shape = isl["shape"]
    H = isl["H"]
    rt = L.ISLAND_TOP_FILLET
    c = 0.6

    def f(p):
        d2 = shape.d(p[:, :2])
        wx = d2 + rt
        wy = p[:, 2] - (H - rt)
        d = np.minimum(np.maximum(wx, wy), 0) + np.sqrt(np.maximum(wx, 0) ** 2 + np.maximum(wy, 0) ** 2) - rt
        dch = (d2 + c - p[:, 2]) / math.sqrt(2)
        return np.maximum(d, dch)

    return Func(f, color="cream")


def label_pocket_cs(txt, cap, margin=2.2):
    cs = geo.text_cs(txt, cap)
    w, h = geo.text_size(cs)
    return geo.rrect_cs(w + 2 * margin, h + 2 * margin, 1.5), (w + 2 * margin, h + 2 * margin)


def build_island(isl, variant="timbul", h=0.3):
    ol = isl["shape"].outline()
    mn, mx = ol.min(0) - 2, ol.max(0) + 2
    v, f, c = mesh_sdf(island_sdf(isl), ((mn[0], mn[1], 0), (mx[0], mx[1], isl["H"] + 0.2)), h=h, target_faces=40000)
    # ratakan bidang atas tepat di Z = H (hasil marching cubes sudah sangat dekat)
    top = np.abs(v[:, 2] - isl["H"]) < 0.02
    v[top, 2] = isl["H"]
    m = geo.from_mesh(v, f, c)
    H = isl["H"]
    stickers = []
    if variant == "timbul":
        txt = []
        for (t, cap, x, y) in isl["labels"]:
            cs = geo.text_cs(t, cap).translate((x, y))
            txt.append(tag(cs.extrude(L.LABEL_RAISE + 0.3).translate((0, 0, H - 0.3)), "label"))
        m = geo.union([m] + txt)
    else:
        cuts = []
        for (t, cap, x, y) in isl["labels"]:
            cs, size = label_pocket_cs(t, cap)
            cuts.append(tag(cs.translate((x, y)).extrude(L.STICKER_DEPTH + 1.0).translate((0, 0, H - L.STICKER_DEPTH)), "sticker"))
            stickers.append(dict(text=t, w=round(size[0] - 0.4, 1), h=round(size[1] - 0.4, 1), cap=cap))
        m = m - geo.union(cuts)
    v, f, c = geo.to_arrays(m)
    return v, f, c, stickers
