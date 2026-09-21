"""Square infrastructure tiles inspired by the supplied AWS reference."""
import copy
import hashlib
import html
import json
import math
import random
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
COLOR='#202124'

NAMES={'CVM':'Cloud Virtual Machine','CLB':'Cloud Load Balancer','DNS':'Domain Name System','COS':'Cloud Object Storage'}

def oval(cx,cy,rx,ry,start=0,end=2*math.pi,n=32):
    return [(cx+rx*math.cos(start+(end-start)*i/n),cy+ry*math.sin(start+(end-start)*i/n)) for i in range(n+1)]

def box(x,y,w,h):return [(x,y),(x+w,y),(x+w,y+h),(x,y+h),(x,y)]

def geometry(style,name):
    if style=='single':
        return {
          'CVM':[box(49,29,62,101),[(50,62),(110,62)],[(50,96),(110,96)],[(61,47),(68,47)],[(61,80),(68,80)],[(61,113),(68,113)]],
          'CLB':[box(22,65,27,27),[(49,79),(80,79)],[(80,41),(80,118)],[(80,41),(110,41)],[(80,118),(110,118)],box(111,29,25,25),box(111,106,25,25)],
          'DNS':[oval(80,78,49,49),oval(80,78,20,49),[(32,78),(128,78)]],
          'COS':[[(37,39),(44,116)]+oval(80,116,36,11,math.pi,0,16)+[(123,39),(37,39)],oval(80,39,43,13),box(68,68,24,24)]
        }[name]

def stroke(points,style,ident):
    # Projective vertex placement preserves straight edges without adding wobble.
    # Apply the same map to joined paths so their endpoints stay connected.
    return [((x+.075*y+.5)/(1+.00045*x-.00035*y),
             (y-.045*x+.2)/(1+.00045*x-.00035*y)) for x,y in points]

def element(points,style,ident,group):
    p=stroke(points,style,ident);x,y=p[0]
    return dict(id=ident,type='line',x=x,y=y,width=max(a for a,b in p)-min(a for a,b in p),height=max(b for a,b in p)-min(b for a,b in p),angle=0,strokeColor=COLOR,backgroundColor='transparent',fillStyle='solid',strokeWidth=2,strokeStyle='solid',roughness=0,opacity=100,groupIds=[group],frameId=None,roundness=None,seed=int(hashlib.sha256(ident.encode()).hexdigest()[:7],16),version=3,versionNonce=3,isDeleted=False,boundElements=None,updated=1790006400000,link=None,locked=False,points=[[a-x,b-y] for a,b in p],startBinding=None,endBinding=None,startArrowhead=None,endArrowhead=None,lastCommittedPoint=None)

def label(text,ident,x,y,width=160,size=20):
    return dict(id=ident,type='text',x=x,y=y,width=width,height=size*1.25,angle=0,strokeColor=COLOR,backgroundColor='transparent',fillStyle='solid',strokeWidth=1,strokeStyle='solid',roughness=0,opacity=100,groupIds=[],frameId=None,roundness=None,seed=1,version=3,versionNonce=3,isDeleted=False,boundElements=None,updated=1790006400000,link=None,locked=False,fontSize=size,fontFamily=5,text=text,originalText=text,textAlign='center',verticalAlign='top',containerId=None,autoResize=False,lineHeight=1.25)

def dump(path,data):path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
def scene(elements):return dict(type='excalidraw',version=2,source='https://excalidraw.com',elements=elements,appState={'viewBackgroundColor':'#ffffff','gridSize':None},files={})

PALETTE={'CVM':('#fff0dc','#ef9b45'),'CLB':('#fce5ed','#e8759e'),'DNS':('#ebe8ff','#9c87e9'),'COS':('#e6f4dc','#80bd65')}
VARIANTS=[('cross','Cross-hatch','Perfect square frames. Irregular inner geometry. Light cross-hatching.'),('solid','Solid fill','Alternative solid background.')]
all_items={};sections=[];comparison=[]

def raw_line(points,ident,group):
    e=element(points,'single',ident,group)
    x,y=points[0]
    e.update(x=x,y=y,width=max(p[0] for p in points)-min(p[0] for p in points),
             height=max(p[1] for p in points)-min(p[1] for p in points),
             points=[[u-x,v-y] for u,v in points])
    return e

FRAME=[(0,0),(120,0),(120,120),(0,120),(0,0)]

