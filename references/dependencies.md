# Dependencies And Downloads

This skill does not bundle the full browser automation toolchain. It bundles the cloning workflow, capture/diff helper scripts, and QA templates.

## What Is Bundled

- `SKILL.md`: the clone workflow.
- `scripts/capture_site.py`: Browser Harness capture script.
- `scripts/diff_images.py`: screenshot diff script.
- `scripts/check_dependencies.py`: local dependency checker.
- `references/command-patterns.md`: command templates.
- `references/checker-agent-prompt.md`: reviewer-agent prompt.

## What Must Exist On The User's Machine

- Chrome or Edge with CDP/remote debugging available.
- Python 3.12+ for Browser Harness and helper scripts.
- Pillow for `diff_images.py`.
- Node.js and npm for OpenCLI.
- OpenCLI.
- Browser Harness.
- A local static or app server such as Python `http.server` or Vite.

If the user's request mentions a local workspace path, treat it as that user's convention, not a universal dependency. On another computer, copy this skill folder into that user's workspace or Codex skills directory and adjust paths in commands.

## Check First

Run:

```powershell
$env:PIXEL_CLONE_SKILL_ROOT="<path-to-skill>"
python "$env:PIXEL_CLONE_SKILL_ROOT\scripts\check_dependencies.py"
```

On another machine, set `PIXEL_CLONE_SKILL_ROOT` if the skill lives elsewhere:

```powershell
$env:PIXEL_CLONE_SKILL_ROOT="<path-to-skill>"
python "$env:PIXEL_CLONE_SKILL_ROOT\scripts\check_dependencies.py"
```

Optional environment variables for nonstandard installs:

- `OPENCLI_CMD`: full path to an OpenCLI executable or wrapper.
- `BROWSER_HARNESS_CMD`: full path to a Browser Harness executable or wrapper.
- `BROWSER_HARNESS_FALLBACK`: full path to a fallback Browser Harness launcher.
- `TOOLCHAIN_ROOT`: directory whose `bin/` folder contains local wrappers.
- `CHROME_PATH`: full path to Chrome or Edge when it is not in a standard location.

## Fresh Install Commands

Use these only with user approval and network access.

### OpenCLI

OpenCLI is distributed through npm:

```powershell
node --version
npm install -g @jackwener/opencli
opencli --help
```

If global npm installs are not allowed, install it in a project folder and call the local binary:

```powershell
npm install @jackwener/opencli
.\node_modules\.bin\opencli --help
```

### Browser Harness

Browser Harness is installed with `uv`:

```powershell
uv tool install --python 3.12 --upgrade --force browser-harness
browser-harness skill > "$env:USERPROFILE\.codex\skills\browser-harness\SKILL.md"
browser-harness --doctor
```

Verify browser control:

```powershell
@'
print(page_info())
'@ | browser-harness
```

If Chrome asks to allow remote debugging, the user must approve it.

### Pillow

```powershell
python -m pip install pillow
```

## Direct Download Policy

An agent may download/install missing tools only when all are true:

- The user asked for setup or approved installation.
- Network access is available.
- The environment policy permits downloads and installs.
- The install location is clear.
- The agent records installed tools in the local tool index after installation.

Do not silently install tools while claiming to only clone a website. If dependencies are missing, report the missing items and ask for permission or follow the user's existing tool policy.
