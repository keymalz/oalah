"""Gambar teknik & dokumen cetak:
  docs/template_penempatan_1-1_penuh_600x360.pdf   (cetak di percetakan, skala 100%)
  docs/template_penempatan_1-1_A4.pdf              (12 lembar A4 bersambung)
  docs/denah_tata_letak_mm.png                     (denah ber-dimensi)
  docs/simulasi_meja_96x60.png                     (tampak atas + depan meja)
  docs/sambungan_ubin_alas.png                     (opsi alas cetak 3D)
"""
import os, sys, json, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, FancyArrowPatch
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.font_manager import FontProperties

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import layout as L
import base_tiles

FB = FontProperties(fname="/usr/share/fonts/opentype/inter/Inter-Bold.otf")
FR = FontProperties(fname="/usr/share/fonts/opentype/inter/Inter-Regular.otf")
FM = FontProperties(fname="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")
MAN = json.load(open(os.path.join(ROOT, "reports", "manifest.json")))
DOCS = os.path.join(ROOT, "docs")
FIGNAMES = {o["id"]: o["name"] for o in MAN["objects"]}


def _draw_template(ax, lw=0.5, details=True):
    """Gambar template di koordinat mm dengan origin pojok kiri-depan alas."""
    ox, oy = L.BASE_W / 2, L.BASE_D / 2
    ax.add_patch(Rectangle((0, 0), L.BASE_W, L.BASE_D, fill=False, lw=lw * 1.6))
    for isl in MAN["islands"]:
        ol = np.array(isl["outline"]) + np.array([ox, oy])
        ax.add_patch(Polygon(ol, closed=True, fill=False, lw=lw, ec="k"))
        cx, cy = isl["center"][0] + ox, isl["center"][1] + oy
        ax.plot([cx - 6, cx + 6], [cy, cy], "k", lw=lw * 0.6)
        ax.plot([cx, cx], [cy - 6, cy + 6], "k", lw=lw * 0.6)
        if details:
            ax.text(cx, cy + 9, isl["id"], fontproperties=FB, fontsize=9, ha="center")
            ax.text(cx, cy - 12, isl["name"], fontproperties=FR, fontsize=5.5, ha="center")
            ax.text(cx, cy - 18, f"pusat ({cx:.0f}, {cy:.0f}) mm", fontproperties=FR, fontsize=5, ha="center", color="#444")
    # tanda depan
    ax.text(L.BASE_W / 2, -8, "DEPAN (sisi pengunjung)", fontproperties=FB, fontsize=8, ha="center", va="top")
    ax.text(4, 4, "(0,0) pojok kiri-depan", fontproperties=FR, fontsize=5, va="bottom")


def template_full(path):
    W, H = L.BASE_W + 40, L.BASE_D + 50
    fig = plt.figure(figsize=(W / 25.4, H / 25.4))
    ax = fig.add_axes([20 / W, 30 / H, L.BASE_W / W, L.BASE_D / H])
    ax.set_xlim(0, L.BASE_W); ax.set_ylim(0, L.BASE_D); ax.axis("off")
    _draw_template(ax)
    fig.text(0.5, 1 - 8 / H, "TEMPLATE PENEMPATAN DUDUKAN 1:1 - alas 600 x 360 mm - CETAK SKALA 100%",
             fontproperties=FB, fontsize=10, ha="center", va="top")
    # skala kalibrasi 100 mm
    fig.add_artist(Rectangle((20 / W, 8 / H), 100 / W, 4 / H, transform=fig.transFigure, fill=False, lw=0.6))
    fig.text((20 + 50) / W, 14 / H, "kalibrasi: kotak ini = 100 mm", fontproperties=FR, fontsize=6, ha="center")
    fig.savefig(path)
    plt.close(fig)


