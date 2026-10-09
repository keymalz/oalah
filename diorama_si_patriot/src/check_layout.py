"""Periksa & gambar tata letak tampak atas: batas alas, jarak antar dudukan,
figur di dalam bidang datar dudukan, figur tidak saling tabrak dengan label."""
import sys, os, math, json
import numpy as np
from scipy.spatial import ConvexHull
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import layout as L
from build_figs import load
import geo


def fig_footprint(fid, cache):
    v, f, c = load(fid, cache)
    pts = v[:, :2]
    low = v[:, 2] < 25.0  # jejak tapak (bagian bawah) + bayangan atas tetap dihitung semua
    h = ConvexHull(pts)
    return pts[h.vertices]


def xf(pts, dx, dy, rot):
    a = math.radians(rot)
    R = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
    return pts @ R.T + np.array([dx, dy])


def label_boxes(isl):
    out = []
    for (txt, cap, x, y) in isl["labels"]:
        w, h = geo.text_size(geo.text_cs(txt, cap))
        out.append((txt, x - w / 2, y - h / 2, w, h))
    return out


def poly_inside_min(shape, pts):
    """Nilai SDF maksimum (paling dekat tepi) dari titik-titik poligon."""
    # sampel tepi poligon
    s = []
    for a, b in zip(pts, np.roll(pts, -1, 0)):
        for t in np.linspace(0, 1, 8, endpoint=False):
            s.append(a + (b - a) * t)
    return float(shape.d(np.array(s)).max())


def poly_dist(a, b):
    from shapely.geometry import Polygon as SP
    return SP(a).distance(SP(b)) if not SP(a).intersects(SP(b)) else -SP(a).intersection(SP(b)).area


def run(cache, out_png, report_json=None):
    from shapely.geometry import Polygon as SP
    rep = {"islands": [], "pairs": [], "problems": []}
    fig, ax = plt.subplots(figsize=(15, 9.5))
    ax.add_patch(Rectangle((-L.BASE_W / 2, -L.BASE_D / 2), L.BASE_W, L.BASE_D, fc="#6B4A2F", ec="k"))
    outlines = {}
    for isl in L.ISLANDS:
        ol = isl["shape"].outline() + np.array(isl["pos"])
        outlines[isl["id"]] = ol
        ax.add_patch(Polygon(ol, fc="#EFEADC", ec="#999", lw=1))
        bb = ol.min(0), ol.max(0)
        margin = min(bb[0][0] + L.BASE_W / 2, L.BASE_W / 2 - bb[1][0], bb[0][1] + L.BASE_D / 2, L.BASE_D / 2 - bb[1][1])
        size = bb[1] - bb[0]
        rep["islands"].append(dict(id=isl["id"], name=isl["name"], pos=isl["pos"], size=[round(float(s), 1) for s in size],
                                   edge_margin=round(float(margin), 1)))
        if margin < L.MIN_EDGE_MARGIN:
            rep["problems"].append(f"{isl['id']} terlalu dekat tepi alas ({margin:.1f} mm)")
        if max(size) > 215:
            rep["problems"].append(f"{isl['id']} tidak muat bed 220 ({size})")
        objs = []
        for (txt, x0, y0, w, h) in label_boxes(isl):
            r = np.array([(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h)])
            m = poly_inside_min(isl["shape"], r)
            if m > -(L.ISLAND_TOP_FILLET + 1.5):
                rep["problems"].append(f"{isl['id']} label '{txt}' terlalu dekat tepi ({m:.1f})")
            rr = r + np.array(isl["pos"])
            ax.add_patch(Polygon(rr, fc="#1E4D2B", alpha=0.8, ec="none"))
            ax.text(*(rr.mean(0)), txt.replace("\n", " "), color="w", fontsize=5.5, ha="center", va="center")
            objs.append(("L:" + txt, r))
        for (fid, dx, dy, rot) in isl["figures"]:
            fp = xf(fig_footprint(fid, cache), dx, dy, rot)
            m = poly_inside_min(isl["shape"], fp)
            if m > -(L.ISLAND_TOP_FILLET + 0.5):
                rep["problems"].append(f"{isl['id']} figur {fid} keluar bidang datar ({m:.1f})")
            fpw = fp + np.array(isl["pos"])
            ax.add_patch(Polygon(fpw, fc="#3E8A4D", alpha=0.55, ec="#1F5A35"))
            ax.text(*(fpw.mean(0)), fid, fontsize=7, ha="center", va="center")
            objs.append((fid, fp))
        for i in range(len(objs)):
            for j in range(i + 1, len(objs)):
                d = poly_dist(objs[i][1], objs[j][1])
                if d < 1.5:
                    rep["problems"].append(f"{isl['id']}: {objs[i][0]} vs {objs[j][0]} jarak {d:.1f}")
        ax.text(isl["pos"][0], bb[1][1] + 3, isl["id"], fontsize=8, ha="center")
    ids = list(outlines)
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            d = SP(outlines[ids[i]]).distance(SP(outlines[ids[j]]))
            rep["pairs"].append((ids[i], ids[j], round(float(d), 1)))
            if d < 8.0:
                rep["problems"].append(f"{ids[i]}-{ids[j]} jarak antar dudukan {d:.1f} mm")
    ax.set_xlim(-320, 320); ax.set_ylim(-195, 195); ax.set_aspect("equal")
    ax.grid(alpha=0.25)
    ax.set_title("Tata letak tampak atas (mm) - alas 600 x 360")
    fig.savefig(out_png, dpi=110, bbox_inches="tight")
    if report_json:
        json.dump(rep, open(report_json, "w"), indent=1)
    for p in rep["problems"]:
        print("MASALAH:", p)
    mind = sorted(rep["pairs"], key=lambda x: x[2])[:6]
    print("jarak antar dudukan terdekat:", mind)
    print("margin tepi:", [(i["id"], i["edge_margin"]) for i in rep["islands"]])
    return rep


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
