"""Kandang (bangunan peternakan) beratap gambrel seperti pada gambar acuan.

Lokal: pintu ganda menghadap -Y, X = lebar, Z = atas, alas di Z = 0.
Dicetak tegak. Tritisan samping diberi chamfer 45 derajat di bawahnya dan tritisan
ujung pelana hanya 0,5 mm supaya tidak perlu support.
"""
import numpy as np
from manifold3d import CrossSection, FillRule, JoinType
import geo
from geo import box, union, tag

W, D, HW = 56.0, 70.0, 31.0   # lebar ujung pelana, panjang, tinggi dinding (sebelum skala)
SCALE = 1.1
EAVE, T_ROOF, OVH = 1.8, 2.2, 0.5


def _outer_profile():
    w, e = W / 2, EAVE
    right = [(w + e, HW - 0.6), (w + e - 2.6, HW + 9.0), (w * 0.62, HW + 18.0), (w * 0.28, HW + 22.6), (0, HW + 24.2)]
    poly = [(w + e, -5.0)] + right + [(-x, z) for (x, z) in right[-2::-1]] + [(-(w + e), -5.0)]
    return CrossSection([np.array(poly)], FillRule.Positive)


def _extrude_y(cs, length, y0, color):
    """Ekstrusi profil XZ sepanjang Y dari y0 ke y0+length."""
    m = cs.extrude(length).rotate((90, 0, 0)).translate((0, y0 + length, 0))
    return tag(m, color)


class Face:
    """Koordinat lokal sebuah muka dinding: u = mendatar di muka, z = atas,
    d = jarak ke luar dari bidang dinding (negatif = masuk dinding)."""

    def __init__(self, axis, plane, sign):
        self.axis, self.plane, self.sign = axis, plane, sign

    def slab(self, u0, u1, z0, z1, d0, d1):
        lo, hi = self.plane + self.sign * d0, self.plane + self.sign * d1
        a, b = min(lo, hi), max(lo, hi)
        if self.axis == "y":
            return geo.Manifold.cube((u1 - u0, b - a, z1 - z0)).translate((u0, a, z0))
        return geo.Manifold.cube((b - a, u1 - u0, z1 - z0)).translate((a, u0, z0))

    def recess(self, u0, u1, z0, z1, depth, color):
        """Pemotong ceruk dengan plafon miring 45 derajat (tanpa support)."""
        A = self.slab(u0, u1, z0, z1, 0.0, 1.5)
        B = self.slab(u0, u1, z0, z1 - depth, -depth, -depth + 0.01)
        return tag(geo.Manifold.batch_hull([A, B]), color)

    def bar(self, u0, u1, z0, z1, protrude, color, d_back=-0.5, d_full=0.0, chamfer_bottom=True):
        """List timbul dari d_back sampai protrude. Sisi bawah yang menggantung
        (dari d_full ke protrude) dimiringkan 45 derajat bila tidak di bed."""
        A = self.slab(u0, u1, z0, z1, d_back, d_full)
        rise = protrude - d_full
        zb = z0 + (rise if (chamfer_bottom and z0 > 0.01) else 0.0)
        B = self.slab(u0, u1, min(zb, z1 - 0.2), z1, protrude - 0.01, protrude)
        return tag(geo.Manifold.batch_hull([A, B]), color)

    def xbar(self, uc, zc, w, h, thick, protrude, color):
        """Silang X (dua bilah diagonal) di dalam bingkai w x h."""
        out = []
        L = float(np.hypot(w, h))
        for ang in (1, -1):
            a = np.degrees(np.arctan2(h, w)) * ang
            if self.axis == "y":
                b = geo.Manifold.cube((L, 1.0, thick), center=True).rotate((0, -a, 0)) ^ geo.Manifold.cube((w, 4, h), center=True)
                b = b.translate((uc, 0, zc))
            else:
                b = geo.Manifold.cube((1.0, L, thick), center=True).rotate((a, 0, 0)) ^ geo.Manifold.cube((4, w, h), center=True)
                b = b.translate((0, uc, zc))
            out.append(b)
        # tebal ke arah d: dari -1,2 (masuk dinding) sampai protrude
        x = geo.Manifold.batch_boolean(out, geo.m3.OpType.Add)
        span = self.slab(uc - w / 2, uc + w / 2, zc - h / 2, zc + h / 2, -1.2, protrude)
        if self.axis == "y":
            x = x.scale((1, 40, 1))
        else:
            x = x.scale((40, 1, 1))
        if self.axis == "y":
            x = x.translate((0, self.plane, 0))
        else:
            x = x.translate((self.plane, 0, 0))
        return tag(x ^ span, color)


