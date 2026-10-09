"""Figur lain: susu, pendapatan, limbah ternak, biodigester, hasil olahan
limbah (biogas, slurry, energi & pupuk, limbah padat), pupuk organik, HP."""
import math
import numpy as np
from manifold3d import Manifold, CrossSection, FillRule, JoinType
import geo
from geo import tag, box, union, cyl, rbox_xy, revolve_profile, cyl_between
from sdf import (Sphere, Ellipsoid, RoundBox, Capsule, Cylinder, Cone, Torus, SU, Union,
                 Displace, Inter, Diff, HalfSpace, Func, Paint, Xform, rot_matrix, vnoise3, mesh_sdf)


# =============================================================== susu sapi
def _bottle(h=30.0, r=5.0, color="milk"):
    hb = h * 0.62
    prof = [(0, 0), (r - 0.5, 0), (r, 0.5), (r, hb), (r * 0.93, hb + 2.0), (r * 0.72, hb + 4.3),
            (r * 0.55, hb + 6.0), (r * 0.52, h - 2.4), (0, h - 2.4)]
    body = revolve_profile(prof, color=color, segs=64)
    cap = revolve_profile([(0, h - 2.6), (r * 0.62, h - 2.6), (r * 0.62, h - 0.4), (r * 0.62 - 0.4, h), (0, h)],
                          color="cap_green", segs=48)
    return body + cap


def build_milk():
    """Tiga botol susu saling menempel (satu badan, alas datar)."""
    b1 = _bottle(31.0, 5.2).translate((-5.0, 4.0, 0))
    b2 = _bottle(31.0, 5.2).translate((5.0, 4.0, 0))
    b3 = _bottle(27.5, 5.0).translate((0.0, -4.4, 0))
    return geo.to_arrays(union([b1, b2, b3]))


# =============================================================== pendapatan
def _moneybag_sdf(c, s=1.0):
    cx, cy = c
    body = SU(2.0 * s,
              Ellipsoid((cx, cy, 8.0 * s), (8.6 * s, 7.6 * s, 8.4 * s), color="money_bag"),
              Cylinder((cx, cy, 0), 7.9 * s, 8.0 * s, re=2.4 * s, color="money_bag"))
    neck = Capsule((cx, cy, 15.0 * s), (cx, cy, 17.6 * s), 2.6 * s, 2.3 * s, color="money_bag")
    tie = Torus((cx, cy, 16.6 * s), 2.75 * s, 0.75 * s, color="gold")
    tuft = SU(1.0 * s,
              Cone((cx, cy, 0), 17.2 * s, 21.0 * s, 2.4 * s, 4.6 * s, color="money_bag"),
              Ellipsoid((cx, cy, 20.6 * s), (4.6 * s, 4.4 * s, 1.5 * s), color="money_bag"))
    return SU(0.8 * s, body, neck, tuft) | tie


def build_money():
    big = _moneybag_sdf((0.0, 2.0), 1.0)
    small = _moneybag_sdf((12.5, 5.5), 0.72)
    coins = Union([Cylinder((11.0 + 0.25 * k, -5.0 + 0.15 * (k % 2), 1.25 * k), 3.6, 1.3, re=0.35, color="gold")
                   for k in range(4)])
    coin2 = Cylinder((4.2, -8.0, 0), 3.6, 1.3, re=0.35, color="gold")
    node = SU(0.6, big, small) | SU(0.5, coins, coin2)
    node = SU(0.6, node, Cylinder((7.0, -4.0, 0), 4.0, 0.8, re=0.3, color="gold"))
    v, f, c = mesh_sdf(node, ((-10, -12, 0), (19, 12, 23)), h=0.16, target_faces=60000)
    big_m = geo.from_mesh(v, f, c)
    # huruf "Rp" timbul 0,6 mm mengikuti permukaan kantong besar
    shell_node = Ellipsoid((0.0, 2.0, 8.0), (9.2, 8.2, 9.0), color="gold")
    sv, sf, sc = mesh_sdf(shell_node, ((-10, -7, 0), (10, 11, 18)), h=0.25, target_faces=20000)
    shell = geo.from_mesh(sv, sf, ["gold"] * len(sf))
    txt = geo.text_cs("Rp", 5.4, font=geo.FONT_XBOLD)
    txt3 = txt.extrude(12.0).rotate((90, 0, 0)).translate((0, 6.0, 7.6))
    letters = tag(txt3, "gold") ^ shell
    return geo.to_arrays(big_m + letters)


