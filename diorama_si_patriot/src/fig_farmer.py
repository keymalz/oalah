"""Figur peternak (skala +-1:40, tinggi 43 mm dengan caping).

Badan dan caping dicetak terpisah: caping dicetak dengan tepi di bawah
(tanpa support) lalu dilem di atas kepala yang rata. Figur menghadap -Y.
"""
import numpy as np
from sdf import (Sphere, Ellipsoid, RoundBox, Capsule, Cylinder, Cone, SU, Union,
                 Mirror, Inter, HalfSpace, Diff, mesh_sdf)
import geo

HEAD_TOP = 38.4
SCALE = 0.92   # tinggi akhir +-41 mm termasuk caping


def farmer_body_sdf():
    base = Cylinder((0, 0, 0), 1.0, 1.6, re=0.5, color="cream")
    # alas elips: skala via ellipsoid terpotong
    base = Inter(Ellipsoid((0, 0, 0.8), (9.0, 7.0, 2.4), color="cream"),
                 Cylinder((0, 0, 0), 20, 1.6, re=0.0, color="cream"))
    boots = Mirror(SU(0.8,
                      RoundBox((2.25, -0.6, 3.4), (1.75, 2.6, 1.9), 1.2, color="boots"),
                      Capsule((2.2, 0.2, 3.0), (2.15, 0.1, 7.6), 1.85, 1.75, color="boots")), axis=0)
    legs = Mirror(Capsule((2.1, 0.1, 7.0), (2.15, 0.1, 18.5), 1.85, 2.25, color="pants"), axis=0)
    hips = Ellipsoid((0, 0.1, 19.2), (4.4, 2.7, 2.9), color="pants")
    torso = SU(1.6,
               RoundBox((0, 0.1, 25.6), (4.2, 2.55, 5.4), 2.0, color="shirt"),
               Ellipsoid((0, 0.1, 30.2), (5.3, 2.7, 1.9), color="shirt"))
    belt = Cylinder((0, 0.1, 20.6), 4.15, 0.9, re=0.3, color="pants")
    # lengan menempel ke badan (kokoh, tanpa overhang)
    arm_r = SU(0.9,
               Capsule((4.9, 0.2, 29.6), (5.7, 0.0, 24.2), 1.45, 1.35, color="shirt"),
               Capsule((5.7, 0.0, 24.2), (5.4, -0.9, 19.6), 1.3, 1.2, color="skin"),
               Sphere((5.3, -1.0, 19.0), 1.35, color="skin"))
    # lengan kiri: tangan di pinggang (siku keluar)
    arm_l = SU(0.9,
               Capsule((-4.9, 0.2, 29.6), (-6.9, 0.6, 24.8), 1.45, 1.35, color="shirt"),
               Capsule((-6.9, 0.6, 24.8), (-4.3, 0.3, 21.6), 1.3, 1.25, color="skin"),
               Sphere((-4.1, 0.2, 21.6), 1.35, color="skin"))
    neck = Capsule((0, 0.1, 31.0), (0, 0.0, 34.0), 1.35, 1.3, color="skin")
    head = Ellipsoid((0, -0.1, 35.9), (2.7, 2.8, 3.1), color="skin")
    nose = Ellipsoid((0, -2.7, 35.4), (0.6, 0.6, 0.8), color="skin")
    head = SU(0.5, head, nose)
    head = Inter(head, HalfSpace((0, 0, 1), HEAD_TOP, color="skin"))
    body = SU(1.0, legs, hips, torso, belt)
    body = SU(0.8, body, arm_r, arm_l)
    body = SU(0.9, body, neck, head)
    body = Union([SU(0.6, body, boots), base])
    return body


def build_farmer_body(h=0.14, target_faces=70000):
    v, f, c = mesh_sdf(farmer_body_sdf(), ((-10, -8, 0), (10, 8, HEAD_TOP + 0.5)), h=h,
                       target_faces=target_faces)
    return v * SCALE, f, c


def build_caping():
    """Caping (topi kerucut) - dicetak tepi di bawah, tanpa support."""
    R = 7.2
    prof = [(0, 0.8), (2.6, 0.8), (2.6, 0.0), (R, 0.0), (R, 0.9), (R - 0.5, 1.3), (1.2, 5.6), (0.5, 6.4), (0, 6.5)]
    hat = geo.revolve_profile(prof, color="straw", segs=72).scale((SCALE, SCALE, SCALE))
    v, f, c = geo.to_arrays(hat)
    return v, f, c


def build_farmer_assembled():
    """Hanya untuk pratinjau: badan + caping terpasang."""
    v1, f1, c1 = build_farmer_body()
    v2, f2, c2 = build_caping()
    v2 = v2 + np.array([0, 0, (HEAD_TOP - 0.8) * SCALE])
    return np.vstack([v1, v2]), np.vstack([f1, f2 + len(v1)]), list(c1) + list(c2)
