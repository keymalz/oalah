"""Render pratinjau cepat sebuah komponen (depan + tiga perempat).

Pemakaian:  python preview.py <modul:fungsi> <out_dir> [args...]
"""
import sys, os, time, importlib, json
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))


def render_mesh(v, f, cols, out_prefix, res=(900, 700), samples=24, views=("front", "three_quarter")):
    import bscene
    bscene.reset()
    bscene.studio(world_strength=1.0)
    ob = bscene.mesh_object("part", v, f, cols, smooth_angle=35)
    # lantai krem tipis agar bayangan terlihat
    import bpy
    bpy.ops.mesh.primitive_plane_add(size=2000, location=(0, 0, -0.01))
    fl = bpy.context.active_object
    fl.data.materials.append(bscene.material("cream"))
    mn, mx = v.min(0), v.max(0)
    outs = []
    for kind in views:
        loc, tgt, sc = bscene.frame_views((mn, mx), kind)
        bscene.camera(f"cam_{kind}", loc, tgt, ortho=sc * (1.05 if kind != "front" else 1.0))
        p = f"{out_prefix}_{kind}.png"
        bscene.render(p, res=res, samples=samples)
        outs.append(p)
    return outs


if __name__ == "__main__":
    spec, out = sys.argv[1], sys.argv[2]
    args = sys.argv[3:]
    mod, fn = spec.split(":")
    t = time.time()
    res = getattr(importlib.import_module(mod), fn)(*args)
    v, f, c = res[:3]
    print(f"built {spec} {args}: {len(v)} verts {len(f)} faces in {time.time()-t:.1f}s; bbox {v.min(0).round(2)} {v.max(0).round(2)}")
    os.makedirs(out, exist_ok=True)
    name = fn + ("_" + "_".join(args) if args else "")
    np.savez_compressed(os.path.join(out, name + ".npz"), v=v, f=f, c=np.array(c))
    render_mesh(np.asarray(v), np.asarray(f), c, os.path.join(out, name))
    print("rendered", time.time() - t)
