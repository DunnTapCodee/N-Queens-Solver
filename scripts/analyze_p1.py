"""Audit and plot the completed P1 artifacts without running any solver."""

import csv
import json
import math
import statistics
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUTS = {
    "Glucose3": ROOT / "results/p1/glucose3.json",
    "CaDiCaL": ROOT / "results/p1/cadical195.json",
    "DPLL fallback": ROOT / "results/p1/dpll_final.json",
    "CPLEX MIP": ROOT / "results/p1/cplex_mip.json",
    "CPLEX CP Optimizer": ROOT / "results/p1/cplex_cp.json",
    "Gurobi": ROOT / "results/p1/gurobi.json",
}
PARTIAL_INPUTS = {
    "DPLL initial error": ROOT / "results/p1/dpll.json",
    "DPLL partial N16": ROOT / "results/p1/dpll_v2.json",
}
STATUSES = ("SAT", "UNSAT", "FEASIBLE", "OPTIMAL", "TIMEOUT", "ERROR", "LICENSE_LIMIT")


def load(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    return data, data.get("records", [])


def summary(rows):
    completed = [float(r["total_time_s"]) for r in rows if r["status"] in {"SAT", "UNSAT", "FEASIBLE", "OPTIMAL"}]
    build = [float(r["build_time_s"]) for r in rows if r.get("build_time_s") is not None]
    solve = [float(r["solve_time_s"]) for r in rows if r.get("solve_time_s") is not None]
    def stats(values):
        return {
            "samples": len(values),
            "median_s": statistics.median(values) if values else None,
            "mean_s": statistics.mean(values) if values else None,
            "stdev_s": statistics.stdev(values) if len(values) > 1 else None,
        }
    return {
        "records": len(rows),
        "completed_records": len(completed),
        "valid_solutions": sum(r.get("solution_valid") is True for r in rows),
        **{status.lower(): sum(r["status"] == status for r in rows) for status in STATUSES},
        "total_time": stats(completed),
        "build_time": stats(build),
        "solve_time": stats(solve),
    }


def group_rows(rows, key):
    groups = {}
    for row in rows:
        groups.setdefault(key(row), []).append(row)
    return groups


def write_csv(path, rows):
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def svg_header(width, height, title):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            '<style>text{font-family:Arial,sans-serif;font-size:12px} .title{font-size:16px;font-weight:bold} .axis{stroke:#333;stroke-width:1} .grid{stroke:#ddd;stroke-width:1} .legend{font-size:11px}</style>',
            f'<text x="{width/2:.1f}" y="24" text-anchor="middle" class="title">{title}</text>']


def finish_svg(lines):
    lines.append("</svg>")
    return "\n".join(lines)


