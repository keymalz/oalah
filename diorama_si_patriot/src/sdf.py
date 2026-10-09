"""SDF (signed distance field) sederhana berbasis numpy untuk figur organik
(sapi, peternak, karung, limbah). Mesh dibuat dengan marching cubes, lalu
disederhanakan. Bidang bawah dipotong rata di Z = 0.

Konvensi: jarak negatif = di dalam benda. Satuan mm.
"""
import math
import numpy as np
from palette import COLOR_INDEX, COLOR_KEYS


def _v(a):
    return np.asarray(a, dtype=np.float64)


def _len(p):
    return np.sqrt(np.einsum("ij,ij->i", p, p))


class Node:
    color = None

    def d(self, p):
        raise NotImplementedError

    def lab(self, p):
        """(jarak, label warna) untuk sejumlah kecil titik (centroid segitiga)."""
        return self.d(p), np.full(len(p), COLOR_INDEX[self.color or "cream"])

    # operator
    def __or__(self, o):
        return Union([self, o])

    def __sub__(self, o):
        return Diff(self, o)

    def __and__(self, o):
        return Inter(self, o)

    def move(self, t):
        return Xform(self, np.eye(3), _v(t))

    def rot(self, axis, deg, about=(0, 0, 0)):
        R = rot_matrix(axis, deg)
        about = _v(about)
        return Xform(self, R, about - R @ about)

    def paint(self, color, region=None):
        return Paint(self, color, region)


def rot_matrix(axis, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    if axis == "x":
        return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    if axis == "y":
        return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


class Leaf(Node):
    def __init__(self, color):
        self.color = color


class Sphere(Leaf):
    def __init__(self, c, r, color="cream"):
        super().__init__(color); self.c = _v(c); self.r = r

    def d(self, p):
        return _len(p - self.c) - self.r


class Ellipsoid(Leaf):
    def __init__(self, c, radii, color="cream"):
        super().__init__(color); self.c = _v(c); self.r = _v(radii)

    def d(self, p):
        q = p - self.c
        k0 = _len(q / self.r)
        k1 = _len(q / (self.r * self.r))
        return k0 * (k0 - 1.0) / np.maximum(k1, 1e-9)


class RoundBox(Leaf):
    def __init__(self, c, half, r, color="cream"):
        super().__init__(color); self.c = _v(c); self.h = _v(half) - r; self.r = r

    def d(self, p):
        q = np.abs(p - self.c) - self.h
        out = _len(np.maximum(q, 0.0))
        inn = np.minimum(np.max(q, axis=1), 0.0)
        return out + inn - self.r


class Capsule(Leaf):
    """Kapsul meruncing (round cone) dari a (jari-jari ra) ke b (rb)."""

    def __init__(self, a, b, ra, rb=None, color="cream"):
        super().__init__(color)
        self.a = _v(a); self.b = _v(b); self.ra = ra; self.rb = ra if rb is None else rb

    def d(self, p):
        a, b, r1, r2 = self.a, self.b, self.ra, self.rb
        ba = b - a
        l2 = float(ba @ ba)
        rr = r1 - r2
        a2 = l2 - rr * rr
        il2 = 1.0 / l2
        pa = p - a
        y = pa @ ba
        z = y - l2
        xv = pa * l2 - np.outer(y, ba)
        x2 = np.einsum("ij,ij->i", xv, xv)
        y2 = y * y * l2
        z2 = z * z * l2
        k = math.copysign(1.0, rr) * rr * rr * x2
        res = np.empty(len(p))
        m1 = np.sign(z) * a2 * z2 > k
        m2 = (np.sign(y) * a2 * y2 < k) & ~m1
        m3 = ~(m1 | m2)
        res[m1] = np.sqrt(x2[m1] + z2[m1]) * il2 - r2
        res[m2] = np.sqrt(x2[m2] + y2[m2]) * il2 - r1
        res[m3] = (np.sqrt(x2[m3] * a2 * il2) + y[m3] * rr) * il2 - r1
        return res


class Cylinder(Leaf):
    """Silinder tegak (sumbu Z) dengan tepi membulat r_e."""

    def __init__(self, c, r, h, re=0.0, color="cream"):
        super().__init__(color); self.c = _v(c); self.r = r; self.h = h; self.re = re

    def d(self, p):
        q = p - self.c
        dx = np.sqrt(q[:, 0] ** 2 + q[:, 1] ** 2) - (self.r - self.re)
        dz = np.abs(q[:, 2] - self.h / 2) - (self.h / 2 - self.re)
        return np.minimum(np.maximum(dx, dz), 0) + np.sqrt(np.maximum(dx, 0) ** 2 + np.maximum(dz, 0) ** 2) - self.re


class Cone(Leaf):
    """Frustum tegak: jari-jari r0 di z0, r1 di z1 (sumbu Z)."""

    def __init__(self, c, z0, z1, r0, r1, color="cream"):
        super().__init__(color); self.c = _v(c); self.z0 = z0; self.z1 = z1; self.r0 = r0; self.r1 = r1

    def d(self, p):
        q = p - self.c
        h = (self.z1 - self.z0) / 2
        qx = np.sqrt(q[:, 0] ** 2 + q[:, 1] ** 2)
        qy = q[:, 2] - (self.z0 + h)
        r1, r2 = self.r0, self.r1
        k1 = np.array([r2, h])
        k2 = np.array([r2 - r1, 2 * h])
        cax = qx - np.minimum(qx, np.where(qy < 0, r1, r2))
        cay = np.abs(qy) - h
        kq = np.stack([k1[0] - qx, k1[1] - qy], 1)
        t = np.clip((kq @ k2) / (k2 @ k2), 0, 1)
        cbx = qx - k1[0] + k2[0] * t
        cby = qy - k1[1] + k2[1] * t
        s = np.where((cbx < 0) & (cay < 0), -1.0, 1.0)
        return s * np.sqrt(np.minimum(cax * cax + cay * cay, cbx * cbx + cby * cby))


class Torus(Leaf):
    def __init__(self, c, R, r, color="cream"):
        super().__init__(color); self.c = _v(c); self.R = R; self.r = r

    def d(self, p):
        q = p - self.c
        qx = np.sqrt(q[:, 0] ** 2 + q[:, 1] ** 2) - self.R
        return np.sqrt(qx ** 2 + q[:, 2] ** 2) - self.r


class HalfSpace(Leaf):
    """Ruang di bawah bidang n·p = h (n dinormalisasi)."""

    def __init__(self, n, h, color="cream"):
        super().__init__(color); self.n = _v(n) / np.linalg.norm(n); self.hh = h

    def d(self, p):
        return p @ self.n - self.hh


class Func(Leaf):
    def __init__(self, fn, color="cream"):
        super().__init__(color); self.fn = fn

    def d(self, p):
        return self.fn(p)


# ------------------------------------------------------------ kombinasi
def smin(a, b, k):
    if k <= 0:
        return np.minimum(a, b)
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0.0, 1.0)
    return b * (1 - h) + a * h - k * h * (1 - h)