def template_a4(path):
    """Ubin A4 potret (lebar efektif 190 x 277), tumpang tindih 10 mm, tanda sambung."""
    pw, ph = 210.0, 297.0
    m = 10.0
    ew, eh = pw - 2 * m, ph - 2 * m
    ov = 10.0
    sx, sy = ew - ov, eh - ov
    nx = math.ceil((L.BASE_W - ov) / sx)
    ny = math.ceil((L.BASE_D - ov) / sy)
    with PdfPages(path) as pdf:
        for j in range(ny):
            for i in range(nx):
                x0, y0 = i * sx, j * sy
                fig = plt.figure(figsize=(pw / 25.4, ph / 25.4))
                ax = fig.add_axes([m / pw, m / ph, ew / pw, eh / ph])
                ax.set_xlim(x0, x0 + ew); ax.set_ylim(y0, y0 + eh); ax.axis("off")
                _draw_template(ax, lw=0.6)
                # garis tumpang tindih
                ax.axvline(x0 + ew - ov, color="#c33", lw=0.4, ls="--")
                ax.axhline(y0 + eh - ov, color="#c33", lw=0.4, ls="--")
                fig.text(0.5, 1 - 4 / ph, f"Lembar {j * nx + i + 1}/{nx * ny}  (kolom {i + 1}, baris {j + 1} dari depan)  "
                         f"x {x0:.0f}-{x0 + ew:.0f} mm, y {y0:.0f}-{y0 + eh:.0f} mm. Tempel lembar berikut di garis putus merah.",
                         fontproperties=FR, fontsize=6, ha="center", va="top")
                fig.add_artist(Rectangle((m / pw, 2.5 / ph), 50 / pw, 3 / ph, transform=fig.transFigure, fill=False, lw=0.5))
                fig.text((m + 55) / pw, 3.5 / ph, "= 50 mm (cek skala)", fontproperties=FR, fontsize=5)
                pdf.savefig(fig)
                plt.close(fig)
    return nx * ny


def plan_drawing(path):
    fig, ax = plt.subplots(figsize=(16, 10.5))
    ox, oy = L.BASE_W / 2, L.BASE_D / 2
    ax.add_patch(Rectangle((0, 0), L.BASE_W, L.BASE_D, fc="#6B4A2F", ec="k"))
    for isl in MAN["islands"]:
        ol = np.array(isl["outline"]) + np.array([ox, oy])
        ax.add_patch(Polygon(ol, fc="#EFEADC", ec="#777", lw=0.8))
        cx, cy = isl["center"][0] + ox, isl["center"][1] + oy
        ax.plot(cx, cy, "+", color="#1E4D2B", ms=10)
        ax.text(cx, cy + 4, f"{isl['id']}", fontproperties=FB, fontsize=10, ha="center", color="#1E4D2B")
        ax.text(cx, cy - 7, f"({cx:.0f}; {cy:.0f})\nt = {isl['thickness']:.0f} mm", fontproperties=FR, fontsize=7,
                ha="center", va="top", color="#333")
    # dimensi alas
    def dim(x0, y0, x1, y1, txt, off=(0, 0)):
        ax.annotate("", (x0, y0), (x1, y1), arrowprops=dict(arrowstyle="<->", lw=0.8))
        ax.text((x0 + x1) / 2 + off[0], (y0 + y1) / 2 + off[1], txt, fontproperties=FR, fontsize=9, ha="center", va="center",
                bbox=dict(fc="white", ec="none", pad=1))
    dim(0, -14, L.BASE_W, -14, "600 mm")
    dim(-14, 0, -14, L.BASE_D, "360 mm")
    ax.text(L.BASE_W / 2, -26, "DEPAN (sisi pengunjung)", fontproperties=FB, fontsize=10, ha="center")
    rows = [f"{i['id']}  {i['name']:<32s} pusat X={i['center_from_front_left'][0]:5.0f}  Y={i['center_from_front_left'][1]:5.0f}  "
            f"ukuran {i['size'][0]:.0f}x{i['size'][1]:.0f} mm  tebal {i['thickness']:.0f}" for i in MAN["islands"]]
    ax.text(0, L.BASE_D + 12, "Koordinat pusat dudukan diukur dari pojok KIRI-DEPAN alas (mm):\n" + "\n".join(rows),
            fontproperties=FM, fontsize=7.5, va="bottom")
    ax.set_xlim(-30, L.BASE_W + 10); ax.set_ylim(-35, L.BASE_D + 140); ax.set_aspect("equal"); ax.axis("off")
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)