# =============================================================== limbah ternak
def manure_sdf():
    lumps = [((0, 0, 0), (19.5, 14.5, 7.0)), ((-1.5, 0.8, 5.5), (15.0, 11.0, 6.0)), ((0.8, -0.4, 10.5), (10.0, 7.6, 5.0)),
             ((0.2, 0.2, 14.5), (5.6, 4.6, 3.6)), ((0.6, 0.0, 17.6), (2.2, 2.0, 1.8)),
             ((10.5, 5.0, 3.0), (7.0, 5.5, 4.2)), ((-11.0, -4.5, 2.0), (7.0, 5.0, 3.8))]
    heap = SU(3.0, *[Ellipsoid(c, r, color="manure") for c, r in lumps])
    clods = Union([Ellipsoid((17.5, -9.5, 0.0), (4.0, 3.2, 2.6), color="manure"),
                   Ellipsoid((-17.0, 9.0, 0.0), (3.4, 2.8, 2.2), color="manure")])
    heap = SU(2.2, heap, clods)
    # gulungan/lipatan bertingkat seperti kotoran ternak yang rapi
    heap = Displace(heap, lambda p: 0.45 * np.sin(p[:, 2] * 1.6) * np.clip(p[:, 2] / 4, 0, 1)
                    + 0.45 * vnoise3(p, 1.8, 7))
    heap = Paint(heap, "manure_light", lambda p: (vnoise3(p, 2.5, 9) > 0.35))
    return heap


def build_manure():
    return mesh_sdf(manure_sdf(), ((-24, -16, 0), (24, 16, 21)), h=0.2, target_faces=60000)


# =============================================================== biodigester
def _elbow(R, r, deg, color):
    cs = CrossSection.circle(r, 24).translate((R, 0))
    m = cs.revolve(48, deg)
    return tag(m, color)


def _pipe_path(points, r, color, bend=3.0):
    """Pipa melalui titik-titik dengan sambungan bola (siku halus)."""
    parts = []
    for a, b in zip(points[:-1], points[1:]):
        parts.append(cyl_between(a, b, r, color=color))
    for p in points[1:-1]:
        parts.append(geo.sphere(r, p, color=color))
    for p in (points[0], points[-1]):
        parts.append(geo.sphere(r, p, color=color)) if p[2] > 0.5 else None
    return union(parts)


