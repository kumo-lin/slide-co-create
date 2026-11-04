"""
setup.py — 初回セットアップを1回で済ませる（Mac / Windows / Linux 共通）。

  python3 scripts/setup.py      # Mac / Linux
  python  scripts\\setup.py     # Windows

やること:
  1. スキル直下に .venv を作り、PyMuPDF を入れる（システムの Python は汚さない。Mac の Homebrew Python でも通る）
  2. npm run setup（playwright と chromium。check_layout.mjs 用）
  3. Edge / Chrome の有無を確認する（render_pdf.py 用）
  4. 動作確認として、2枚のテストデッキを生成・検査・PDF 化する（generated/ に出す）
"""
import os, pathlib, shutil, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
WIN = os.name == "nt"
VENV_PY = ROOT / ".venv" / ("Scripts/python.exe" if WIN else "bin/python")


def run(cmd, **kw):
    print("$", " ".join(str(c) for c in cmd))
    subprocess.run([str(c) for c in cmd], check=True, cwd=ROOT, shell=WIN and cmd[0] in ("npm", "npx"), **kw)


def main():
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)  # 子プロセスの出力と順番を揃える
    if sys.version_info < (3, 9):
        sys.exit("Python 3.9 以上が要る")
    if ROOT.name != "slide-co-create":
        print(f"注意: フォルダ名が {ROOT.name}。SKILL.md は ~/.claude/skills/slide-co-create を前提にしている")

    print("\n[1/4] Python 環境（.venv + PyMuPDF）")
    if not VENV_PY.exists():
        try:
            run([sys.executable, "-m", "venv", ".venv"])
        except subprocess.CalledProcessError:
            shutil.rmtree(ROOT / ".venv", ignore_errors=True)  # 作りかけを残すと次回 pip が無いまま進む
            sys.exit("venv を作れない。Debian / Ubuntu なら `sudo apt install python3-venv` を入れてから再実行する")
    run([VENV_PY, "-m", "pip", "install", "-q", "--disable-pip-version-check", "pymupdf"])

    print("\n[2/4] playwright + chromium")
    if not shutil.which("npm"):
        sys.exit("Node.js（npm）が見つからない。https://nodejs.org から入れてから再実行する")
    run(["npm", "run", "setup"])
    launch = subprocess.run(["node", "-e", "require('playwright').chromium.launch().then(b => b.close())"],
                            cwd=ROOT, capture_output=True, text=True)
    if launch.returncode:
        print(launch.stderr[-800:])
        hint = "`sudo npx playwright install-deps chromium` で OS のライブラリを入れてから" if sys.platform.startswith("linux") else ""
        sys.exit(f"chromium が起動しない。{hint}再実行する")

    print("\n[3/4] PDF 化用のブラウザ")
    env =dict(os.environ, PYTHONIOENCODING="utf-8")
    found = subprocess.run([VENV_PY, "-W", "ignore", "-c",
                            "import render_pdf, sys; print(render_pdf.browser())"],
                           cwd=ROOT / "scripts", env=env, capture_output=True, text=True)
    if found.returncode:
        sys.exit("Edge / Chrome が見つからない。入れるか、環境変数 MBB_BROWSER に実行ファイルのパスを入れる")
    print("  ", found.stdout.strip())

    print("\n[4/4] 動作確認")
    out = ROOT / "generated" / "setup_check"
    out.mkdir(parents=True, exist_ok=True)
    html = out / "test.html"
    s = ROOT / "scripts"
    run([VENV_PY, "-W", "ignore", s / "new_deck.py", "--parts", "b01,m05", "--title", "確認用", "-o", html], env=env)
    run([VENV_PY, "-W", "ignore", s / "check_deck.py", html], env=env)
    run(["node", s / "check_layout.mjs", html])
    run([VENV_PY, "-W", "ignore", s / "render_pdf.py", html], env=env)
    print(f"\nセットアップ完了。確認用 PDF: {out / 'test.pdf'}")


if __name__ == "__main__":
    main()