class Union(Node):
    def __init__(self, kids, k=0.0):
        self.kids = []
        for c in kids:
            if isinstance(c, Union) and c.k == k:
                self.kids += c.kids
            else:
                self.kids.append(c)
        self.k = k

    def d(self, p):
        r = self.kids[0].d(p)
        for c in self.kids[1:]:
            r = smin(r, c.d(p), self.k)
        return r

    def lab(self, p):
        ds, ls = zip(*[c.lab(p) for c in self.kids])
        D = np.stack(ds, 1)
        L = np.stack(ls, 1)
        i = np.argmin(D, axis=1)
        r = D[:, 0]
        for j in range(1, D.shape[1]):
            r = smin(r, D[:, j], self.k)
        return r, L[np.arange(len(p)), i]


def SU(k, *kids):
    """Smooth union dengan radius blend k."""
    return Union(list(kids), k)


class Diff(Node):
    def __init__(self, a, b, k=0.0):
        self.a = a; self.b = b; self.k = k

    def d(self, p):
        if self.k > 0:
            return -smin(-self.a.d(p), self.b.d(p), self.k)
        return np.maximum(self.a.d(p), -self.b.d(p))

    def lab(self, p):
        da, la = self.a.lab(p)
        return self.d(p), la


class Inter(Node):
    def __init__(self, a, b):
        self.a = a; self.b = b

    def d(self, p):
        return np.maximum(self.a.d(p), self.b.d(p))

    def lab(self, p):
        da, la = self.a.lab(p)
        return self.d(p), la


class Xform(Node):
    """p_world = R p_local + t."""

    def __init__(self, child, R, t):
        self.c = child; self.R = R; self.t = t

    def _loc(self, p):
        return (p - self.t) @ self.R  # R^T (p - t)

    def d(self, p):
        return self.c.d(self._loc(p))

    def lab(self, p):
        return self.c.lab(self._loc(p))


class Mirror(Node):
    """Cermin terhadap bidang x=0 / y=0 (tubuh simetris)."""

    def __init__(self, child, axis=1):
        self.c = child; self.ax = axis

    def _loc(self, p):
        q = p.copy(); q[:, self.ax] = np.abs(q[:, self.ax]); return q

    def d(self, p):
        return self.c.d(self._loc(p))

    def lab(self, p):
        return self.c.lab(self._loc(p))


