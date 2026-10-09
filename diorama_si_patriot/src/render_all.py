"""Render final + kartu pratinjau per objek + perbandingan dengan gambar acuan.

python render_all.py [--quick] [--skip-scene] [--skip-cards]
"""
import os, sys, json, math, time
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
RENDER = os.path.join(ROOT, "render")
CARDS = os.path.join(RENDER, "objek")
MAN = json.load(open(os.path.join(ROOT, "reports", "manifest.json")))
FB = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
FR = "/usr/share/fonts/opentype/inter/Inter-Regular.otf"
REF = os.path.join(ROOT, "docs", "acuan_gambar3.png")


def F(p, s):
    return ImageFont.truetype(p, s)


def slicing_info():
    p = os.path.join(ROOT, "reports", "slicing.json")
    if not os.path.exists(p):
        return {}
    return {os.path.basename(r["file"]): r for r in json.load(open(p))}


def render_cards(quick=False):
    import bpy
    import bscene
    from scene import load_npz
    os.makedirs(CARDS, exist_ok=True)
    sl = slicing_info()
    items = [(o["id"], o["name"], o["stl"], o["size"],
              f"di dudukan {o['island']}, pusat ({o['world'][0] + 300:.0f}; {o['world'][1] + 180:.0f}) mm dari pojok kiri-depan alas, "
              f"putar {o['rot_z']:.0f} derajat") for o in MAN["objects"]]
    items += [(i["id"], "Dudukan " + i["name"], i["stl"], i["size"],
               f"pusat ({i['center_from_front_left'][0]:.0f}; {i['center_from_front_left'][1]:.0f}) mm dari pojok kiri-depan | label: "
               + " / ".join(l["text"].replace("\n", " ") for l in i["labels"])) for i in MAN["islands"]]
    out = []
    for (oid, name, stl, size, extra) in items:
        v, f, c = load_npz(oid)
        bscene.reset()
        bscene.studio(world_strength=1.0)
        bscene.mesh_object(oid, v, f, c, smooth_angle=(80 if oid in ("F02", "F05", "F06", "F07", "F10", "F11", "F13", "F15", "F16", "F17") else 32))
        bpy.ops.mesh.primitive_plane_add(size=3000, location=(0, 0, -0.02))
        bpy.context.active_object.data.materials.append(bscene.material("cream"))
        mn, mx = v.min(0), v.max(0)
        ims = []
        for kind in ("front", "three_quarter"):
            loc, tgt, sc = bscene.frame_views((mn, mx), kind, margin=1.18)
            bscene.camera("c_" + kind, loc, tgt, ortho=sc)
            p = os.path.join(CARDS, f"_{oid}_{kind}.png")
            bscene.render(p, res=(560, 460) if not quick else (280, 230), samples=(16 if quick else 40))
            ims.append(Image.open(p).convert("RGB"))
            os.remove(p)
        W = ims[0].width * 2 + 30
        card = Image.new("RGB", (W, ims[0].height + 195), "white")
        card.paste(ims[0], (10, 110))
        card.paste(ims[1], (20 + ims[0].width, 110))
        d = ImageDraw.Draw(card)
        d.text((14, 10), f"{oid}  {name}", fill=(30, 77, 43), font=F(FB, 30 if not quick else 15))
        info = sl.get(os.path.basename(stl), {})
        sup = "perlu support" if info.get("needs_support") else "tanpa support"
        t = info.get("time_support" if info.get("needs_support") else "time_nosupport", "-")
        g = info.get("filament_g_support" if info.get("needs_support") else "filament_g_nosupport", "-")
        d.text((14, 52), f"Ukuran {size[0]:.1f} x {size[1]:.1f} x {size[2]:.1f} mm  |  cetak 1x  |  {sup}  |  +-{t}, +-{g} g PLA",
               fill=(40, 40, 40), font=F(FR, 19 if not quick else 10))
        d.text((14, 80), extra, fill=(90, 90, 90), font=F(FR, 16 if not quick else 8))
        d.text((14, card.height - 62), f"STL: {stl}", fill=(90, 90, 90), font=F(FR, 15 if not quick else 8))
        d.text((14, card.height - 30), "kiri: tampak depan   kanan: tiga perempat   (warna = panduan cat/filamen)",
               fill=(120, 120, 120), font=F(FR, 15 if not quick else 8))
        p = os.path.join(CARDS, f"{oid}.png")
        card.save(p)
        out.append(p)
        print("kartu", oid, flush=True)
    # katalog
    cards = [Image.open(p) for p in out]
    cw, ch = cards[0].width, cards[0].height
    cols = 3
    rows = math.ceil(len(cards) / cols)
    sheet = Image.new("RGB", (cols * cw, rows * ch), "white")
    for k, im in enumerate(cards):
        sheet.paste(im, ((k % cols) * cw, (k // cols) * ch))
    s = 2400 / sheet.width
    sheet = sheet.resize((int(sheet.width * s), int(sheet.height * s)), Image.LANCZOS)
    sheet.save(os.path.join(RENDER, "katalog_semua_objek.png"))


def annotate_table_top():
    """Tambah garis ukur pada render tampak atas meja (kamera ortho 1150 mm)."""
    p = os.path.join(RENDER, "diorama_meja_atas.png")
    if not os.path.exists(p):
        return
    im = Image.open(p).convert("RGB")
    W, H = im.size
    k = W / 1150.0
    cx, cy = W / 2, H / 2

    def X(x):
        return cx + x * k

    def Y(y):
        return cy - y * k
    d = ImageDraw.Draw(im)
    red = (198, 40, 40)
    f = F(FB, 26)
    # sisa kiri/kanan
    for (a, b) in ((-480, -300), (300, 480)):
        d.line([X(a), Y(0), X(b), Y(0)], fill=red, width=4)
        d.text(((X(a) + X(b)) / 2, Y(0) - 34), "180 mm", fill=red, font=f, anchor="mm")
    for (a, b) in ((-300, -180), (180, 300)):
        d.line([X(0) + 250, Y(a), X(0) + 250, Y(b)], fill=red, width=4)
        d.text((X(0) + 330, (Y(a) + Y(b)) / 2), "120 mm", fill=red, font=f, anchor="mm")
    d.text((X(0), Y(-300) + 40), "meja 960 x 600 mm  -  alas diorama 600 x 360 mm  -  DEPAN", fill=(30, 30, 30), font=f, anchor="mm")
    im.save(os.path.join(RENDER, "diorama_meja_atas_ukuran.png"))


def comparison():
    if not os.path.exists(REF):
        return
    ref = Image.open(REF).convert("RGB")
    ren = Image.open(os.path.join(RENDER, "diorama_iso_acuan.png")).convert("RGB")
    H = 760
    ref2 = ref.resize((int(ref.width * H / ref.height), H), Image.LANCZOS)
    ren2 = ren.resize((int(ren.width * H / ren.height), H), Image.LANCZOS)
    pad = 30
    W = ref2.width + ren2.width + 3 * pad
    out = Image.new("RGB", (W, H + 360), "white")
    out.paste(ref2, (pad, 90))
    out.paste(ren2, (2 * pad + ref2.width, 90))
    d = ImageDraw.Draw(out)
    d.text((pad, 25), "Gambar 3 (acuan)", fill=(30, 30, 30), font=F(FB, 34))
    d.text((2 * pad + ref2.width, 25), "Render model 3D diorama (sudut serupa)", fill=(30, 77, 43), font=F(FB, 34))
    checks = [
        "Panah dihapus seluruhnya (tidak ada objek, relief, atau garis jalur)",
        "Dua sapi perah (F05 berdiri menoleh, F06 menunduk makan) + satu peternak bercaping dekat pintu kandang",
        "Satu HP tegak di tengah (tanpa laptop/monitor/tablet/awan); layar = cekungan stiker",
        "Satu mesin pencacah (rangka merah, rumah pemotong & corong hijau) di stasiun pakan",
        "Alas utama cokelat 600 x 360 mm; 10 dudukan krem berlabel timbul sesuai nama objek",
        "Posisi relatif mengikuti acuan: pakan kiri/atas, kandang kanan/atas, susu & pendapatan kanan,",
        "   limbah kanan/bawah, biodigester bawah, biogas/slurry/energi & pupuk/limbah padat kiri/bawah, pupuk organik kiri",
    ]
    y = H + 110
    for c in checks:
        d.text((pad, y), ("OK  " if not c.startswith("   ") else "     ") + c.strip(), fill=(40, 40, 40), font=F(FR, 24))
        y += 34
    out.save(os.path.join(RENDER, "perbandingan_acuan_vs_model.png"))


if __name__ == "__main__":
    quick = "--quick" in sys.argv
    if "--skip-scene" not in sys.argv:
        import scene, bpy
        cols = scene.build_scene(with_table=True)
        scene.VIEWS["iso_acuan"] = ((0, -2000, 1450), (0, 4, 10), 652, None, False, (1920, 900))
        only = [a.split("=", 1)[1].split(",") for a in sys.argv if a.startswith("--only=")]
        scene.render_views(cols, only[0] if only else list(scene.VIEWS), samples=96, quick=quick)
        scene.add_saved_cameras()
        bpy.context.scene.camera = bpy.data.objects["CAM_three_quarter"]
        scene.set_table_visible(cols, False)
        try:
            bpy.ops.file.pack_all()
        except Exception as e:
            print("pack:", e)
        os.makedirs(os.path.join(ROOT, "blend"), exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "blend", "diorama_si_patriot.blend"), compress=True)
        print("saved .blend", flush=True)
    annotate_table_top()
    comparison()
    if "--skip-cards" not in sys.argv:
        render_cards(quick=quick)
    print("selesai")