def build_barn():
    w = W / 2
    O = _outer_profile()
    I = O.offset(-T_ROOF, JoinType.Miter)
    clip_roof = CrossSection.square((W + 20, 40), center=False).translate((-(W + 20) / 2, HW - 0.6))
    shell = (O - I) ^ clip_roof
    walls2d = (I.offset(0.3, JoinType.Miter) + CrossSection.square((W, HW), center=False).translate((-w, 0))) ^ \
        CrossSection.square((W, 200), center=False).translate((-w, 0))
    # chamfer 45 derajat di bawah tritisan samping (tanpa support)
    ze = HW - 0.6
    for sx in (-1, 1):
        tri = np.array([(sx * (w - 0.3), ze - EAVE - 0.8), (sx * (w + EAVE + 0.8), ze + 0.3), (sx * (w - 0.3), ze + 0.3)])
        if sx < 0:
            tri = tri[::-1]
        walls2d = walls2d + (CrossSection([tri], FillRule.Positive) ^ O)

    parts = []
    parts.append(_extrude_y(walls2d, D, -D / 2, "barn_wall"))
    fas = 0.8
    # atap rata dengan dinding ujung pelana (tanpa tritisan depan/belakang -> tanpa support)
    parts.append(_extrude_y(shell, D - 2 * fas + 0.6, -D / 2 + fas - 0.3, "barn_roof"))
    parts.append(_extrude_y(shell, fas, -D / 2, "barn_trim"))
    parts.append(_extrude_y(shell, fas, D / 2 - fas, "barn_trim"))
    parts.append(tag(geo.Manifold.cylinder(D, 1.3, 1.3, 24, center=True).rotate((90, 0, 0))
                     .translate((0, 0, HW + 24.0)), "barn_roof"))

    front, back = Face("y", -D / 2, -1), Face("y", D / 2, 1)
    left, right = Face("x", -w, -1), Face("x", w, 1)
    cuts, trims = [], []
    # ---- pintu ganda depan
    dw, dh, rec, t = 21.0, 21.0, 0.9, 1.5
    cuts.append(front.recess(-dw / 2, dw / 2, -1.0, dh, rec, "barn_trim"))
    for sg in (-1, 1):
        trims.append(front.bar(sg * dw / 2 - (t if sg > 0 else 0) * 0 + (0 if sg > 0 else -t), sg * dw / 2 + (t if sg > 0 else 0),
                               0.0, dh + t, 0.6, "barn_trim"))
    trims.append(front.bar(-dw / 2 - t, dw / 2 + t, dh, dh + t, 0.6, "barn_trim"))
    trims.append(front.bar(-0.6, 0.6, 0.0, dh, 0.0, "barn_trim", d_back=-1.2, d_full=-0.9))
    for cx in (-dw / 4, dw / 4):
        trims.append(front.xbar(cx, dh / 2, dw / 2 - 1.2, dh, 1.4, 0.0, "barn_trim"))
    # ---- pintu loteng di kedua ujung pelana
    hw_, hh, hz = 10.0, 8.5, HW + 2.5
    for fc in (front, back):
        cuts.append(fc.recess(-hw_ / 2, hw_ / 2, hz, hz + hh, 0.7, "barn_trim"))
        trims.append(fc.bar(-hw_ / 2 - 1.2, hw_ / 2 + 1.2, hz + hh, hz + hh + 1.2, 0.5, "barn_trim"))
        trims.append(fc.bar(-hw_ / 2 - 1.2, hw_ / 2 + 1.2, hz - 1.2, hz, 0.5, "barn_trim"))
        for sg in (-1, 1):
            trims.append(fc.bar(sg * (hw_ / 2) + (0 if sg > 0 else -1.2), sg * (hw_ / 2) + (1.2 if sg > 0 else 0),
                                hz - 1.2, hz + hh + 1.2, 0.5, "barn_trim"))
        trims.append(fc.xbar(0.0, hz + hh / 2, hw_, hh, 1.2, 0.0, "barn_trim"))
    # ---- jendela samping (2 per sisi)
    ww, wh, wz = 8.0, 7.0, 15.0
    for fc in (left, right):
        for yy in (-16.0, 16.0):
            cuts.append(fc.recess(yy - ww / 2, yy + ww / 2, wz, wz + wh, 0.9, "window"))
            trims.append(fc.bar(yy - ww / 2 - 1.2, yy + ww / 2 + 1.2, wz - 1.2, wz, 0.5, "barn_trim"))
            trims.append(fc.bar(yy - ww / 2 - 1.2, yy + ww / 2 + 1.2, wz + wh, wz + wh + 1.2, 0.5, "barn_trim"))
            for sg in (-1, 1):
                u0 = yy + sg * ww / 2 + (0 if sg > 0 else -1.2)
                trims.append(fc.bar(u0, u0 + 1.2, wz - 1.2, wz + wh + 1.2, 0.5, "barn_trim"))
            trims.append(fc.bar(yy - 0.45, yy + 0.45, wz - 0.01, wz + wh, 0.0, "barn_trim", d_back=-1.2, d_full=-0.9,
                                chamfer_bottom=False))
            trims.append(fc.bar(yy - ww / 2, yy + ww / 2, wz + wh / 2 - 0.7, wz + wh / 2 + 0.7, 0.0, "barn_trim",
                                d_back=-1.2, d_full=-0.9))
    # ---- papan sudut
    for sx in (-1, 1):
        for sy in (-1, 1):
            trims.append(box((1.6, 1.6, HW - 0.3), (sx * (w - 0.5), sy * (D / 2 - 0.5), 0), color="barn_trim", base=True))
    body = union(parts)
    body = body - union(cuts)
    body = union([body] + trims)
    body = body.trim_by_plane((0, 0, 1), 0.0).scale((SCALE, SCALE, SCALE))
    return geo.to_arrays(body)