def build_biodigester():
    """Biodigester kubah tetap gaya skema: badan silinder zaitun, kubah hijau tua,
    tutup atas, pipa inlet (bak masuk limbah) kiri, outlet slurry kanan, pipa gas."""
    R, Hc, Hd = 25.0, 23.0, 12.5
    parts = []
    parts.append(cyl(R, Hc, (0, 0, 0), color="digester_low", segs=96))
    # sabuk atas: bawahnya kerucut 45 derajat (tanpa support)
    parts.append(revolve_profile([(0, Hc - 3.4), (R - 0.1, Hc - 3.4), (R + 0.7, Hc - 2.6), (R + 0.7, Hc), (0, Hc)],
                                 color="digester", segs=128))
    parts.append(cyl(R + 0.5, 1.6, (0, 0, 0), color="digester", segs=96))
    # kubah: tutup bola
    Rs = (R ** 2 + Hd ** 2) / (2 * Hd)
    dome = Manifold.sphere(Rs, 128).translate((0, 0, Hc + Hd - Rs))
    dome = dome ^ Manifold.cylinder(Hd + 1, R + 0.2, R + 0.2, 96).translate((0, 0, Hc - 0.01))
    parts.append(tag(dome, "digester"))
    # tutup/manhole atas + pipa gas
    parts.append(cyl(5.2, 3.2, (0, 0, Hc + Hd - 0.8), color="digester_band", segs=48))
    parts.append(cyl(3.6, 1.2, (0, 0, Hc + Hd + 2.3), color="digester_band", segs=48))
    gz = Hc + Hd + 1.2
    # pipa gas menempel di permukaan kubah lalu turun di dinding tangki (tertopang, tanpa support)
    gdir = np.array([-0.86, 0.51])
    gas = []
    for rho in (3.0, 9.0, 15.0, 20.0, 23.5):
        zz = Hc + Hd - Rs + math.sqrt(Rs ** 2 - rho ** 2) + 0.6
        gas.append((gdir[0] * rho, gdir[1] * rho, zz))
    gas.append((gdir[0] * (R + 1.0), gdir[1] * (R + 1.0), Hc - 1.5))
    gas.append((gdir[0] * (R + 1.0), gdir[1] * (R + 1.0), 0.0))
    parts.append(_pipe_path(gas, 1.6, "pipe"))
    parts.append(cyl(2.6, 2.0, (gdir[0] * (R + 1.0), gdir[1] * (R + 1.0), 0.0), color="pipe"))
    vx, vy = gdir[0] * (R + 1.0), gdir[1] * (R + 1.0)
    parts.append(revolve_profile([(0, Hc - 11.5), (1.6, Hc - 11.5), (2.4, Hc - 10.7), (2.4, Hc - 8.4), (1.6, Hc - 7.6), (0, Hc - 7.6)],
                                 color="machine_red", segs=32, center=(vx, vy, 0)))  # katup gas
    # ---- inlet: bak pemasukan kotak di kiri depan + pipa miring ke tangki
    ix, iy = -33.0, -9.0
    inlet = Manifold.cube((13.0, 13.0, 10.0), center=True).translate((ix, iy, 5.0))
    inlet = inlet - Manifold.batch_hull([Manifold.cube((7.0, 7.0, 0.1), center=True).translate((ix, iy, 4.0)),
                                         Manifold.cube((10.4, 10.4, 0.1), center=True).translate((ix, iy, 10.2))])
    parts.append(tag(inlet, "concrete"))
    rim = Manifold.batch_hull([Manifold.cube((13.0, 13.0, 0.1), center=True).translate((ix, iy, 8.6)),
                               Manifold.cube((14.6, 14.6, 1.0), center=True).translate((ix, iy, 10.2))])
    parts.append(tag(rim - Manifold.cube((10.4, 10.4, 6), center=True).translate((ix, iy, 11.5)), "concrete"))
    # pipa inlet tertanam setengah di permukaan dudukan (rata bawah, tanpa support)
    parts.append(cyl_between((ix + 4.5, iy + 1.5, 1.4), (-R * 0.86, -R * 0.40, 1.4), 2.1, color="digester_band"))
    # isian limbah di bak inlet
    fill = Manifold.cube((11.0, 11.0, 3.4), center=True).translate((ix, iy, 5.4)) ^ \
        Manifold.batch_hull([Manifold.cube((7.4, 7.4, 0.1), center=True).translate((ix, iy, 3.7)),
                             Manifold.cube((10.8, 10.8, 0.1), center=True).translate((ix, iy, 10.4))])
    parts.append(tag(fill, "manure"))
    # ---- outlet slurry: pipa dari sisi kanan menurun ke bak keluaran
    ox, oy = 34.0, -10.0
    out_pts = [(R * 0.86, -R * 0.40, 17.0), (ox - 5.1, oy + 0.6, 8.2)]
    parts.append(_pipe_path(out_pts, 2.0, "digester_band"))
    outlet = Manifold.cube((12.0, 12.0, 8.0), center=True).translate((ox, oy, 4.0)) - \
        Manifold.cube((8.6, 8.6, 6.0), center=True).translate((ox, oy, 8.0))
    parts.append(tag(outlet, "concrete"))
    parts.append(tag(Manifold.cube((9.0, 9.0, 1.6), center=True).translate((ox, oy, 5.6)), "slurry"))
    # pipa depan kedua seperti gambar acuan (melengkung keluar-turun)
    fr = [(6.0, -R * 0.97, 15.0), (9.0, -R - 6.0, 6.5), (9.0, -R - 6.0, 0.0)]
    parts.append(_pipe_path(fr, 1.7, "digester_low"))
    parts.append(cyl(2.8, 1.6, (9.0, -R - 6.0, 0.0), color="digester_low"))
    fr2 = [(-7.0, -R * 0.96, 15.0), (-10.0, -R - 6.0, 6.5), (-10.0, -R - 6.0, 0.0)]
    parts.append(_pipe_path(fr2, 1.7, "digester_band"))
    parts.append(cyl(2.8, 1.6, (-10.0, -R - 6.0, 0.0), color="digester_band"))
    m = union(parts).trim_by_plane((0, 0, 1), 0.0)
    return geo.to_arrays(m)


