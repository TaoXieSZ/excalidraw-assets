"""Build a complete editable library from the official package's rendered ink.

Uses preinstalled numpy, Pillow and contourpy. No embedded bitmap is delivered:
contours and clipped hatch segments become native Excalidraw line elements.
"""
import copy
import hashlib
import html
import json
import math
import re
import random
from collections import defaultdict
from pathlib import Path
import zipfile

import contourpy
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SIZE = 192
STAMP = 1790006400000
BLUE = '#0052d9'
INK = '#343a40'

def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(',', ':'))+'\n')

def simplify(points, tolerance):
    a = np.asarray(points, dtype=float)
    if len(a) < 3:
        return a.tolist()
    v = a[-1]-a[0]
    length = np.linalg.norm(v)
    distances = np.linalg.norm(a-a[0], axis=1) if length == 0 else np.abs(v[0]*(a[:,1]-a[0,1])-v[1]*(a[:,0]-a[0,0]))/length
    i = int(np.argmax(distances))
    if distances[i] <= tolerance:
        return [a[0].tolist(), a[-1].tolist()]
    return simplify(a[:i+1], tolerance)[:-1] + simplify(a[i:], tolerance)

def trace(mask):
    padded = np.pad(mask.astype(float), 1)
    paths = contourpy.contour_generator(z=padded).lines(.5)
    result=[]
    for path in paths:
        path -= 1
        mid = len(path)//2
        reduced = simplify(path[:mid+1], .6)[:-1] + simplify(path[mid:], .6)
        if len(reduced) >= 4:
            result.append(reduced)
    return result

def ink_mask(path):
    a = np.asarray(Image.open(path).convert('RGBA'), dtype=float)/255
    # White shape overlays and masks are cut-outs, not ink. The official
    # artwork is monochromatized intentionally; alpha alone loses white holes.
    return a[:,:,3] * (1-a[:,:,:3].min(axis=2)) > .12

def hatches(mask):
    height,width=mask.shape
    step=round(width*5.5/SIZE)
    segments=[]
    rng=random.Random(27)
    totals=[]; total=0
    while total<width+height:
        totals.append(total); total+=max(6,round(step*rng.uniform(.8,1.5)))
    for total in totals:
        points=[]
        for x in range(max(0,total-height+1),min(width,total+1)):
            y=total-x
            if mask[y,x]:
                points.append((x,y))
            elif points:
                if len(points)>3: segments.append([points[0],points[-1]])
                points=[]
        if len(points)>3:segments.append([points[0],points[-1]])
    return segments

def coverage(mask, contours):
    restored=np.zeros_like(mask,dtype=bool)
    for points in contours:
        im=Image.new('1',(mask.shape[1],mask.shape[0]))
        ImageDraw.Draw(im).polygon([(round(x),round(y)) for x,y in points],fill=1)
        restored ^= np.asarray(im,dtype=bool)
    union=np.count_nonzero(restored|mask)
    return np.count_nonzero(restored&mask)/union if union else 1

def sketch_points(points, hatch=False):
    """Slight, repeatable pen drift in display pixels; never alters source data."""
    a=np.asarray(points,dtype=float)*SIZE/512
    # Subdivide long straight edges so pen drift can gently bow them.
    sampled=[]
    for first,last in zip(a[:-1],a[1:]):
        count=max(1,int(np.linalg.norm(last-first)/7))
        sampled.extend(first+(last-first)*i/count for i in range(count))
    sampled.append(a[-1]);xy=np.asarray(sampled)
    x,y=xy[:,0].copy(),xy[:,1].copy()
    xy[:,0]+=1.65*np.sin(y/21+x/53)+.5*np.sin(y/7)
    xy[:,1]+=1.55*np.sin(x/25-y/61)+.45*np.sin(x/8)
    if hatch:
        phase=float(a[0].sum())
        t=np.linspace(0,1,len(xy))
        xy[:,0]+=1.25*np.sin(phase)*np.sin(t*math.pi)
        xy[:,1]+=1.0*np.cos(phase)*np.sin(t*math.pi)
    return xy

