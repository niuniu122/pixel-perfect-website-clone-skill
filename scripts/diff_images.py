import argparse
import json
import os
import sys

try:
    from PIL import Image, ImageChops
except ImportError:
    print("Pillow is required: python -m pip install pillow", file=sys.stderr)
    raise


def parse_viewports(value):
    out = []
    for part in value.split(","):
        part = part.strip().lower()
        if not part:
            continue
        w, h = part.split("x", 1)
        out.append((int(w), int(h)))
    return out


def compare_pair(ref_path, rep_path, diff_path, threshold):
    ref = Image.open(ref_path).convert("RGBA")
    rep = Image.open(rep_path).convert("RGBA")
    cw = min(ref.width, rep.width)
    ch = min(ref.height, rep.height)
    refc = ref.crop((0, 0, cw, ch))
    repc = rep.crop((0, 0, cw, ch))
    diff = ImageChops.difference(refc, repc).convert("RGB")

    pix = diff.load()
    total = cw * ch
    changed = 0
    total_delta = 0.0
    max_delta = 0
    mask = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    mask_pix = mask.load()

    for y in range(ch):
        for x in range(cw):
            r, g, b = pix[x, y]
            value = max(r, g, b)
            total_delta += (r + g + b) / 3
            max_delta = max(max_delta, value)
            if value > threshold:
                changed += 1
                mask_pix[x, y] = (255, 0, 255, 180)

    overlay = refc.copy()
    overlay.alpha_composite(mask)
    os.makedirs(os.path.dirname(diff_path), exist_ok=True)
    overlay.convert("RGB").save(diff_path)

    return {
        "refSize": [ref.width, ref.height],
        "repSize": [rep.width, rep.height],
        "comparedSize": [cw, ch],
        "sizeMismatch": ref.size != rep.size,
        "changedPixels": changed,
        "totalPixels": total,
        "changedRatio": round(changed / total, 8) if total else 0,
        "avgChannelDelta": round(total_delta / total, 5) if total else 0,
        "maxChannelDelta": max_delta,
        "bbox": diff.getbbox(),
        "diff": diff_path,
    }


def main():
    parser = argparse.ArgumentParser(description="Compare breakpoint screenshots for a website clone.")
    parser.add_argument("--root", required=True, help="Clone root containing screenshot folders.")
    parser.add_argument("--ref", required=True, help="Reference screenshot folder name, relative to root.")
    parser.add_argument("--rep", required=True, help="Replica screenshot folder name, relative to root.")
    parser.add_argument("--out", default="diff", help="Output diff folder name, relative to root.")
    parser.add_argument("--prefix", default="site", help="Screenshot filename prefix.")
    parser.add_argument("--viewports", default="1920x1000,1440x1000,1024x1000,768x1000,375x812")
    parser.add_argument("--kinds", default="top,full")
    parser.add_argument("--threshold", type=int, default=16)
    parser.add_argument("--report", default="report.json")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if any pixel/size difference remains.")
    args = parser.parse_args()

    viewports = parse_viewports(args.viewports)
    kinds = [k.strip() for k in args.kinds.split(",") if k.strip()]
    records = []
    failed = False

    for w, h in viewports:
        for kind in kinds:
            filename = f"{args.prefix}-{w}x{h}-{kind}.png"
            ref_path = os.path.join(args.root, args.ref, filename)
            rep_path = os.path.join(args.root, args.rep, filename)
            diff_path = os.path.join(args.root, args.out, f"{args.prefix}-{w}x{h}-{kind}-diff.png")

            if not os.path.exists(ref_path) or not os.path.exists(rep_path):
                record = {
                    "viewport": [w, h],
                    "kind": kind,
                    "missing": True,
                    "ref": ref_path,
                    "rep": rep_path,
                }
                records.append(record)
                failed = True
                continue

            record = compare_pair(ref_path, rep_path, diff_path, args.threshold)
            record.update({"viewport": [w, h], "kind": kind, "ref": ref_path, "rep": rep_path})
            records.append(record)
            if record["sizeMismatch"] or record["changedPixels"] or record["maxChannelDelta"]:
                failed = True

    report_path = os.path.join(args.root, args.out, args.report)
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    print(json.dumps(records, ensure_ascii=False, indent=2))
    if args.strict and failed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