# =============================================================== biogas
def biogas_sdf():
    ped = SU(0.8,
             Cylinder((0, 0, 0), 8.0, 4.0, re=1.0, color="digester"),
             Cylinder((0, 0, 3.0), 5.4, 2.6, re=0.8, color="digester_band"))
    # api: dua lidah, alas lebar, ujung >= 1,6 mm
    main = SU(2.2,
              Sphere((0, 0, 9.6), 4.7, color="flame"),
              Capsule((0, 0, 10.0), (0.8, 0, 16.0), 3.7, 2.2, color="flame"),
              Capsule((0.8, 0, 16.0), (-0.6, 0, 21.0), 2.2, 0.85, color="flame"))
    side = SU(1.2,
              Capsule((2.6, 0.3, 10.5), (4.6, 0.2, 15.6), 2.1, 0.9, color="flame"))
    side2 = Capsule((-2.8, -0.2, 10.0), (-4.2, -0.2, 14.0), 1.9, 0.85, color="flame")
    flame = SU(1.0, main, side, side2)
    flame = Inter(flame, RoundBox((0, 0, 14), (9, 3.6, 10), 2.4, color="flame"))
    flame = Paint(flame, "flame_core", lambda p: (p[:, 2] < 13.2) & (np.abs(p[:, 0]) < 3.2))
    return SU(1.4, ped, flame)


def build_biogas():
    return mesh_sdf(biogas_sdf(), ((-9, -9, 0), (9, 9, 23)), h=0.14, target_faces=50000)


# =============================================================== slurry (jeriken)
def build_jerrycan():
    W, Dd, H = 17.0, 10.5, 18.0
    parts = [geo.rbox((W, Dd, H), 2.2, (0, 0, 0), color="jerrycan", base=True)]
    # pegangan atas dengan lubang
    hnd = geo.rbox((10.0, 3.6, 6.0), 1.2, (-2.2, 0, H - 1.5), color="jerrycan", base=True)
    # lubang pegangan berpuncak 45 derajat (tanpa jembatan datar)
    hole_cs = CrossSection([np.array([(-3.2, -1.3), (3.2, -1.3), (3.2, 0.2), (1.7, 1.7), (-1.7, 1.7), (-3.2, 0.2)])],
                           FillRule.Positive)
    hole = hole_cs.extrude(10.0).rotate((90, 0, 0)).translate((-2.2, 5.0, H + 1.9))
    parts.append(hnd - hole)
    # mulut/tutup
    parts.append(cyl(2.3, 3.4, (5.6, 0, H - 1.0), color="jerrycan"))
    parts.append(cyl(2.6, 1.8, (5.6, 0, H + 2.0), color="dark_metal"))
    # panel label timbul + ikon tetesan
    # panel label timbul 0,5 mm dengan sisi bawah 45 derajat
    pA = Manifold.cube((11.0, 0.6, 9.0), center=True).translate((0, -Dd / 2 + 0.3, 8.5))
    pB = Manifold.cube((11.0, 0.05, 8.5), center=True).translate((0, -Dd / 2 - 0.5, 8.75))
    parts.append(tag(Manifold.batch_hull([pA, pB]), "lid"))
    circ = CrossSection.circle(2.3, 40)
    tip = CrossSection([np.array([(1.62, 1.62), (0, 4.6), (-1.62, 1.62)])], FillRule.Positive)
    drop_cs = (circ + tip).translate((0, -0.9))
    # ikon tetes timbul 0,5 mm, sisi meruncing (tanpa tepi menggantung)
    dm = drop_cs.extrude(1.0, scale_top=(0.72, 0.72)).rotate((90, 0, 0)).translate((0, -Dd / 2 - 0.5 + 0.5, 8.6))
    parts.append(tag(dm, "slurry"))
    return geo.to_arrays(union(parts))


