"""Bangun SELURUH berkas cetak diorama SI PATRIOT + pemeriksaan otomatis.

    python build_all.py            # dari folder src/, butuh paket di requirements.txt

Keluaran (relatif folder diorama_si_patriot/):
    stl/figur/*.stl                    figur & alat (F01..F18)
    stl/dudukan/*.stl                  dudukan krem berlabel timbul (D01..D10)
    stl/dudukan_varian_stiker/*.stl    dudukan dengan cekungan stiker label
    stl/sapi_varian_belah/*.stl        sapi dibelah dua (cetak tanpa support)
    stl/alas_cetak3d/*.stl             6 ubin alas + kunci sambungan (opsional)
    build/meshes/*.npz                 mesh + warna untuk adegan Blender
    reports/manifest.json              posisi, ukuran, jumlah cetak
    reports/stl_check.csv / .md        hasil pemeriksaan STL
"""
import sys, os, json, math, time, re
import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import layout as L
import geo
from build_figs import build_one, load
from islands import build_island
import base_tiles

OUT = {k: os.path.join(ROOT, "stl", k) for k in ("figur", "dudukan", "dudukan_varian_stiker", "sapi_varian_belah", "alas_cetak3d")}
MESH = os.path.join(ROOT, "build", "meshes")
REP = os.path.join(ROOT, "reports")
BED = (220.0, 220.0, 250.0)


def slug(s):
    s = s.lower().replace("&", "dan")
    s = re.sub(r"\(.*?\)", "", s)
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return s


def save_npz(name, v, f, c):
    np.savez_compressed(os.path.join(MESH, name + ".npz"), v=np.asarray(v), f=np.asarray(f), c=np.array(c))


CLEAN_LOG = {}


def export_stl(path, v, f, c=None):
    """Bersihkan lalu ekspor STL biner. Mengembalikan (path, v, f, c) hasil bersih."""
    v, f, c, info = geo.clean_mesh(v, f, c)
    CLEAN_LOG[os.path.basename(path)] = info
    tm = trimesh.Trimesh(np.asarray(v, float), np.asarray(f), process=False)
    tm.export(path)
    return path, v, f, c


# ------------------------------------------------------------------ pemeriksaan
def check_stl(path, sample=4000, seed=0):
    tm = trimesh.load(path, force="mesh", process=True)
    r = {}
    r["file"] = os.path.relpath(path, ROOT)
    r["tri"] = len(tm.faces)
    r["watertight"] = bool(tm.is_watertight)
    r["winding_ok"] = bool(tm.is_winding_consistent)
    r["is_volume"] = bool(tm.is_volume)
    r["volume_cm3"] = round(float(tm.volume) / 1000.0, 2)
    bodies = tm.split(only_watertight=False)
    r["bodies"] = len(bodies)
    r["smallest_body_mm3"] = round(float(min(b.volume for b in bodies)), 2) if len(bodies) > 1 else None
    mn, mx = tm.bounds
    r["min_z"] = round(float(mn[2]), 4)
    r["size_mm"] = [round(float(x), 1) for x in (mx - mn)]
    # bidang alas: luas segitiga yang menyentuh z=0 dan menghadap bawah
    fz = tm.triangles[:, :, 2]
    on_bed = (np.abs(fz).max(axis=1) < 1e-3) & (tm.face_normals[:, 2] < -0.99)
    r["bed_contact_mm2"] = round(float(tm.area_faces[on_bed].sum()), 1)
    # overhang > 45 derajat yang tidak di atas bed
    cen_z = tm.triangles_center[:, 2]
    oh = (tm.face_normals[:, 2] < -math.cos(math.radians(45))) & (cen_z > 0.3)
    r["overhang45_mm2"] = round(float(tm.area_faces[oh].sum()), 1)
    oh60 = (tm.face_normals[:, 2] < -math.cos(math.radians(30))) & (cen_z > 0.3)
    r["overhang60_mm2"] = round(float(tm.area_faces[oh60].sum()), 1)
    # ketebalan lokal (ray ke dalam dari titik acak permukaan)
    try:
        pts, fi = trimesh.sample.sample_surface(tm, sample, seed=seed)
        nrm = tm.face_normals[fi]
        orig = pts - nrm * 1e-3
        loc, idx_ray, idx_tri = tm.ray.intersects_location(orig, -nrm, multiple_hits=False)
        th = np.full(len(pts), np.nan)
        th[idx_ray] = np.linalg.norm(loc - orig[idx_ray], axis=1)
        th = th[~np.isnan(th)]
        r["thick_p1_mm"] = round(float(np.percentile(th, 1)), 2)
        r["thick_p5_mm"] = round(float(np.percentile(th, 5)), 2)
        r["thin_lt_0p8_pct"] = round(float((th < 0.8).mean() * 100), 2)
    except Exception as e:
        r["thick_p1_mm"] = r["thick_p5_mm"] = r["thin_lt_0p8_pct"] = None
    # validasi kedua dengan manifold3d
    from manifold3d import Manifold, Mesh, Error
    mm = Manifold(Mesh(vert_properties=np.asarray(tm.vertices, np.float32), tri_verts=np.asarray(tm.faces, np.uint32)))
    r["manifold3d_ok"] = mm.status() == Error.NoError and not mm.is_empty()
    r["fits_bed"] = bool(r["size_mm"][0] <= BED[0] - 5 and r["size_mm"][1] <= BED[1] - 5 and r["size_mm"][2] <= BED[2]) or \
        bool(r["size_mm"][1] <= BED[0] - 5 and r["size_mm"][0] <= BED[1] - 5 and r["size_mm"][2] <= BED[2])
    r["PASS"] = bool(r["watertight"] and r["winding_ok"] and r["is_volume"] and r["volume_cm3"] > 0 and r["bodies"] == 1
                     and abs(r["min_z"]) < 1e-3 and r["manifold3d_ok"] and r["fits_bed"])
    return r


