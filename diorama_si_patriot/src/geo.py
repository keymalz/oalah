"""Helper geometri CSG berbasis manifold3d (semua satuan milimeter).

Setiap primitif berwarna dibuat lewat `tag(manifold, warna)` sehingga setelah
operasi boolean kita masih tahu asal (dan warna) tiap segitiga. Hasil akhir
selalu satu mesh manifold tertutup yang sama persis dengan STL yang dicetak.
"""
import math
import numpy as np
import manifold3d as m3
from manifold3d import Manifold, CrossSection, Mesh, JoinType, FillRule
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties

from palette import COLOR_INDEX

m3.set_min_circular_angle(6.0)
m3.set_min_circular_edge_length(0.35)

FONT_BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
FONT_XBOLD = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"

# original_id -> color key (untuk primitif CSG)
_COLOR_BY_ID = {}


def tag(man, color):
    """Tandai manifold sebagai primitif asli dengan warna tertentu."""
    mm = man.as_original()
    _COLOR_BY_ID[mm.original_id()] = color
    return mm


def from_mesh(verts, faces, face_colors):
    """Manifold dari mesh (mis. hasil SDF); face_id menyimpan indeks warna global."""
    fid = np.array([COLOR_INDEX[c] for c in face_colors], dtype=np.uint32)
    mesh = Mesh(vert_properties=np.asarray(verts, dtype=np.float32),
                tri_verts=np.asarray(faces, dtype=np.uint32), face_id=fid)
    man = Manifold(mesh)
    if man.status() != m3.Error.NoError:
        raise RuntimeError(f"mesh bukan manifold: {man.status()}")
    return man


def to_arrays(man):
    """Manifold -> (verts float64, faces int, warna per segitiga)."""
    from palette import COLOR_KEYS
    me = man.to_mesh()
    v = np.array(me.vert_properties[:, :3], dtype=np.float64)
    f = np.array(me.tri_verts, dtype=np.int64)
    fid = np.array(me.face_id, dtype=np.int64) if me.face_id is not None and len(me.face_id) else np.zeros(len(f), np.int64)
    cols = np.empty(len(f), dtype=object)
    ri = list(me.run_index)
    for r, oid in enumerate(me.run_original_id):
        a, b = ri[r] // 3, ri[r + 1] // 3
        if oid in _COLOR_BY_ID:
            cols[a:b] = _COLOR_BY_ID[oid]
        else:
            cols[a:b] = [COLOR_KEYS[i] if 0 <= i < len(COLOR_KEYS) else "cream" for i in fid[a:b]]
    return v, f, list(cols)


def union(parts):
    parts = [p for p in parts if p is not None and not p.is_empty()]
    if not parts:
        return Manifold()
    return Manifold.batch_boolean(parts, m3.OpType.Add)


# ---------------------------------------------------------------- primitif
def box(size, center=(0, 0, 0), color="cream", base=False):
    """Kotak. base=True artinya `center` adalah titik tengah bidang bawah."""
    sx, sy, sz = size
    cx, cy, cz = center
    if base:
        cz += sz / 2
    return tag(Manifold.cube((sx, sy, sz), center=True).translate((cx, cy, cz)), color)


def rbox(size, r, center=(0, 0, 0), color="cream", base=False, segs=None):
    """Kotak bersudut membulat (Minkowski dengan bola melalui hull 8 bola)."""
    sx, sy, sz = size
    r = min(r, sx / 2 - 1e-3, sy / 2 - 1e-3, sz / 2 - 1e-3)
    cx, cy, cz = center
    if base:
        cz += sz / 2
    s = Manifold.sphere(r, segs or 0)
    pts = []
    for dx in (-1, 1):
        for dy in (-1, 1):
            for dz in (-1, 1):
                pts.append(s.translate((dx * (sx / 2 - r), dy * (sy / 2 - r), dz * (sz / 2 - r))))
    return tag(Manifold.batch_hull(pts).translate((cx, cy, cz)), color)