def table_drawing(path, tallest):
    TW, TD, TH = 960.0, 600.0, 750.0
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(17, 7.2), gridspec_kw=dict(width_ratios=[1.25, 1]))
    # tampak atas
    a1.add_patch(Rectangle((0, 0), TW, TD, fc="#D9D3C7", ec="k"))
    bx, by = (TW - L.BASE_W) / 2, (TD - L.BASE_D) / 2
    a1.add_patch(Rectangle((bx, by), L.BASE_W, L.BASE_D, fc="#6B4A2F", ec="k"))
    for isl in MAN["islands"]:
        ol = np.array(isl["outline"]) + np.array([bx + L.BASE_W / 2, by + L.BASE_D / 2])
        a1.add_patch(Polygon(ol, fc="#EFEADC", ec="#999", lw=0.5))

    def dim(ax, x0, y0, x1, y1, txt, rot=0):
        ax.annotate("", (x0, y0), (x1, y1), arrowprops=dict(arrowstyle="<->", lw=0.9))
        ax.text((x0 + x1) / 2, (y0 + y1) / 2, txt, fontproperties=FR, fontsize=9, ha="center", va="center", rotation=rot,
                bbox=dict(fc="white", ec="none", pad=1))
    dim(a1, 0, -30, TW, -30, "meja 960 mm")
    dim(a1, -30, 0, -30, TD, "600 mm (perkiraan)", 90)
    dim(a1, 0, TD / 2, bx, TD / 2, f"{bx:.0f}")
    dim(a1, bx + L.BASE_W, TD / 2, TW, TD / 2, f"{bx:.0f}")
    dim(a1, TW / 2, 0, TW / 2, by, f"{by:.0f}")
    dim(a1, TW / 2, by + L.BASE_D, TW / 2, TD, f"{by:.0f}")
    dim(a1, bx, by - 16, bx + L.BASE_W, by - 16, "alas 600")
    a1.text(TW / 2, -60, "DEPAN (pengunjung)", fontproperties=FB, fontsize=10, ha="center")
    a1.set_xlim(-60, TW + 20); a1.set_ylim(-80, TD + 20); a1.set_aspect("equal"); a1.axis("off")
    a1.set_title("Tampak atas: diorama 600 x 360 mm di meja 960 x 600 mm", fontproperties=FB)
    # tampak samping (potongan dari kiri)
    a2.add_patch(Rectangle((0, TH - 25), TD, 25, fc="#D9D3C7", ec="k"))
    for x in (45, TD - 85):
        a2.add_patch(Rectangle((x, 0), 40, TH - 25, fc="#D9D3C7", ec="k"))
    a2.add_patch(Rectangle((by, TH), L.BASE_D, L.BASE_T, fc="#6B4A2F", ec="k"))
    a2.add_patch(Rectangle((by + 40, TH + L.BASE_T), L.BASE_D - 80, tallest, fc="#EFEADC", ec="#999", ls="--"))
    a2.text(TD / 2, TH + L.BASE_T + tallest + 12, f"objek tertinggi +-{tallest:.0f} mm (kandang/HP)", fontproperties=FR,
            fontsize=8, ha="center")
    # pengunjung
    px = -1000.0
    a2.plot([px, px], [0, 1550], color="#888", lw=6, solid_capstyle="round")
    a2.add_patch(plt.Circle((px, 1600), 70, color="#888"))
    a2.plot([px, TD / 2], [1550, TH + 20], color="#C62828", lw=0.8, ls="--")
    ang = math.degrees(math.atan2(1550 - TH - 12, TD / 2 - px))
    a2.text(px + 300, 1450, f"mata 155 cm, 1 m dari meja\nsudut pandang +-{ang:.0f} derajat ke bawah", fontproperties=FR, fontsize=8)
    dim(a2, TD + 60, 0, TD + 60, TH, "750 mm", 90)
    dim(a2, px, -40, 0, -40, "1000 mm")
    a2.set_xlim(px - 150, TD + 120); a2.set_ylim(-90, 1800); a2.set_aspect("equal"); a2.axis("off")
    a2.set_title("Tampak samping (kiri)", fontproperties=FB)
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)


