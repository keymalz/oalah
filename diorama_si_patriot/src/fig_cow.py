"""Sapi perah (Holstein) bergaya miniatur. Dua pose berbeda, gaya sama.

Koordinat lokal: +X = arah kepala, Y = samping, Z = atas, kuku di Z = 0.
Skala sekitar 1:40 (panjang badan +-62 mm, tinggi punggung +-37 mm).
"""
import numpy as np
from sdf import (Sphere, Ellipsoid, RoundBox, Capsule, Cylinder, SU, Union,
                 Xform, rot_matrix, Mirror, Paint, mesh_sdf)


def _leg(top, knee, foot, r_top, r_knee, r_foot, color="cow_white"):
    """Kaki: paha -> lutut -> kuku (kuku berwarna 'hoof')."""
    fx, fy = foot[0], foot[1]
    upper = Capsule(top, knee, r_top, r_knee, color=color)
    lower = Capsule(knee, (fx, fy, 4.2), r_knee, r_foot, color=color)
    hoof = Cylinder((fx + 0.3, fy, 0.0), r_foot + 0.25, 3.0, re=0.7, color="hoof")
    return SU(1.2, upper, lower, hoof)


def cow_sdf(pose="A"):
    # ---------------- badan
    barrel = Ellipsoid((0.5, 0, 26.5), (19.5, 9.6, 9.4), color="cow_white")
    chest = Ellipsoid((13.0, 0, 27.5), (9.0, 8.6, 9.6), color="cow_white")
    hips = RoundBox((-13.5, 0, 28.0), (7.5, 9.0, 8.2), 4.8, color="cow_white")
    hook_bones = Mirror(Sphere((-13.0, 7.2, 34.2), 2.6, color="cow_white"))
    back = RoundBox((0, 0, 32.5), (18.5, 7.0, 3.8), 3.6, color="cow_white")
    belly = Ellipsoid((1.0, 0, 21.5), (14.0, 8.4, 5.0), color="cow_white")
    body = SU(3.5, barrel, chest, hips, back, belly, hook_bones)

    # ---------------- ambing + puting (ciri sapi perah)
    udder = Ellipsoid((-9.5, 0, 18.0), (6.4, 5.6, 4.8), color="cow_pink")
    teats = Union([Capsule((-9.5 + dx, dy, 15.0), (-9.5 + dx, dy, 11.6), 1.15, 1.0, color="cow_pink")
                   for dx in (-2.4, 2.4) for dy in (-2.5, 2.5)])
    udder = SU(1.0, udder, teats)

    # ---------------- kaki (pose)
    if pose == "A":
        fl = ((13.5, 5.2, 22), (14.0, 5.0, 11.5), (14.0, 5.0, 0))
        fr = ((13.5, -5.2, 22), (14.5, -5.0, 11.5), (15.0, -5.0, 0))
        hl = ((-14.5, 5.6, 25), (-17.8, 5.4, 11.5), (-16.0, 5.2, 0))
        hr = ((-14.5, -5.6, 25), (-17.5, -5.4, 11.5), (-15.5, -5.2, 0))
    else:  # pose B: kaki depan kanan melangkah maju, kaki belakang sedikit lebar
        fl = ((13.5, 5.2, 22), (13.0, 5.0, 11.5), (12.0, 5.0, 0))
        fr = ((13.5, -5.2, 22), (16.5, -5.2, 11.0), (18.5, -5.4, 0))
        hl = ((-14.5, 5.6, 25), (-18.5, 5.8, 11.5), (-17.5, 6.0, 0))
        hr = ((-14.5, -5.6, 25), (-17.0, -5.4, 11.5), (-14.0, -5.2, 0))
    legs = Union([_leg(*l, 3.6, 2.7, 2.35) for l in (fl, fr, hl, hr)])

    # ---------------- ekor (menempel di paha belakang supaya kokoh dicetak)
    tail = SU(1.4,
              Capsule((-20.5, 0, 34.5), (-22.6, 0, 26.0), 1.7, 1.55, color="cow_white"),
              Capsule((-22.6, 0, 26.0), (-22.4, 0, 14.5), 1.55, 1.45, color="cow_white"),
              Ellipsoid((-22.2, 0, 12.6), (2.0, 2.0, 3.2), color="cow_black"))
    if pose == "B":
        root = np.array([-20.5, 0, 34.5])
        Rt = rot_matrix("x", -9)
        tail = Xform(tail, Rt, root - Rt @ root)

    # ---------------- leher + kepala
    neck = Capsule((14.5, 0, 30.5), (24.0, 0, 34.5), 7.6, 5.3, color="cow_white")
    dewlap = Ellipsoid((20.0, 0, 26.5), (5.0, 3.6, 5.5), color="cow_white")
    skull = Capsule((26.8, 0, 38.0), (33.8, 0, 30.2), 5.2, 4.0, color="cow_white")
    eyes = Mirror(Sphere((29.0, 4.6, 36.0), 1.0, color="cow_black"))
    cheeks = Mirror(Ellipsoid((28.5, 2.4, 33.8), (3.6, 2.8, 3.6), color="cow_white"))
    muzzle = Ellipsoid((35.0, 0, 28.4), (3.6, 4.3, 3.3), color="cow_pink")
    ears = Mirror(Xform(Ellipsoid((0, 0, 0), (2.2, 4.0, 1.35), color="cow_white"),
                        rot_matrix("x", -18), np.array([26.6, 7.3, 37.6])))
    horns = Mirror(Capsule((26.6, 3.2, 41.2), (26.2, 4.6, 42.4), 1.2, 0.9, color="hoof"))
    head = SU(1.6, skull, cheeks, muzzle, ears, horns)
    head = Union([head, eyes])

    if pose == "A":
        # kepala sedikit menoleh ke arah penonton (-Y) dan terangkat
        pivot = np.array([22.0, 0, 33.0])
        R = rot_matrix("z", -22) @ rot_matrix("y", -6)
        head = Xform(head, R, pivot - R @ pivot)
    else:
        # kepala menunduk seperti sedang makan, menoleh sedikit
        pivot = np.array([20.5, 0, 31.5])
        R = rot_matrix("z", 14) @ rot_matrix("y", 30)
        head = Xform(head, R, pivot - R @ pivot)
        neck = Xform(neck, rot_matrix("y", 16), pivot - rot_matrix("y", 16) @ pivot)

    neckhead = SU(2.4, neck, dewlap, head)
    cow = SU(2.6, body, neckhead, udder)
    cow = SU(2.0, cow, legs)
    cow = SU(1.0, cow, tail)
    return cow


SCALE = 0.9  # 1,0 = panjang +-63 mm; 0,9 dipilih agar serasi dengan kandang


def build_cow(pose="A", h=0.22, target_faces=90000, scale=SCALE):
    node = cow_sdf(pose)
    v, f, c = mesh_sdf(node, ((-27, -13, 0), (43, 13, 47)), h=h, target_faces=target_faces)
    return v * scale, f, c
