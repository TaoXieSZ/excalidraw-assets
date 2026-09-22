"""Rebuild four editable icons from the approved pencil-style study (stdlib only)."""
import copy
import hashlib
import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INK = '#292a28'
COLORS = {'CVM': '#e99a59', 'CLB': '#df819e', 'DNS': '#a38bd5', 'COS': '#8ba87c'}


def oval(cx, cy, rx, ry, start=0, end=2 * math.pi, count=48):
    return [(cx + rx * math.cos(start + (end-start)*i/count),
             cy + ry * math.sin(start + (end-start)*i/count)) for i in range(count+1)]


def box(x, y, w, h):
    return [(x,y), (x+w,y), (x+w,y+h), (x,y+h), (x,y)]


def shape(name):
    # White silhouettes mask the background strokes. Detail paths remain editable.
    if name == 'CVM':
        silhouettes = [[(34,35),(61,23),(125,24),(126,126),(105,140),(34,139),(34,35)]]
        details = [[(34,35),(104,36),(125,24)], [(104,36),(105,140)],
                   box(40,43,57,23), box(40,75,57,23), box(40,107,57,24),
                   [(115,94),(115,110)], [(120,91),(120,106)],
                   [(36,140),(37,144),(44,144),(44,140)],
                   [(95,141),(95,144),(101,143),(102,140)]]
        details += [oval(49,y,1.6,1.6,count=12) for y in (55,87,119)]
        details += [[(76,y),(85,y)] for y in (55,87,119)]
        return silhouettes, details
    if name == 'CLB':
        return [box(18,62,35,36), box(107,25,34,36), box(107,105,34,36)], [
            [(53,80),(81,80),(81,43),(107,43)], [(81,80),(81,123),(107,123)]]
    if name == 'DNS':
        return [oval(80,81,56,56)], [oval(80,81,24,56), [(24,81),(136,81)],
            [(80,25),(80,137)], oval(80,29,68,30,.25*math.pi,.75*math.pi,24),
            oval(80,133,68,30,1.25*math.pi,1.75*math.pi,24)]
    return [[(29,44),(40,132)] + oval(80,132,40,10,math.pi,0,24) + [(132,44)]
             + oval(80.5,44,51.5,13,0,-math.pi,24)], [
        oval(80.5,44,51.5,13), oval(51,72,4.1,5,count=24),
        bezier((52,72),(74,103),(158,131),(131,72))]


def bezier(a,b,c,d):
    return [tuple((1-t)**3*a[k]+3*(1-t)**2*t*b[k]+3*(1-t)*t*t*c[k]+t**3*d[k]
                  for k in (0,1)) for t in (i/48 for i in range(49))]


def base(ident, group):
    seed = int(hashlib.sha256(ident.encode()).hexdigest()[:7],16)
    return dict(id=ident,type='line',x=0,y=0,width=0,height=0,angle=0,
                strokeColor=INK,backgroundColor='transparent',fillStyle='solid',
                strokeWidth=1,strokeStyle='solid',roughness=0,opacity=100,
                groupIds=[group],frameId=None,roundness=None,seed=seed,version=1,
                versionNonce=seed,isDeleted=False,boundElements=None,
                updated=1790006400000,link=None,locked=False)


def line(points, ident, group, color=INK, width=1, opacity=100, fill='transparent'):
    e = base(ident,group)
    x,y = points[0]
    e.update(x=x,y=y,width=max(p[0] for p in points)-min(p[0] for p in points),
             height=max(p[1] for p in points)-min(p[1] for p in points),
             points=[[round(a-x,3),round(b-y,3)] for a,b in points],
             strokeColor=color,strokeWidth=width,opacity=opacity,backgroundColor=fill,
             startBinding=None,endBinding=None,startArrowhead=None,endArrowhead=None,
             lastCommittedPoint=None)
    return e