def rbox_xy(size, r, center=(0, 0, 0), color="cream", base=True):
    """Kotak dengan sudut vertikal membulat (alas datar, atas datar)."""
    sx, sy, sz = size
    r = min(r, sx / 2 - 1e-3, sy / 2 - 1e-3)
    cs = CrossSection.square((sx - 2 * r, sy - 2 * r), center=True).offset(r, JoinType.Round)
    m = cs.extrude(sz)
    cx, cy, cz = center
    if not base:
        cz -= sz / 2
    return tag(m.translate((cx, cy, cz)), color)


def cyl(r, h, center=(0, 0, 0), color="cream", r2=None, axis="z", segs=0, base=True):
    """Silinder/frustum. base=True: center = pusat lingkaran bawah (untuk axis z)."""
    m = Manifold.cylinder(h, r, r if r2 is None else r2, segs, center=not base)
    if axis == "x":
        m = m.rotate((0, 90, 0))
    elif axis == "y":
        m = m.rotate((-90, 0, 0))
    return tag(m.translate(center), color)


def cyl_between(p0, p1, r, color="cream", r2=None, segs=0):
    """Silinder dari titik p0 ke p1."""
    p0 = np.asarray(p0, float)
    p1 = np.asarray(p1, float)
    d = p1 - p0
    L = float(np.linalg.norm(d))
    m = Manifold.cylinder(L, r, r if r2 is None else r2, segs, center=False)
    m = m.transform(_align_z_to(d / L, p0))
    return tag(m, color)


def capsule(p0, p1, r, color="cream", r2=None):
    r2 = r if r2 is None else r2
    a = Manifold.sphere(r).translate(tuple(p0))
    b = Manifold.sphere(r2).translate(tuple(p1))
    return tag(Manifold.batch_hull([a, b]), color)


def sphere(r, center=(0, 0, 0), color="cream", scale=(1, 1, 1), segs=0):
    m = Manifold.sphere(r, segs).scale(scale).translate(center)
    return tag(m, color)


def torus(R, r, center=(0, 0, 0), color="cream", axis="z", segs=48):
    cs = CrossSection.circle(r, 24).translate((R, 0))
    m = cs.revolve(segs)
    if axis == "x":
        m = m.rotate((0, 90, 0))
    elif axis == "y":
        m = m.rotate((90, 0, 0))
    return tag(m.translate(center), color)


def revolve_profile(pts, color="cream", segs=64, center=(0, 0, 0)):
    """Putar profil (r, z) mengelilingi sumbu Z. pts berurutan, r>=0."""
    cs = CrossSection([np.asarray(pts, float)], FillRule.Positive)
    if cs.area() < 0:
        cs = CrossSection([np.asarray(pts, float)[::-1]], FillRule.Positive)
    return tag(cs.revolve(segs).translate(center), color)


def extrude_poly(pts, h, color="cream", z0=0.0, center=(0, 0)):
    cs = CrossSection([np.asarray(pts, float)], FillRule.EvenOdd)
    return tag(cs.extrude(h).translate((center[0], center[1], z0)), color)


def _align_z_to(d, origin):
    """Matriks 3x4 yang memetakan sumbu +Z ke arah d lalu translasi ke origin."""
    z = np.array([0, 0, 1.0])
    d = np.asarray(d, float)
    v = np.cross(z, d)
    c = float(np.dot(z, d))
    if np.linalg.norm(v) < 1e-9:
        R = np.eye(3) if c > 0 else np.diag([1, -1, -1.0])
    else:
        vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
        R = np.eye(3) + vx + vx @ vx * (1 / (1 + c))
    M = np.zeros((3, 4))
    M[:, :3] = R
    M[:, 3] = origin
    return M


def place(man, pos=(0, 0, 0), rot_z=0.0):
    return man.rotate((0, 0, rot_z)).translate(pos)


