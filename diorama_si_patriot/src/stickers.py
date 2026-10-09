"""Gambar stiker: placeholder layar HP, label karung pupuk, dan lembar stiker
label dudukan (untuk varian stiker) dalam skala 1:1 (PDF + PNG 600 dpi)."""
import os, sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
FONT_B = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
FONT_R = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
GREEN = (30, 77, 43)
CREAM = (246, 243, 232)


def _font(path, px):
    return ImageFont.truetype(path, int(px))


def phone_placeholder(path, w_mm=23.1, h_mm=43.1, dpi=600):
    """Placeholder netral. WAJIB diganti tangkapan layar App/Website SI PATRIOT asli."""
    W, H = int(w_mm / 25.4 * dpi), int(h_mm / 25.4 * dpi)
    im = Image.new("RGB", (W, H), (236, 244, 238))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, int(H * 0.13)], fill=GREEN)
    d.text((W / 2, H * 0.065), "SI PATRIOT", fill="white", font=_font(FONT_B, H * 0.05), anchor="mm")
    y = H * 0.17
    for k in range(4):
        d.rounded_rectangle([W * 0.07, y, W * 0.93, y + H * 0.11], radius=int(W * 0.04), fill=(255, 255, 255),
                            outline=(200, 214, 204), width=3)
        d.rectangle([W * 0.12, y + H * 0.025, W * 0.12 + W * 0.18, y + H * 0.085], fill=(95, 160, 58))
        d.rectangle([W * 0.36, y + H * 0.03, W * 0.86, y + H * 0.045], fill=(170, 180, 175))
        d.rectangle([W * 0.36, y + H * 0.065, W * 0.70, y + H * 0.078], fill=(205, 212, 208))
        y += H * 0.135
    d.text((W / 2, H * 0.80), "CONTOH TATA LETAK", fill=(150, 60, 40), font=_font(FONT_B, H * 0.032), anchor="mm")
    d.text((W / 2, H * 0.85), "ganti dengan tangkapan", fill=(90, 90, 90), font=_font(FONT_R, H * 0.026), anchor="mm")
    d.text((W / 2, H * 0.885), "layar App/Website asli", fill=(90, 90, 90), font=_font(FONT_R, H * 0.026), anchor="mm")
    d.rectangle([W * 0.35, H * 0.955, W * 0.65, H * 0.962], fill=(120, 120, 120))
    im.save(path, dpi=(dpi, dpi))
    return path


def bag_label(path, w_mm=17.6, h_mm=13.6, dpi=600):
    W, H = int(w_mm / 25.4 * dpi), int(h_mm / 25.4 * dpi)
    im = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(im)
    d.text((W / 2, H * 0.22), "PUPUK", fill=GREEN, font=_font(FONT_B, H * 0.2), anchor="mm")
    d.text((W / 2, H * 0.44), "ORGANIK", fill=GREEN, font=_font(FONT_B, H * 0.2), anchor="mm")
    cx, cy = W / 2, H * 0.76
    d.line([cx, cy + H * 0.16, cx, cy - H * 0.05], fill=(60, 120, 50), width=int(H * 0.035))
    d.ellipse([cx - W * 0.2, cy - H * 0.13, cx - W * 0.01, cy + H * 0.01], fill=(95, 160, 58))
    d.ellipse([cx + W * 0.01, cy - H * 0.17, cx + W * 0.2, cy - H * 0.03], fill=(95, 160, 58))
    im.save(path, dpi=(dpi, dpi))
    return path


def label_sheet(manifest, out_pdf):
    """Lembar stiker label dudukan 1:1 (A4) untuk varian 'stiker'."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    from matplotlib.backends.backend_pdf import PdfPages
    from matplotlib.font_manager import FontProperties
    fp = FontProperties(fname=FONT_B)
    st = manifest["stickers"]
    A4 = (210.0, 297.0)
    with PdfPages(out_pdf) as pdf:
        fig = plt.figure(figsize=(A4[0] / 25.4, A4[1] / 25.4))
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, A4[0]); ax.set_ylim(0, A4[1]); ax.axis("off")
        ax.text(10, 287, "STIKER LABEL DUDUKAN - CETAK SKALA 100% (tanpa 'fit to page')", fontproperties=fp, fontsize=9)
        ax.text(10, 282, "Ukur kotak kalibrasi = 50 mm. Potong di garis tepi. Untuk varian dudukan_varian_stiker.",
                fontsize=7)
        ax.add_patch(plt.Rectangle((150, 278), 50, 5, fill=False, lw=0.6))
        ax.text(175, 280.5, "50 mm", fontsize=6, ha="center", va="center")
        x, y, rowh = 10.0, 270.0, 0.0
        for s in st:
            w, h = s["w"], s["h"]
            if x + w > A4[0] - 10:
                x = 10.0; y -= rowh + 6; rowh = 0
            ax.add_patch(FancyBboxPatch((x, y - h), w, h, boxstyle="round,pad=0,rounding_size=1.3",
                                        fc="#F6F3E8", ec="#888", lw=0.4))
            lines = s["text"].split("\n")
            cap = s["cap"]
            pt = cap / 0.727 / 25.4 * 72  # tinggi kapital -> ukuran font (pt)
            n = len(lines)
            for i, ln in enumerate(lines):
                yy = y - h / 2 + (n - 1) * cap * 0.725 - i * cap * 1.45
                ax.text(x + w / 2, yy, ln, fontproperties=fp, fontsize=pt, ha="center", va="center", color="#1E4D2B")
            ax.text(x, y + 1.2, s["island"], fontsize=5, color="#666")
            x += w + 6
            rowh = max(rowh, h)
        # stiker tambahan
        y -= rowh + 14
        ax.text(10, y + 5, "STIKER FIGUR", fontproperties=fp, fontsize=8)
        im1 = Image.open(os.path.join(ROOT, "docs", "stiker_layar_hp_placeholder.png"))
        ax.imshow(np.asarray(im1), extent=(10, 10 + 23.1, y - 43.1, y))
        ax.add_patch(plt.Rectangle((10, y - 43.1), 23.1, 43.1, fill=False, lw=0.4))
        ax.text(42, y - 4, "Layar HP 23,1 x 43,1 mm (F18), sudut r = 2,4 mm.\nGANTI dengan tangkapan layar\nApp/Website SI PATRIOT asli\n(rasio +-1:2, potong sedikit bila perlu).",
                fontsize=7, va="top")
        im2 = Image.open(os.path.join(ROOT, "docs", "stiker_karung_pupuk.png"))
        ax.imshow(np.asarray(im2), extent=(110, 110 + 17.6, y - 13.6, y))
        ax.add_patch(plt.Rectangle((110, y - 13.6), 17.6, 13.6, fill=False, lw=0.4))
        ax.text(131, y - 2, "Karung pupuk organik\n17,6 x 13,6 mm (F17)", fontsize=7, va="top")
        pdf.savefig(fig)
        plt.close(fig)


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "docs"), exist_ok=True)
    phone_placeholder(os.path.join(ROOT, "docs", "stiker_layar_hp_placeholder.png"))
    bag_label(os.path.join(ROOT, "docs", "stiker_karung_pupuk.png"))
    man = json.load(open(os.path.join(ROOT, "reports", "manifest.json")))
    label_sheet(man, os.path.join(ROOT, "docs", "stiker_label_A4_skala_1-1.pdf"))
    print("ok")