# ------------------------------------------------------------------ varian sapi belah
def split_cow(v, f, c):
    from manifold3d import Manifold
    m = geo.from_mesh(v, f, c)
    pos, neg = m.split_by_plane((0, 1, 0), 0.0)
    # dua lubang pin 1,75 mm (pakai potongan filamen) untuk menyelaraskan
    holes = geo.union([geo.cyl(0.95, 14.0, (x, 0, z), axis="y", base=False) for (x, z) in ((-9.0, 25.0), (9.0, 25.0))])
    out = []
    for half, ang in ((pos, 90), (neg, -90)):
        h = (half - holes).rotate((ang, 0, 0))
        bb = h.bounding_box()
        h = h.translate((0, 0, -bb[2]))
        out.append(geo.to_arrays(h))
    return out


def main():
    t0 = time.time()
    for d in list(OUT.values()) + [MESH, REP]:
        os.makedirs(d, exist_ok=True)
    cache = os.path.join(ROOT, "build", "cache")
    os.makedirs(cache, exist_ok=True)
    manifest = {"units": "mm", "base": dict(w=L.BASE_W, d=L.BASE_D, t=L.BASE_T), "objects": [], "islands": []}
    files = []

    # ---------------- figur
    from concurrent.futures import ProcessPoolExecutor
    todo = [fid for fid in L.FIGURES if not os.path.exists(os.path.join(cache, fid + ".npz")) or "--rebuild" in sys.argv]
    if todo:
        with ProcessPoolExecutor(4) as ex:
            for fid, n, dt in ex.map(build_one, todo, [cache] * len(todo)):
                print(f"  figur {fid}: {n} segitiga ({dt:.1f}s)", flush=True)
    fig_world = {}
    for isl in L.ISLANDS:
        for (fid, dx, dy, rot) in isl["figures"]:
            fig_world[fid] = (isl["id"], isl["pos"][0] + dx, isl["pos"][1] + dy, isl["H"], rot)
    for fid, (name, spec) in L.FIGURES.items():
        v, f, c = load(fid, cache)
        fn = f"{fid}_{slug(name)}.stl"
        p, v, f, c = export_stl(os.path.join(OUT["figur"], fn), v, f, c)
        save_npz(fid, v, f, c)
        files.append(p)
        if fid in fig_world:
            iid, X, Y, Z, rot = fig_world[fid]
        else:
            parent, off = L.ATTACH[fid]
            iid, X0, Y0, Z0, rot = fig_world[parent]
            a = math.radians(rot)
            X = X0 + off[0] * math.cos(a) - off[1] * math.sin(a)
            Y = Y0 + off[0] * math.sin(a) + off[1] * math.cos(a)
            Z = Z0 + off[2]
        mn, mx = v.min(0), v.max(0)
        manifest["objects"].append(dict(id=fid, name=name, kind="figur", stl=os.path.relpath(p, ROOT), count=1,
                                        island=iid, world=[round(X, 2), round(Y, 2), round(Z, 2)], rot_z=rot,
                                        size=[round(float(x), 1) for x in (mx - mn)],
                                        colors=sorted(set(c))))
        print(f"  ekspor {fn}", flush=True)

    # ---------------- varian sapi belah
    for fid, tag_ in (("F05", "A"), ("F06", "B")):
        v, f, c = load(fid, cache)
        for k, (side, (hv, hf, hc)) in enumerate(zip(("kiri", "kanan"), split_cow(v, f, c))):
            fn = f"{fid}-{k + 1}_sapi_{tag_}_belahan_{side}.stl"
            files.append(export_stl(os.path.join(OUT["sapi_varian_belah"], fn), hv, hf)[0])

    # ---------------- dudukan
    stickers = []
    for isl in L.ISLANDS:
        for variant in ("timbul", "stiker"):
            v, f, c, st = build_island(isl, variant)
            sub = "dudukan" if variant == "timbul" else "dudukan_varian_stiker"
            fn = f"{isl['id']}_dudukan_{slug(isl['name'])}" + ("" if variant == "timbul" else "_stiker") + ".stl"
            p, v, f, c = export_stl(os.path.join(OUT[sub], fn), v, f, c)
            files.append(p)
            if variant == "timbul":
                save_npz(isl["id"], v, f, c)
                ol = isl["shape"].outline()
                mn, mx = v.min(0), v.max(0)
                manifest["islands"].append(dict(
                    id=isl["id"], name=isl["name"], stl=os.path.relpath(p, ROOT), count=1,
                    center=list(isl["pos"]), center_from_front_left=[isl["pos"][0] + L.BASE_W / 2, isl["pos"][1] + L.BASE_D / 2],
                    thickness=isl["H"], size=[round(float(x), 1) for x in (mx - mn)],
                    labels=[dict(text=t, cap_mm=cap, at=[x, y]) for (t, cap, x, y) in isl["labels"]],
                    color_change_z=isl["H"],
                    outline=[[round(float(a) + isl["pos"][0], 2), round(float(b) + isl["pos"][1], 2)] for a, b in ol[::4]]))
            else:
                for s_ in st:
                    s_["island"] = isl["id"]
                stickers += st
            print(f"  ekspor {fn}", flush=True)
    manifest["stickers"] = stickers

    # ---------------- alas cetak 3D
    for name, origin, (v, f, c) in base_tiles.build_tiles():
        fn = f"{name}_ubin_alas_{['depan', 'belakang'][int(name[1]) - 1]}_{['kiri', 'tengah', 'kanan'][int(name[2]) - 1]}.stl"
        p, v, f, c = export_stl(os.path.join(OUT["alas_cetak3d"], fn), v, f, c)
        files.append(p)
        save_npz(name, v, f, c)
        manifest.setdefault("tiles", []).append(dict(id=name, stl=os.path.relpath(p, ROOT), origin=list(origin)))
    v, f, c = base_tiles.build_key()
    p = export_stl(os.path.join(OUT["alas_cetak3d"], "K01_kunci_sambungan_bowtie.stl"), v, f, c)[0]
    files.append(p)
    manifest["tile_keys"] = dict(stl=os.path.relpath(p, ROOT), count=len(base_tiles.key_positions()),
                                 positions=base_tiles.key_positions())
    json.dump(manifest, open(os.path.join(REP, "manifest.json"), "w"), indent=1)

    # ---------------- pemeriksaan
    print("Memeriksa STL ...", flush=True)
    rows = []
    for p in files:
        r = check_stl(p)
        rows.append(r)
        print(("  OK   " if r["PASS"] else "  GAGAL") + f" {r['file']}  bodies={r['bodies']} vol={r['volume_cm3']}cm3 "
              f"size={r['size_mm']} p1={r['thick_p1_mm']} oh45={r['overhang45_mm2']}", flush=True)
    keys = list(rows[0].keys())
    with open(os.path.join(REP, "stl_check.csv"), "w") as fh:
        fh.write(",".join(keys) + "\n")
        for r in rows:
            fh.write(",".join('"' + str(r[k]).replace('"', "'") + '"' for k in keys) + "\n")
    for r in rows:
        r["cleanup"] = CLEAN_LOG.get(os.path.basename(r["file"]), {})
    json.dump(rows, open(os.path.join(REP, "stl_check.json"), "w"), indent=1)
    n_ok = sum(r["PASS"] for r in rows)
    print(f"{n_ok}/{len(rows)} STL lolos. Selesai dalam {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
