"""Utilitas Blender (bpy): material dari palet, objek mesh berwarna per-segitiga,
pencahayaan studio, kamera, dan render Cycles (CPU)."""
import math
import numpy as np
import bpy
import addon_utils
from mathutils import Vector

from palette import PALETTE, hex_to_rgb, srgb_to_linear

_MATS = {}


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    try:
        addon_utils.enable("cycles", default_set=True)
    except Exception:
        pass
    _MATS.clear()


def material(key):
    if key in _MATS:
        return _MATS[key]
    hx, rough, _ = PALETTE[key]
    mat = bpy.data.materials.new(name=f"M_{key}")
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    rgb = [srgb_to_linear(c) for c in hex_to_rgb(hx)]
    bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    if key in ("metal", "pipe", "gold", "dark_metal"):
        bsdf.inputs["Metallic"].default_value = 0.6
    if key in ("screen",):
        img_node = None
    if key == "cow_white":
        _holstein(nt, bsdf, rgb)
    if key in ("base_brown", "tile_brown"):
        _soil_texture(nt, bsdf, rgb)
    if key == "grass":
        _grass_texture(nt, bsdf, rgb)
    _MATS[key] = mat
    return mat


def _holstein(nt, bsdf, rgb):
    """Corak sapi perah hitam-putih prosedural (hanya untuk render/panduan cat)."""
    tc = nt.nodes.new("ShaderNodeTexCoord")
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 0.075
    noise.inputs["Detail"].default_value = 1.2
    noise.inputs["Roughness"].default_value = 0.45
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (*rgb, 1)
    ramp.color_ramp.elements[1].position = 0.54
    k = [srgb_to_linear(c) for c in hex_to_rgb(PALETTE["cow_black"][0])]
    ramp.color_ramp.elements[1].color = (*k, 1)
    nt.links.new(tc.outputs["Object"], noise.inputs["Vector"])
    nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])


def _soil_texture(nt, bsdf, rgb):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 0.08
    noise.inputs["Detail"].default_value = 6.0
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*[c * 0.82 for c in rgb], 1)
    ramp.color_ramp.elements[1].color = (*[min(1, c * 1.15) for c in rgb], 1)
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[1].position = 0.65
    nt.links.new(tc.outputs["Object"], noise.inputs["Vector"])
    nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])


def _grass_texture(nt, bsdf, rgb):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 3.0
    mr.inputs["From Max"].default_value = 30.0
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    dk = [srgb_to_linear(c) for c in hex_to_rgb(PALETTE["grass_dark"][0])]
    ramp.color_ramp.elements[0].color = (*dk, 1)
    ramp.color_ramp.elements[1].color = (*[min(1, c * 1.25) for c in rgb], 1)
    nt.links.new(tc.outputs["Object"], sep.inputs["Vector"])
    nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])


def image_material(name, path, rough=0.25):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(path)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(tc.outputs["UV"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = rough
    return mat


def mesh_object(name, v, f, cols, collection=None, smooth_angle=None, location=(0, 0, 0), rot_z=0.0):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(x) for x in np.asarray(v, float)], [], [tuple(int(i) for i in t) for t in f])
    keys = []
    idx = {}
    for c in cols:
        if c not in idx:
            idx[c] = len(keys); keys.append(c)
    for k in keys:
        me.materials.append(material(k))
    mi = np.array([idx[c] for c in cols], dtype=np.int32)
    me.polygons.foreach_set("material_index", mi)
    me.update()
    ob = bpy.data.objects.new(name, me)
    (collection or bpy.context.scene.collection).objects.link(ob)
    ob.location = location
    ob.rotation_euler = (0, 0, math.radians(rot_z))
    if smooth_angle:
        try:
            me.shade_smooth_by_angle(angle=math.radians(smooth_angle)) if hasattr(me, "shade_smooth_by_angle") else None
        except Exception:
            pass
        _smooth_by_angle(ob, smooth_angle)
    return ob


def _smooth_by_angle(ob, deg):
    me = ob.data
    try:
        me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
        mod = ob.modifiers.new("Smooth", "EDGE_SPLIT")
        mod.split_angle = math.radians(deg)
        mod.use_edge_sharp = False
    except Exception:
        pass


def collection(name, parent=None):
    col = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(col)
    return col


def studio(world_strength=0.9, sun=True, bg=(1, 1, 1)):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.use_denoising = True
    try:
        sc.cycles.denoiser = "OPENIMAGEDENOISE"
    except Exception:
        pass
    # "Standard" menjaga warna palet (hijau-putih-cokelat) setia seperti gambar acuan
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.view_settings.exposure = 0.0
    w = bpy.data.worlds.new("W")
    sc.world = w
    w.use_nodes = True
    bgn = w.node_tree.nodes.get("Background")
    bgn.inputs["Color"].default_value = (*bg, 1)
    bgn.inputs["Strength"].default_value = world_strength
    if sun:
        L = bpy.data.lights.new("Key", "SUN")
        L.energy = 2.6
        L.angle = math.radians(12)
        o = bpy.data.objects.new("Key", L)
        sc.collection.objects.link(o)
        o.rotation_euler = (math.radians(42), math.radians(-18), math.radians(-35))
        F = bpy.data.lights.new("Fill", "SUN")
        F.energy = 0.6
        F.angle = math.radians(30)
        of = bpy.data.objects.new("Fill", F)
        sc.collection.objects.link(of)
        of.rotation_euler = (math.radians(60), math.radians(25), math.radians(140))


def camera(name="Cam", loc=(0, -1, 1), target=(0, 0, 0), ortho=None, lens=50):
    sc = bpy.context.scene
    cam = bpy.data.cameras.new(name)
    if ortho:
        cam.type = "ORTHO"
        cam.ortho_scale = ortho
    else:
        cam.lens = lens
    cam.clip_start = 1
    cam.clip_end = 100000
    ob = bpy.data.objects.new(name, cam)
    sc.collection.objects.link(ob)
    ob.location = loc
    d = Vector(target) - Vector(loc)
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    sc.camera = ob
    return ob


def render(path, res=(1200, 900), samples=48, transparent=False):
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.cycles.samples = samples
    sc.render.film_transparent = transparent
    sc.render.image_settings.file_format = "PNG"
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


def frame_views(bounds, kind="three_quarter", margin=1.25):
    """Posisi kamera ortografik untuk bounding box (min, max)."""
    mn, mx = np.asarray(bounds[0]), np.asarray(bounds[1])
    c = (mn + mx) / 2
    size = mx - mn
    if kind == "front":
        dirv = np.array([0, -1, 0.12])
    elif kind == "top":
        dirv = np.array([0, -0.0001, 1])
    elif kind == "iso_ref":
        dirv = np.array([0, -1, 0.72])
    else:
        dirv = np.array([0.75, -1, 0.68])
    dirv = dirv / np.linalg.norm(dirv)
    dist = float(np.linalg.norm(size)) * 4 + 200
    loc = c + dirv * dist
    scale = float(max(size)) * margin
    return tuple(loc), tuple(c), scale
