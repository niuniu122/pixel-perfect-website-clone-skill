import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def command_version(command):
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=12,
            shell=False,
        )
        return {
            "exists": result.returncode == 0,
            "returncode": result.returncode,
            "output": result.stdout.strip().splitlines()[:5],
        }
    except Exception as exc:
        return {"exists": False, "error": str(exc)}


def path_status(path):
    if not path:
        return {"path": None, "exists": False, "isFile": False, "isDir": False}
    p = Path(path)
    return {"path": str(p), "exists": p.exists(), "isFile": p.is_file(), "isDir": p.is_dir()}


def first_existing(paths):
    for path in paths:
        if path and Path(path).exists():
            return str(Path(path))
    return None


def main():
    skill_root = Path(os.environ.get("PIXEL_CLONE_SKILL_ROOT", Path(__file__).resolve().parents[1]))
    toolchain_root = os.environ.get("TOOLCHAIN_ROOT")
    toolchain_bin = Path(toolchain_root) / "bin" if toolchain_root else None
    report = {"ok": True, "checks": {}, "missing": [], "recommendations": []}

    opencli_candidates = [
        os.environ.get("OPENCLI_CMD"),
        shutil.which("opencli"),
        shutil.which("opencli.cmd"),
        str(toolchain_bin / "opencli.ps1") if toolchain_bin else None,
    ]
    browser_harness_candidates = [
        os.environ.get("BROWSER_HARNESS_CMD"),
        shutil.which("browser-harness"),
        shutil.which("browser-harness.cmd"),
        str(toolchain_bin / "browser-harness.ps1") if toolchain_bin else None,
    ]
    browser_harness_fallback = (
        os.environ.get("BROWSER_HARNESS_FALLBACK")
        or (str(toolchain_bin / "browser-harness-python.cmd") if toolchain_bin else None)
    )
    chrome_candidates = [
        os.environ.get("CHROME_PATH"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        shutil.which("chrome"),
        shutil.which("chrome.exe"),
        shutil.which("msedge"),
        shutil.which("msedge.exe"),
    ]

    opencli_path = first_existing(opencli_candidates)
    browser_harness_path = first_existing(browser_harness_candidates)
    chrome_path = first_existing(chrome_candidates)

    report["checks"]["opencli"] = {"found": bool(opencli_path), "path": opencli_path}
    report["checks"]["browserHarness"] = {"found": bool(browser_harness_path), "path": browser_harness_path}
    report["checks"]["browserHarnessFallback"] = path_status(browser_harness_fallback)
    browser_harness_available = (
        report["checks"]["browserHarness"]["found"]
        or report["checks"]["browserHarnessFallback"]["exists"]
    )
    report["checks"]["chrome"] = {"found": bool(chrome_path), "path": chrome_path}
    report["checks"]["python"] = {"version": sys.version, "executable": sys.executable}
    report["checks"]["pillow"] = {"found": importlib.util.find_spec("PIL") is not None}
    node_cmd = shutil.which("node")
    npm_cmd = shutil.which("npm")
    uv_cmd = shutil.which("uv")
    report["checks"]["node"] = command_version([node_cmd, "--version"]) if node_cmd else {"exists": False}
    report["checks"]["npm"] = command_version([npm_cmd, "--version"]) if npm_cmd else {"exists": False}
    report["checks"]["uv"] = command_version([uv_cmd, "--version"]) if uv_cmd else {"exists": False}
    report["checks"]["skillScripts"] = {
        "capture": path_status(skill_root / "scripts" / "capture_site.py"),
        "diff": path_status(skill_root / "scripts" / "diff_images.py"),
    }

    required = {
        "OpenCLI": report["checks"]["opencli"]["found"],
        "Browser Harness": browser_harness_available,
        "Chrome or Edge": report["checks"]["chrome"]["found"],
        "Pillow": report["checks"]["pillow"]["found"],
        "capture_site.py": report["checks"]["skillScripts"]["capture"]["exists"],
        "diff_images.py": report["checks"]["skillScripts"]["diff"]["exists"],
    }
    for name, ok in required.items():
        if not ok:
            report["missing"].append(name)

    if not report["checks"]["node"].get("exists"):
        report["recommendations"].append("Install Node.js before installing OpenCLI from npm.")
    if not report["checks"]["npm"].get("exists"):
        report["recommendations"].append("Install npm or use a Node.js distribution that includes npm.")
    if not report["checks"]["uv"].get("exists"):
        report["recommendations"].append("Install uv before installing Browser Harness with uv tool install.")
    if not report["checks"]["pillow"]["found"]:
        report["recommendations"].append("Install Pillow for image diffing: python -m pip install pillow")
    if not report["checks"]["opencli"]["found"]:
        report["recommendations"].append("Install OpenCLI: npm install -g @jackwener/opencli")
    if not report["checks"]["browserHarness"]["found"]:
        report["recommendations"].append("Install Browser Harness: uv tool install --python 3.12 --upgrade --force browser-harness")
    if not report["checks"]["chrome"]["found"]:
        report["recommendations"].append("Install Chrome or Edge and enable remote debugging when Browser Harness asks.")

    report["ok"] = not report["missing"]
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
