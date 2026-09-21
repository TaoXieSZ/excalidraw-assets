# Hand-drawn square infrastructure icons

Four resources only: CVM, CLB, DNS and COS. Cross-hatching is the selected direction; expansion awaits visual approval.

[Preview](./output/index.html) · [Cross-hatch library](./output/cross.excalidrawlib) · [Editable icon sheet](./output/comparison.excalidraw) · [Architecture example](./output/architecture.excalidraw)

- Consistent 120 × 120 square frames, with English labels outside.
- Colored native cross-hatching, loose black outlines and simple symbols.
- Frame roughness 1.9; symbol roughness 1.5 with gentle, repeatable pen drift.
- Editable rectangle, line and text elements. No embedded images.
- Category colors are visual choices for this study, not official Tencent Cloud specifications.
- The alternate solid-fill files are retained, but the preview and architecture use cross-hatching.

![Native icon rendering](./assets/native-comparison.png)

![Native architecture rendering](./assets/native-architecture.png)

## Rebuild and validation

Run `python3 tencent-cloud/square-study/scripts/build.py`. The script uses only Python's standard library and does not change earlier studies or the full catalog.

Checks cover square dimensions, unique item element IDs, finite geometry, English-only HTML and exported Excalidraw files, and all 12 preview/download links. The four cross-hatched icons and architecture example were rendered in Excalidraw. SVG previews approximate native pen strokes and cross-hatching.
