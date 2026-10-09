"""Versi alas cetak 3D (opsional): alas 600 x 360 mm dipecah 3 x 2 ubin
200 x 180 mm (muat bed 220 x 220). Sambungan: kunci kupu-kupu (bowtie)
yang dimasukkan dari bawah + lem. Bagian atas ubin diberi cekungan
penempatan 0,6 mm sesuai jejak setiap dudukan (dudukan langsung pas posisi).
"""
import numpy as np
from manifold3d import Manifold, CrossSection, FillRule, JoinType
import geo
from geo import tag
import layout as L

TILE_T = 8.0
KEY_T = 4.0
KEY_CLEAR = 0.2
POCKET_DEPTH = 0.6
POCKET_CLEAR = 0.3
NX, NY = 3, 2


def bowtie_cs(L_=30.0, w_end=14.0, w_mid=7.0, r=1.0):
    pts = np.array([(-L_ / 2, -w_end / 2), (0, -w_mid / 2), (L_ / 2, -w_end / 2),
                    (L_ / 2, w_end / 2), (0, w_mid / 2), (-L_ / 2, w_end / 2)])
    cs = CrossSection([pts], FillRule.Positive)
    return cs.offset(-r, JoinType.Round).offset(r, JoinType.Round)


def key_positions():
    """(x, y, sudut) kunci; sumbu panjang tegak lurus garis sambungan."""
    tw, td = L.BASE_W / NX, L.BASE_D / NY
    keys = []
    for i in range(1, NX):
        x = -L.BASE_W / 2 + i * tw
        for y in (-135.0, -45.0, 45.0, 135.0):
            keys.append((x, y, 0.0))
    for j in range(1, NY):
        y = -L.BASE_D / 2 + j * td
        for k in range(NX):
            x0 = -L.BASE_W / 2 + k * tw
            for fx in (0.28, 0.72):
                keys.append((x0 + fx * tw, y, 90.0))
    return keys


def build_key():
    m = tag(bowtie_cs().extrude(KEY_T), "tile_brown")
    return geo.to_arrays(m)


def island_footprints():
    out = []
    for isl in L.ISLANDS:
        ol = isl["shape"].outline(res=0.5)
        pts = ol + np.array(isl["pos"])
        keep = [0]
        for i in range(1, len(pts)):
            if np.linalg.norm(pts[i] - pts[keep[-1]]) > 0.25:
                keep.append(i)
        pts = pts[keep]
        cs = CrossSection([pts], FillRule.Positive)
        if cs.area() <= 0:
            cs = CrossSection([pts[::-1]], FillRule.Positive)
        out.append(cs.offset(POCKET_CLEAR, JoinType.Round, circular_segments=32).simplify(0.02))
    return out


def build_tiles():
    tw, td = L.BASE_W / NX, L.BASE_D / NY
    pockets = geo.union([tag(cs.extrude(POCKET_DEPTH + 1).translate((0, 0, TILE_T - POCKET_DEPTH)), "cream")
                         for cs in island_footprints()])
    keyp = []
    for (x, y, a) in key_positions():
        cs = bowtie_cs().offset(KEY_CLEAR, JoinType.Round).rotate(a).translate((x, y))
        keyp.append(tag(cs.extrude(KEY_T + KEY_CLEAR + 1.0).translate((0, 0, -1.0)), "tile_brown"))
    keyp = geo.union(keyp)
    tiles = []
    for j in range(NY):
        for i in range(NX):
            x0 = -L.BASE_W / 2 + i * tw
            y0 = -L.BASE_D / 2 + j * td
            t = tag(Manifold.cube((tw, td, TILE_T)).translate((x0, y0, 0)), "tile_brown")
            # chamfer 1 mm pada tepi luar atas alas
            ch = []
            if i == 0:
                ch.append((x0, "x-"))
            if i == NX - 1:
                ch.append((x0 + tw, "x+"))
            if j == 0:
                ch.append((y0, "y-"))
            if j == NY - 1:
                ch.append((y0 + td, "y+"))
            for (c, side) in ch:
                if side in ("x-", "x+"):
                    w3 = Manifold.cube((3.0, td + 2, 3.0), center=True).rotate((0, 45, 0)).translate((c, y0 + td / 2, TILE_T))
                else:
                    w3 = Manifold.cube((tw + 2, 3.0, 3.0), center=True).rotate((45, 0, 0)).translate((x0 + tw / 2, c, TILE_T))
                t = t - w3
            t = t - pockets - keyp
            name = f"T{j + 1}{i + 1}"
            # pindahkan ke origin lokal (pojok kiri depan di 0,0)
            tiles.append((name, (x0, y0), t.translate((-x0, -y0, 0))))
    return [(n, o, geo.to_arrays(m)) for (n, o, m) in tiles]
