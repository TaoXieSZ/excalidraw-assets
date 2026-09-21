# 方形基础架构图标小样

参考用户提供的 AWS 图库截图：统一方形外框、分类底色、居中的黑色手绘符号。仅试画 CVM、CLB、DNS、COS，等待满意后再扩展。

[对比页面](./output/index.html) · [色块底素材库](./output/solid.excalidrawlib) · [交叉排线素材库](./output/cross.excalidrawlib) · [架构图示例](./output/architecture.excalidraw)

- 四种资源的图标区域均为 120 × 120，标签位于框外。
- 色块版延续大色块偏好，排线版更接近参考截图。
- 原生 rectangle 外框、line 符号和 text 标签，支持拆组、改色及编辑。
- 颜色仅用于这组小样的视觉分类，不代表腾讯云官方规范。

![两种底纹的实际渲染](./assets/native-comparison.png)

![在架构图中的实际渲染](./assets/native-architecture.png)

## 重建与验证

运行 `python3 tencent-cloud/square-study/scripts/build.py`。仅依赖 Python 标准库；产出位于 assets 和 output 子目录，不改已有全量图库。

已检查两套共 8 个图标的正方形尺寸、ID、坐标和 21 个预览/下载链接；两种底纹和架构图均已在 Excalidraw 中实际渲染。网页排线为近似预览，实际素材使用 Excalidraw 原生 cross-hatch 填充。