def line_plot(path, series, title, y_label, log_y=False, width=1000, height=620):
    left, top, right, bottom = 78, 55, 30, 82
    pw, ph = width - left - right, height - top - bottom
    xs = sorted({x for points, _ in series for x, _ in points})
    values = [y for points, _ in series for _, y in points if y is not None and y > 0]
    if not values:
        return
    transform = (lambda y: math.log10(y)) if log_y else (lambda y: y)
    ys = [transform(y) for y in values]
    ymin, ymax = min(ys), max(ys)
    if ymin == ymax: ymax = ymin + 1
    def xmap(x): return left + (xs.index(x) / max(1, len(xs)-1)) * pw
    def ymap(y): return top + (ymax - transform(y)) / (ymax-ymin) * ph
    colors = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#ff7f0e", "#17becf", "#8c564b", "#e377c2"]
    lines = svg_header(width, height, title)
    for i in range(6):
        y = top + ph*i/5
        lines.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left+pw}" y2="{y:.1f}" class="grid"/>')
        val = ymax - (ymax-ymin)*i/5
        label = f"{10**val:.3g}" if log_y else f"{val:.3g}"
        lines.append(f'<text x="{left-8}" y="{y+4:.1f}" text-anchor="end">{label}</text>')
    lines.append(f'<line x1="{left}" y1="{top+ph}" x2="{left+pw}" y2="{top+ph}" class="axis"/>')
    lines.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top+ph}" class="axis"/>')
    for x in xs:
        px=xmap(x); lines.append(f'<text x="{px:.1f}" y="{top+ph+20}" text-anchor="middle">N={x}</text>')
    lines.append(f'<text x="18" y="{top+ph/2}" transform="rotate(-90 18 {top+ph/2})" text-anchor="middle">{y_label}</text>')
    for i, (points, label) in enumerate(series):
        color=colors[i%len(colors)]
        points = [(x,y) for x,y in points if y is not None]
        if points:
            d=" ".join(("M" if j==0 else "L")+f" {xmap(x):.1f},{ymap(y):.1f}" for j,(x,y) in enumerate(points))
            lines.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2"/>')
            for x,y in points: lines.append(f'<circle cx="{xmap(x):.1f}" cy="{ymap(y):.1f}" r="3" fill="{color}"/>')
        lx=left+pw-245; ly=top+16+i*16
        lines.append(f'<line x1="{lx}" y1="{ly}" x2="{lx+18}" y2="{ly}" stroke="{color}" stroke-width="2"/>')
        lines.append(f'<text x="{lx+23}" y="{ly+4}" class="legend">{label}</text>')
    path.write_text(finish_svg(lines), encoding="utf-8")


def bar_plot(path, rows, title, width=1100, height=620):
    left, top, right, bottom = 70, 55, 30, 90
    pw, ph = width-left-right, height-top-bottom
    labels=[f"{r['family']} N={r['n']}" for r in rows]
    maximum=max((r['records'] for r in rows), default=1)
    lines=svg_header(width,height,title)
    for i in range(6):
        y=top+ph*i/5; val=maximum*(5-i)/5
        lines.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left+pw}" y2="{y:.1f}" class="grid"/><text x="{left-8}" y="{y+4:.1f}" text-anchor="end">{val:.0f}</text>')
    groupw=pw/max(1,len(rows)); colors={"SAT":"#1f77b4","FEASIBLE":"#ff7f0e","OPTIMAL":"#2ca02c","UNSAT":"#9467bd","TIMEOUT":"#d62728","ERROR":"#8c564b","LICENSE_LIMIT":"#7f7f7f"}
    for i,r in enumerate(rows):
        x=left+i*groupw+groupw*.12; bw=groupw*.76; y=top+ph
        for status in STATUSES:
            count=r[status.lower()]; h=(count/max(1,maximum))*ph
            if count: lines.append(f'<rect x="{x:.1f}" y="{y-h:.1f}" width="{bw:.1f}" height="{h:.1f}" fill="{colors[status]}"/>')
            y-=h
        lines.append(f'<text x="{x+bw/2:.1f}" y="{top+ph+16}" transform="rotate(55 {x+bw/2:.1f} {top+ph+16})" text-anchor="start">{labels[i]}</text>')
    for i,status in enumerate(STATUSES):
        x=left+i*125; lines.append(f'<rect x="{x}" y="{height-25}" width="12" height="12" fill="{colors[status]}"/><text x="{x+16}" y="{height-14}">{status}</text>')
    lines.append(f'<line x1="{left}" y1="{top+ph}" x2="{left+pw}" y2="{top+ph}" class="axis"/>')
    lines.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top+ph}" class="axis"/>')
    path.write_text(finish_svg(lines), encoding="utf-8")


