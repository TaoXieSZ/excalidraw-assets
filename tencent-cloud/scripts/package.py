"""Create the portable download with assets, libraries, sources and scripts."""
from pathlib import Path
import zipfile
ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'output/tencent-cloud-handdrawn.zip'
paths=[ROOT/'README.md']
paths+=list((ROOT/'output').rglob('*.excalidraw'))+list((ROOT/'output').rglob('*.excalidrawlib'))+[ROOT/'output/index.html']
paths+=list((ROOT/'assets/all').glob('*.svg'))
paths += [ROOT/'assets/all-contact-sheet.png',ROOT/'assets/all-excalidraw-validation.png',ROOT/'assets/preview.png']
paths+=list((ROOT/'scripts').glob('*.py'))+list((ROOT/'scripts').glob('*.cjs'))
paths += [ROOT/'data'/name for name in ['official-icons.zip','source-catalog.json','build-report.json','render-report.json','verification.json','qa-sample.excalidraw']]
with zipfile.ZipFile(TARGET,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for path in sorted(set(paths)):z.write(path,Path('tencent-cloud')/path.relative_to(ROOT))
with zipfile.ZipFile(TARGET) as z:
    assert z.testzip() is None
    count=len(z.namelist())
print(f'ZIP PASS: {count} files, {TARGET.stat().st_size/1024**2:.1f} MiB')