# =============================================================== energi & pupuk
def build_energy():
    """Bola lampu (energi) + tunas tanaman (pupuk) di atas gundukan tanah."""
    mound = Displace(Ellipsoid((0, 0, 0), (13.0, 8.0, 3.2), color="soil"), lambda p: 0.2 * vnoise3(p, 1.5, 4))
    bx = -4.5
    # profil lampu: ulir di bawah, kerucut 45 derajat, bola kaca
    # (dibuat dari SDF supaya menyatu halus dengan gundukan)
    screw = Union([Cylinder((bx, 0, 1.0 + 1.25 * k), 2.75 if k % 2 == 0 else 2.45, 1.25, re=0.35, color="metal")
                   for k in range(5)])
    neck = Cone((bx, 0, 0), 7.0, 9.0, 2.6, 3.6, color="bulb")
    glass = Sphere((bx, 0, 12.6), 5.0, color="bulb")
    glass = SU(0.8, glass, neck)
    bulb = Union([screw, glass])
    sx = 6.5
    stem = Capsule((sx, 0, 1.5), (sx + 0.3, 0, 11.0), 1.05, 0.9, color="grass")
    T = np.array([sx + 0.3, 0, 10.6])
    dL = np.array([-math.cos(math.radians(50)), 0, math.sin(math.radians(50))])
    dR = np.array([math.cos(math.radians(46)), 0, math.sin(math.radians(46))])
    leafL = Xform(Ellipsoid((0, 0, 0), (4.6, 2.4, 0.85), color="grass"), rot_matrix("y", 50), T + 4.0 * dL)
    leafR = Xform(Ellipsoid((0, 0, 0), (4.1, 2.2, 0.85), color="grass"), rot_matrix("y", -46), T + 3.6 * dR)
    sprout = SU(0.7, stem, leafL, leafR)
    node = SU(1.0, mound, bulb, sprout)
    return mesh_sdf(node, ((-14, -9, 0), (14, 9, 18.5)), h=0.13, target_faces=55000)


# =============================================================== limbah padat
def compost_sdf():
    layers = []
    for k in range(3):
        z = 1.8 + k * 4.1
        layers.append(RoundBox((0.3 * (k % 2) - 0.15, 0.2 * ((k + 1) % 2), z), (22.5 - 0.35 * k, 16.0 - 0.3 * k, 2.2), 1.6,
                               color="compost" if k % 2 == 0 else "compost_light"))
    blk = SU(0.6, *layers)
    # serat/jerami bergelombang
    blk = Displace(blk, lambda p: 0.32 * np.sin(p[:, 0] * 1.7 + 2.0 * np.sin(p[:, 1] * 0.6)) * np.cos(p[:, 2] * 1.5)
                   + 0.22 * vnoise3(p, 1.1, 5))
    return blk


def build_compost():
    return mesh_sdf(compost_sdf(), ((-24, -17.5, 0), (24, 17.5, 14.5)), h=0.18, target_faces=50000)