def tile_drawing(path):
    from matplotlib.patches import Polygon as P
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(17, 6.5), gridspec_kw=dict(width_ratios=[1.6, 1]))
    tw, td = L.BASE_W / base_tiles.NX, L.BASE_D / base_tiles.NY
    for j in range(base_tiles.NY):
        for i in range(base_tiles.NX):
            a1.add_patch(Rectangle((i * tw, j * td), tw, td, fc="#8A6340" if (i + j) % 2 else "#6B4A2F", ec="k"))
            a1.text(i * tw + tw / 2, j * td + td / 2, f"T{j + 1}{i + 1}", fontproperties=FB, fontsize=14, ha="center", color="w")
    bt = base_tiles.bowtie_cs()
    poly = np.array(bt.to_polygons()[0])
    for (x, y, a) in base_tiles.key_positions():
        r = math.radians(a)
        R = np.array([[math.cos(r), -math.sin(r)], [math.sin(r), math.cos(r)]])
        pp = poly @ R.T + np.array([x + L.BASE_W / 2, y + L.BASE_D / 2])
        a1.add_patch(P(pp, fc="#F2C14E", ec="k", lw=0.6))
    for isl in MAN["islands"]:
        ol = np.array(isl["outline"]) + np.array([L.BASE_W / 2, L.BASE_D / 2])
        a1.add_patch(P(ol, fill=False, ec="#EFEADC", lw=0.8, ls="--"))
    a1.set_xlim(-10, L.BASE_W + 10); a1.set_ylim(-25, L.BASE_D + 10); a1.set_aspect("equal"); a1.axis("off")
    a1.text(L.BASE_W / 2, -15, f"Tampak BAWAH-ke-atas (posisi sebenarnya): 6 ubin 200 x 180 x {base_tiles.TILE_T:.0f} mm, "
            f"{len(base_tiles.key_positions())} kunci kupu-kupu (kuning)", fontproperties=FR, fontsize=9, ha="center")
    # detail potongan
    T, K = base_tiles.TILE_T, base_tiles.KEY_T
    a2.add_patch(Rectangle((0, 0), 60, T, fc="#6B4A2F", ec="k"))
    a2.add_patch(Rectangle((60.4, 0), 60, T, fc="#8A6340", ec="k"))
    a2.add_patch(Rectangle((45, 0), 30.4, K, fc="#F2C14E", ec="k"))
    a2.add_patch(Rectangle((20, T - base_tiles.POCKET_DEPTH), 80, base_tiles.POCKET_DEPTH + 10, fc="#EFEADC", ec="#777"))
    a2.text(60, T + 12, "dudukan masuk cekungan 0,6 mm", fontproperties=FR, fontsize=8, ha="center")
    a2.text(60, -5, f"kunci {K:.0f} mm masuk kantong {K + base_tiles.KEY_CLEAR:.1f} mm dari bawah + lem", fontproperties=FR,
            fontsize=8, ha="center", va="top")
    a2.text(60, T / 2 + 1, "sambungan", fontproperties=FR, fontsize=7, ha="center", rotation=90)
    a2.set_xlim(-5, 125); a2.set_ylim(-14, 30); a2.set_aspect("equal"); a2.axis("off")
    a2.set_title("Potongan sambungan (mm)", fontproperties=FB)
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)


