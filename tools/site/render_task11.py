"""Render saved economy outputs; no model solve is called here."""
from __future__ import annotations
import argparse
import html
import json
import math
from pathlib import Path
from export_task11 import atomic_bytes, atomic_json, file_hash, freeze, read_json, require, MOMENTS


def svg_figure(result, design, step, mobile=False):
    """Use ordinary economic units and label every scale and comparison."""
    w, h = (360, 580) if mobile else (960, 540)
    left, right = (26, 334) if mobile else (66, 894)
    width = right-left
    navy, teal, coral, muted = '#172b40', '#137c78', '#db785d', '#596d7e'
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img">',
           '<rect width="100%" height="100%" rx="20" fill="#f6f8fa"/>',
           '<style>text{font-family:Inter,Arial,sans-serif}</style>']
    def text(x,y,value,size=18,color=navy,anchor='start',weight=400):
        out.append(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{html.escape(str(value))}</text>')
    def line(x1,y1,x2,y2,color='#cdd8df',size=1):
        out.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{color}" stroke-width="{size}"/>')
    def rect(x,y,ww,hh,color):
        out.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{max(0,ww):.2f}" height="{max(0,hh):.2f}" rx="3" fill="{color}"/>')
    def dot(x,y,color,r=4):
        out.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="{color}"/>')
    def poly(points,color):
        out.append('<polyline fill="none" stroke="'+color+'" stroke-width="3" points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in points)+'"/>')
    def legend(y, first='Period 1', second='Period 2'):
        dot(left+4,y-5,teal);text(left+17,y,first,18 if mobile else 17)
        x=left+167 if mobile else right-130
        dot(x,y-5,coral);text(x+13,y,second,18 if mobile else 17)
    titles=['Productivity','Shares settle','100 workers','Firms leave','Model vs data']
    subtitles=['One market, the same firms','Shares and Cournot markups','Where employment goes','Re-solve after firms exit','One economy, three targets']
    text(left,36,f'0{step+1}',17,teal,weight=700)
    text(left,78,titles[step],29 if mobile else 34,weight=700)
    text(left,110,subtitles[step],17 if mobile else 19,muted)
    if step == 0:
        first,second=[p['share_calls'][0]['z'] for p in result['period_trace']]
        top,bottom=175,440 if mobile else 414
        x0=left+30; pw=right-x0
        ymax=max(max(first),max(second))*1.1
        text(left,148,'Relative productivity z',17,muted)
        for f in (0,.5,1):
            y=bottom-f*(bottom-top);line(x0,y,right,y)
            text(x0-8,y+6,f'{f*ymax:.1f}',15,muted,'end')
        stride=pw/len(first)
        for i,(a,b) in enumerate(zip(first,second)):
            x=x0+i*stride+stride*.1
            for dx,v,c in ((0,a,teal),(.4,b,coral)):
                bh=v/ymax*(bottom-top);rect(x+stride*dx,bottom-bh,stride*.32,bh,c)
            if not mobile or i in (0,len(first)//2,len(first)-1):
                text(x0+(i+.5)*stride,bottom+26,i+1,15,muted,'middle')
        text((x0+right)/2,bottom+59,'Firm identity',17,muted,'middle')
        legend(h-37)
    elif step == 1:
        call=result['period_trace'][0]['share_calls'][0]
        shares,markups,steps=call['final_share'],call['final_markup'],call['steps']
        top,bottom=169,295 if mobile else 403
        pw=width if mobile else width*.58
        stride=pw/len(shares);ymax=max(shares)*1.18
        text(left,145,'Share (%) by firm',17,teal)
        line(left,bottom,left+pw,bottom)
        for i,v in enumerate(shares):
            bh=v/ymax*(bottom-top);rect(left+(i+.15)*stride,bottom-bh,stride*.68,bh,teal)
            if not mobile or i in (0,len(shares)//2,len(shares)-1):
                text(left+(i+.5)*stride,bottom+25,i+1,14,muted,'middle')
                if not mobile: text(left+(i+.5)*stride,bottom-bh-9,f'{v*100:.1f}',14,teal,'middle')
        active=[v for v in markups if v>0]
        text(left,bottom+60,f'Markup range: {min(active):.2f}–{max(active):.2f}',17,coral)
        firm=max(range(len(shares)),key=shares.__getitem__)
        rx=left if mobile else left+pw+50
        rw=width if mobile else width-pw-50
        ytop,ybottom=(438,506) if mobile else (225,340)
        values=[call['initial_share'][firm]]+[s['share'][firm] for s in steps]
        lo,hi=min(values),max(values);pad=max((hi-lo)*.15,.005)
        lo=max(0,lo-pad);hi=min(1,hi+pad)
        points=[(rx+i/max(1,len(values)-1)*rw,ybottom-(v-lo)/(hi-lo)*(ybottom-ytop)) for i,v in enumerate(values)]
        text(rx,ytop-49,f'Firm {firm+1} · share updates',17,weight=600)
        text(rx,ytop-20,f'{100*values[0]:.1f}% → {100*values[-1]:.1f}%',20,teal)
        line(rx,ybottom,rx+rw,ybottom)
        poly(points,teal);dot(*points[0],teal);dot(*points[-1],teal)
        text(rx,ybottom+27,'Start',16,muted)
        text(rx+rw,ybottom+27,f"{call['iterations']} updates",16,muted,'end')
        if not mobile: text(rx,ybottom+78,'Then prices and shares agree.',17,muted)
    elif step == 2:
        totals=result['period_totals']
        rounds=[p['rounds'][-1] for p in result['period_trace']]
        barw=width-13
        for t,(p,r) in enumerate(zip(totals,rounds)):
            y=177+t*(158 if mobile else 137)
            production=100*p['production_labor']/p['total_employment']
            fixed=100*p['fixed_labor']/p['total_employment']
            text(left,y,f'Period {t+1}',21,weight=600)
            a=barw*production/100;b=barw*fixed/100
            rect(left,y+22,a,42,teal);rect(left+a,y+22,b,42,coral)
            for cx,v in ((left+a/2,production),(left+a+b/2,fixed)):
                if v>=12: text(cx,y+49,f'{v:.1f}',19,'#ffffff','middle',600)
            marker=left+barw*r['labor_supply']/p['total_employment']
            line(marker,y+13,marker,y+73,navy,3);dot(marker,y+13,navy)
            text(left,y+99,f'{production:.1f} production + {fixed:.1f} overhead',17,muted)
        legend(h-74,'Production','Overhead')
        line(left,h-37,left+17,h-37,navy,3);dot(left+8,h-42,navy)
        text(left+27,h-31,'Marker: labor supplied = 100',17,muted)
    elif step == 3:
        markets=design['config']['markets']
        series=[[r['active_firms']/markets for r in p['rounds']] for p in result['period_trace']]
        last=max(map(len,series))-1
        lo=min(min(v) for v in series)*.94;hi=max(max(v) for v in series)*1.03
        x0=left+32;pw=right-x0;top,bottom=175,396
        text(left,146,'Operating firms per market',17,muted)
        for f in (0,.5,1):
            y=bottom-f*(bottom-top);line(x0,y,right,y)
            text(x0-8,y+6,f'{lo+f*(hi-lo):.1f}',15,muted,'end')
        for t,values in enumerate(series):
            c=teal if t==0 else coral
            points=[(x0+i/max(1,last)*pw,bottom-(v-lo)/(hi-lo)*(bottom-top)) for i,v in enumerate(values)]
            poly(points,c)
            for xy in points:dot(*xy,c,3)
        text(x0,bottom+28,'1',16,muted)
        text(right,bottom+28,str(last+1),16,muted,'end')
        text((x0+right)/2,bottom+58,'Solver round · not time',17,muted,'middle')
        for t,values in enumerate(series):
            text(left,h-57+t*28,f'P{t+1}: {values[0]:.2f} → {values[-1]:.2f} firms / market',18,teal if t==0 else coral)
    else:
        names=[('Reallocation',MOMENTS[0],100,'%','pp'),('Markup',MOMENTS[1],1,'','ratio'),('SGA / cost',MOMENTS[2],100,'%','pp')]
        for i,(label,name,mult,suffix,unit) in enumerate(names):
            y=163+i*(124 if mobile else 105)
            value,target=result['moments'][name]*mult,design['target'][name]*mult
            text(left,y,label,20,weight=600)
            text(right,y,f'{value:.3f}{suffix}',22,teal,'end',600)
            maximum=max(value,target)*1.12
            rect(left,y+19,value/maximum*width,18,teal)
            marker=left+target/maximum*width;line(marker,y+12,marker,y+45,coral,3)
            if mobile:
                text(left,y+68,f'Data {target:.3f}{suffix}',16,coral)
                text(left,y+94,f'Gap {value-target:+.3f} {unit}',17,muted)
            else:
                text(left,y+67,f'Data {target:.3f}{suffix}  ·  gap {value-target:+.3f} {unit}',17,muted)
        text(left,h-24,'Each row has its own scale.',16,muted)
    out.append('</svg>')
    return ''.join(out)

def build_gallery(run_dir, design, results, manifest, output_dir=None):
    out=Path(output_dir) if output_dir is not None else Path(run_dir)/"export"
    by_id={r["id"]:r for r in results}
    titles=["Firms differ","Shares settle","Labor clears","Firms leave","Compare the fit"]
    explanations=["Productivity changes; firm identities stay the same.","Prices and demand shares adjust until they agree.",
                  "Every worker produces goods or covers fixed operations.","After exits, solve prices and employment again.",
                  "Teal = model. Coral marker = year-2000 data."]
    captions=["Market 1, fixed in advance. Teal: period 1; coral: period 2.","Actual updates for the largest final-share firm in market 1, first exit round.",
              "Each bar = 100 employed workers. The dark marker is household labor supplied.","Teal: period 1; coral: period 2. Rounds are solver steps, not years.",
              "Each row has its own scale. pp = percentage points; markup is a ratio."]
    cases=[]
    for point in design["points"]:
        case={"id":point["id"],"label":"Baseline" if point["id"]=="baseline" else point["id"].replace("_"," "),
              "description":"Fixed-parameter evaluation", "sigma_label":f"σ = {point['x'][3]:.6f}",
              "N_label":f"N = {point['x'][4]:g}","M_label":f"M = {math.floor(point['x'][4])}",
              "zeta_label":f"ζ = {point['x'][5]:.6f}","seed_label":f"seed {point['seed']}","modes":{}}
        for mode in ("sample","reference","direct"):
            result=by_id[f"{point['id']}_{mode}"]
            steps=[]
            for step in range(5):
                name=f"{point['id']}_{mode}_{step+1}"
                for mobile in (False,True):
                    suffix="_mobile" if mobile else ""
                    atomic_bytes(out/"assets"/f"{name}{suffix}.svg",svg_figure(result,design,step,mobile).encode())
                steps.append({"title":titles[step],"explanation":explanations[step],"image":f"assets/{name}.svg",
                              "mobile_image":f"assets/{name}_mobile.svg","alt":titles[step]+" from the solved economy","caption":captions[step]})
            case["modes"][mode]={"phi_label":f"{result['phi']*1e6:.3f} per million",
                                 "phi_readout":f"{result['phi']*1e6:.3f} per million",
                                 "mbar_label":f"{result['period_totals'][0]['mean_active_firms']:.3f}",
                                 "moments":{"reallocation_label":f"{100*result['moments'][MOMENTS[0]]:.3f}%",
                                            "markup_label":f"{result['moments'][MOMENTS[1]]:.4f}",
                                            "sga_label":f"{100*result['moments'][MOMENTS[2]]:.3f}%"},
                                 "status_label":"All numerical checks passed · 10,000 markets · two periods", "steps":steps}
        cases.append(case)
    gallery={"schema_version":1,"title":"One economy, five steps","cases":cases,"paths":design["paths"],
             "default_case":"baseline","default_path":"sigma","default_point":2,"default_mode":"sample",
             "provenance":{"run_fingerprint":manifest["run_fingerprint"],"cases":51,"parameter_points":17,
                           "anchor_definition_check_sha256":manifest["input_sha256"]["inputs/anchor_definition_check.json"]},
             "boundary_note":"2000 targets are references. One evaluation; no new estimation."}
    text=json.dumps(gallery,ensure_ascii=False,separators=(",",":"),allow_nan=False)
    atomic_bytes(out/"task11_gallery.json",(text+"\n").encode())
    atomic_bytes(out/"task11_gallery.js",("window.TASK11_GALLERY="+text+";\n").encode())
    freeze(Path(run_dir)/"inputs/anchor_definition_check.json",out/"assets/anchor_definition_check.json")
    freeze(Path(run_dir)/"manifest.json",out/"assets/manifest.json")
    return gallery


def render(run_dir, output_dir=None):
    run_dir=Path(run_dir).resolve()
    out=Path(output_dir).resolve() if output_dir is not None else run_dir/"export"
    bundle=read_json(run_dir/"export/task11_data.json")
    manifest=read_json(run_dir/"manifest.json")
    audit=read_json(run_dir/"export_audit.json")
    require(audit["passed"] and audit["ok"]==audit["expected"]==51,"all 51 scenarios must pass before rendering")
    require(bundle["provenance"]["run_fingerprint"]==manifest["run_fingerprint"]==audit["run_fingerprint"],"numerical run identities differ")
    require(bundle["provenance"]["export_audit_sha256"]==file_hash(run_dir/"export_audit.json"),"export audit hash differs")
    gallery=build_gallery(run_dir,bundle["design"],bundle["scenarios"],manifest,out)
    record={"schema_version":1,"run_fingerprint":manifest["run_fingerprint"],
            "renderer_sha256":file_hash(Path(__file__)),"numeric_driver_sha256":manifest["driver_sha256"],
            "data_sha256":file_hash(run_dir/"export/task11_data.json"),
            "files_sha256":{str(path.relative_to(out)).replace('\\','/'):file_hash(path)
                            for path in sorted(out.rglob('*')) if path.is_file() and '__pycache__' not in path.parts and path.name not in ('render_manifest.json','page_manifest.json')},
            "interpretation":"Only formatting and precomputed graphics are rendered; no model is solved."}
    # The record of what was rendered stays with the run, not in the website folder.
    atomic_json(run_dir/"render_manifest.json",record)
    return {"cases":len(gallery["cases"]),"mode_evaluations":51,"files":len(record["files_sha256"]),
            "run_fingerprint":manifest["run_fingerprint"]}


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir',required=True)
    parser.add_argument('--output-dir')
    args=parser.parse_args()
    print(json.dumps(render(args.run_dir,args.output_dir),sort_keys=True))


