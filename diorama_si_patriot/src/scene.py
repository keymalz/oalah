"""Rakit adegan lengkap di Blender (bpy), simpan .blend, dan render semua tampilan.

python scene.py [--quick] [--only top,front,...]
Butuh build_all.py sudah dijalankan (build/meshes/*.npz, reports/manifest.json).
"""
import sys, os, json, math, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import bpy
from mathutils import Vector, Euler
import bscene
import layout as L
from fig_misc import PHONE

MESH = os.path.join(ROOT, "build", "meshes")
RENDER = os.path.join(ROOT, "render")
MAN = json.load(open(os.path.join(ROOT, "reports", "manifest.json")))

TABLE_W, TABLE_D, TABLE_H, TABLE_T = 960.0, 600.0, 750.0, 25.0
VIEW_DIST = 1000.0      # jarak pengunjung dari tepi depan meja
EYE_H = 1550.0          # tinggi mata pengunjung dari lantai


def load_npz(name):
    z = np.load(os.path.join(MESH, name + ".npz"), allow_pickle=True)
    return z["v"], z["f"], list(z["c"])


def board_mesh():
    """Papan alas utama 600 x 360 x 12 mm, chamfer 2 mm di tepi atas. Atas di Z = 0."""
    import geo
    from manifold3d import Manifold
    b = geo.box((L.BASE_W, L.BASE_D, L.BASE_T), (0, 0, -L.BASE_T), color="base_brown", base=True)
    for sx in (-1, 1):
        b = b - geo.tag(Manifold.cube((4.0, L.BASE_D + 10, 4.0), center=True).rotate((0, 45, 0))
                        .translate((sx * L.BASE_W / 2, 0, 0)), "base_brown")
    for sy in (-1, 1):
        b = b - geo.tag(Manifold.cube((L.BASE_W + 10, 4.0, 4.0), center=True).rotate((45, 0, 0))
                        .translate((0, sy * L.BASE_D / 2, 0)), "base_brown")
    return geo.to_arrays(b)


def sticker_plane(name, img, size, loc, rot_euler, col):
    bpy.ops.mesh.primitive_plane_add(size=1.0)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = (size[0], size[1], 1.0)
    ob.location = loc
    ob.rotation_euler = rot_euler
    ob.data.materials.append(bscene.image_material("M_" + name, img))
    for c in ob.users_collection:
        c.objects.unlink(ob)
    col.objects.link(ob)
    return ob


def phone_screen_transform(X, Y, Z, rot_z):
    P = PHONE
    t, h, tilt = P["t"], P["h"], math.radians(P["tilt"])
    y0, z0 = -t / 2 + 0.6 - 0.06, h / 2 + 0.6
    y1 = y0 * math.cos(tilt) + z0 * math.sin(tilt) + 2.0
    z1 = -y0 * math.sin(tilt) + z0 * math.cos(tilt) + (3.0 - 1.4)
    a = math.radians(rot_z)
    loc = (X + 0 * math.cos(a) - y1 * math.sin(a), Y + 0 * math.sin(a) + y1 * math.cos(a), Z + z1)
    return loc, Euler((math.radians(90 - P["tilt"]), 0, a))