# ---------------------------------------------------------------- footprint 2D
def rrect_cs(w, d, r):
    r = min(r, w / 2 - 0.01, d / 2 - 0.01)
    return CrossSection.square((w - 2 * r, d - 2 * r), center=True).offset(r, JoinType.Round, circular_segments=48)


def superellipse_cs(w, d, n=4.0, segs=160):
    t = np.linspace(0, 2 * np.pi, segs, endpoint=False)
    c, s = np.cos(t), np.sin(t)
    x = (w / 2) * np.sign(c) * np.abs(c) ** (2 / n)
    y = (d / 2) * np.sign(s) * np.abs(s) ** (2 / n)
    return CrossSection([np.stack([x, y], 1)], FillRule.Positive)


def rpoly_cs(n, R, r, rot=0.0):
    """Poligon beraturan bersudut membulat (mis. heksagon)."""
    t = np.radians(rot) + np.arange(n) * 2 * np.pi / n
    pts = np.stack([np.cos(t), np.sin(t)], 1) * (R - r / math.cos(math.pi / n))
    return CrossSection([pts], FillRule.Positive).offset(r, JoinType.Round, circular_segments=48)


def filleted_slab(cs, h, r_top=2.5, chamfer_bot=0.5, steps=8, color="cream"):
    """Pelat/dudukan dengan fillet atas melingkar & chamfer bawah (footprint konveks)."""
    eps = 0.01
    sl = []
    sl.append(cs.offset(-chamfer_bot, JoinType.Round).extrude(eps))
    sl.append(cs.extrude(eps).translate((0, 0, chamfer_bot)))
    sl.append(cs.extrude(eps).translate((0, 0, h - r_top - eps)))
    for i in range(1, steps + 1):
        th = (math.pi / 2) * i / steps
        inset = r_top * (1 - math.cos(th))
        z = h - r_top + r_top * math.sin(th)
        sl.append(cs.offset(-inset, JoinType.Round).extrude(eps).translate((0, 0, z - eps)))
    return tag(Manifold.batch_hull(sl), color)


