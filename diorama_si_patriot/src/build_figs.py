"""Bangun semua figur (F01..F18) dan simpan cache mesh .npz.

python build_figs.py <cache_dir> [F01 F05 ...]
"""
import sys, os, time, importlib
import numpy as np
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from layout import FIGURES


def build_one(fid, cache):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    name, spec = FIGURES[fid]
    parts = spec.split(":")
    mod, fn, args = parts[0], parts[1], parts[2:]
    t = time.time()
    v, f, c = getattr(importlib.import_module(mod), fn)(*args)
    np.savez_compressed(os.path.join(cache, fid + ".npz"), v=np.asarray(v), f=np.asarray(f), c=np.array(c))
    return fid, len(f), time.time() - t


def load(fid, cache):
    z = np.load(os.path.join(cache, fid + ".npz"), allow_pickle=True)
    return z["v"], z["f"], list(z["c"])


if __name__ == "__main__":
    cache = sys.argv[1]
    os.makedirs(cache, exist_ok=True)
    ids = sys.argv[2:] or list(FIGURES)
    with ProcessPoolExecutor(4) as ex:
        for fid, n, dt in ex.map(build_one, ids, [cache] * len(ids)):
            print(f"{fid}: {n} faces, {dt:.1f}s", flush=True)
