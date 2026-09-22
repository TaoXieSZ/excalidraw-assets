# 手绘技术图标 Skill

[查看 SKILL.md](./handdraw-tech-icons/SKILL.md) · [下载完整 ZIP](./output/handdraw-tech-icons.zip) · [流程与复用包](../icon-workflow/README.md)

`handdraw-tech-icons` 将组件定义压缩成技术图标规格，再用固定模板与参考 PNG 调用绘图工具。它是普通 Agent Skills 目录，不依赖 Astra 或专有 Agent SDK。图像生成仍需要运行环境提供支持参考图的工具；弱模型等效画质尚未实测。

## 安装

下载 ZIP 并解压后，让你的 Agent 执行包内的 `scripts/install.py` 即可。或者从仓库根目录执行：

```bash
python3 skills/handdraw-tech-icons/scripts/install.py
```

安装器复制一份到 `~/.agents/skills/handdraw-tech-icons`，再建立 Codex 入口；若本机存在 Claude Code、Cursor 或 Gemini CLI 的用户目录，也建立相应技能入口。Codex 尊重当前 `CODEX_HOME`。不会覆盖已有不同版本，不会改变应用配置或添加绘图服务凭据。重复安装相同版本是幂等的。

| Agent | 默认个人入口 | 调用示例 |
|---|---|---|
| Codex | `~/.codex/skills/handdraw-tech-icons` | `$handdraw-tech-icons 根据这份组件定义画一个技术 icon` |
| Claude Code | `~/.claude/skills/handdraw-tech-icons` | `/handdraw-tech-icons 根据这份组件定义画一个技术 icon` |
| Cursor | `~/.cursor/skills/handdraw-tech-icons` | 在技能选择器中选择或直接说明使用 handdraw-tech-icons |
| Gemini CLI | `~/.gemini/skills/handdraw-tech-icons` | 说明使用 handdraw-tech-icons 并附上组件定义 |

安装文件不等于已经在每个应用中完成发现和绘图验证。让目标 Agent 在新会话读取技能；长会话需要按应用的刷新方式加载新技能。也可以直接指定 `SKILL.md` 路径，不依赖快捷命令是否已刷新。

个人技能路径依据：[Claude Code](https://code.claude.com/docs/en/skills)、[Cursor](https://prod.cursor.com/docs/skills)、[Gemini CLI](https://geminicli.com/docs/cli/skills/)。Skill 的标准 Markdown、Python 标准库脚本和 PNG 可一起拷贝到其他机器；Windows 可手动复制完整目录到目标应用的技能目录，安装器的目录链接方式主要面向当前 macOS/Linux 环境。

## 交付范围

- 内置已认可的铅笔排线风格参考图，避免每个 Agent 自由重选画风。
- 规格提取规则、图形词表、JSON 示例和确定性提示词编译器。
- 原生 Excalidraw 重绘、实际导入验证及一键安装链接的限制说明。
- 无图片工具时明确交付提示词，不冒充已经生成图片。
- 不因画图而自动公开上传公司资料。

ZIP 包只包含 skill 本体，解压即包含全部相对引用。`icon-workflow/` 保留这次抽取前的工作流和示例；后续执行规则以本 skill 为准。
