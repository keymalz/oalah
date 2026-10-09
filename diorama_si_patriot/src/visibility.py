"""Uji keterbacaan dari posisi pengunjung (ray casting).

Mata pengunjung: tinggi 155 cm dari lantai, 1 m di depan tepi meja (meja 75 cm,
dalam 60 cm), di tiga posisi: kiri (-30 cm), tengah, kanan (+30 cm).
Untuk setiap label: persentase titik huruf yang terlihat (tidak terhalang).
Untuk setiap figur: persentase titik permukaan atas yang terlihat.
Hasil: reports/visibility.json + ringkasan di layar.
"""
import os, sys, json, math
import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import layout as L
import geo

MESH = os.path.join(ROOT, "build", "meshes")
MAN = json.load(open(os.path.join(ROOT, "reports", "manifest.json")))
TABLE_D, TABLE_H, VIEW = 600.0, 750.0, 1000.0
EYE_H = float(os.environ.get("EYE_H", "1550"))
EYE_Z = EYE_H - TABLE_H - L.BASE_T
EYES = {"kiri": (-300.0, -TABLE_D / 2 - VIEW, EYE_Z), "tengah": (0.0, -TABLE_D / 2 - VIEW, EYE_Z),
        "kanan": (300.0, -TABLE_D / 2 - VIEW, EYE_Z)}


def world_mesh(name, pos, rot):
    z = np.load(os.path.join(MESH, name + ".npz"), allow_pickle=True)
    v = z["v"].copy()
    a = math.radians(rot)
    R = np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])
    v = v @ R.T + np.asarray(pos)
    return trimesh.Trimesh(v, z["f"], process=False)


def label_points(isl, n_per=160, rng=None):
    pts = []
    for (txt, cap, x, y) in [(l["text"], l["cap_mm"], l["at"][0], l["at"][1]) for l in isl["labels"]]:
        cs = geo.text_cs(txt, cap).translate((x, y))
        polys = cs.to_polygons()
        from matplotlib.path import Path
        x0, y0, x1, y1 = cs.bounds()
        cand = np.column_stack([rng.uniform(x0, x1, n_per * 8), rng.uniform(y0, y1, n_per * 8)])
        inside = np.zeros(len(cand), bool)
        for p in polys:
            inside ^= Path(np.asarray(p)).contains_points(cand)
        c = cand[inside][:n_per]
        pts.append((txt, np.column_stack([c + np.array(isl["center"]), np.full(len(c), isl["thickness"] + L.LABEL_RAISE)])))
    return pts


def run():
    rng = np.random.default_rng(1)
    meshes = []
    for isl in MAN["islands"]:
        meshes.append(world_mesh(isl["id"], (isl["center"][0], isl["center"][1], 0), 0))
    figs = {}
    for o in MAN["objects"]:
        m = world_mesh(o["id"], o["world"], o["rot_z"])
        figs[o["id"]] = m
        meshes.append(m)
    scene = trimesh.util.concatenate(meshes)
    rep = {"labels": {}, "figures": {}}
    for isl in MAN["islands"]:
        for txt, P in label_points(isl, rng=rng):
            key = txt.replace("\n", " ")
            rep["labels"][key] = {}
            for en, e in EYES.items():
                e = np.asarray(e)
                d = P - e
                dist = np.linalg.norm(d, axis=1)
                dirs = d / dist[:, None]
                loc, ir, it = scene.ray.intersects_location(np.repeat(e[None], len(P), 0), dirs, multiple_hits=False)
                hit = np.full(len(P), np.inf)
                hit[ir] = np.linalg.norm(loc - e, axis=1)
                vis = hit >= dist - 0.25
                rep["labels"][key][en] = round(float(vis.mean() * 100), 1)
    for fid, m in figs.items():
        pts, fi = trimesh.sample.sample_surface(m, 600, seed=2)
        up = m.face_normals[fi][:, 2] > -0.2
        P = pts[up] + m.face_normals[fi][up] * 0.05
        rep["figures"][fid] = {}
        for en, e in EYES.items():
            e = np.asarray(e)
            d = P - e
            dist = np.linalg.norm(d, axis=1)
            dirs = d / dist[:, None]
            # hanya titik yang menghadap mata
            facing = np.einsum("ij,ij->i", -dirs, m.face_normals[fi][up]) > 0.05
            loc, ir, it = scene.ray.intersects_location(np.repeat(e[None], len(P), 0), dirs, multiple_hits=False)
            hit = np.full(len(P), np.inf)
            hit[ir] = np.linalg.norm(loc - e, axis=1)
            vis = (hit >= dist - 0.3) & facing
            rep["figures"][fid][en] = round(float(vis.sum() / max(1, facing.sum()) * 100), 1)
    rep["eye_height_mm"] = EYE_H
    json.dump(rep, open(os.path.join(ROOT, "reports", f"visibility_mata{int(EYE_H)}.json"), "w"), indent=1)
    print("LABEL (% huruf terlihat: kiri / tengah / kanan)")
    for k, v in rep["labels"].items():
        flag = "  <-- TERHALANG" if min(v.values()) < 90 else ""
        print(f"  {k:32s} {v['kiri']:5.1f} {v['tengah']:5.1f} {v['kanan']:5.1f}{flag}")
    print("FIGUR (% permukaan menghadap mata yang terlihat)")
    for k, v in rep["figures"].items():
        print(f"  {k:5s} {v['kiri']:5.1f} {v['tengah']:5.1f} {v['kanan']:5.1f}")
    return rep


if __name__ == "__main__":
    run()