# =============================================================== pupuk organik
def build_fertilizer():
    """Karung kraft berdiri + area stiker label + gundukan butiran di depan."""
    bag = SU(2.0,
             RoundBox((0, 0, 14.0), (12.5, 6.8, 14.0), 3.0, color="kraft"),
             RoundBox((0, 0, 30.0), (11.6, 3.4, 4.2), 1.6, color="kraft"))
    seal = RoundBox((0, 0, 34.4), (11.8, 1.6, 1.4), 0.6, color="kraft")
    bag = SU(0.8, bag, seal)
    # alas pita hijau (seperti gambar) - dicat
    bag = Paint(bag, "jar_green", lambda p: (p[:, 2] < 5.2) & (p[:, 1] < -5.0))
    pile = Displace(SU(1.2,
                       Ellipsoid((6.0, -10.5, 0), (6.5, 4.6, 3.4), color="granule"),
                       Ellipsoid((-2.0, -10.0, 0), (4.0, 3.4, 2.4), color="granule")),
                    lambda p: 0.4 * vnoise3(p, 0.7, 11))
    node = SU(1.0, bag, pile)
    v, f, c = mesh_sdf(node, ((-14, -16, 0), (14, 8, 36.5)), h=0.18, target_faces=50000)
    m = geo.from_mesh(v, f, c)
    # cekungan stiker 18 x 14 mm, dalam 0,5 mm di muka depan
    pocket = geo.rbox((18.0, 2.0, 14.0), 1.0, (0, -6.8, 12.0), color="sticker", base=True)
    m = m - pocket
    return geo.to_arrays(m)


# =============================================================== HP SI PATRIOT
PHONE = dict(w=27.0, h=50.0, t=5.2, r=4.0, scr_w=23.5, scr_h=43.5, scr_r=2.6, tilt=16.0)


def build_phone():
    """Satu HP tegak pada dudukan (satu badan cetak). Layar = cekungan 0,6 mm
    untuk stiker tangkapan layar App/Website SI PATRIOT (23,5 x 43,5 mm)."""
    P = PHONE
    w, h, t = P["w"], P["h"], P["t"]
    # HP dalam koordinat lokal: lebar X, tinggi Z, tebal Y (layar menghadap -Y)
    ph = geo.rbox((w, t, h), 1.6, (0, 0, h / 2), color="phone")
    ph = ph ^ tag(rbox_xy((w, h, t + 4), P["r"], (0, 0, 0), base=False).rotate((90, 0, 0)).translate((0, 0, h / 2)), "phone")
    # pemotong tebal 1,2 mm berpusat di muka depan -> cekungan layar 0,6 mm
    scr = tag(rbox_xy((P["scr_w"], P["scr_h"], 1.2), P["scr_r"], (0, 0, 0), base=False).rotate((90, 0, 0))
              .translate((0, -t / 2, h / 2 + 0.6)), "screen")
    ph = ph - scr
    # tombol samping & kamera belakang
    ph = ph + box((0.8, 1.6, 7.0), (w / 2 + 0.2, 0, h * 0.62), color="phone", base=True)
    # condongkan ke belakang
    tilt = P["tilt"]
    ph = ph.rotate((-tilt, 0, 0))
    # dudukan
    zlift = 3.0
    ph_z = zlift - 1.4   # bawah HP masuk 1,8 mm ke dudukan (tepi bulat tidak menggantung)
    ph = ph.translate((0, 2.0, ph_z))
    base = geo.rbox((w + 12.0, 34.0, 3.4), 1.4, (0, 1.0, 0), color="phone", base=True)
    lip = geo.rbox((w + 4.0, 4.0, 7.0), 1.0, (0, -3.0, 0), color="phone", base=True)
    # penyangga belakang: baji yang muka depannya mengikuti punggung HP
    a = math.radians(tilt)

    def y_back(Z):
        zl = (Z - ph_z + (t / 2) * math.sin(a)) / math.cos(a)
        return (t / 2) * math.cos(a) + zl * math.sin(a) + 2.0

    Z0, Z1 = zlift - 0.2, 40.0
    tri = CrossSection([np.array([(y_back(Z0) - 0.8, Z0), (y_back(Z0) + 15.0, Z0), (y_back(Z1) - 0.8, Z1)])],
                       FillRule.Positive)
    if tri.area() <= 0:
        tri = CrossSection([np.array([(y_back(Z0) - 0.8, Z0), (y_back(Z1) - 0.8, Z1), (y_back(Z0) + 15.0, Z0)])],
                           FillRule.Positive)
    sup = tri.extrude(10.0).rotate((90, 0, 90)).translate((-5.0, 0, 0))
    stand = union([base, lip, tag(sup, "phone")])
    m = union([stand, ph]).trim_by_plane((0, 0, 1), 0.0)
    return geo.to_arrays(m)
