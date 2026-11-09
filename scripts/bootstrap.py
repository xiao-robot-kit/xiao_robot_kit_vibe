#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""XIAO Robot Kit workspace bootstrap.

Two jobs, no third-party dependencies (stdlib only):

  1. dependency doctor  -- is git / python / cmake / ESP-IDF / arduino-cli /
                           QEMU / esptool present, new enough, and where to
                           install it if not
  2. repo bootstrap     -- clone or fast-forward the sibling repos listed in
                           repos.json into ./repos/

Usage (run from the vibe repo root):

    python scripts/bootstrap.py            # doctor + repo status (read-only)
    python scripts/bootstrap.py --clone    # also clone missing repos
    python scripts/bootstrap.py --update   # also fast-forward existing repos
    python scripts/bootstrap.py --all      # clone + update
    python scripts/bootstrap.py --json     # machine-readable report
    python scripts/bootstrap.py --strict   # exit 1 if a required item is missing

Nothing outside this repo is written except ./repos/<repo>/ (clones).
`--update` never merges into a dirty working tree: it skips and says so.
"""

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OK, MISS, WARN = "ok", "missing", "warn"


# --------------------------------------------------------------------------- #
# tool detection
# --------------------------------------------------------------------------- #
def run(cmd, timeout=25):
    try:
        p = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
            encoding="utf-8", errors="replace",
            shell=(os.name == "nt" and cmd[0].lower().endswith((".bat", ".cmd"))),
        )
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except (OSError, subprocess.SubprocessError):
        return 127, ""


def first_version(text):
    m = re.search(r"(\d+)\.(\d+)(?:\.(\d+))?", text)
    if not m:
        return None
    return tuple(int(g) if g else 0 for g in m.groups())


def vstr(v):
    return ".".join(str(x) for x in v) if v else "?"


TOOLS = [
    # key, display name, probe command, minimum version, needed for, install hints
    dict(key="git", name="git", probe=["git", "--version"], minimum=(2, 20),
         need="克隆/更新所有仓库",
         hint={"windows": "winget install --id Git.Git -e",
               "darwin": "brew install git",
               "linux": "sudo apt install git  # 或 dnf/pacman"}),
    dict(key="python", name="python3", probe=None, minimum=(3, 9),
         need="bootstrap 脚本 + 上位机 + 工具链",
         hint={"windows": "winget install --id Python.Python.3.12 -e",
               "darwin": "brew install python@3.12",
               "linux": "sudo apt install python3 python3-venv"}),
    dict(key="cmake", name="cmake", probe=["cmake", "--version"], minimum=(3, 16),
         need="ESP-IDF 构建（IDF 自带一份，本机有更省事）",
         hint={"windows": "winget install --id Kitware.CMake -e",
               "darwin": "brew install cmake",
               "linux": "sudo apt install cmake"}),
    dict(key="ninja", name="ninja", probe=["ninja", "--version"], minimum=(1, 10),
         need="ESP-IDF 默认生成器", optional=True,
         hint={"windows": "winget install --id Ninja-build.Ninja -e",
               "darwin": "brew install ninja",
               "linux": "sudo apt install ninja-build"}),
    dict(key="idf", name="ESP-IDF (idf.py)", probe=["idf.py", "--version"], minimum=(6, 0),
         need="烧 ESP-IDF 固件 / 构建 28 个例程",
         hint={"any": "装 ESP-IDF v6.1 并激活环境：Windows 跑 esp-idf\\export.bat（每个新 shell 一次）\n"
                      "     macOS/Linux: . $HOME/esp/esp-idf/export.sh\n"
                      "     官方教程 https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/get-started/"}),
    dict(key="arduino_cli", name="arduino-cli", probe=["arduino-cli", "version"], minimum=(1, 0),
         need="Arduino 线路编译/上传（纯 Arduino IDE 用户可跳过）", optional=True,
         hint={"any": "winget install --id ArduinoSA.CLI -e  |  brew install arduino-cli  |  "
                      "curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh\n"
                      "     装完把 ESP32 核心加上：arduino-cli core install esp32:esp32"}),
    dict(key="esptool", name="esptool", probe=["esptool.py", "version"], minimum=(4, 0),
         need="手动擦写/读 flash（IDF 里已内置，独立装可选）", optional=True,
         hint={"any": "pip install esptool    （IDF 环境里已有，一般不用单独装）"}),
    dict(key="qemu", name="QEMU (esp32s3)", probe=["qemu-system-xtensa", "--version"], minimum=(8, 0),
         need="无实物板跑固件（xiao_robot_kit_qemu 线路）", optional=True,
         hint={"any": "用 xiao_robot_kit_qemu 的一键脚本装 Espressif 版 QEMU：\n"
                      "     powershell -ExecutionPolicy Bypass -File scripts/setup-qemu.ps1"}),
    dict(key="node", name="node", probe=["node", "--version"], minimum=(18, 0),
         need="上位机页面 JS 测试（只跑固件不需要）", optional=True,
         hint={"windows": "winget install --id OpenJS.NodeJS.LTS -e",
               "darwin": "brew install node",
               "linux": "sudo apt install nodejs"}),
]


def write_cmd_available():
    for exe in ("write.exe", "notepad.exe"):
        if shutil.which(exe):
            return exe
    return None


def check_python():
    v = sys.version_info
    return (OK if v >= (3, 9) else MISS), vstr((v.major, v.minor, v.micro))


def check_tool(t):
    if t["key"] == "python":
        return check_python()
    exe = shutil.which(t["probe"][0])
    if not exe:
        # ESP-IDF sets IDF_PATH even when idf.py is not on PATH in this shell
        if t["key"] == "idf" and os.environ.get("IDF_PATH"):
            return WARN, "IDF_PATH set, idf.py not on PATH (环境未激活)"
        return MISS, ""
    rc, out = run(t["probe"])
    v = first_version(out)
    if rc != 0 and not v:
        return WARN, "probe failed"
    if v and t.get("minimum") and v < t["minimum"]:
        return WARN, vstr(v) + " (<%s)" % vstr(t["minimum"])
    return OK, vstr(v)


def os_key():
    s = platform.system().lower()
    return "windows" if s.startswith("win") else ("darwin" if s == "darwin" else "linux")


# --------------------------------------------------------------------------- #
# repos
# --------------------------------------------------------------------------- #
def load_registry():
    with open(os.path.join(ROOT, "repos.json"), encoding="utf-8") as f:
        return json.load(f)


def git(path, *args, timeout=180):
    return run(["git", "-C", path] + list(args), timeout=timeout)


def repo_state(reg, entry):
    path = os.path.join(ROOT, reg["clone_root"], entry["name"])
    st = dict(name=entry["name"], path=path, layer=entry["layer"],
              required=bool(entry["required"]), why=entry["why"],
              present=os.path.isdir(os.path.join(path, ".git")),
              head="", dirty=False, behind="", state="")
    if not st["present"]:
        st["state"] = "absent"
        return st
    rc, out = git(path, "rev-parse", "--short", "HEAD")
    st["head"] = out.strip().splitlines()[0] if rc == 0 else "?"
    rc, out = git(path, "status", "--porcelain")
    st["dirty"] = rc == 0 and bool(out.strip())
    rc, out = git(path, "rev-list", "--count", "HEAD..origin/%s" % reg["branch"])
    st["behind"] = out.strip() if rc == 0 else ""
    st["state"] = "dirty" if st["dirty"] else (
        "behind %s" % st["behind"] if st["behind"] not in ("", "0") else "current")
    return st


def clone_repo(reg, entry):
    dest = os.path.join(ROOT, reg["clone_root"], entry["name"])
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    url = "https://github.com/%s/%s.git" % (reg["org"], entry["name"])
    rc, out = run(["git", "clone", "--depth", "1", "--branch", reg["branch"], url, dest], timeout=600)
    return (rc == 0), (out.strip().splitlines() or [""])[-1]


def update_repo(reg, entry, st):
    if st["dirty"]:
        return False, "本地有未提交改动，跳过（不覆盖你的工作）"
    path = st["path"]
    rc, out = git(path, "fetch", "--prune", "origin")
    if rc != 0:
        return False, "fetch 失败：" + (out.strip().splitlines() or [""])[-1]
    rc, out = git(path, "merge", "--ff-only", "origin/%s" % reg["branch"])
    return (rc == 0), ("已更新到最新" if rc == 0 else "ff-only 合并失败（本地有分叉提交？）")


# --------------------------------------------------------------------------- #
# report
# --------------------------------------------------------------------------- #
def fmt_row(cols, widths):
    return "  ".join(str(c).ljust(w) for c, w in zip(cols, widths)).rstrip()


def main():
    ap = argparse.ArgumentParser(description="XIAO Robot Kit workspace bootstrap")
    ap.add_argument("--clone", action="store_true", help="clone repos that are missing")
    ap.add_argument("--update", action="store_true", help="fast-forward repos that exist")
    ap.add_argument("--all", action="store_true", help="clone + update")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--strict", action="store_true", help="exit 1 when a required item is missing")
    ap.add_argument("--no-network", action="store_true", help="skip git fetch (offline doctor)")
    a = ap.parse_args()
    do_clone = a.clone or a.all
    do_update = (a.update or a.all) and not a.no_network

    reg = load_registry()
    tools = []
    for t in TOOLS:
        status, ver = check_tool(t)
        tools.append(dict(key=t["key"], name=t["name"], status=status, version=ver,
                          minimum=vstr(t.get("minimum")), need=t["need"],
                          optional=bool(t.get("optional")), hint=t["hint"]))
    repos = [repo_state(reg, e) for e in reg["repos"]]

    actions = []
    if do_clone:
        for e, st in zip(reg["repos"], repos):
            if not st["present"]:
                ok, msg = clone_repo(reg, e)
                actions.append(dict(repo=e["name"], action="clone", ok=ok, message=msg))
        repos = [repo_state(reg, e) for e in reg["repos"]]
    if do_update:
        for e, st in zip(reg["repos"], repos):
            if st["present"]:
                ok, msg = update_repo(reg, e, st)
                actions.append(dict(repo=e["name"], action="update", ok=ok, message=msg))
        repos = [repo_state(reg, e) for e in reg["repos"]]

    hard_missing = [t for t in tools if t["status"] == MISS and not t["optional"]]
    soft_missing = [t for t in tools if t["status"] == MISS and t["optional"]]
    repo_missing = [r for r in repos if not r["present"] and r["required"]]
    exit_code = 1 if (hard_missing and a.strict) else 0

    if a.json:
        print(json.dumps(dict(tools=tools, repos=repos, actions=actions,
                              required_missing=[t["key"] for t in hard_missing],
                              exit_code=exit_code), ensure_ascii=False, indent=2))
        return exit_code

    icon = {OK: "[ok]", MISS: "[--]", WARN: "[!!]"}
    print("\nXIAO Robot Kit — workspace bootstrap")
    print("repo root : %s" % ROOT)
    print("platform  : %s %s / python %s" % (platform.system(), platform.release(),
                                             vstr(sys.version_info[:3])))
    print("\n== 1. Dependency doctor ==")
    print(fmt_row(["", "tool", "version", "need"], [4, 18, 12, 22]))
    for t in tools:
        tag = "[opt]" if t["optional"] else ""
        print(fmt_row([icon[t["status"]], t["name"], t["version"] or "-", tag],
                      [4, 18, 12, 22]))
    if hard_missing or soft_missing:
        print("\n  缺的怎么装（只列缺失项）：")
        k = os_key()
        for t in hard_missing + soft_missing:
            how = t["hint"].get(k) or t["hint"].get("any") or t["hint"].get("linux", "")
            print("   - %-16s %s" % (t["name"], t["need"]))
            for line in str(how).splitlines():
                print("     %s" % line)
    else:
        print("\n  必需依赖齐全，可以直接构建。")

    print("\n== 2. Repo status (./%s) ==" % reg["clone_root"])
    print(fmt_row(["", "repo", "HEAD", "state", "layer"], [4, 24, 9, 12, 30]))
    for r in repos:
        mark = "[ok]" if r["present"] else ("[--]" if r["required"] else "[opt]")
        print(fmt_row([mark, r["name"], r["head"] or "-", r["state"], r["layer"]],
                      [4, 24, 9, 12, 30]))
    for r in repos:
        print("     %-24s %s" % (r["name"], r["why"]))
    if actions:
        print("\n== 3. Actions ==")
        for x in actions:
            print("   %-6s %-24s %s  %s" % (x["action"], x["repo"],
                                            "OK" if x["ok"] else "SKIP", x["message"]))
    if repo_missing:
        print("\n  必需仓库还缺 %d 个：%s" % (len(repo_missing),
                                          ", ".join(r["name"] for r in repo_missing)))
        print("  下一步：python scripts/bootstrap.py --clone")
    elif not hard_missing:
        print("\n  下一步：进 repos/xiao_robot_kit_idf/examples 挑一个工程，"
              "或读 repos/xiao_robot_kit_docs/README.md")
    print()
    return exit_code


if __name__ == "__main__":
    sys.exit(main())