def figure_templates(path):
    """Satu halaman A4 per dudukan: kontur dudukan + jejak figur 1:1 (garis putus)."""
    from scipy.spatial import ConvexHull
    from matplotlib.patches import Polygon as P
    mesh_dir = os.path.join(ROOT, "build", "meshes")
    pw, ph = 210.0, 297.0
    with PdfPages(path) as pdf:
        for isl in MAN["islands"]:
            fig = plt.figure(figsize=(pw / 25.4, ph / 25.4))
            ax = fig.add_axes([0, 0, 1, 1])
            ax.set_xlim(-pw / 2, pw / 2); ax.set_ylim(-ph / 2 - 30, ph / 2 - 30); ax.axis("off")
            ol = np.array(isl["outline"]) - np.array(isl["center"])
            ax.add_patch(P(ol, fill=False, lw=0.8))
            for o in MAN["objects"]:
                if o["island"] != isl["id"] or o["id"] == "F08":
                    continue
                z = np.load(os.path.join(mesh_dir, o["id"] + ".npz"), allow_pickle=True)
                v = z["v"]
                low = v[v[:, 2] < 1.0][:, :2]  # tapak yang menyentuh dudukan
                pts = low if len(low) > 10 else v[:, :2]
                hull = pts[ConvexHull(pts).vertices]
                a = math.radians(o["rot_z"])
                R = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
                dx = o["world"][0] - isl["center"][0]
                dy = o["world"][1] - isl["center"][1]
                hp = hull @ R.T + np.array([dx, dy])
                ax.add_patch(P(hp, fill=False, lw=0.6, ls="--", ec="#1E4D2B"))
                ax.plot(dx, dy, "+", color="#1E4D2B", ms=8)
                ax.text(dx, dy + 3, o["id"], fontproperties=FB, fontsize=8, ha="center", color="#1E4D2B")
                hx = dx + 10 * math.cos(a)
                hy = dy + 10 * math.sin(a)
                ax.annotate("", (hx, hy), (dx, dy), arrowprops=dict(arrowstyle="-|>", lw=0.5, color="#888"))
            for l in isl["labels"]:
                ax.text(l["at"][0], l["at"][1], l["text"], fontproperties=FR, fontsize=6, ha="center", va="center", color="#999")
            ax.text(0, ph / 2 - 40, f"{isl['id']}  {isl['name']}  -  jejak figur 1:1 (garis putus = tapak menyentuh dudukan)",
                    fontproperties=FB, fontsize=8, ha="center")
            ax.text(0, ph / 2 - 47, "Cetak 100%. Gunting kontur, letakkan di atas dudukan, tandai titik + dengan jarum. "
                    "Panah abu = arah 'depan' lokal figur (kepala sapi, moncong mesin).", fontproperties=FR, fontsize=6, ha="center")
            ax.text(0, -ph / 2 - 20, "DEPAN (sisi pengunjung)", fontproperties=FB, fontsize=8, ha="center")
            ax.add_patch(Rectangle((-pw / 2 + 12, -ph / 2 - 24), 50, 4, fill=False, lw=0.5))
            ax.text(-pw / 2 + 66, -ph / 2 - 22, "= 50 mm", fontproperties=FR, fontsize=6, va="center")
            pdf.savefig(fig)
            plt.close(fig)


if __name__ == "__main__":
    figure_templates(os.path.join(DOCS, "template_figur_per_dudukan_1-1_A4.pdf"))
    os.makedirs(DOCS, exist_ok=True)
    template_full(os.path.join(DOCS, "template_penempatan_1-1_penuh_600x360.pdf"))
    n = template_a4(os.path.join(DOCS, "template_penempatan_1-1_A4.pdf"))
    plan_drawing(os.path.join(DOCS, "denah_tata_letak_mm.png"))
    tallest = max(o["size"][2] + (o["world"][2]) for o in MAN["objects"])
    table_drawing(os.path.join(DOCS, "simulasi_meja_96x60.png"), tallest)
    tile_drawing(os.path.join(DOCS, "sambungan_ubin_alas.png"))
    print("dokumen dibuat; template A4 =", n, "lembar; objek tertinggi", round(tallest, 1))