def pen_style(points,hatch):
    phase=sum(points[0])*.17
    return ((.7+.25*(1+math.sin(phase))/2, 55+int(15*(1+math.cos(phase))/2))
            if hatch else (1.65,100))

def native_line(points, ident, group, color, hatch=False):
    xy=sketch_points(points,hatch)
    lo=xy.min(axis=0); hi=xy.max(axis=0);first=xy[0]
    width,opacity=pen_style(points,hatch)
    return dict(id=ident,type='line',x=round(float(first[0]),3),y=round(float(first[1]),3),
        width=round(float(hi[0]-lo[0]),3),height=round(float(hi[1]-lo[1]),3),angle=0,
        strokeColor=color,backgroundColor='transparent',fillStyle='hachure',
        strokeWidth=width,strokeStyle='solid',roughness=1.5 if hatch else 1.9,
        opacity=opacity,groupIds=[group],frameId=None,roundness=None,
        seed=int(hashlib.sha256(ident.encode()).hexdigest()[:7],16),version=3,versionNonce=3,
        isDeleted=False,boundElements=None,updated=STAMP,link=None,locked=False,
        points=np.round(xy-first,3).tolist(),startBinding=None,endBinding=None,
        startArrowhead=None,endArrowhead=None,lastCommittedPoint=None)

def label(name, ident, group, color):
    # Separate from the icon geometry but included in the same draggable group.
    size=14 if len(name)>18 else 16
    lines=[]; current=''
    for token in re.findall(r'[A-Za-z0-9][A-Za-z0-9._+-]*|.', name):
        if current and len(current+token)>16:
            lines.append(current); current=''
        current+=token
    if current:lines.append(current)
    value='\n'.join(lines)
    return dict(id=ident,type='text',x=-34,y=208,width=260,height=size*1.25*len(lines),
        angle=0,strokeColor=color,backgroundColor='transparent',fillStyle='solid',
        strokeWidth=1,strokeStyle='solid',roughness=0,opacity=100,groupIds=[group],
        frameId=None,roundness=None,seed=1,version=1,versionNonce=1,isDeleted=False,
        boundElements=None,updated=STAMP,link=None,locked=False,fontSize=size,fontFamily=5,
        text=value,originalText=name,textAlign='center',verticalAlign='top',
        containerId=None,autoResize=False,lineHeight=1.25)

def scene(elements):
    return dict(type='excalidraw',version=2,source='https://excalidraw.com',elements=elements,
        appState=dict(viewBackgroundColor='#ffffff',gridSize=None),files={})

def library(items):
    return dict(type='excalidrawlib',version=2,source='https://excalidraw.com',libraryItems=items)

def preview_svg(contours, hatch_segments, name):
    out=['<svg xmlns="http://www.w3.org/2000/svg" width="240" height="272" viewBox="0 0 240 272">',
         '<g transform="translate(24 12)" fill="none" stroke-linecap="round" stroke-linejoin="round">']
    for paths,color,is_hatch in [(hatch_segments,'#6c9dde',True),(contours,BLUE,False)]:
        for p in paths:
            xy=sketch_points(p,is_hatch);width,opacity=pen_style(p,is_hatch)
            points=' '.join(f'{x:.3f},{y:.3f}' for x,y in xy)
            out.append(f'<polyline points="{points}" stroke="{color}" stroke-width="{width}" opacity="{opacity/100}"/>')
            if not is_hatch:
                # Faint second pen pass conveys the native renderer's double stroke.
                echo=xy.copy();echo[:,0]+=1.0*np.sin(xy[:,1]/13);echo[:,1]+=1.0*np.cos(xy[:,0]/17)
                points=' '.join(f'{x:.3f},{y:.3f}' for x,y in echo)
                out.append(f'<polyline points="{points}" stroke="{color}" stroke-width=".85" opacity=".45"/>')
    out.append('</g>')
    for i in range(0,len(name),16):
        out.append(f'<text x="120" y="{238+(i//16)*18}" text-anchor="middle" font-size="13" fill="#344054" font-family="system-ui,sans-serif">{html.escape(name[i:i+16])}</text>')
    return ''.join(out)+'</svg>'

