"""Uji iris (slicing) setiap STL dengan PrusaSlicer CLI untuk memastikan
benar-benar bisa dicetak, dan mengukur kebutuhan support secara objektif.

python slice_check.py   (butuh `prusa-slicer` di PATH)
Hasil: reports/slicing.csv, reports/slicing.json
"""
import os, sys, re, json, glob, subprocess, tempfile
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

COMMON = ["--nozzle-diameter", "0.4", "--filament-diameter", "1.75", "--bed-shape", "0x0,220x0,220x220,0x220",
          "--temperature", "210", "--bed-temperature", "60", "--gcode-flavor", "marlin2",
          "--use-relative-e-distances", "--layer-gcode", "G92 E0", "--center", "110,110",
          "--first-layer-height", "0.2", "--thin-walls", "--filament-type", "PLA"]
PROFILES = {
    "figur": ["--layer-height", "0.12", "--perimeters", "3", "--fill-density", "15%"],
    "dudukan": ["--layer-height", "0.2", "--perimeters", "3", "--fill-density", "12%", "--top-solid-layers", "5"],
    "alas": ["--layer-height", "0.24", "--perimeters", "2", "--fill-density", "10%"],
}


def parse(gcode):
    E = {}
    cur = None
    t = None
    fil = None
    with open(gcode) as fh:
        for ln in fh:
            if ln.startswith(";TYPE:"):
                cur = ln[6:].strip()
            elif ln.startswith("G1") and " E" in ln and cur:
                m = re.search(r"E(-?[\d.]+)", ln)
                if m:
                    e = float(m.group(1))
                    if e > 0:
                        E[cur] = E.get(cur, 0.0) + e
            elif ln.startswith("; estimated printing time (normal mode)"):
                t = ln.split("=")[1].strip()
            elif ln.startswith("; filament used [cm3]"):
                fil = round(float(ln.split("=")[1]) * 1.24, 1)  # PLA 1,24 g/cm3
    return E, t, fil


def tsec(t):
    s = 0
    for v, u in re.findall(r"(\d+)([dhms])", t or ""):
        s += int(v) * {"d": 86400, "h": 3600, "m": 60, "s": 1}[u]
    return s


def slice_one(path):
    rel = os.path.relpath(path, ROOT)
    prof = "figur" if ("/figur/" in rel or "sapi_varian" in rel) else ("alas" if "alas_cetak3d" in rel else "dudukan")
    out = {}
    with tempfile.TemporaryDirectory() as td:
        for mode in ("support", "nosupport"):
            g = os.path.join(td, mode + ".gcode")
            args = ["prusa-slicer", "--export-gcode"] + COMMON + PROFILES[prof] + \
                (["--support-material", "--support-material-auto", "--support-material-threshold", "0",
                  "--support-material-buildplate-only"] if mode == "support" else []) + ["--output", g, path]
            p = subprocess.run(args, capture_output=True, text=True, timeout=1200)
            if p.returncode != 0 or not os.path.exists(g):
                out[mode] = dict(ok=False, err=(p.stdout + p.stderr)[-400:])
                continue
            E, t, fil = parse(g)
            tot = sum(E.values())
            sup = E.get("Support material", 0) + E.get("Support material interface", 0)
            warn = [l for l in (p.stdout + p.stderr).splitlines() if "warn" in l.lower() or "empty" in l.lower()]
            out[mode] = dict(ok=True, time=t, time_s=tsec(t), filament_g=fil, support_pct=round(100 * sup / tot, 2) if tot else 0,
                             overhang_perim_mm=round(E.get("Overhang perimeter", 0), 1), warnings=warn[:3])
    s = out.get("support", {})
    need = s.get("ok") and s.get("support_pct", 0) > 1.5
    return dict(file=rel, profile=prof, needs_support=bool(need), **{f"{k}_{m}": v for m, d in out.items() for k, v in d.items()})


if __name__ == "__main__":
    files = sorted(glob.glob(os.path.join(ROOT, "stl", "*", "*.stl")))
    files = [f for f in files if "varian_stiker" not in f]
    with ThreadPoolExecutor(4) as ex:
        rows = list(ex.map(slice_one, files))
    for r in rows:
        print(f"{r['file']:70s} ok={r.get('ok_support')} support={r.get('support_pct_support')}% "
              f"t={r.get('time_nosupport')} g={r.get('filament_g_nosupport')} perlu_support={r['needs_support']}")
    json.dump(rows, open(os.path.join(ROOT, "reports", "slicing.json"), "w"), indent=1)
    keys = ["file", "profile", "ok_support", "needs_support", "support_pct_support", "time_support", "filament_g_support",
            "time_nosupport", "filament_g_nosupport", "overhang_perim_mm_nosupport"]
    with open(os.path.join(ROOT, "reports", "slicing.csv"), "w") as fh:
        fh.write(",".join(keys) + "\n")
        for r in rows:
            fh.write(",".join(str(r.get(k, "")) for k in keys) + "\n")
