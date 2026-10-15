"""Create dependency-free SVG plots from multi-solver summary JSON."""
import argparse
import json
from pathlib import Path


def plot(path, title, ylabel, series, logy=False):
    import math
    W,H,L,B=900,520,90,70; points=[p for vs in series.values() for p in vs]
    if not points: return
    xs=[p[0] for p in points]; ys=[p[1] for p in points]; xmin,xmax=min(xs),max(xs); ymin,ymax=min(ys),max(ys)
    if xmax==xmin: xmax += 1
    if logy: ymin,ymax=min(math.log10(max(y,1e-9)) for y in ys),max(math.log10(max(y,1e-9)) for y in ys)
    if ymax==ymin: ymax += 1
    def xy(x,y):
        yy=math.log10(max(y,1e-9)) if logy else y
        return L+(x-xmin)/(xmax-xmin)*(W-L-30), H-B-(yy-ymin)/(ymax-ymin)*(H-B-30)
    colors=['#2563eb','#dc2626','#059669','#9333ea','#ea580c']; out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"><rect width="100%" height="100%" fill="white"/><text x="{W/2}" y="28" text-anchor="middle" font-size="20">{title}</text><text x="20" y="{H/2}" transform="rotate(-90 20 {H/2})" text-anchor="middle">{ylabel}</text><line x1="{L}" y1="{H-B}" x2="{W-30}" y2="{H-B}" stroke="black"/><line x1="{L}" y1="30" x2="{L}" y2="{H-B}" stroke="black"/>']
    for i,(name,vals) in enumerate(series.items()):
        color=colors[i%len(colors)]; vals=sorted(vals); out.append('<polyline points="'+' '.join(f'{xy(x,y)[0]:.1f},{xy(x,y)[1]:.1f}' for x,y in vals)+f'" fill="none" stroke="{color}" stroke-width="3"/>')
        for x,y in vals:
            px,py=xy(x,y); out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="{color}"/>')
        ly=55+i*22; out.append(f'<line x1="{W-180}" y1="{ly}" x2="{W-160}" y2="{ly}" stroke="{color}" stroke-width="3"/><text x="{W-152}" y="{ly+5}">{name}</text>')
    for x in sorted(set(xs)):
        px,_=xy(x,min(ys)); out.append(f'<text x="{px:.1f}" y="{H-B+22}" text-anchor="middle">{x}</text>')
    out.append('</svg>'); path.write_text('\n'.join(out),encoding='utf-8')


def main():
    p=argparse.ArgumentParser(); p.add_argument('--input',default='results/raw/benchmark_comparison_summary.json'); p.add_argument('--output',default='results/figures/comparison'); a=p.parse_args()
    rows=json.loads(Path(a.input).read_text(encoding='utf-8'))['summaries']; out=Path(a.output); out.mkdir(parents=True,exist_ok=True)
    series={}
    for r in rows:
        if r['median_total_time_s'] is not None: series.setdefault(r['solver'] + (f'/{r["encoding"]}' if r['encoding'] != 'n/a' else ''),[]).append((r['n'],r['median_total_time_s']))
    plot(out/'runtime_by_solver.svg','Median total runtime by solver','Seconds',series,True)
    completion={}
    for r in rows: completion.setdefault(r['solver'] + (f'/{r["encoding"]}' if r['encoding'] != 'n/a' else ''),[]).append((r['n'],r['sat']+r['unsat']))
    plot(out/'completed_by_solver.svg','Completed trials by solver','Completed trials',completion,False)
    print(f'generated {len(list(out.glob("*.svg")))} comparison plots')


if __name__=='__main__': main()
