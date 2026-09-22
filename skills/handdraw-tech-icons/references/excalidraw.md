# 原生素材与导入

仅在用户需要可编辑 Excalidraw 输出时读取。

1. 以已认可小样为基准，用 Excalidraw 原生线条、形状和文本重绘。排线、白色主体遮罩和轮廓分层；一个 icon 归为一组。字形和纸张颗粒可能有差异，要明确说明。
2. 导出 `.excalidraw` 和 `.excalidrawlib`。v2 库包含 `type: excalidrawlib`、`version: 2`、`libraryItems`；条目包含独立 ID、name、status、created 和 elements。实际格式以当前 Excalidraw schema 为准，不靠改文件后缀转换图片。
3. 验证 JSON、有限坐标、非负尺寸、条目/元素 ID 唯一性、分组和无意外嵌入位图。实际在 Excalidraw 加载检查四周留白、排线遮罩、文字和缩放；只做 HTTP 下载检查不能证明能导入。
4. 在已打开的 workspace 导入：右侧 Library → ⋯ → Open，选择 `.excalidrawlib`。这个入口加载素材，不替换当前画布。
5. 仅在用户明确要求时公开提交。官方图库通常要求至少三个相关条目、全英文名称/说明、每项独立可用且分组；提交前重新读取 [官方指引](https://github.com/excalidraw/excalidraw-libraries#create-your-own-library)。

## 一键链接的重要限制

当前 Excalidraw 的地址校验接受 `excalidraw.com` 及 `raw.githubusercontent.com/excalidraw/excalidraw-libraries`，不接受任意个人 fork。公开可下载、HTTP 200 和 CORS 正常不等于 Excalidraw 会接受安装链接。

官方 PR 提交后，若该提交 SHA 已能从官方仓库的 raw 地址读取，可使用：

```text
https://excalidraw.com/#addLibrary=<URL-encoded allowed raw library URL>
```

生成链接后必须在真实浏览器验证：出现导入确认 → 加入后素材显示正常。若当前版本不允许该地址，回退为下载文件、通过 Library → Open 导入；不要通过代理或绕开地址校验解决。

维护者审核和 Vercel 预览授权由上游控制。已提交 PR 不等于图库已收录，局部导入成功也不等于发布成功。实现参考：[library.ts 的地址校验](https://github.com/excalidraw/excalidraw/blob/master/packages/excalidraw/data/library.ts)。
