"""Stasiun pakan: petak rumput hijauan, kelompok pakan ternak, mesin pencacah."""
import math
import numpy as np
from manifold3d import Manifold, CrossSection, FillRule, JoinType
import geo
from geo import tag, box, union, cyl, rbox_xy
from sdf import (Sphere, Ellipsoid, RoundBox, Capsule, Cylinder, Cone, Torus, SU, Union,
                 Displace, Inter, Diff, HalfSpace, Func, vnoise3, mesh_sdf)


# =============================================================== rumput
def _blade(base, h, lean_dir, lean_deg, w0=2.5, t0=1.4, w1=1.05, t1=1.0, z0=0.0, twist=0.0):
    """Helai rumput pipih meruncing (min. 1,0 mm di ujung -> tercetak nozzle 0,4)."""
    bx, by = base
    ld = np.radians(lean_dir)
    off = math.tan(math.radians(lean_deg)) * h
    tx, ty = bx + off * math.cos(ld), by + off * math.sin(ld)
    # orientasi lebar helai tegak lurus arah condong + sedikit puntiran
    ang = math.degrees(ld) + 90 + twist
    b = Manifold.cube((w0, t0, 0.05), center=True).rotate((0, 0, ang)).translate((bx, by, z0))
    m = Manifold.cube((w0 * 0.78, t0 * 0.9, 0.05), center=True).rotate((0, 0, ang + twist * 0.5)) \
        .translate((bx + (tx - bx) * 0.55, by + (ty - by) * 0.55, z0 + h * 0.55))
    t = Manifold.cube((w1, t1, 0.05), center=True).rotate((0, 0, ang + twist)).translate((tx, ty, z0 + h))
    return Manifold.batch_hull([b, m]) + Manifold.batch_hull([m, t])


def build_grass(seed=3):
    rng = np.random.default_rng(seed)
    W, Dp, Hs = 68.0, 54.0, 6.0
    soil = rbox_xy((W, Dp, Hs), 3.0, (0, 0, 0), color="soil")
    blades = []
    nx, ny = 10, 8
    for i in range(nx):
        for j in range(ny):
            cx = -W / 2 + 4.2 + (W - 8.4) * (i + 0.5 * (j % 2) * 0.9) / (nx - 0.55)
            cy = -Dp / 2 + 4.2 + (Dp - 8.4) * j / (ny - 1)
            cx += rng.uniform(-1.2, 1.2)
            cy += rng.uniform(-1.2, 1.2)
            cx = float(np.clip(cx, -W / 2 + 3.6, W / 2 - 3.6))
            nb = int(rng.integers(6, 9))
            edge = min(W / 2 - abs(cx), Dp / 2 - abs(cy))
            for k in range(nb):
                a = rng.uniform(0, 360)
                r = rng.uniform(0.0, 1.6)
                bx, by = cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))
                h = rng.uniform(12.0, 21.0)
                lean = rng.uniform(5, 21)
                # helai di tepi condong ke luar sedikit, tidak keluar dari tanah
                lean_dir = a
                tipx = bx + math.tan(math.radians(lean)) * h * math.cos(math.radians(lean_dir))
                tipy = by + math.tan(math.radians(lean)) * h * math.sin(math.radians(lean_dir))
                if abs(tipx) > W / 2 + 1.0 or abs(tipy) > Dp / 2 + 1.0:
                    lean_dir = (a + 180) % 360
                blades.append(_blade((bx, by), h, lean_dir, lean, z0=Hs - 0.6, twist=rng.uniform(-25, 25)))
    g = tag(union(blades), "grass")
    return geo.to_arrays(union([soil, g]))


