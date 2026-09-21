"""Verify source coverage, native geometry, packaging and gallery links."""
import json
import math
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import zipfile
ROOT=Path(__file__).resolve().parents[1]

def load(path):return json.loads(path.read_text())

def validate_item(item):
    assert item['elements'],item['id']
    ids=[e['id'] for e in item['elements']]
    assert len(ids)==len(set(ids)),item['id']
    labels=[]
    for e in item['elements']:
        assert e['type'] in {'line','text'},e['id']
        assert e['width']>=0 and e['height']>=0,e['id']
        assert e['groupIds']==[item['id']],e['id']
        for key in ['x','y','width','height','strokeWidth']:
            assert math.isfinite(e[key]),(e['id'],key)
        if e['type']=='line':
            ps=e['points'];assert len(ps)>=2 and ps[0]==[0,0],e['id']
            assert all(math.isfinite(v) for p in ps for v in p),e['id']
            xs,ys=zip(*ps)
            assert abs(max(xs)-min(xs)-e['width'])<.003,e['id']
            assert abs(max(ys)-min(ys)-e['height'])<.003,e['id']
        else:
            assert e['fontFamily']==5,e['id']
            labels.append(e['originalText'])
    assert labels==[item['name']],item['id']

class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        for key,value in attrs:
            if key in {'href','src'} and not value.startswith(('https:','http:','#')):self.links.append(value)

def main():
    catalog=load(ROOT/'data/source-catalog.json')
    with zipfile.ZipFile(ROOT/'data/official-icons.zip') as z:sources={n for n in z.namelist() if n.endswith('.svg')}
    mapped=[s for r in catalog for s in r['source_paths']]
    assert len(mapped)==len(set(mapped))==896 and set(mapped)==sources
    assert len(catalog)==455 and len({r['slug'] for r in catalog})==455
    all_counts={};element_counts={};category_counts={}
    for variant in ['blue','mono']:
        whole=load(ROOT/f'output/all/tencent-cloud-all-{variant}.excalidrawlib')
        assert whole['type']=='excalidrawlib' and whole['version']==2
        items=whole['libraryItems'];assert len(items)==455
        assert len({i['id'] for i in items})==455
        all_ids=[e['id'] for i in items for e in i['elements']];assert len(all_ids)==len(set(all_ids))
        for i in items:validate_item(i)
        all_counts[variant]=len(items);element_counts[variant]=len(all_ids)
        packs=list((ROOT/'output/all/libraries').glob(f'*-{variant}.excalidrawlib'));assert len(packs)==13
        category_items=[i for p in packs for i in load(p)['libraryItems']]
        assert Counter(i['id'] for i in category_items)==Counter(i['id'] for i in items)
        category_counts[variant]=len(category_items)
    singles=list((ROOT/'output/all/icons').rglob('*.excalidraw'));assert len(singles)==455
    for r in catalog:
        path=ROOT/f'output/all/icons/{r["category_slug"]}/{r["slug"]}.excalidraw'
        data=load(path);assert data['type']=='excalidraw' and not data['files']
        assert [e['originalText'] for e in data['elements'] if e['type']=='text']==[r['name']]
    parser=Links();gallery=(ROOT/'output/index.html').read_text();parser.feed(gallery)
    missing=[x for x in parser.links if not (ROOT/'output'/x).exists()];assert not missing,missing
    assert 'cos' in gallery and 'cvm' in gallery
    report=load(ROOT/'data/build-report.json')
    assert report['total']==455 and report['min_geometry_iou']>=.95
    assert {s for i in report['items'] for s in i['source_paths']}==sources
    out=dict(status='passed',source_files=len(mapped),catalog_entries=len(catalog),
        library_entries=all_counts,native_elements=element_counts,category_entries=category_counts,
        single_files=len(singles),boards=len(list((ROOT/'output/all/boards').glob('*.excalidraw'))),
        checked_gallery_links=len(parser.links),missing_links=missing,
        min_geometry_iou=report['min_geometry_iou'],
        browser_checks=['COS/CVM alias search','category selection','464 native elements rendered in Excalidraw'],
        limitation='Full .excalidrawlib file import and full-library browser performance not tested')
    (ROOT/'data/verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
