import base64
import json
import os
import time


def _env(name, default=None, required=False):
    value = os.environ.get(name, default)
    if required and not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _parse_viewports(value):
    out = []
    for part in value.split(","):
        part = part.strip().lower()
        if not part:
            continue
        w, h = part.split("x", 1)
        out.append((int(w), int(h)))
    return out


ROOT = _env("CLONE_ROOT", required=True)
URL = _env("TARGET_URL", required=True)
CAPTURE_DIR = _env("CAPTURE_DIR", "reference")
PREFIX = _env("CAPTURE_PREFIX", "site")
VIEWPORTS = _parse_viewports(_env("VIEWPORTS", "1920x1000,1440x1000,1024x1000,768x1000,375x812"))
WAIT_SECONDS = float(_env("WAIT_SECONDS", "3"))
CONTROL_VIDEO = _env("CONTROL_VIDEO", "0").lower() in ("1", "true", "yes", "on")
LAZY_SCROLL = _env("LAZY_SCROLL", "1").lower() not in ("0", "false", "no", "off")

capture_root = os.path.join(ROOT, CAPTURE_DIR)
qa_root = os.path.join(ROOT, ".qa")
os.makedirs(capture_root, exist_ok=True)
os.makedirs(qa_root, exist_ok=True)


def write_json(name, payload):
    path = os.path.join(qa_root, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path


def freeze_videos():
    return js(
        """
(async () => {
  const videos = [...document.querySelectorAll('video')];
  await Promise.all(videos.map(v => new Promise(resolve => {
    let done = false;
    const finish = () => { if (done) return; done = true; resolve(); };
    try {
      v.pause();
      v.muted = true;
      v.addEventListener('seeked', finish, { once: true });
      v.currentTime = 0;
      setTimeout(finish, 1200);
    } catch (e) {
      finish();
    }
  })));
  return videos.map(v => ({
    src: v.currentSrc || v.src,
    currentTime: v.currentTime,
    readyState: v.readyState,
    paused: v.paused,
    width: v.videoWidth,
    height: v.videoHeight
  }));
})()
"""
    )


new_tab(URL)
wait_for_load()
time.sleep(WAIT_SECONDS)

dom_summary = js(
    """
(() => ({
  title: document.title,
  url: location.href,
  readyState: document.readyState,
  bodyHeight: Math.max(document.documentElement.scrollHeight, document.body.scrollHeight),
  bodyWidth: Math.max(document.documentElement.scrollWidth, document.body.scrollWidth),
  textSample: document.body.innerText.slice(0, 2000),
  anchors: [...document.querySelectorAll('a')].slice(0, 120).map(a => ({ text: a.innerText, href: a.href, className: a.className })),
  scripts: [...document.scripts].map(s => ({ src: s.src, type: s.type, inline: !s.src, length: s.textContent.length })),
  stylesheets: [...document.styleSheets].map(ss => {
    try { return { href: ss.href, rules: ss.cssRules ? ss.cssRules.length : null }; }
    catch (e) { return { href: ss.href, inaccessible: true }; }
  }),
  images: [...document.images].map(img => ({
    src: img.currentSrc || img.src,
    ok: img.complete && img.naturalWidth > 0,
    width: img.naturalWidth,
    height: img.naturalHeight,
    alt: img.alt,
    className: img.className
  })),
  videos: [...document.querySelectorAll('video')].map(v => ({
    src: v.currentSrc || v.src,
    poster: v.poster,
    readyState: v.readyState,
    autoplay: v.autoplay,
    loop: v.loop,
    muted: v.muted,
    paused: v.paused,
    currentTime: v.currentTime,
    width: v.videoWidth,
    height: v.videoHeight,
    className: v.className
  })),
  canvases: [...document.querySelectorAll('canvas')].map(c => ({
    width: c.width,
    height: c.height,
    clientWidth: c.clientWidth,
    clientHeight: c.clientHeight,
    className: c.className
  })),
  fonts: [...document.fonts].map(f => ({ family: f.family, weight: f.weight, style: f.style, status: f.status })),
  textNodes: [...document.querySelectorAll('h1,h2,h3,h4,p,span,a,button,li,div')].map(el => {
    const text = (el.innerText || '').trim();
    if (!text) return null;
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    return {
      tag: el.tagName,
      text: text.slice(0, 200),
      className: el.className,
      rect: { x: r.x, y: r.y, width: r.width, height: r.height },
      font: { family: cs.fontFamily, size: cs.fontSize, weight: cs.fontWeight, lineHeight: cs.lineHeight, color: cs.color }
    };
  }).filter(Boolean).slice(0, 400)
}))()
"""
)

write_json(f"dom-summary-{CAPTURE_DIR}.json", dom_summary)
with open(os.path.join(qa_root, f"rendered-{CAPTURE_DIR}.html"), "w", encoding="utf-8") as f:
    f.write(js("document.documentElement.outerHTML"))

if LAZY_SCROLL:
    height = int(dom_summary.get("bodyHeight") or 0)
    for y in range(0, height + 1000, 900):
        js(f"window.scrollTo(0,{y})")
        time.sleep(0.06)
    js("window.scrollTo(0,0)")
    time.sleep(0.8)

resources = js(
    """
(() => performance.getEntriesByType('resource').map(r => ({
  name: r.name,
  initiatorType: r.initiatorType,
  transferSize: r.transferSize,
  encodedBodySize: r.encodedBodySize,
  decodedBodySize: r.decodedBodySize,
  duration: r.duration
})))()
"""
)
write_json(f"resources-{CAPTURE_DIR}.json", resources)

shots = []
for w, h in VIEWPORTS:
    cdp("Emulation.setDeviceMetricsOverride", width=w, height=h, deviceScaleFactor=1, mobile=(w <= 480))
    cdp("Emulation.setVisibleSize", width=w, height=h)
    time.sleep(0.6)
    js("window.scrollTo(0,0)")
    time.sleep(0.6)
    video_state = freeze_videos() if CONTROL_VIDEO else None
    time.sleep(0.2)

    top = cdp("Page.captureScreenshot", format="png", fromSurface=True)
    top_path = os.path.join(capture_root, f"{PREFIX}-{w}x{h}-top.png")
    with open(top_path, "wb") as f:
        f.write(base64.b64decode(top["data"]))

    full = cdp("Page.captureScreenshot", format="png", fromSurface=True, captureBeyondViewport=True)
    full_path = os.path.join(capture_root, f"{PREFIX}-{w}x{h}-full.png")
    with open(full_path, "wb") as f:
        f.write(base64.b64decode(full["data"]))

    shots.append({
        "viewport": [w, h],
        "pageHeight": js("Math.max(document.documentElement.scrollHeight, document.body.scrollHeight)"),
        "video": video_state,
        "top": top_path,
        "full": full_path,
    })

report = {
    "url": URL,
    "captureDir": CAPTURE_DIR,
    "prefix": PREFIX,
    "controlledVideo": CONTROL_VIDEO,
    "pageInfo": page_info(),
    "shots": shots,
}
write_json(f"shots-{CAPTURE_DIR}.json", report)
print(json.dumps(report, ensure_ascii=False, indent=2))