# =============================================================== pakan ternak
def feed_group_sdf():
    # karung goni terbuka berisi pakan
    sack_body = SU(3.0,
                   Cylinder((0, 0, 0), 13.0, 27.0, re=4.0, color="burlap"),
                   Ellipsoid((0, 0, 12.0), (14.2, 13.6, 11.0), color="burlap"))
    rim = Torus((0, 0, 27.0), 11.6, 2.1, color="burlap")
    hollow = Cylinder((0, 0, 25.5), 10.6, 6.0, re=1.0, color="burlap")
    grains = Displace(Ellipsoid((0, 0, 26.6), (11.0, 11.0, 3.6), color="feed"),
                      lambda p: 0.35 * vnoise3(p, 0.9, 1))
    sack = SU(1.2, sack_body, rim)
    sack = Diff(sack, hollow)
    sack = Union([sack, grains])
    # kerut karung (alur vertikal halus)
    sack = Displace(sack, lambda p: 0.18 * np.sin(np.arctan2(p[:, 1], p[:, 0]) * 9) * np.clip(p[:, 2] / 25, 0, 1))
    # wadah/toples pakan (konsentrat)
    jx, jy = 20.0, -6.0
    jar = Cylinder((jx, jy, 0), 7.6, 19.0, re=1.6, color="jar_green")
    band = Cylinder((jx, jy, 5.0), 7.85, 8.0, re=0.4, color="lid")
    lid = Cylinder((jx, jy, 18.4), 6.9, 3.6, re=1.0, color="dark_metal")
    jar = Union([jar, band, lid])
    # gundukan pakan kecil di depan (penghubung + detail)
    pile = Displace(SU(1.5,
                       Ellipsoid((6.0, -14.5, 0.0), (8.5, 6.0, 3.8), color="feed"),
                       Ellipsoid((13.0, -16.0, 0.0), (4.5, 3.8, 2.6), color="feed")),
                    lambda p: 0.3 * vnoise3(p, 0.8, 2))
    return SU(1.2, sack, pile) | jar


def build_feed_group():
    return mesh_sdf(feed_group_sdf(), ((-16, -23, 0), (29, 16, 33)), h=0.2, target_faces=70000)