# ---------------------------------------------------------------- teks
def _flatten_path(path, seg_per_curve=10):
    """Ubah Path matplotlib (dengan kurva Bezier) menjadi list poligon tertutup."""
    from matplotlib.path import Path
    polys = []
    cur = []
    verts = path.vertices
    codes = path.codes
    i = 0
    last = None
    while i < len(verts):
        c = codes[i]
        if c == Path.MOVETO:
            if len(cur) > 2:
                polys.append(np.array(cur))
            cur = [verts[i]]
            last = verts[i]
            i += 1
        elif c == Path.LINETO:
            cur.append(verts[i]); last = verts[i]; i += 1
        elif c == Path.CURVE3:
            p0, p1, p2 = last, verts[i], verts[i + 1]
            for t in np.linspace(0, 1, seg_per_curve + 1)[1:]:
                cur.append((1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2)
            last = p2; i += 2
        elif c == Path.CURVE4:
            p0, p1, p2, p3 = last, verts[i], verts[i + 1], verts[i + 2]
            for t in np.linspace(0, 1, seg_per_curve + 1)[1:]:
                cur.append((1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3)
            last = p3; i += 3
        elif c == Path.CLOSEPOLY:
            if len(cur) > 2:
                polys.append(np.array(cur))
            cur = []
            i += 1
        else:
            i += 1
    if len(cur) > 2:
        polys.append(np.array(cur))
    out = []
    for p in polys:
        # buang titik duplikat berurutan
        keep = np.ones(len(p), bool)
        keep[1:] = np.linalg.norm(np.diff(p, axis=0), axis=1) > 1e-6
        p = p[keep]
        if len(p) > 2 and np.linalg.norm(p[0] - p[-1]) < 1e-6:
            p = p[:-1]
        if len(p) > 2:
            out.append(p)
    return out


def cap_height_per_em(font=FONT_BOLD):
    tp = TextPath((0, 0), "H", size=1.0, prop=FontProperties(fname=font))
    return float(tp.vertices[:, 1].max())


def text_cs(text, cap_h, font=FONT_BOLD, tracking=0.0, align="center", line_gap=0.45):
    """CrossSection teks (bisa multi-baris '\n'), tinggi huruf kapital = cap_h mm.
    Baris dipusatkan; titik (0,0) = tengah blok teks."""
    fp = FontProperties(fname=font)
    em = cap_h / cap_height_per_em(font)
    lines = text.split("\n")
    line_cs = []
    for ln in lines:
        polys = []
        x = 0.0
        for ch in ln:
            if ch == " ":
                tp = TextPath((0, 0), "n", size=em, prop=fp)
                x += em * 0.28
                continue
            tp = TextPath((x, 0), ch, size=em, prop=fp)
            polys += _flatten_path(tp)
            # lebar huruf (advance) diperkirakan dari bounding box + spasi
            adv = TextPath((0, 0), ch + "|", size=em, prop=fp).vertices[:, 0].max() - \
                  TextPath((0, 0), "|", size=em, prop=fp).vertices[:, 0].max()
            x += adv + tracking * em
        cs = CrossSection(polys, FillRule.EvenOdd)
        line_cs.append(cs)
    # susun baris
    total_h = cap_h * len(lines) + cap_h * line_gap * (len(lines) - 1)
    out = CrossSection()
    y_top = total_h / 2
    for k, cs in enumerate(line_cs):
        (x0, y0, x1, y1) = cs.bounds()
        w = x1 - x0
        if align == "center":
            dx = -x0 - w / 2
        elif align == "left":
            dx = -x0
        else:
            dx = -x1
        baseline = y_top - cap_h - k * cap_h * (1 + line_gap)
        out = out + cs.translate((dx, baseline))
    return out


def text_size(cs):
    x0, y0, x1, y1 = cs.bounds()
    return x1 - x0, y1 - y0


def mesh_stats(v, f):
    import trimesh
    tm = trimesh.Trimesh(v, f, process=False)
    return tm.bounds


def clean_mesh(v, f, cols=None, min_keep_mm3=1.0):
    """Bersihkan mesh: gabung verteks, buang komponen degenerat/nol-volume,
    rongga internal kecil, dan serpihan mengambang. Mengembalikan
    (v, f, cols, laporan)."""
    import trimesh
    tm = trimesh.Trimesh(np.asarray(v, float), np.asarray(f), process=False)
    if cols is not None:
        tm.face_attributes["c"] = np.arange(len(f))
    tm.merge_vertices()
    comps = trimesh.graph.connected_components(tm.face_adjacency, nodes=np.arange(len(tm.faces)), min_len=1)
    info = []
    keep = []
    vols = []
    for cidx in comps:
        sub = tm.submesh([cidx], append=True, repair=False)
        vol = float(sub.volume) if sub.is_watertight else 0.0
        vols.append((vol, cidx, float(sub.area)))
    vols.sort(key=lambda x: -abs(x[0]))
    main_vol = vols[0][0]
    dropped = 0.0
    for vol, cidx, area in vols:
        if cidx is vols[0][1]:
            keep.append(cidx)
            continue
        if vol > min_keep_mm3:
            keep.append(cidx)  # badan nyata: dilaporkan, tidak dibuang diam-diam
            info.append(f"badan tambahan {vol:.2f} mm3 dipertahankan")
        else:
            dropped += abs(vol)
            info.append(f"buang komponen vol={vol:.4f} luas={area:.3f}")
    fk = np.sort(np.concatenate(keep))
    nv = tm.vertices
    nf = tm.faces[fk]
    used, inv = np.unique(nf.ravel(), return_inverse=True)
    out_v = nv[used]
    out_f = inv.reshape(-1, 3)
    out_c = None
    if cols is not None:
        cols = np.asarray(cols, dtype=object)
        out_c = list(cols[fk])
    return out_v, out_f, out_c, dict(n_dropped=len(vols) - len(keep), dropped_mm3=round(dropped, 4),
                                     main_mm3=round(main_vol, 2), notes=info[:6])