def pencil(points, ident, group, width=1.25):
    rng = random.Random(ident)
    # A few close, independent graphite strands, not a periodic sine distortion.
    out=[]
    for strand in range(3):
        sampled=[]
        for a,b in zip(points,points[1:]):
            count=max(1,math.ceil(math.dist(a,b)/3.5))
            for i in range(count):
                t=i/count
                sampled.append((a[0]+(b[0]-a[0])*t+rng.uniform(-.30,.30),
                                a[1]+(b[1]-a[1])*t+rng.uniform(-.30,.30)))
        sampled.append((points[-1][0]+rng.uniform(-.2,.2),points[-1][1]+rng.uniform(-.2,.2)))
        if points[0]==points[-1]: sampled[-1]=sampled[0]
        out.append(line(sampled,f'{ident}-{strand}',group,width=width if strand==0 else .45,
                        opacity=90 if strand==0 else 45))
    return out


def hatch(group, color):
    rng=random.Random(group)
    result=[]
    # The approved image has a dominant diagonal grain with a quieter cross pass.
    for slope,spacing,opacity in [(-1.14,2.5,53),(.94,10,20)]:
        offset=-190.0
        while offset<350:
            hits=[]
            for a,b in zip(box(1.5,1.5,157,157),box(1.5,1.5,157,157)[1:]):
                den=(b[1]-a[1])-slope*(b[0]-a[0])
                if not den: continue
                t=(slope*a[0]+offset-a[1])/den
                if 0<=t<=1: hits.append((a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])))
            if len(hits)==2 and math.dist(*hits)>2:
                a,b=hits
                pts=[a]+[(a[0]+(b[0]-a[0])*t+rng.uniform(-.35,.35),
                           a[1]+(b[1]-a[1])*t+rng.uniform(-.35,.35)) for t in (.2,.4,.6,.8)]+[b]
                result.append(line(pts,f'{group}-hatch-{len(result)}',group,color,
                                   rng.uniform(.45,.95),rng.randint(opacity-10,opacity+10)))
            offset+=rng.uniform(spacing*.7,spacing*1.3)
    return result


def icon(name):
    group='pencil-'+name
    silhouettes,details=shape(name)
    elements=[line(box(0,0,160,160),group+'-paper',group,'transparent',0,fill='#ffffff')]
    elements+=hatch(group,COLORS[name])
    for i,p in enumerate(silhouettes):
        elements.append(line(p,f'{group}-mask-{i}',group,'transparent',0,fill='#ffffff'))
    for i,p in enumerate(silhouettes+details):
        elements+=pencil(p,f'{group}-symbol-{i}',group)
    elements+=pencil(box(0,0,160,160),group+'-frame',group,1.4)
    # Square base geometry is preserved; graphite strands vary by at most 0.3px.
    text=base(group+'-label',group)
    text.update(type='text',x=0,y=167,width=160,height=27.5,fontSize=22,fontFamily=5,
                text=name,originalText=name,textAlign='center',verticalAlign='top',
                containerId=None,autoResize=False,lineHeight=1.25)
    elements.append(text)
    return dict(id=group,name=name+' · Pencil',status='unpublished',created=1790006400000,elements=elements)


def scene(elements):
    return dict(type='excalidraw',version=2,source='https://excalidraw.com',elements=elements,
                appState={'viewBackgroundColor':'#ffffff','gridSize':None},files={})


def dump(path, value):
    path.write_text(json.dumps(value,ensure_ascii=False,separators=(',',':'))+'\n')


def svg(elements):
    parts=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="-4 -4 168 205">']
    for e in elements:
        if e['type']=='text':
            parts.append(f'<text x="80" y="190" text-anchor="middle" fill="{INK}" font-family="cursive" font-size="22">{e["text"]}</text>')
            continue
        pts=' '.join(f'{x+e["x"]:.3f},{y+e["y"]:.3f}' for x,y in e['points'])
        parts.append(f'<polyline points="{pts}" fill="{e["backgroundColor"]}" stroke="{e["strokeColor"]}" stroke-width="{e["strokeWidth"]}" opacity="{e["opacity"]/100}" stroke-linejoin="round" stroke-linecap="round"/>')
    return ''.join(parts)+'</svg>'