def hatch_segments(polygon):
    rng=random.Random(42)
    for direction in (-1,1):
        offset=-145.0
        while offset<265:
            slope=direction*rng.uniform(.91,1.09)
            hits=[]
            for (x,y),(u,v) in zip(polygon[:-1],polygon[1:]):
                denom=(v-y)-slope*(u-x)
                if abs(denom)<1e-9:continue
                t=(slope*x+offset-y)/denom
                if 0<=t<=1:hits.append((x+t*(u-x),y+t*(v-y)))
            if len(hits)==2 and math.dist(*hits)>3:yield hits
            offset+=rng.uniform(10,14)

def svg_for(elements,variant,name):
    out=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="-5 -5 130 130">']
    for e in elements:
        if e['type']=='text':continue
        pts=' '.join(f'{x+e["x"]:.3f},{y+e["y"]:.3f}' for x,y in e['points'])
        fill=e['backgroundColor'] if e['backgroundColor']!='transparent' else 'none'
        out.append(f'<polyline points="{pts}" fill="{fill}" stroke="{e["strokeColor"]}" stroke-width="{e["strokeWidth"]}" opacity="{e["opacity"]/100}" stroke-linejoin="round" stroke-linecap="round"/>')
    return ''.join(out)+'</svg>'

for row,(variant,title,description) in enumerate(VARIANTS):
    items=[];cards=[]
    if variant=='cross':comparison.append(label('Cross-hatch',variant+'-heading',0,45,160,20))
    for col,name in enumerate(NAMES):
        group=f'square-{variant}-{name}';light,accent=PALETTE[name]
        frame=raw_line(FRAME,group+'-frame',group)
        frame.update(backgroundColor=light if variant=='solid' else '#ffffff',strokeWidth=2)
        elems=[frame]
        if variant=='cross':
            for i,points in enumerate(hatch_segments(FRAME)):
                hatch=raw_line(points,group+f'-hatch-{i}',group)
                hatch.update(strokeColor=accent,strokeWidth=.8,opacity=60)
                elems.append(hatch)
        for i,p in enumerate(geometry('single',name)):
            # Uniform icon scale; every resource occupies the same square footprint.
            scaled=[(60+(x-80)*.72,60+(y-78)*.72) for x,y in p]
            e=element(scaled,'single',group+f'-{i}',group);e['strokeWidth']=2.2;elems.append(e)
        t=label(name,group+'-label',0,130,120,19);t['groupIds']=[group];elems.append(t)
        item=dict(id=group,status='unpublished',created=1790006400000,name=f'{name} · {title}',elements=elems)
        items.append(item);dump(ROOT/'output'/f'{group}.excalidraw',scene(elems))
        (ROOT/'assets'/f'{group}.svg').write_text(svg_for(elems,variant,name))
        if variant=='cross':
            for e in copy.deepcopy(elems):e['x']+=190+col*185;comparison.append(e)
        cards.append(f'<a class="tile" href="{group}.excalidraw"><img src="../assets/{group}.svg" alt="{name} {title}"><strong>{name}</strong><span>{NAMES[name]}</span></a>')
    all_items[variant]=items
    dump(ROOT/'output'/f'{variant}.excalidrawlib',dict(type='excalidrawlib',version=2,source='https://excalidraw.com',libraryItems=items))
    if variant=='cross':sections.append(f'<section><div><h2>{title}</h2><p>{description}</p><a href="{variant}.excalidrawlib">Download library ↗</a></div><div class="tiles">'+''.join(cards)+'</div></section>')
dump(ROOT/'output'/'comparison.excalidraw',scene(comparison))
# DNS lookup is separate from the application request path.
architecture=[]
positions={'DNS':(0,0),'CLB':(230,230),'CVM':(460,230),'COS':(690,230)}
for name,(x,y) in positions.items():
    item=next(i for i in all_items['cross'] if i['name'].startswith(name+' '))
    for e in copy.deepcopy(item['elements']):
        e['x']+=x;e['y']+=y;architecture.append(e)
client=copy.deepcopy(all_items['cross'][0]['elements'][0]);client.update(id='client',x=0,y=230,backgroundColor='#f1f3f5',fillStyle='solid',groupIds=[])
architecture.extend([client,label('Client','client-label',0,273,120,20)])
connections=[([(60,220),(60,163)],'DNS query',True), ([(133,290),(215,290)],'HTTPS',False), ([(363,290),(445,290)],'request',False), ([(593,290),(675,290)],'objects',False)]
for i,(points,title,dashed) in enumerate(connections):
    e=raw_line(points,f'edge-{i}','');e.update(type='arrow',endArrowhead='arrow',groupIds=[],strokeStyle='dashed' if dashed else 'solid')
    architecture.append(e)
    x,y=points[0];architecture.append(label(title,f'edge-label-{i}',x-3 if not dashed else x+12,y-30 if not dashed else y-47,90,13))
