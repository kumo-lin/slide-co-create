"""
render_pdf.py — HTML デッキを Edge（Chromium）のヘッドレス印刷で PDF にし、目視用に各ページを PNG にする。
Edge / Chrome を自動で探す（見つからなければ環境変数 MBB_BROWSER にブラウザの実行ファイルのパスを入れる）。要 PyMuPDF（pip install pymupdf）。

  python scripts/render_pdf.py mydeck.html                # mydeck.pdf と mydeck_png/p01.png ...
  python scripts/render_pdf.py mydeck.html --pages 2,5    # PNG は指定ページだけ
  python scripts/render_pdf.py mydeck.html --no-png

PNG は Claude が Read で画像として確認するためのもの（既定 1280px 幅）。
"""
import argparse, os, pathlib, shutil, subprocess, sys

import fitz  # PyMuPDF

BROWSERS = [
    os.environ.get("MBB_BROWSER", ""),
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
]


def browser():
    for b in BROWSERS:
        if b and pathlib.Path(b).exists():
            return b
    # Edge / Chrome が無い環境でも、npm run setup が入れた playwright の chromium で印刷できる
    root = pathlib.Path(__file__).resolve().parent.parent
    try:
        p = subprocess.run(["node", "-e", "console.log(require('playwright').chromium.executablePath())"],
                           cwd=root, capture_output=True, text=True, timeout=30).stdout.strip()
        if p and pathlib.Path(p).exists():
            return p
    except (OSError, subprocess.TimeoutExpired):
        pass
    sys.exit("Edge / Chrome が見つからない。入れるか、MBB_BROWSER にパスを入れるか、npm run setup を実行する")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("--pages", help="PNG にするページ（1始まり、カンマ区切り）")
    ap.add_argument("--no-png", action="store_true")
    ap.add_argument("--width", type=int, default=1280)
    a = ap.parse_args()

    html = pathlib.Path(a.html).resolve()
    pdf = html.with_suffix(".pdf")
    tmp_profile = html.parent / ".render_profile"
    cmd = [browser(), "--headless", "--disable-gpu", "--no-pdf-header-footer",
           f"--user-data-dir={tmp_profile}", f"--print-to-pdf={pdf}", html.as_uri()]
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        cmd.insert(1, "--no-sandbox")  # root（Docker / CI）では Chromium のサンドボックスが起動しない
    subprocess.run(cmd, check=True, capture_output=True, timeout=180)
    shutil.rmtree(tmp_profile, ignore_errors=True)

    doc = fitz.open(pdf)
    print(f"wrote {pdf}: {doc.page_count} pages")
    if a.no_png:
        return
    want = {int(x) for x in a.pages.split(",")} if a.pages else set(range(1, doc.page_count + 1))
    out = html.parent / f"{html.stem}_png"
    out.mkdir(exist_ok=True)
    for i, page in enumerate(doc, 1):
        if i in want:
            zoom = a.width / page.rect.width
            page.get_pixmap(matrix=fitz.Matrix(zoom, zoom)).save(out / f"p{i:02d}.png")
    print(f"png: {out}")


if __name__ == "__main__":
    main()