def main():
    catalog=json.loads((ROOT/'data/source-catalog.json').read_text())
    if isinstance(catalog,dict):catalog=catalog.get('items',catalog.get('resources',[]))
    all_items={'blue':[],'mono':[]}; categories=defaultdict(lambda:{'blue':[],'mono':[]})
    report=[]; gallery=[]
    for index,entry in enumerate(catalog):
        source=entry['source_path']; name=entry['name']; slug=entry['slug']
        cat=entry['category_slug']; cat_name=entry['category']
        relative_source=source.replace('tencent_cloud_product_icons_zh/', 'zh/').replace('tencent_cloud_product_icons_en/', 'en/')
        rendered=ROOT/'data/rendered'/Path(relative_source).with_suffix('.png')
        mask=ink_mask(rendered)
        if not mask.any():raise ValueError(f'Blank source: {source}')
        contours=trace(mask); hatch_segments=hatches(mask)
        iou=coverage(mask,contours)
        if iou < .95:raise ValueError(f'Geometry mismatch {name}: {iou:.4f}')
        for variant,color in [('blue',BLUE),('mono',INK)]:
            group=f'tc-{slug}-{variant}'; elements=[]
            for number,points in enumerate(hatch_segments+contours):
                is_hatch=number<len(hatch_segments)
                elements.append(native_line(points,f'{group}-{number}',group,
                    ('#6c9dde' if variant=='blue' else '#8b929a') if is_hatch else color,is_hatch))
            elements.append(label(name,group+'-label',group,color))
            item=dict(id=group,status='unpublished',created=STAMP,name=name,elements=elements)
            all_items[variant].append(item); categories[cat][variant].append(item)
            if variant=='blue':
                dump(ROOT/f'output/all/icons/{cat}/{slug}.excalidraw',scene(elements))
        svg=ROOT/f'assets/all/{slug}.svg';svg.parent.mkdir(parents=True,exist_ok=True)
        svg.write_text(preview_svg(contours,hatch_segments,name))
        row=dict(name=name,slug=slug,category=cat_name,category_slug=cat,source_path=source,
            source_paths=entry.get('source_paths',[source]),aliases=entry.get('aliases',[]),
            contours=len(contours),hatch_segments=len(hatch_segments),geometry_iou=round(iou,5),
            native_elements=len(contours)+len(hatch_segments)+1)
        report.append(row);gallery.append({**entry,**row})
        if (index+1)%50==0:print(f'Generated {index+1}/{len(catalog)}',flush=True)
    for variant,items in all_items.items():
        dump(ROOT/f'output/all/tencent-cloud-all-{variant}.excalidrawlib',library(items))
    for cat,variants in categories.items():
        for variant,items in variants.items():
            dump(ROOT/f'output/all/libraries/{cat}-{variant}.excalidrawlib',library(items))
        # Boards are bounded to 24 icons for practical editing and inspection.
        items=variants['blue']
        for start in range(0,len(items),24):
            elements=[]
            for i,item in enumerate(items[start:start+24]):
                copied=copy.deepcopy(item['elements'])
                for e in copied:e['x']+=(i%6)*300+50;e['y']+=(i//6)*310+40
                elements.extend(copied)
            dump(ROOT/f'output/all/boards/{cat}-{start//24+1:02}.excalidraw',scene(elements))
    dump(ROOT/'data/build-report.json',dict(total=len(report),variants=2,
        native_elements=sum(r['native_elements'] for r in report)*2,
        min_geometry_iou=min(r['geometry_iou'] for r in report),items=report))
    build_gallery(gallery,categories)
    print(f'COMPLETE {len(report)} icons, {len(categories)} categories, 2 variants',flush=True)


def build_gallery(items,categories):
    category_names={r['category_slug']:r['category'] for r in items}
    tabs=''.join(f'<option value="{c}">{html.escape(category_names[c])}（{len(v["blue"])}）</option>' for c,v in categories.items())
    cards=[]
    for r in items:
        name=html.escape(r['name']);cat=r['category_slug'];slug=r['slug']
        search_terms=' '.join([r['name']]+r.get('aliases',[])).lower()
        cards.append(f'<a class="card" data-category="{cat}" data-name="{html.escape(search_terms,quote=True)}" href="all/icons/{cat}/{slug}.excalidraw" download><img loading="lazy" src="../assets/all/{slug}.svg" alt="{name}"/><span>{html.escape(r["category"])}</span></a>')
    links=''.join(f'<a href="all/libraries/{c}-blue.excalidrawlib" download>{html.escape(category_names[c])} · {len(v["blue"])}</a>' for c,v in categories.items())
    page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>腾讯云 · 手绘素材库</title><style>
*{box-sizing:border-box}body{margin:0;background:#f7f8fa;color:#172b4d;font:16px system-ui,-apple-system,sans-serif}main{max-width:1320px;margin:auto;padding:48px 28px}h1{font-size:36px;margin:12px 0}p{color:#62708a;line-height:1.7}.eyebrow{color:#0052d9;font-size:13px;letter-spacing:2px}a{color:#0052d9;text-decoration:none}.actions{display:flex;gap:12px;flex-wrap:wrap;margin:24px 0}.actions a{background:#0052d9;color:white;border-radius:8px;padding:12px 18px}.actions a+ a{background:white;color:#0052d9;border:1px solid #d5def0}.filters{display:flex;gap:12px;position:sticky;top:0;padding:14px 0;background:#f7f8fa;z-index:1}input,select{padding:12px;font:inherit;border:1px solid #d5def0;border-radius:8px;background:white}input{flex:1;min-width:0}select{max-width:40%}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(205px,1fr));gap:16px;margin-top:20px}.card{display:flex;align-items:center;flex-direction:column;background:white;border:1px solid #e1e7f0;border-radius:10px;padding:15px 5px 18px;transition:box-shadow .15s}.card:hover{box-shadow:0 4px 18px #173a6c15;border-color:#87aceb}.card img{width:100%;max-width:220px;aspect-ratio:240/272}.card span{font-size:11px;color:#8a96a9}.card[hidden]{display:none}details{padding:14px 0;border-bottom:1px solid #dce4ef}summary{cursor:pointer}.packs{display:flex;gap:10px 22px;flex-wrap:wrap;padding:20px 0;font-size:14px}footer{margin-top:40px;color:#758299;font-size:13px}
</style><main><div class="eyebrow">TENCENT CLOUD / EXCALIDRAW</div><h1>腾讯云手绘素材库</h1><p>__COUNT__ 个图标 · 蓝色 / 黑白两套 · 原生线条，可拆组编辑<br>根据官方资源包制作的非官方手绘改编；保留官方变体。点击图标下载单个可编辑文件。</p><div class="actions"><a href="all/tencent-cloud-all-blue.excalidrawlib" download>下载蓝色合集</a><a href="all/tencent-cloud-all-mono.excalidrawlib" download>下载黑白合集</a></div><details><summary>按类别下载，适合轻量导入</summary><div class="packs">__PACKS__</div></details><div class="filters"><input id="search" type="search" placeholder="搜索产品名称，如：对象存储、Redis、容器" aria-label="搜索产品"><select id="category" aria-label="筛选类别"><option value="">全部类别</option>__TABS__</select></div><p id="count">共 __COUNT__ 个图标</p><div class="grid">__CARDS__</div><footer>轮廓预览用于查找素材；Excalidraw 会依据每个元素的手绘参数渲染线条。<br>来源：<a href="https://cloud.tencent.com/act/event/icons">腾讯云官方架构图素材库</a> · <a href="../README.md">制作与验证说明</a></footer></main><script>
const search=document.querySelector('#search'), category=document.querySelector('#category'), cards=[...document.querySelectorAll('.card')];function filter(){let n=0;const q=search.value.trim().toLowerCase();for(const card of cards){const show=(!category.value||card.dataset.category===category.value)&&card.dataset.name.includes(q);card.hidden=!show;if(show)n++}document.querySelector('#count').textContent=`显示 ${n} / ${cards.length} 个图标`}search.addEventListener('input',filter);category.addEventListener('change',filter);
</script></html>'''
    for k,v in [('__COUNT__',str(len(items))),('__PACKS__',links),('__TABS__',tabs),('__CARDS__',''.join(cards))]:page=page.replace(k,v)
    (ROOT/'output/index.html').write_text(page)

if __name__=='__main__':main()