def build_scene(with_table=True):
    bscene.reset()
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    sc.unit_settings.scale_length = 0.001
    sc.unit_settings.length_unit = "MILLIMETERS"
    cols = {k: bscene.collection(k) for k in ("ALAS_UTAMA", "DUDUKAN", "FIGUR", "STIKER_RENDER", "MEJA_PAMERAN")}
    v, f, c = board_mesh()
    bscene.mesh_object("Alas_utama_600x360", v, f, c, collection=cols["ALAS_UTAMA"])
    for isl in MAN["islands"]:
        v, f, c = load_npz(isl["id"])
        ob = bscene.mesh_object(f"{isl['id']}_{isl['name']}", v, f, c, collection=cols["DUDUKAN"],
                                location=(isl["center"][0], isl["center"][1], 0.0))
        ob["label"] = " / ".join(l["text"].replace("\n", " ") for l in isl["labels"])
        ob["stl"] = isl["stl"]
    for o in MAN["objects"]:
        v, f, c = load_npz(o["id"])
        organic = o["id"] in ("F02", "F05", "F06", "F07", "F10", "F11", "F13", "F15", "F16", "F17")
        ob = bscene.mesh_object(f"{o['id']}_{o['name']}", v, f, c, collection=cols["FIGUR"],
                                location=tuple(o["world"]), rot_z=o["rot_z"], smooth_angle=(80 if organic else 32))
        ob["stl"] = o["stl"]
        ob["dudukan"] = o["island"]
    # stiker (render saja; di dunia nyata = stiker kertas/vinyl)
    f18 = next(o for o in MAN["objects"] if o["id"] == "F18")
    loc, rot = phone_screen_transform(*f18["world"], f18["rot_z"])
    sticker_plane("Stiker_layar_HP_placeholder", os.path.join(ROOT, "docs", "stiker_layar_hp_placeholder.png"),
                  (PHONE["scr_w"] - 0.4, PHONE["scr_h"] - 0.4), loc, rot, cols["STIKER_RENDER"])
    f17 = next(o for o in MAN["objects"] if o["id"] == "F17")
    X, Y, Z = f17["world"]
    sticker_plane("Stiker_karung_pupuk", os.path.join(ROOT, "docs", "stiker_karung_pupuk.png"),
                  (17.6, 13.6), (X, Y - 5.86, Z + 19.0), Euler((math.radians(90), 0, 0)), cols["STIKER_RENDER"])
    # meja pameran 96 x 60 x 75 cm (atas meja di Z = -12, lantai di Z = -762)
    if with_table:
        tz = -L.BASE_T
        import geo
        parts = [geo.box((TABLE_W, TABLE_D, TABLE_T), (0, 0, tz - TABLE_T), color="table", base=True)]
        for sx in (-1, 1):
            for sy in (-1, 1):
                parts.append(geo.box((40, 40, TABLE_H - TABLE_T), (sx * (TABLE_W / 2 - 45), sy * (TABLE_D / 2 - 45),
                                                                  tz - TABLE_H), color="table", base=True))
        v, f, c = geo.to_arrays(geo.union(parts))
        bscene.mesh_object("Meja_96x60x75", v, f, c, collection=cols["MEJA_PAMERAN"])
        # pengunjung (siluet sederhana 165 cm) 1 m di depan meja
        from sdf import Capsule, Sphere, Ellipsoid, SU, mesh_sdf
        floor = tz - TABLE_H
        py = -TABLE_D / 2 - VIEW_DIST
        person = SU(40,
                    Capsule((-90, 0, 0), (-90, 0, 850), 70, 75, color="concrete"),
                    Capsule((90, 0, 0), (90, 0, 850), 70, 75, color="concrete"),
                    Ellipsoid((0, 0, 1150), (210, 120, 330), color="concrete"),
                    Capsule((-230, 0, 1380), (-260, 20, 800), 55, 45, color="concrete"),
                    Capsule((230, 0, 1380), (260, 20, 800), 55, 45, color="concrete"),
                    Sphere((0, 0, 1550), 110, color="concrete"))
        pv, pf, pc = mesh_sdf(person, ((-340, -140, 0), (340, 140, 1665)), h=12.0, target_faces=20000)
        bscene.mesh_object("Pengunjung_165cm", pv, pf, pc, collection=cols["MEJA_PAMERAN"],
                           location=(-420, py - 60, floor), smooth_angle=80)
        bpy.ops.mesh.primitive_plane_add(size=6000, location=(0, -800, floor))
        fl = bpy.context.active_object
        fl.name = "Lantai"
        fl.data.materials.append(bscene.material("cream"))
        for cc in fl.users_collection:
            cc.objects.unlink(fl)
        cols["MEJA_PAMERAN"].objects.link(fl)
    bscene.studio(world_strength=0.85)
    return cols


