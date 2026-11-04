"""
setup.py: one-time setup for macOS / Windows / Linux.

  python3 scripts/setup.py      # macOS / Linux
  python  scripts\\setup.py     # Windows

What it does:
  1. Creates .venv in the skill folder and installs PyMuPDF into it
     (leaves the system Python alone, so Homebrew Python on macOS works too)
  2. Runs `npm run setup` (playwright + chromium, used by check_layout.mjs)
  3. Finds a browser for PDF export (render_pdf.py)
  4. Smoke test: builds, checks, and exports a two-slide test deck to generated/setup_check/
"""
import os, pathlib, shutil, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
WIN = os.name == "nt"
VENV_PY = ROOT / ".venv" / ("Scripts/python.exe" if WIN else "bin/python")


def run(cmd, **kw):
    print("$", " ".join(str(c) for c in cmd))
    subprocess.run([str(c) for c in cmd], check=True, cwd=ROOT, shell=WIN and cmd[0] in ("npm", "npx"), **kw)


def check(label, cmd, env=None):
    """Run a smoke-test step quietly; show its output only if it fails."""
    r = subprocess.run([str(c) for c in cmd], cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8")
    if r.returncode:
        print(r.stdout[-1500:], r.stderr[-1500:], sep="\n")
        sys.exit(f"Smoke test failed at: {label}")
    print(f"   ok  {label}")


def main():
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)  # keep our output in order with child processes
    if sys.version_info < (3, 9):
        sys.exit("Python 3.9 or later is required")
    if ROOT.name != "slide-co-create":
        print(f"Warning: the folder is named {ROOT.name}. SKILL.md expects ~/.claude/skills/slide-co-create")

    print("\n[1/4] Python environment (.venv + PyMuPDF)")
    if not VENV_PY.exists():
        try:
            run([sys.executable, "-m", "venv", ".venv"])
        except subprocess.CalledProcessError:
            shutil.rmtree(ROOT / ".venv", ignore_errors=True)  # a half-built .venv would skip creation next time and fail at pip
            sys.exit("Could not create a venv. On Debian / Ubuntu, run `sudo apt install python3-venv` and try again")
    run([VENV_PY, "-m", "pip", "install", "-q", "--disable-pip-version-check", "pymupdf"])

    print("\n[2/4] playwright + chromium")
    if not shutil.which("npm"):
        sys.exit("Node.js (npm) not found. Install it from https://nodejs.org and try again")
    run(["npm", "run", "setup"])
    launch = subprocess.run(["node", "-e", "require('playwright').chromium.launch().then(b => b.close())"],
                            cwd=ROOT, capture_output=True, text=True)
    if launch.returncode:
        print(launch.stderr[-800:])
        hint = " Run `sudo npx playwright install-deps chromium` to install the OS libraries, then" if sys.platform.startswith("linux") else ""
        sys.exit(f"chromium won't start.{hint} try again")

    print("\n[3/4] Browser for PDF export")
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    found = subprocess.run([VENV_PY, "-W", "ignore", "-c",
                            "import render_pdf, sys; print(render_pdf.browser())"],
                           cwd=ROOT / "scripts", env=env, capture_output=True, text=True)
    if found.returncode:
        sys.exit("No Edge / Chrome found. Install one, or set MBB_BROWSER to the browser's executable path")
    print("  ", found.stdout.strip())

    print("\n[4/4] Smoke test")
    out = ROOT / "generated" / "setup_check"
    out.mkdir(parents=True, exist_ok=True)
    html = out / "test.html"
    s = ROOT / "scripts"
    check("build deck (new_deck.py)", [VENV_PY, "-W", "ignore", s / "new_deck.py", "--parts", "b01,m05", "--title", "Setup check", "-o", html], env)
    check("rule check (check_deck.py)", [VENV_PY, "-W", "ignore", s / "check_deck.py", html], env)
    check("layout check (check_layout.mjs)", ["node", s / "check_layout.mjs", html])
    check("PDF export (render_pdf.py)", [VENV_PY, "-W", "ignore", s / "render_pdf.py", html], env)
    print(f"\nSetup complete. Test PDF: {out / 'test.pdf'}")


if __name__ == "__main__":
    main()
