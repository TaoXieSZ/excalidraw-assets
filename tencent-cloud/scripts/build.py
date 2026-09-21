"""Rebuild the complete library from the bundled official SVG archive."""
import json
from pathlib import Path
import subprocess
import zipfile
from catalog import build_catalog
from build_all import main as build_all

ROOT = Path(__file__).resolve().parents[1]

def main():
    archive=ROOT/'data/official-icons.zip'
    with zipfile.ZipFile(archive) as z:
        for name in z.namelist():
            if not name.endswith('.svg'):continue
            parts=Path(name).parts
            if len(parts)!=2 or parts[0] not in {'tencent_cloud_product_icons_zh','tencent_cloud_product_icons_en'}:
                raise ValueError(f'Unexpected archive member: {name}')
            language='zh' if parts[0].endswith('_zh') else 'en'
            target=ROOT/'data/official-svg'/language/parts[1]
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(z.read(name))
    catalog=build_catalog(str(archive))
    (ROOT/'data/source-catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
    subprocess.run(['node',str(ROOT/'scripts/render_sources.cjs')],check=True)
    build_all()

if __name__=='__main__':main()
