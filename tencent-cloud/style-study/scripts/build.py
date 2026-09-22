"""Twelve editable, intentionally simplified infrastructure icon studies."""
import copy
import hashlib
import html
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
COLOR='#24466b'
STYLES=[('single','单线简笔','推荐从这里开始。去掉排线和双层边框，用少量线条保留物体特征。'),('sketch','随手速写','轮廓略歪、带一点透视，像白板上随手画的设备。'),('symbol','极简符号','只留最少的识别信息；缩小后依然清楚，更适合密集架构图。')]
NAMES={'CVM':'云服务器','CLB':'负载均衡','DNS':'域名解析','COS':'对象存储'}

def oval(cx,cy,rx,ry,start=0,end=2*math.pi,n=32):
    return [(cx+rx*math.cos(start+(end-start)*i/n),cy+ry*math.sin(start+(end-start)*i/n)) for i in range(n+1)]

def box(x,y,w,h):return [(x,y),(x+w,y),(x+w,y+h),(x,y+h),(x,y)]

def geometry(style,name):
    if style=='single':
        return {
          'CVM':[box(49,29,62,101),[(50,62),(110,62)],[(50,96),(110,96)],[(61,47),(68,47)],[(61,80),(68,80)],[(61,113),(68,113)]],
          'CLB':[box(22,65,27,27),[(49,79),(80,79)],[(80,41),(80,118)],[(80,41),(110,41)],[(80,118),(110,118)],box(111,29,25,25),box(111,106,25,25)],
          'DNS':[oval(80,78,49,49),oval(80,78,20,49),[(32,78),(128,78)]],
          'COS':[oval(80,39,43,13),[(37,39),(44,116)],[(123,39),(116,116)],oval(80,116,36,11,0,math.pi,16),box(68,68,24,24)]
        }[name]
    if style=='sketch':
        return {
          'CVM':[[(46,39),(100,32),(101,125),(48,132),(46,39)],[(46,39),(66,23),(120,18),(120,108),(101,125)],[(100,32),(120,18)],[(49,70),(100,64)],[(50,100),(99,94)],[(59,54),(67,53)],[(60,85),(68,84)],[(60,117),(68,116)]],
          'CLB':[oval(39,80,17,16),[(57,80),(82,80),(104,42)],[(82,80),(105,118)],[(96,47),(104,42),(105,53)],[(97,114),(105,118),(106,108)],oval(122,34,14,14),oval(122,126,14,14)],
          'DNS':[oval(77,76,46,48),[(77,29),(65,47),(61,76),(66,103),(81,124)],[(32,75),(61,79),(99,77),(124,72)],[(116,113),(129,128)],[(119,127),(130,129),(129,118)]],
          'COS':[[(37,44),(80,22),(126,46),(82,69),(37,44)],[(37,44),(41,106),(82,130),(122,106),(126,46)],[(82,69),(82,130)],[(59,34),(104,57),(103,78)]]
        }[name]
    return {
      'CVM':[box(42,43,76,67),[(55,61),(67,61)],[(55,92),(104,92)]],
      'CLB':[[(33,80),(76,80),(116,43)],[(76,80),(116,118)],[(103,43),(116,43),(116,56)],[(103,118),(116,118),(116,105)]],
      'DNS':[oval(80,78,45,45),[(80,33),(80,123)],[(35,78),(125,78)]],
      'COS':[oval(80,44,40,12),[(40,44),(47,113),(80,124),(113,113),(120,44)]]
    }[name]

def stroke(points,style,ident):
    # One gently wandering centerline, with no artificial echo or hatch fill.
    result=[]
    amount={'single':.38,'sketch':1.05,'symbol':.2}[style]
    for a,b in zip(points[:-1],points[1:]):
        n=max(1,int(math.dist(a,b)/15))
        for k in range(n):
            x=a[0]+(b[0]-a[0])*k/n;y=a[1]+(b[1]-a[1])*k/n
            result.append((x+amount*math.sin(y/24),y+amount*math.sin(x/27)))
    x,y=points[-1];result.append((x+amount*math.sin(y/24),y+amount*math.sin(x/27)))
    return result

def element(points,style,ident,group):
    p=stroke(points,style,ident);x,y=p[0]
    return dict(id=ident,type='line',x=x,y=y,width=max(a for a,b in p)-min(a for a,b in p),height=max(b for a,b in p)-min(b for a,b in p),angle=0,strokeColor=COLOR,backgroundColor='transparent',fillStyle='solid',strokeWidth=2,strokeStyle='solid',roughness={'single':.7,'sketch':1.1,'symbol':.5}[style],opacity=100,groupIds=[group],frameId=None,roundness=None,seed=int(hashlib.sha256(ident.encode()).hexdigest()[:7],16),version=1,versionNonce=1,isDeleted=False,boundElements=None,updated=1790006400000,link=None,locked=False,points=[[a-x,b-y] for a,b in p],startBinding=None,endBinding=None,startArrowhead=None,endArrowhead=None,lastCommittedPoint=None)

