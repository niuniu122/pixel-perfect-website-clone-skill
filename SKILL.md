---
name: pixel-perfect-website-clone
description: Pixel-perfect website cloning workflow for inspecting a live site, building a local clone, and proving fidelity with OpenCLI, Browser Harness, screenshots, resource checks, animation checks, pixel diffs, and mandatory reviewer-agent QA. Use when Codex is asked to reproduce, mirror, clone, copy, or one-to-one rebuild a website or landing page, especially when the user demands exact visual/layout/motion parity across breakpoints.
---

# Pixel Perfect Website Clone

## Purpose

Create a local website clone that is proven against the live reference, not judged by eye. Treat screenshots, runtime checks, and pixel diffs as required deliverables.

## Non-Negotiables

- Use a real browser through OpenCLI and Browser Harness for inspection and verification.
- Work in an isolated clone folder unless the user explicitly wants to overwrite an existing app.
- Capture reference evidence before editing.
- Verify at least these breakpoints unless the user provides others: `1920x1000`, `1440x1000`, `1024x1000`, `768x1000`, `375x812`.
- Compare both `top` and `full` screenshots.
- For dynamic video/canvas/WebGL, collect live evidence and a controlled-state comparison. Freeze videos to the same `currentTime`, stabilize canvases/WebGL when possible, then diff.
- Do not output final success until an independent checker agent has reviewed the artifact when the user requires multi-agent QA.

## Workflow

### 0. Run Environment Check

Run the dependency checker before opening the target site or creating files:

```powershell
python "<skill-root>\scripts\check_dependencies.py"
```

On another machine, set the skill root explicitly:

```powershell
$env:PIXEL_CLONE_SKILL_ROOT="<path-to-skill>"
python "$env:PIXEL_CLONE_SKILL_ROOT\scripts\check_dependencies.py"
```

Continue only when required browser-control and diff dependencies are available. If the report has `missing`, read `references/dependencies.md`, explain the missing items, and install only after user approval.

### 1. Load Local Rules And Clone Standards

Read the workspace instructions, memory/tool index, and any site-building guide in the target workspace. Confirm available tools:

- OpenCLI entrypoint.
- Browser Harness entrypoint.
- Browser Harness fallback path when native executables are blocked.
- Local server/runtime already used by the workspace.

This skill bundles workflow scripts and references, not the full OpenCLI, Browser Harness, Chrome, Node, Python, or a private workspace toolchain. If tools are missing, read `references/dependencies.md`, run `scripts/check_dependencies.py`, and install only with user approval.

If a required browser-control or diff capability is missing and cannot be replaced safely, block and report the missing dependency before attempting the clone.

Always read `references/pixel-fidelity-guidelines.md` before planning the clone. If the active workspace has its own `AGENT.md`, read it too and let the stricter pixel-fidelity rule win.

See `references/command-patterns.md` for reusable PowerShell commands.
See `references/dependencies.md` for fresh-machine setup and download guidance.

### 2. Create The Evidence Layout

Create a fresh folder such as:

```text
<workspace>/<site-slug>-clone/
  index.html
  public/
  reference/
  replica/
  reference-controlled/
  replica-controlled/
  diff/
  .qa/
```

Keep old clone attempts separate. Do not mix evidence from different sites.

### 3. Inspect The Live Site

Use OpenCLI for high-level page state and Browser Harness for CDP-level evidence:

- Open the target URL.
- Save `page_info()`, page title, text sample, rendered HTML, resource manifest, images, videos, fonts, canvases, scripts, stylesheets, colors, and key text node metrics.
- Scroll through the page once to trigger lazy assets.
- Capture reference screenshots for all breakpoints.
- Record console messages if available.

Preferred capture helper:

```powershell
$env:TARGET_URL="https://example.com/"
$env:WORKSPACE_ROOT="<path-to-workspace>"
$env:PIXEL_CLONE_SKILL_ROOT="<path-to-skill>"
$env:CLONE_ROOT=(Join-Path $env:WORKSPACE_ROOT "example-clone")
$env:CAPTURE_DIR="reference"
$env:CAPTURE_PREFIX="example"
$browserHarness = if ($env:BROWSER_HARNESS_CMD) { $env:BROWSER_HARNESS_CMD } else { "browser-harness" }
Get-Content (Join-Path $env:PIXEL_CLONE_SKILL_ROOT "scripts\capture_site.py") |
  & $browserHarness
```

For controlled video-frame evidence:

```powershell
$env:CONTROL_VIDEO="1"
$env:CAPTURE_DIR="reference-controlled"
Get-Content (Join-Path $env:PIXEL_CLONE_SKILL_ROOT "scripts\capture_site.py") |
  & $browserHarness
```

### 4. Choose The Clone Strategy

Prefer the strategy with the least behavioral drift:

- **Mirror original runtime** when the goal is exact cloning and the site exposes static HTML/CSS/JS/assets. Preserve original DOM, script order, CSS, data attributes, and asset paths. Fix only path/base issues required for localhost.
- **Bundle/resource mirror** when the page is a Vite/Next/Webflow/static bundle. Copy or route the original hashed bundles and required assets, then make local entrypoints load the same files.
- **Manual rebuild** only when mirroring is impossible or not appropriate. Extract exact tokens, fonts, media, text, spacing, breakpoints, and animations first; build against screenshots, not memory.

Dynamic-commerce or form endpoints may remain inert if the user only requested visual fidelity. Preserve visible controls, quantities, totals, and disabled/enabled states unless the user asks for functional checkout.

### 5. Implement With Minimal Drift

Keep the original names, attributes, order, and media where possible. Fix local-only issues:

- Convert root-relative or relative asset paths that break on localhost.
- Copy small same-origin assets into `public/`.
- Keep CDN URLs when they are part of the original runtime and stable enough for the clone.
- Preserve Webflow/GSAP/Lenis/ScrollTrigger/Three.js initialization order.
- Avoid adding framework wrappers, global resets, dev overlays, or extra bundle preload scripts that change pixels.

### 6. Serve Locally

Start the smallest suitable local server:

- Static mirror: `python -m http.server <port> --bind 127.0.0.1`.
- Existing Vite app: use the repo's existing `npm run dev` or Vite binary.
- If a port is occupied, choose the next free port.

Record the local URL and process id in `.qa/`.

### 7. Verify Like A Release Gate

Run the same capture script against the local URL:

```powershell
$env:TARGET_URL="http://127.0.0.1:5180/"
$env:WORKSPACE_ROOT="<path-to-workspace>"
$env:PIXEL_CLONE_SKILL_ROOT="<path-to-skill>"
$env:CLONE_ROOT=(Join-Path $env:WORKSPACE_ROOT "example-clone")
$browserHarness = if ($env:BROWSER_HARNESS_CMD) { $env:BROWSER_HARNESS_CMD } else { "browser-harness" }
$env:CAPTURE_DIR="replica"
$env:CONTROL_VIDEO="0"
Get-Content (Join-Path $env:PIXEL_CLONE_SKILL_ROOT "scripts\capture_site.py") |
  & $browserHarness

$env:CAPTURE_DIR="replica-controlled"
$env:CONTROL_VIDEO="1"
Get-Content (Join-Path $env:PIXEL_CLONE_SKILL_ROOT "scripts\capture_site.py") |
  & $browserHarness
```

Then diff:

```powershell
python (Join-Path $env:PIXEL_CLONE_SKILL_ROOT "scripts\diff_images.py") `
  --root $env:CLONE_ROOT `
  --ref reference-controlled `
  --rep replica-controlled `
  --out diff `
  --prefix example `
  --threshold 16 `
  --strict
```

Acceptance target for a true one-to-one clone:

- Controlled diff: `changedRatio=0`, `changedPixels=0`, `maxChannelDelta=0`, no size mismatch.
- Live diff: differences must be explainable by dynamic content only, such as autoplay video frame timing.
- Resource checks: all local assets return 200; `badImages=[]`; no missing local public assets.
- Runtime checks: console errors are empty; expected libraries exist; videos/canvases/WebGL are nonblank; scroll animations change state as expected.
- Page heights and screenshot dimensions match at every breakpoint.

If controlled diff is not zero, fix before final delivery unless the user explicitly accepts documented dynamic variance.

### 8. Use A Checker Agent

When the user asks for multi-agent QA, spawn a checker agent after implementation and before final output. The checker must not modify files. It should review visual evidence, diff reports, runtime resources, console state, motion, layout, and breakpoints.

Use `references/checker-agent-prompt.md` as the prompt template. If the checker returns `BLOCK`, fix the blockers and rerun the relevant evidence. Only final when it returns `PASS`.

### 9. Final Delivery

Report only verified facts:

- Local URL.
- Main clone folder and entry file.
- Screenshot/diff evidence path.
- Controlled diff summary.
- Live diff explanation for dynamic media.
- Runtime/resource/motion check summary.
- Checker-agent result.

Avoid claiming "perfect" without evidence paths and metrics.

## Bundled Resources

- `scripts/capture_site.py`: run through Browser Harness to capture DOM/resource summaries and breakpoint screenshots.
- `scripts/diff_images.py`: run with normal Python to compare reference and replica PNGs and write overlay diffs plus JSON reports.
- `scripts/check_dependencies.py`: check whether OpenCLI, Browser Harness, Chrome, Python/Pillow, Node/npm, and this skill's scripts are present.
- `references/command-patterns.md`: OpenCLI, Browser Harness, server, and resource-check command templates.
- `references/dependencies.md`: what is bundled, what must be installed, and how to download missing dependencies.
- `references/pixel-fidelity-guidelines.md`: the portable pixel-perfect website cloning standards folded into this skill.
- `references/checker-agent-prompt.md`: reviewer-agent prompt template.
