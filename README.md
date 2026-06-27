# Pixel Perfect Website Clone Skill

这是一个给 Coding Agent / Codex 使用的网站一比一复刻 skill。它的目标不是“做一个相似的网站”，而是让 Agent 按固定证据链完成复刻：检查真实网站、搭建本地复刻、采集多断点截图、检查资源和动效、执行像素 diff，并在交付前使用独立检查 Agent 审查结果。

## 这个 skill 代表的目标

- 把网站复刻从“凭眼睛判断像不像”变成“用浏览器证据和像素差异证明是否一致”。
- 让 Agent 能够复刻网站、landing page、Webflow/Vite/Next/static bundle 页面，以及带视频、Canvas、WebGL、滚动动效的页面。
- 沉淀真实项目复刻中验证过的工作流：先采集原站证据，再本地实现，再用同一套脚本截图和 diff。
- 强制把视觉、排版、响应式断点、资源加载、控制台错误、动效状态、动态媒体帧差异都纳入验收。
- 在用户要求多 Agent 审查时，交付前必须生成检查 Agent，独立审查视觉、动效、排版、要素、证据和风险。

适用边界：这个 skill 适合学习、研究、授权内部还原和高保真前端重建。不要把他人网站的品牌、文案、图片、视频或专有素材包装成新的商业产品。

## 安装后能实现什么

安装这个 skill 后，Agent 会获得一套可复用的网站复刻方法、检查清单、采集脚本、像素 diff 脚本、环境检查脚本和检查 Agent 模板。

如果用户电脑已经具备 OpenCLI、Browser Harness、Chrome/Edge、Python/Pillow、Node/npm 等依赖，就可以直接按 skill 流程执行网站复刻。如果缺少依赖，先运行环境检查脚本，按报告补齐后再开始复刻。

这个仓库不会把 OpenCLI、Browser Harness、Chrome、Node、Python 或任何私有工作区里的大型工具一起打包。它会检查这些依赖是否存在，并说明如何安装。

## 涉及的工具

| 工具 | 作用 |
| --- | --- |
| OpenCLI | 作为统一 CLI 入口，读取页面状态或调用 Browser Harness。 |
| Browser Harness | 通过 CDP 控制真实 Chrome/Edge，完成打开页面、滚动、截图、读取 DOM/资源/控制台状态。 |
| Chrome / Edge | 真实浏览器渲染环境，用来避免只靠静态 HTML 判断页面。 |
| Python | 运行环境检查、截图差异分析等辅助脚本。 |
| Pillow | 用于逐像素比较 reference 和 replica 截图。 |
| Node.js / npm | 安装或运行 OpenCLI，也可用于 Vite/Next 等前端复刻项目。 |
| 本地 server | 用 Python `http.server`、Vite 或项目自带 server 托管本地复刻页面。 |
| GSAP / ScrollTrigger / Lenis / Three.js / Motion | 不是强制依赖；当目标站包含对应滚动、平滑滚动、WebGL 或复杂动效时优先采用。 |
| 多 Agent 检查 | 交付前用独立检查 Agent 审核视觉、动效、排版、资源、diff 证据和风险。 |

## 仓库内容

```text
pixel-perfect-website-clone/
  SKILL.md
  agents/
    openai.yaml
  references/
    checker-agent-prompt.md
    command-patterns.md
    dependencies.md
    pixel-fidelity-guidelines.md
  scripts/
    capture_site.py
    check_dependencies.py
    diff_images.py
```

- `SKILL.md`：主工作流。定义从环境检查、原站采集、本地构建、截图 diff 到检查 Agent 审查的完整流程。
- `agents/openai.yaml`：Codex UI 使用的 skill 名称、描述和默认提示词。
- `scripts/check_dependencies.py`：环境检查脚本，确认 OpenCLI、Browser Harness、Chrome、Python/Pillow、Node/npm、uv 和 skill 脚本是否可用。
- `scripts/capture_site.py`：通过 Browser Harness 采集页面信息、资源清单、控制台状态和多断点截图。
- `scripts/diff_images.py`：对 reference 和 replica 截图做像素 diff，输出 JSON 报告和差异图。
- `references/dependencies.md`：说明哪些内容已内置、哪些外部工具必须存在、缺失时如何下载或安装。
- `references/command-patterns.md`：常用 PowerShell 命令模板，包括 OpenCLI、Browser Harness、本地 server 和 diff 命令。
- `references/pixel-fidelity-guidelines.md`：内置的高保真复刻标准。
- `references/checker-agent-prompt.md`：检查 Agent 审查模板。

## 基本使用流程

1. 安装 skill 到 Codex 能发现的位置，例如：

   ```powershell
   git clone https://github.com/<owner>/pixel-perfect-website-clone-skill.git "$env:USERPROFILE\.codex\skills\pixel-perfect-website-clone"
   ```

   如果你使用独立工作区，也可以放在：

   ```powershell
   git clone https://github.com/<owner>/pixel-perfect-website-clone-skill.git "<workspace>\skills\pixel-perfect-website-clone"
   ```

2. 运行环境检查：

   ```powershell
   python "$env:USERPROFILE\.codex\skills\pixel-perfect-website-clone\scripts\check_dependencies.py"
   ```

3. 如果报告有 `missing`，先按 `references/dependencies.md` 补齐依赖。

4. 在 Codex 中提出任务，例如：

   ```text
   使用 $pixel-perfect-website-clone 复刻 https://example.com/，要求一比一，并在结束前使用检查 Agent 审查。
   ```

5. Agent 会按流程生成本地复刻目录、reference 截图、replica 截图、diff 报告、资源检查、动效检查和检查 Agent 结论。

## 验收标准

严格的一比一复刻至少要满足：

- Reference 和 replica 都覆盖 `1920x1000`、`1440x1000`、`1024x1000`、`768x1000`、`375x812`。
- 每个断点都有首屏截图和整页截图。
- 动态视频、Canvas、WebGL 需要做受控状态对比，例如冻结到同一视频帧。
- 受控 diff 尽量达到 `changedRatio=0`、`changedPixels=0`、`maxChannelDelta=0`。
- 页面高度、截图尺寸、字体、颜色、间距、图片、视频、sticky 元素和响应式行为一致。
- 控制台没有错误，本地必需资源返回 200，图片和视频非空。
- 检查 Agent 返回 `PASS` 后才可以最终交付。

## 重要说明

- 这个仓库是 skill，不是某个具体网站的复刻产物。
- 这个 skill 可以指导 Agent 下载或安装缺失工具，但必须先得到用户授权，并遵守当前机器的权限策略。
- 如果电脑没有 OpenCLI、Browser Harness 或浏览器控制能力，不能跳过环境检查直接宣称可以复刻。
- 如果 diff 仍有结构性差异，必须继续修复，不能只用“视觉接近”作为交付依据。