def main():
    out=ROOT/"results/p2_p3"; out.mkdir(parents=True,exist_ok=True)
    datasets={}; metadata={}
    for family,path in INPUTS.items():
        data,rows=load(path); datasets[family]=rows; metadata[family]={"artifact":str(path.relative_to(ROOT)),"run_id":data.get("metadata",{}).get("run_id"),"records":len(rows)}
    partial={}
    for family,path in PARTIAL_INPUTS.items():
        if path.exists():
            data,rows=load(path); partial[family]=summary(rows)
    stat_rows=[]
    for family,rows in datasets.items():
        for (n,encoding),group in sorted(group_rows(rows,lambda r:(r["n"],r["encoding"])).items()):
            s=summary(group)
            stat_rows.append({"source_artifact":metadata[family]["artifact"],"family":family,"n":n,"encoding":encoding,"samples":len(group),"records":s["records"],"completed_records":s["completed_records"],"valid_solutions":s["valid_solutions"],**{status.lower():s[status.lower()] for status in STATUSES},"median_total_time_s":s["total_time"]["median_s"],"mean_total_time_s":s["total_time"]["mean_s"],"stdev_total_time_s":s["total_time"]["stdev_s"],"median_build_time_s":s["build_time"]["median_s"],"mean_build_time_s":s["build_time"]["mean_s"],"median_solver_time_s":s["solve_time"]["median_s"],"mean_solver_time_s":s["solve_time"]["mean_s"]})
    write_csv(out/"p1_group_statistics.csv",stat_rows)
    (out/"p1_group_statistics.json").write_text(json.dumps({"inputs":metadata,"groups":stat_rows},indent=2),encoding="utf-8")
    status_rows=[]
    for family,rows in datasets.items():
        for n,group in sorted(group_rows(rows,lambda r:r["n"]).items()):
            status_rows.append({"family":family,"source_artifact":metadata[family]["artifact"],"n":n,"records":len(group),**{status.lower():sum(r["status"]==status for r in group) for status in STATUSES}})
    write_csv(out/"p1_status_by_n.csv",status_rows)
    (out/"p1_audit_metadata.json").write_text(json.dumps({"inputs":metadata,"partial_inputs":partial,"notes":{"timeout_runtime":"TIMEOUT records are counted but excluded from completed runtime statistics","missing_metrics":"null values remain excluded; no zero imputation","plot_format":"SVG generated with Python standard library; matplotlib unavailable"}},indent=2),encoding="utf-8")
    sat_families=["Glucose3","CaDiCaL"]
    series=[]
    for family in sat_families:
        for enc in ("pairwise","sequential","binary","commander"):
            points=[]
            for row in stat_rows:
                if row["family"]==family and row["encoding"]==enc: points.append((row["n"],row["median_total_time_s"]))
            series.append((points,f"{family}/{enc}"))
    line_plot(out/"sat_runtime_by_n.svg",series,"SAT runtime by N and encoding","median total runtime (s, log10 scale)",log_y=True)
    line_plot(out/"sat_encoding_median_runtime.svg",series,"SAT encoding comparison","median total runtime (s, log10 scale)",log_y=True)
    model_series=[]
    for family in ("CPLEX MIP","CPLEX CP Optimizer","Gurobi"):
        points=[(r["n"],r["median_total_time_s"]) for r in stat_rows if r["family"]==family]
        model_series.append((points,f"{family} (separate formulation)"))
    line_plot(out/"model_family_runtime.svg",model_series,"Model-family runtime by N","median total runtime (s, log10 scale)",log_y=True)
    final_status=[r for r in status_rows if r["family"] in INPUTS]
    bar_plot(out/"completion_status_by_n.svg",final_status,"P1 completion status by family and N")
    cactus=[]
    for family in sat_families:
        values=sorted(float(r["total_time_s"]) for r in datasets[family] if r["status"] in {"SAT","UNSAT","FEASIBLE","OPTIMAL"})
        cactus.append((list(enumerate(values,1)),family))
    line_plot(out/"sat_cactus.svg",cactus,"SAT backend cactus plot","completed runs (sorted total runtime, s)",log_y=True)
    print(json.dumps({"output":str(out.relative_to(ROOT)),"final_records":sum(len(v) for v in datasets.values()),"stat_rows":len(stat_rows),"partial":partial},indent=2))


if __name__ == "__main__": main()