dump(ROOT/'output'/'architecture.excalidraw',scene(architecture))
flow=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="-5 -5 850 395"><defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8" fill="none" stroke="#667085"/></marker></defs>']
for name,(x,y) in positions.items():
    item=next(i for i in all_items['cross'] if i['name'].startswith(name+' '))
    flow.append(f'<svg x="{x}" y="{y}" width="120" height="120">'+svg_for(item['elements'],'cross',name)+'</svg>')
    flow.append(f'<text x="{x+60}" y="{y+146}" text-anchor="middle" font-family="system-ui" font-size="17">{name}</text>')
flow.append('<rect x="0" y="230" width="120" height="120" fill="#f1f3f5" stroke="#202124" stroke-width="2"/><text x="60" y="296" text-anchor="middle" font-family="system-ui" font-size="20">Client</text>')
for points,title,dashed in connections:
    (x,y),(u,v)=points
    dash='stroke-dasharray="5 5"' if dashed else ''
    flow.append(f'<path d="M{x} {y}L{u} {v}" fill="none" stroke="#667085" stroke-width="1.5" {dash} marker-end="url(#a)"/>')
    flow.append(f'<text x="{x+8 if dashed else (x+u)/2}" y="{y-35 if dashed else y-13}" text-anchor="{"start" if dashed else "middle"}" font-family="system-ui" font-size="13" fill="#667085">{title}</text>')
flow.append('</svg>');(ROOT/'assets'/'architecture.svg').write_text(''.join(flow))
page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Hand-drawn Infrastructure Icons</title><style>*{box-sizing:border-box}body{margin:0;background:#faf9f6;color:#25282d;font:14px/1.6 system-ui}main{max-width:1160px;margin:auto;padding:30px}h1{font-size:28px;margin:8px 0}p{color:#737982}header{margin-bottom:25px}section{display:grid;grid-template-columns:200px 1fr;gap:24px;border-top:1px solid #e1e1dd;padding:24px 0}h2{font-size:19px;margin:0}a{color:#416883;font-size:13px}.tiles{display:grid;grid-template-columns:repeat(4,1fr);gap:24px}.tile{display:flex;align-items:center;flex-direction:column;text-decoration:none;color:inherit}.tile img{width:100%;max-width:128px;aspect-ratio:1}.tile strong{font-size:17px;margin-top:8px}.tile span{font-size:12px;color:#899099}.flow{border-top:1px solid #e1e1dd;padding-top:22px}.flow img{width:100%;max-width:850px;margin-top:20px}footer{color:#899099;font-size:12px;margin-top:22px}@media(max-width:800px){main{padding:22px}section{grid-template-columns:1fr}.tiles{gap:15px}} </style><main><header><small>ARCHITECTURE ICONS / CROSS-HATCH</small><h1>Straight lines. Human angles.</h1><p>Four infrastructure tiles with exact square frames and subtly irregular inner symbols. Straight edges stay straight; circles keep their natural curves.</p><a href="comparison.excalidraw">Download editable icon sheet ↗</a></header>'''+''.join(sections)+'''<div class="flow"><h2>In an architecture diagram</h2><p>The client resolves DNS, sends requests through CLB to CVM, and CVM accesses COS.</p><img src="../assets/architecture.svg" alt="DNS, CLB, CVM and COS architecture"><br><a href="architecture.excalidraw">Download editable diagram ↗</a></div><footer>Original infrastructure symbols inspired by your reference. All elements are editable. Preview and native files share the same straight-line geometry.</footer></main></html>'''
(ROOT/'output'/'index.html').write_text(page)
for variant,items in all_items.items():
    assert len(items)==4
    for item in items:
        f=item['elements'][0];assert f['type']=='line' and len(f['points'])==5 and f['width']==f['height']==120
        assert f['points']==[[0,0],[120,0],[120,120],[0,120],[0,0]]
        assert all(e['roughness']==0 for e in item['elements'])
        assert all(len(e['points'])==2 for e in item['elements'] if '-hatch-' in e['id'])
        assert len({e['id'] for e in item['elements']})==len(item['elements'])
        for e in item['elements']:assert all(math.isfinite(e[k]) for k in ('x','y','width','height'))
import re
links=re.findall(r'(?:href|src)="([^"]+)"',page)
assert all((ROOT/'output'/x).exists() for x in links)
assert not re.search(r'[\u4e00-\u9fff]',page)
for path in (ROOT/'output').glob('*.excalidraw*'):
    assert not re.search(r'[\u4e00-\u9fff]',path.read_text()), path
print(f'PASS: English-only page and files, 8 square icons, {len(links)} links')