def label(text,ident,x,y,width=160,size=20):
    return dict(id=ident,type='text',x=x,y=y,width=width,height=size*1.25,angle=0,strokeColor=COLOR,backgroundColor='transparent',fillStyle='solid',strokeWidth=1,strokeStyle='solid',roughness=0,opacity=100,groupIds=[],frameId=None,roundness=None,seed=1,version=1,versionNonce=1,isDeleted=False,boundElements=None,updated=1790006400000,link=None,locked=False,fontSize=size,fontFamily=5,text=text,originalText=text,textAlign='center',verticalAlign='top',containerId=None,autoResize=False,lineHeight=1.25)

def dump(path,data):path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
def scene(elements):return dict(type='excalidraw',version=2,source='https://excalidraw.com',elements=elements,appState={'viewBackgroundColor':'#ffffff','gridSize':None},files={})

board=[];sections=[];report=[]
for row,(style,title,description) in enumerate(STYLES):
    items=[];cards=[]
    board.append(label(title,style+'-heading',0,row*235+70,190,22))
    for col,name in enumerate(NAMES):
        group=f'{style}-{name}';paths=geometry(style,name)
        elems=[element(p,style,f'{group}-{i}',group) for i,p in enumerate(paths)]
        text=label(name,group+'-label',0,149);text['groupIds']=[group];elems.append(text)
        items.append(dict(id=group,status='unpublished',created=1790006400000,name=f'{name} · {title}',elements=elems))
        dump(ROOT/'output'/f'{group}.excalidraw',scene(elems))
        for e in copy.deepcopy(elems):e['x']+=210+col*205;e['y']+=row*235;board.append(e)
        svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 145" fill="none" stroke="'+COLOR+'" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">']
        for i,p in enumerate(paths):svg.append('<polyline points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in stroke(p,style,str(i)))+'"/>')
        svg.append('</svg>');(ROOT/'assets'/f'{group}.svg').write_text(''.join(svg))
        cards.append(f'<a class="card" href="{group}.excalidraw"><img src="../assets/{group}.svg" alt="{title} {name}"><strong>{name}</strong><span>{NAMES[name]}</span><small>{len(paths)} 笔主体线条</small></a>')
        report.append({'style':style,'resource':name,'strokes':len(paths),'elements':len(elems)})
    dump(ROOT/'output'/f'{style}.excalidrawlib',dict(type='excalidrawlib',version=2,source='https://excalidraw.com',libraryItems=items))
    sections.append(f'<section><div class="intro"><div class="number">0{row+1}</div><h2>{title}</h2><p>{description}</p><a class="download" href="{style}.excalidrawlib">下载这组素材 ↗</a></div><div class="cards">'+''.join(cards)+'</div></section>')
dump(ROOT/'output'/'comparison.excalidraw',scene(board))
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>基础架构 · 简笔风格小样</title><style>*{box-sizing:border-box}body{margin:0;background:#faf9f6;color:#273b50;font:15px/1.6 system-ui,sans-serif}main{max-width:1250px;margin:0 auto;padding:38px 32px 60px}header{margin-bottom:32px}header p{color:#687582;max-width:800px}h1{font-size:30px;margin:8px 0;letter-spacing:-1px}.eyebrow{font-size:12px;letter-spacing:2px;color:#7b8790}section{display:grid;grid-template-columns:210px 1fr;gap:26px;padding:26px 0;border-top:1px solid #dddcd7}.number{color:#8c9a9e;font-size:12px}h2{font-size:21px;margin:5px 0}.intro p{font-size:13px;color:#687582;max-width:200px}.cards{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.card{background:white;border:1px solid #e8e7e2;border-radius:12px;display:flex;align-items:center;flex-direction:column;padding:13px 10px 17px;color:inherit;text-decoration:none}.card:hover{border-color:#718ca4;transform:translateY(-2px)}img{width:100%;max-width:160px;height:145px}strong{font-size:18px;margin-top:7px}span,small{font-size:12px;color:#81909a}small{margin-top:8px}.download,header a{color:#436a8c;font-size:13px}footer{margin-top:25px;color:#7a8790;font-size:13px}@media(max-width:850px){section{grid-template-columns:1fr}.intro p{max-width:none}.cards{gap:8px}main{padding:24px 15px}.card{padding:7px}img{height:115px}}@media(max-width:500px){.cards{grid-template-columns:repeat(2,1fr)}} </style><main><header><div class="eyebrow">STYLE STUDY / 01</div><h1>少画几笔，先把方向定下来。</h1><p>只看 CVM、CLB、DNS、COS。三组都去掉排线、阴影和复笔装饰，以简洁笔触表达资源。可以整组选，也可以挑不同组的图标混搭；确认后再扩展其他资源。</p><a href="comparison.excalidraw">下载可编辑对比画布 ↗</a></header>'''+''.join(sections)+'''<footer>这些是资源语义的简笔小样，不是官方 Logo 的描摹。点击单个图标下载；全部由 Excalidraw 原生线条与文字构成。网页为单线预览，Excalidraw 中会带轻微自然笔触。</footer></main></html>'''
(ROOT/'output'/'index.html').write_text(page)
# Focused checks: every item has only editable lines/text and no fill or hatch.
ids=[e['id'] for e in board];assert len(ids)==len(set(ids))
for e in board:
    assert e['type'] in ('line','text') and e['backgroundColor']=='transparent'
    assert all(math.isfinite(e[k]) for k in ('x','y','width','height'))
assert len(report)==12
print(json.dumps(report,ensure_ascii=False,indent=2))
