"""Generate dependency-free SVG plots from benchmark_summary.json."""
import json
from pathlib import Path


def svg_plot(path: Path, title: str, ylabel: str, series: dict[str, list[tuple[int, float]]], logy: bool = False) -> None:
    width, height, left, bottom = 900, 520, 90, 70
    points = [p for values in series.values() for p in values]
    if not points:
        return
    xs = [p[0] for p in points]; ys = [p[1] for p in points]
    ymin, ymax = (min(ys), max(ys))
    if logy:
        import math
        ys2 = [math.log10(max(y, 1e-9)) for y in ys]; ymin, ymax = min(ys2), max(ys2)
    else:
        ys2 = ys
    if ymax == ymin: ymax += 1
    xmin, xmax = min(xs), max(xs)
    if xmax == xmin: xmax += 1
    def xy(x, y):
        import math
        yy = math.log10(max(y, 1e-9)) if logy else y
        return left + (x-xmin)/(xmax-xmin)*(width-left-30), height-bottom - (yy-ymin)/(ymax-ymin)*(height-bottom-30)
    colors = ["#2563eb", "#dc2626", "#059669", "#9333ea"]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', '<rect width="100%" height="100%" fill="white"/>', f'<text x="{width/2}" y="28" text-anchor="middle" font-size="20">{title}</text>', f'<text x="20" y="{height/2}" transform="rotate(-90 20 {height/2})" text-anchor="middle">{ylabel}</text>', f'<line x1="{left}" y1="{height-bottom}" x2="{width-30}" y2="{height-bottom}" stroke="black"/><line x1="{left}" y1="30" x2="{left}" y2="{height-bottom}" stroke="black"/>']
    for i, (name, values) in enumerate(series.items()):
        pts = " ".join(f"{xy(x,y)[0]:.1f},{xy(x,y)[1]:.1f}" for x,y in values)
        out.append(f'<polyline points="{pts}" fill="none" stroke="{colors[i%len(colors)]}" stroke-width="3"/>')
        for x,y in values:
            px,py=xy(x,y); out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="{colors[i%len(colors)]}"/>')
        lx = width-180; ly = 55 + i*22; out.append(f'<line x1="{lx}" y1="{ly}" x2="{lx+20}" y2="{ly}" stroke="{colors[i%len(colors)]}" stroke-width="3"/><text x="{lx+28}" y="{ly+5}">{name}</text>')
    for x in sorted(set(xs)):
        px,_=xy(x, min(ys)); out.append(f'<text x="{px:.1f}" y="{height-bottom+22}" text-anchor="middle">{x}</text>')
    out.append('</svg>'); path.write_text("\n".join(out), encoding="utf-8")


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(); parser.add_argument("--input", default="results/raw/benchmark_summary.json"); parser.add_argument("--output", default="results/figures"); args = parser.parse_args()
    payload = json.loads(Path(args.input).read_text(encoding="utf-8")); out = Path(args.output); out.mkdir(parents=True, exist_ok=True)
    summaries = payload["summaries"]
    for field, title, ylabel, filename, logy in [("nvars", "SAT variables versus N", "Variables", "variables_vs_n.svg", False), ("nclauses", "SAT clauses versus N", "Clauses", "clauses_vs_n.svg", False), ("median_total_time_s", "Median runtime versus N", "Seconds", "runtime_vs_n.svg", True)]:
        series={}
        for row in summaries:
            value=row.get(field)
            if value is not None: series.setdefault(row["encoding"], []).append((row["n"], value))
        for values in series.values(): values.sort()
        svg_plot(out/filename, title, ylabel, series, logy)
    status = {}
    for row in summaries:
        status[f"{row['encoding']} (completed)"] = [(row["n"], row["sat"] + row["unsat"])]
    svg_plot(out/"completion_summary.svg", "Completed trials by N", "Completed trials", status)
    print(f"generated {len(list(out.glob('*.svg')))} SVG plots in {out}")


if __name__ == "__main__": main()