def main():
    items=[icon(name) for name in COLORS]
    sheet=[]
    for i,item in enumerate(items):
        name=list(COLORS)[i]
        dump(ROOT/'output'/f'{name}.excalidraw',scene(item['elements']))
        (ROOT/'assets'/f'{name}.svg').write_text(svg(item['elements']))
        for e in copy.deepcopy(item['elements']):
            e['x']+=(i%2)*230
            e['y']+=(i//2)*245
            sheet.append(e)
    dump(ROOT/'output'/'pencil.excalidrawlib',dict(type='excalidrawlib',version=2,
         source='https://excalidraw.com',libraryItems=items))
    dump(ROOT/'output'/'icon-sheet.excalidraw',scene(sheet))
    cards=''.join(f'<a href="{name}.excalidraw"><img src="../assets/{name}.svg" alt="{name}"></a>' for name in COLORS)
    (ROOT/'output'/'index.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Pencil infrastructure icons</title><style>*{box-sizing:border-box}body{margin:0;background:#faf9f6;color:#292a28;font:16px/1.6 system-ui}main{max-width:950px;margin:auto;padding:35px 25px}h1{font-size:30px;margin:6px 0}p{color:#72756e}nav{display:flex;gap:22px;flex-wrap:wrap}a{color:#42664a}.icons{display:grid;grid-template-columns:repeat(4,1fr);gap:35px;margin:35px 0;padding:30px;background:white}.icons img{width:100%}details{border-top:1px solid #d9dcd5;padding-top:15px}details img{width:100%;max-width:640px;display:block;margin:25px auto}@media(max-width:650px){.icons{grid-template-columns:repeat(2,1fr);gap:20px}}</style><main><small>CVM / CLB / DNS / COS</small><h1>Pencil infrastructure icons</h1><p>Square frames, colored pencil hatching, simple ink contours. Ungroup to edit individual strokes.</p><nav><a href="pencil.excalidrawlib" download>Download library</a><a href="icon-sheet.excalidraw" download>Download editable sheet</a></nav><div class="icons">'''+cards+'''</div><p>Editable vector adaptation of the approved sketch. Paper grain is simplified; lettering uses Excalidraw's handwriting font.</p><details><summary>Approved style reference</summary><img src="../assets/approved-reference.png" alt="Approved pencil sketch reference"></details></main></html>''')
    ids=[e['id'] for e in sheet]
    assert len(ids)==len(set(ids))
    assert len(items)==4 and all(e['type'] in ('line','text') for e in sheet)
    assert all(math.isfinite(e[k]) for e in sheet for k in ('x','y','width','height'))
    assert all(e['width']>=0 and e['height']>=0 for e in sheet)
    assert all(e['fontFamily']==5 for e in sheet if e['type']=='text')
    for item in items:
        frame=item['elements'][0]
        assert frame['points']==[[0,0],[160,0],[160,160],[0,160],[0,0]]
        assert all(e['groupIds']==[item['id']] for e in item['elements'])
    import re
    page=(ROOT/'output'/'index.html').read_text()
    links=re.findall(r'(?:href|src)="([^"]+)"',page)
    assert all((ROOT/'output'/link).exists() for link in links)
    assert not re.search(r'[\u4e00-\u9fff]',page)
    report=dict(items=4,elements={item['name']:len(item['elements']) for item in items},
                previewLinks=len(links),embeddedImages=0,uniqueIds=True,finiteGeometry=True,
                squareBase=True,grouping=True,englishOnly=True)
    dump(ROOT/'data'/'validation.json',report)
    print(json.dumps(report))


if __name__=='__main__':
    main()