# =============================================================== mesin pencacah
def build_chopper():
    """Mesin pencacah rumput (chopper) miniatur: rangka merah, rumah pemotong &
    corong hijau, motor penggerak, saluran keluar. Lokal: corong di atas,
    saluran keluar menghadap -X. Panjang 42 mm, tinggi 31 mm."""
    parts = []
    L, Wd, Hl = 34.0, 20.0, 10.0  # rangka
    s = 2.4
    # kaki + rel atas + rel bawah
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(box((s, s, Hl), (sx * (L / 2 - s / 2), sy * (Wd / 2 - s / 2), 0), "machine_red", base=True))
    for sy in (-1, 1):
        parts.append(box((L, s, s), (0, sy * (Wd / 2 - s / 2), Hl - s), "machine_red", base=True))
        # rel bawah = skid di atas bed (daya rekat cetak baik)
        parts.append(box((L + 4.0, s + 0.6, 1.8), (0, sy * (Wd / 2 - s / 2), 0), "machine_red", base=True))
    for sx in (-1, 1):
        parts.append(box((s, Wd, s), (sx * (L / 2 - s / 2), 0, Hl - s), "machine_red", base=True))
    # pelat melintang (penopang dek: jembatan cetak <= 9 mm)
    for px in (-12.5, -4.5, 4.0, 12.0):
        parts.append(box((1.8, Wd, Hl), (px, 0, 0), "machine_red", base=True))
    # dek
    parts.append(box((L, Wd, 1.9), (0, 0, Hl - 0.3), "machine_red", base=True))
    deck_top = Hl + 1.6
    # rumah pemotong (drum horizontal, sumbu Y) di atas dek, alas rata
    R = 7.0
    drum = Manifold.cylinder(Wd - 4.0, R, R, 48, center=True).rotate((90, 0, 0)).translate((6.0, 0, deck_top + R - 0.8))
    drum = drum ^ Manifold.cube((40, 40, 40), center=False).translate((-20, -20, deck_top - 0.4))
    parts.append(tag(drum, "machine_green"))
    parts.append(box((2 * R, Wd - 4.0, 3.4), (6.0, 0, deck_top - 0.4), "machine_green", base=True))
    # tutup samping drum (piringan) sedikit lebih besar
    for sy in (-1, 1):
        cap = Manifold.cylinder(1.2, R + 0.6, R + 0.6, 48, center=True).rotate((90, 0, 0)) \
            .translate((6.0, sy * (Wd / 2 - 2.0 + 0.4), deck_top + R - 0.8))
        cap = cap ^ Manifold.cube((40, 40, 40), center=False).translate((-20, -20, deck_top - 0.4))
        parts.append(tag(cap, "machine_green"))
    # corong pemasukan: frustum miring ke belakang, rongga di atas
    zb = deck_top + 2 * R - 2.5
    bot = Manifold.cube((8.0, 10.0, 0.1), center=True).translate((6.0, 0, zb))
    top = Manifold.cube((14.0, 15.0, 0.1), center=True).translate((8.5, 0, zb + 9.5))
    hopper = Manifold.batch_hull([bot, top])
    ibot = Manifold.cube((5.6, 7.6, 0.1), center=True).translate((6.4, 0, zb + 3.0))
    itop = Manifold.cube((11.4, 12.4, 0.1), center=True).translate((8.5, 0, zb + 9.6))
    hopper = hopper - Manifold.batch_hull([ibot, itop])
    parts.append(tag(hopper, "machine_green"))
    # bibir corong
    rim = Manifold.batch_hull([Manifold.cube((14.0, 15.0, 0.1), center=True).translate((8.5, 0, zb + 8.6)),
                               Manifold.cube((15.0, 16.0, 0.6), center=True).translate((8.5, 0, zb + 9.3))]) - \
        Manifold.cube((11.4, 12.4, 4.0), center=True).translate((8.5, 0, zb + 10.0))
    parts.append(tag(rim, "machine_green"))
    # saluran keluar: kanal U menurun ke arah -X (sudut 55 derajat dari horizontal)
    chute = Manifold.cube((10.0, 9.0, 7.0), center=True)
    chute = chute - Manifold.cube((12.0, 6.0, 5.0), center=True).translate((0, 0, 1.6))
    chute = chute.rotate((0, -50, 0)).translate((-2.6, 0, deck_top + 6.0))
    chute = chute ^ Manifold.cube((60, 60, 60), center=False).translate((-30, -30, deck_top - 0.4))
    parts.append(tag(chute, "machine_green"))
    # motor penggerak (mesin bensin) di dek belakang (-X)
    mx = -10.5
    parts.append(geo.rbox((11.0, 12.0, 8.4), 1.2, (mx, -1.5, deck_top - 0.4), color="dark_metal", base=True))
    parts.append(geo.rbox((9.0, 9.0, 4.0), 1.5, (mx + 0.5, -1.5, deck_top + 7.6), color="machine_red", base=True))
    parts.append(cyl(2.6, 3.0, (mx - 2.0, -1.5, deck_top + 11.2), color="dark_metal"))
    # tutup sabuk (belt guard) di sisi +Y
    bg = Manifold.batch_hull([Manifold.cylinder(2.2, 4.2, 4.2, 32, center=True).rotate((90, 0, 0)).translate((mx, 0, deck_top + 4.2)),
                              Manifold.cylinder(2.2, 4.8, 4.8, 32, center=True).rotate((90, 0, 0)).translate((6.0, 0, deck_top + R - 0.8))])
    bg = bg + Manifold.cube((6.0 - mx, 2.2, 4.8), center=False).translate((mx, -1.1, deck_top - 0.4))
    bg = bg.translate((0, Wd / 2 - 1.2, 0)) ^ Manifold.cube((60, 60, 60), center=False).translate((-30, -30, deck_top - 0.4))
    parts.append(tag(bg, "machine_red"))
    return geo.to_arrays(union(parts))
