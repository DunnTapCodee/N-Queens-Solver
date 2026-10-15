"""Generate compact SVG figures from the approved medium performance summary."""
import json
from pathlib import Path


def main():
    root=Path(__file__).resolve().parents[1]; rows=json.loads((root/"results/raw/benchmark_medium_performance_summary.json").read_text(encoding="utf-8"))["summaries"]; out=root/"results/figures/medium"; out.mkdir(parents=True,exist_ok=True)
    series={}
    for r in rows:
        if r["median_total_time_s"] is not None: series.setdefault(r["solver"]+('/'+r["encoding"] if r["encoding"]!='n/a' else ''),[]).append((r["n"],r["median_total_time_s"]))
    colors=['#2563eb','#dc2626','#059669','#9333ea','#ea580c','#0891b2']; W,H,L,B=1000,540,100,75; import math
    xs=[x for v in series.values() for x,y in v]; ys=[y for v in series.values() for x,y in v]; xmin,xmax=min(xs),max(xs); ymin,ymax=min(math.log10(y) for y in ys),max(math.log10(y) for y in ys)
    def xy(x,y): return L+(x-xmin)/(xmax-xmin)*(W-L-40),H-B-(math.log10(y)-ymin)/(ymax-ymin)*(H-B-35)
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"><rect width="100%" height="100%" fill="white"/><text x="{W/2}" y="28" text-anchor="middle" font-size="20">Medium-matrix median total runtime (log scale)</text><line x1="{L}" y1="{H-B}" x2="{W-40}" y2="{H-B}" stroke="black"/><line x1="{L}" y1="35" x2="{L}" y2="{H-B}" stroke="black"/>']
    for i,(name,vals) in enumerate(series.items()):
        c=colors[i%len(colors)]; vals=sorted(vals); s.append(f'<polyline points="{" ".join(f"{xy(x,y)[0]:.1f},{xy(x,y)[1]:.1f}" for x,y in vals)}" fill="none" stroke="{c}" stroke-width="3"/>'); ly=55+i*22; s.append(f'<line x1="{W-290}" y1="{ly}" x2="{W-270}" y2="{ly}" stroke="{c}" stroke-width="3"/><text x="{W-262}" y="{ly+5}">{name}</text>')
    for x in sorted(set(xs)): px,_=xy(x,min(ys)); s.append(f'<text x="{px:.1f}" y="{H-B+22}" text-anchor="middle">{x}</text>')
    s.append('</svg>'); (out/"runtime_by_method.svg").write_text('\n'.join(s),encoding='utf-8'); print('generated',out/"runtime_by_method.svg")


if __name__ == "__main__": main()
