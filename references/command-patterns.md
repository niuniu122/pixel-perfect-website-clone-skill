# Command Patterns

Use these as PowerShell templates. Adjust paths to the current workspace.

## Browser Harness Fallback

```powershell
$env:TOOLCHAIN_ROOT='<path-to-toolchain>'
$env:BROWSER_HARNESS_EXE=(Resolve-Path (Join-Path $env:TOOLCHAIN_ROOT 'bin\browser-harness-python.cmd')).Path
```

## Open The Target With OpenCLI + Browser Harness

```powershell
bin\opencli.ps1 browser-harness open 'https://example.com/'
bin\opencli.ps1 browser-harness page-info

bin\opencli.ps1 browser clone-session open 'https://example.com/' --window background
bin\opencli.ps1 browser clone-session state
bin\opencli.ps1 browser clone-session console
```

## Capture Reference Screenshots

```powershell
$env:TARGET_URL='https://example.com/'
$env:WORKSPACE_ROOT='<path-to-workspace>'
$env:PIXEL_CLONE_SKILL_ROOT='<path-to-skill>'
$env:CLONE_ROOT=(Join-Path $env:WORKSPACE_ROOT 'example-clone')
$env:CAPTURE_DIR='reference'
$env:CAPTURE_PREFIX='example'
$env:CONTROL_VIDEO='0'
$browserHarness = if ($env:BROWSER_HARNESS_CMD) { $env:BROWSER_HARNESS_CMD } else { 'browser-harness' }
Get-Content (Join-Path $env:PIXEL_CLONE_SKILL_ROOT 'scripts\capture_site.py') |
  & $browserHarness
```

## Capture Controlled Screenshots

```powershell
$env:TARGET_URL='https://example.com/'
$env:WORKSPACE_ROOT='<path-to-workspace>'
$env:PIXEL_CLONE_SKILL_ROOT='<path-to-skill>'
$env:CLONE_ROOT=(Join-Path $env:WORKSPACE_ROOT 'example-clone')
$env:CAPTURE_DIR='reference-controlled'
$env:CAPTURE_PREFIX='example'
$env:CONTROL_VIDEO='1'
$browserHarness = if ($env:BROWSER_HARNESS_CMD) { $env:BROWSER_HARNESS_CMD } else { 'browser-harness' }
Get-Content (Join-Path $env:PIXEL_CLONE_SKILL_ROOT 'scripts\capture_site.py') |
  & $browserHarness
```

## Serve A Static Clone

```powershell
$root=(Join-Path '<path-to-workspace>' 'example-clone')
$port=5180
while ((Test-NetConnection -ComputerName 127.0.0.1 -Port $port -InformationLevel Quiet) -eq $true) { $port++ }
Start-Process -FilePath 'python' `
  -ArgumentList @('-m','http.server',"$port",'--bind','127.0.0.1') `
  -WorkingDirectory $root `
  -RedirectStandardOutput (Join-Path $root '.qa\server.stdout.log') `
  -RedirectStandardError (Join-Path $root '.qa\server.stderr.log') `
  -WindowStyle Hidden `
  -PassThru
```

## Capture Replica Screenshots

```powershell
$env:TARGET_URL='http://127.0.0.1:5180/'
$env:WORKSPACE_ROOT='<path-to-workspace>'
$env:PIXEL_CLONE_SKILL_ROOT='<path-to-skill>'
$env:CLONE_ROOT=(Join-Path $env:WORKSPACE_ROOT 'example-clone')
$env:CAPTURE_DIR='replica'
$env:CAPTURE_PREFIX='example'
$env:CONTROL_VIDEO='0'
$browserHarness = if ($env:BROWSER_HARNESS_CMD) { $env:BROWSER_HARNESS_CMD } else { 'browser-harness' }
Get-Content (Join-Path $env:PIXEL_CLONE_SKILL_ROOT 'scripts\capture_site.py') |
  & $browserHarness

$env:CAPTURE_DIR='replica-controlled'
$env:CONTROL_VIDEO='1'
Get-Content (Join-Path $env:PIXEL_CLONE_SKILL_ROOT 'scripts\capture_site.py') |
  & $browserHarness
```

## Pixel Diff

```powershell
$env:PIXEL_CLONE_SKILL_ROOT='<path-to-skill>'
$env:CLONE_ROOT=(Join-Path '<path-to-workspace>' 'example-clone')
python (Join-Path $env:PIXEL_CLONE_SKILL_ROOT 'scripts\diff_images.py') `
  --root $env:CLONE_ROOT `
  --ref reference-controlled `
  --rep replica-controlled `
  --out diff `
  --prefix example `
  --threshold 16 `
  --strict
```

## Resource Checks

```powershell
$urls = @(
  'http://127.0.0.1:5180/',
  'http://127.0.0.1:5180/public/example.png'
)
foreach ($u in $urls) {
  $r = Invoke-WebRequest -Uri $u -Method Head -UseBasicParsing
  [pscustomobject]@{
    url=$u
    status=$r.StatusCode
    length=$r.Headers['Content-Length']
    type=$r.Headers['Content-Type']
  }
}
```

## Runtime And Motion Checks

Run this through Browser Harness after opening the local page:

```python
import json, time
initial = js("""
(() => {
  const v = document.querySelector('video');
  return {
    title: document.title,
    url: location.href,
    height: document.documentElement.scrollHeight,
    badImages: [...document.images].filter(i => !(i.complete && i.naturalWidth > 0)).map(i => i.src),
    video: v ? {paused:v.paused,currentTime:v.currentTime,autoplay:v.autoplay,loop:v.loop,muted:v.muted,readyState:v.readyState} : null,
    hasGSAP: !!window.gsap,
    scrollTriggers: window.ScrollTrigger ? ScrollTrigger.getAll().length : null,
    hasLenis: document.documentElement.classList.contains('lenis')
  };
})()
""")
time.sleep(1)
after = js("(() => { const v=document.querySelector('video'); return v ? {paused:v.paused,currentTime:v.currentTime} : null; })()")
print(json.dumps({"initial": initial, "after": after}, ensure_ascii=False, indent=2))
```