class Paint(Node):
    def __init__(self, child, color, region=None):
        self.c = child; self.color = color; self.region = region

    def d(self, p):
        return self.c.d(p)

    def lab(self, p):
        d, l = self.c.lab(p)
        if self.region is None:
            l = np.full(len(p), COLOR_INDEX[self.color])
        else:
            m = self.region(p)
            l = l.copy(); l[m] = COLOR_INDEX[self.color]
        return d, l


class Displace(Node):
    def __init__(self, child, fn):
        self.c = child; self.fn = fn

    def d(self, p):
        return self.c.d(p) + self.fn(p)

    def lab(self, p):
        d, l = self.c.lab(p)
        return d + self.fn(p), l


class Ground(Node):
    """Potong rata di z = 0 (alas datar untuk cetak)."""

    def __init__(self, child, z=0.0):
        self.c = child; self.z = z

    def d(self, p):
        return np.maximum(self.c.d(p), self.z - p[:, 2])

    def lab(self, p):
        d, l = self.c.lab(p)
        return np.maximum(d, self.z - p[:, 2]), l


# ------------------------------------------------------------ noise
def vnoise3(p, scale=1.0, seed=0):
    """Value noise 3D halus (-1..1)."""
    q = p / scale
    i = np.floor(q).astype(np.int64)
    f = q - i
    u = f * f * (3 - 2 * f)

    def h(ix, iy, iz):
        n = (ix * 73856093) ^ (iy * 19349663) ^ (iz * 83492791) ^ (seed * 2654435761)
        n = (n ^ (n >> 13)) * 1274126177
        return ((n & 0xFFFF) / 32767.5) - 1.0

    res = 0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (u[:, 0] if dx else 1 - u[:, 0]) * (u[:, 1] if dy else 1 - u[:, 1]) * (u[:, 2] if dz else 1 - u[:, 2])
                res = res + w * h(i[:, 0] + dx, i[:, 1] + dy, i[:, 2] + dz)
    return res


# ------------------------------------------------------------ meshing
def mesh_sdf(node, bounds, h=0.25, target_faces=None, ground=True, chunk=2_000_000):
    """Marching cubes. bounds = ((x0,y0,z0),(x1,y1,z1)). Mengembalikan v, f, warna."""
    from skimage.measure import marching_cubes
    (x0, y0, z0), (x1, y1, z1) = bounds
    pad = 2 * h
    xs = np.arange(x0 - pad, x1 + pad + h, h)
    ys = np.arange(y0 - pad, y1 + pad + h, h)
    # grid Z diatur supaya z = 0 jatuh tepat di tengah dua sampel -> alas rata
    nz0 = int(math.ceil((0 - (z0 - pad)) / h))
    zs = (np.arange(-nz0, int(math.ceil((z1 + pad) / h)) + 1) + 0.5) * h
    if ground:
        node = Ground(node)
    nx, ny, nz = len(xs), len(ys), len(zs)
    vol = np.empty((nx, ny, nz), dtype=np.float32)
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    XY = np.stack([X.ravel(), Y.ravel()], 1)
    per = max(1, chunk // len(XY))
    for k0 in range(0, nz, per):
        kk = zs[k0:k0 + per]
        P = np.concatenate([np.column_stack([XY, np.full(len(XY), z)]) for z in kk])
        dv = node.d(P).astype(np.float32)
        vol[:, :, k0:k0 + len(kk)] = dv.reshape(len(kk), nx, ny).transpose(1, 2, 0)
    # tutup batas grid
    vol[0, :, :] = vol[-1, :, :] = h
    vol[:, 0, :] = vol[:, -1, :] = h
    vol[:, :, 0] = vol[:, :, -1] = h
    v, f, _, _ = marching_cubes(vol, level=0.0, spacing=(h, h, h))
    v += np.array([xs[0], ys[0], zs[0]])
    v[np.abs(v[:, 2]) < 1e-4, 2] = 0.0
    f = f.astype(np.int64)
    v, f = _fix_orientation(v, f)
    if target_faces and len(f) > target_faces:
        import fast_simplification
        v2, f2 = fast_simplification.simplify(v.astype(np.float32), f.astype(np.int32),
                                              target_reduction=1 - target_faces / len(f), agg=5)
        v, f = np.asarray(v2, np.float64), np.asarray(f2, np.int64)
        v[v[:, 2] < 0.02, 2] = 0.0
        v, f = _fix_orientation(v, f)
    cen = v[f].mean(axis=1)
    _, lab = node.lab(cen)
    cols = [COLOR_KEYS[i] for i in lab]
    return v, f, cols


def _fix_orientation(v, f):
    # volume bertanda; balik jika negatif
    a, b, c = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    vol = np.einsum("ij,ij->i", a, np.cross(b, c)).sum() / 6.0
    if vol < 0:
        f = f[:, ::-1].copy()
    return v, f