def set_table_visible(cols, vis):
    for ob in cols["MEJA_PAMERAN"].objects:
        ob.hide_render = not vis
        ob.hide_viewport = not vis


def cam(name, loc, tgt, ortho=None, lens=50):
    return bscene.camera(name, loc, tgt, ortho=ortho, lens=lens)


VIEWS = {
    # nama: (lokasi, target, ortho_scale|None, lens, meja?, resolusi)
    "top": ((0, -0.01, 2500), (0, 0, 0), 640, None, False, (1920, 1152)),
    "front_pengunjung_1m": ((0, -TABLE_D / 2 - VIEW_DIST, EYE_H - TABLE_H - L.BASE_T), (0, 10, 20), None, 38, False, (1920, 1080)),
    "three_quarter": ((545, -700, 495), (2, 6, -12), None, 50, False, (1920, 1080)),
    "front_pengunjung_1m_zoom": ((0, -TABLE_D / 2 - VIEW_DIST, EYE_H - TABLE_H - L.BASE_T), (0, 10, 20), None, 85, False, (1920, 1080)),
    "front_elevasi": ((0, -3000, 30), (0, 0, 30), 640, None, False, (1920, 420)),
    "iso_acuan": ((0, -2000, 1450), (0, 8, 10), 610, None, False, (1920, 900)),
    "meja_tiga_perempat": ((2100, -2500, 1300), (-150, -650, -300), None, 32, True, (1920, 1080)),
    "meja_atas": ((0, -0.01, 4000), (0, 0, 0), 1150, None, True, (1920, 1250)),
    "meja_pandangan_pengunjung": ((0, -TABLE_D / 2 - VIEW_DIST, EYE_H - TABLE_H - L.BASE_T), (0, 0, -150), None, 24, True, (1920, 1080)),
}


def render_views(cols, names, samples=96, quick=False):
    sc = bpy.context.scene
    out = []
    for n in names:
        loc, tgt, ortho, lens, table, res = VIEWS[n]
        set_table_visible(cols, table)
        if "Pengunjung_165cm" in bpy.data.objects and n == "meja_pandangan_pengunjung":
            bpy.data.objects["Pengunjung_165cm"].hide_render = True  # kamera = mata pengunjung
        c = cam("CAM_" + n, loc, tgt, ortho=ortho, lens=lens or 50)
        if quick:
            res = (res[0] // 2, res[1] // 2)
        p = os.path.join(RENDER, f"diorama_{n}.png")
        t = time.time()
        bscene.render(p, res=res, samples=(24 if quick else samples))
        print("render", n, round(time.time() - t, 1), "s", flush=True)
        out.append(p)
    set_table_visible(cols, True)
    return out


def add_saved_cameras():
    for n, (loc, tgt, ortho, lens, table, res) in VIEWS.items():
        if "CAM_" + n not in bpy.data.objects:
            cam("CAM_" + n, loc, tgt, ortho=ortho, lens=lens or 50)


if __name__ == "__main__":
    os.makedirs(RENDER, exist_ok=True)
    quick = "--quick" in sys.argv
    only = None
    for a in sys.argv:
        if a.startswith("--only="):
            only = a.split("=", 1)[1].split(",")
    cols = build_scene(with_table=True)
    names = only or list(VIEWS)
    render_views(cols, names, quick=quick)
    if "--save" in sys.argv:
        add_saved_cameras()
        bpy.context.scene.camera = bpy.data.objects["CAM_three_quarter"]
        set_table_visible(cols, False)
        cols["MEJA_PAMERAN"].hide_viewport = False
        os.makedirs(os.path.join(ROOT, "blend"), exist_ok=True)
        try:
            bpy.ops.file.pack_all()
        except Exception as e:
            print("pack:", e)
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "blend", "diorama_si_patriot.blend"), compress=True)
        print("saved .blend")
