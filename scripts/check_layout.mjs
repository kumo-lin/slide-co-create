#!/usr/bin/env node
// フォーマットの機械検査（レンダリングが必要な項目）— slide-rules §8 の目視QAを一部機械化
//   1. フッター（.foot / .footer）と本文要素の重なり
//   2. タイトル（h1 / .title）の右端はみ出し（nowrap + overflow:hidden の黙殺検出）
//   3. スライド外への要素はみ出し
//   4. 下部のまとめ帯（結論・示唆・So what を下部に置く形。slide-rules §4.8）
//   5. 文字サイズ（内容は 12pt 以上、タイトルは 24pt に固定。slide-rules §6・§2.1）
// 使い方: node scripts/check_layout.mjs deck.html   （playwright 必須: リポ直下で `npm run setup`。PLAYWRIGHT_MODULE_DIR でも解決可）
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

async function loadPlaywright() {
  const cands = [
    process.env.PLAYWRIGHT_MODULE_DIR,
    path.join(process.cwd(), "node_modules", "playwright"),
    path.join(path.dirname(fileURLToPath(import.meta.url)), "..", "node_modules", "playwright"),
  ].filter(Boolean);
  for (const c of cands) {
    try { return (await import(pathToFileURL(path.join(c, "index.mjs")).href)); } catch {}
    try { const m = await import(pathToFileURL(path.join(c, "index.js")).href); return m.default ?? m; } catch {}
  }
  return await import("playwright");
}

const file = process.argv[2];
if (!file) { console.error("usage: node check_layout.mjs deck.html"); process.exit(2); }

const pw = await loadPlaywright();
// Windows は既存の Edge を使う（playwright の chromium ダウンロード不要）
const browser = await pw.chromium.launch(process.platform === "win32" ? { channel: "msedge" } : {});
const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
// 印刷レイアウトで検査（ビューポート追従スケーラーの影響を受けない）
await page.emulateMedia({ media: "print" });
await page.goto(pathToFileURL(path.resolve(file)).href);
await page.waitForTimeout(300);

const issues = await page.evaluate(() => {
  const out = [];
  const slides = [...document.querySelectorAll("section.s, section.slide, .slide")];
  slides.forEach((s, i) => {
    const n = i + 1;
    const sr = s.getBoundingClientRect();
    const foot = s.querySelector(".foot, .footer, footer");
    const fr = foot ? foot.getBoundingClientRect() : null;
    const els = [...s.querySelectorAll("*")].filter((el) => {
      if (foot && (el === foot || foot.contains(el))) return false;
      const st = getComputedStyle(el);
      if (st.display === "none" || st.visibility === "hidden") return false;
      return (el.textContent || "").trim().length > 0 || el.tagName === "IMG";
    });
    // 4. 下部のまとめ帯（結論・示唆・So what を下部に置く形）— slide-rules §4.8
    //    許す下部要素は出典行・参照脚注・フッター・成果物チップ/ロゴの列だけ。
    //    スライド下部28%にある幅広のブロックが、塗り・罫線の帯になっているか、結論の書き出し語で始まっていたら FAIL。
    if (!s.classList.contains("cover")) {
      const zoneTop = sr.top + 0.72 * sr.height;
      const alpha = (c) => {
        const m = (c || "").match(/rgba?\(([^)]+)\)/);
        if (!m) return 0;
        const p = m[1].split(",").map((x) => parseFloat(x));
        return p.length === 4 ? p[3] : 1;
      };
      // .base は「柱＋土台」（パーツ19）の土台。図の要素であって結論ではない
      const exempt = (el) =>
        el.closest(".foot, .footer, footer, .src, .ref, .refnote, .fn, .footnote, .conf, .bar, .base, table, svg");
      const LEAD = /^\s*(だから|つまり|したがって|以上より|以上から|まとめ|結論|示唆|ポイント|So\s*what|Key\s*(message|takeaway)?|KEY|GOAL|POINT)/i;
      const bands = [];
      for (const el of s.querySelectorAll("*")) {
        if (exempt(el)) continue;
        const st = getComputedStyle(el);
        if (st.display === "none" || st.visibility === "hidden") continue;
        const text = (el.textContent || "").trim();
        if (text.length < 8) continue;
        const r = el.getBoundingClientRect();
        if (r.width < 0.5 * sr.width || r.top < zoneTop || r.height > 0.2 * sr.height) continue;
        // 成果物チップ・ロゴの列（短い要素が3つ以上並ぶ）は許可
        const kids = [...el.children];
        if (kids.length >= 3 && kids.every((k) => (k.textContent || "").trim().length < 30)) continue;
        const filled = alpha(st.backgroundColor) > 0;
        const ruled = ["Top", "Bottom", "Left"].some(
          (d) => parseFloat(st["border" + d + "Width"]) >= 1.5 && st["border" + d + "Style"] !== "none" && alpha(st["border" + d + "Color"]) > 0
        );
        const lead = LEAD.test(text);
        if (filled || ruled || lead) bands.push({ el, text, why: filled ? "塗りあり" : ruled ? "罫線あり" : "結論の書き出し語" });
      }
      // 入れ子は外側の1件にまとめる
      const outer = bands.filter((b) => !bands.some((o) => o !== b && o.el.contains(b.el)));
      for (const b of outer) {
        out.push(`p${n}: 下部にまとめ帯（${b.why}）: 「${b.text.slice(0, 30)}」→ 結論・示唆はタイトルへ（slide-rules §4.8）`);
      }
    }
    // 5. 文字サイズ（slide-rules §6）: 内容は 12pt 以上、タイトル（h1）は 24pt に固定。
    //    対象外: 表紙・裏表紙（.cover）、出典行・フッター・ページ番号・右上タグ・Confidential バッジ。
    //    図（SVG）の文字は、viewBox の拡大率をかけた実寸で測る。1pt = 4/3 px。
    if (!s.classList.contains("cover")) {
      const PT = 4 / 3, MIN_PT = 12, TITLE_PT = 24, EPS = 0.2;
      // CSS の zoom は getComputedStyle の font-size に反映されない（追加パーツ集は 1600px 幅を zoom:0.8 で縮めている）。
      // 祖先の zoom を掛けて、画面（PDF）上の実寸にそろえる。
      const zoomOf = (el) => {
        let z = 1;
        for (let a = el; a && a.nodeType === 1; a = a.parentElement) {
          const v = parseFloat(getComputedStyle(a).zoom);
          if (v && v !== 1) z *= v;
        }
        return z;
      };
      const h1 = s.querySelector("h1, .title");
      if (h1 && (h1.textContent || "").trim()) {
        const pt = (parseFloat(getComputedStyle(h1).fontSize) * zoomOf(h1)) / PT;
        if (Math.abs(pt - TITLE_PT) > EPS) {
          out.push(`p${n}: タイトルが ${pt.toFixed(1)}pt（${TITLE_PT}pt に固定。slide-rules §2.1）: 「${h1.textContent.trim().slice(0, 24)}」`);
        }
      }
      const SMALL_OK = ".foot, .footer, footer, .src, .ref, .refnote, .fn, .footnote, .conf, .bar, .kicker, .date, .pgno";
      const small = new Map();
      const walker = document.createTreeWalker(s, NodeFilter.SHOW_TEXT);
      for (let node = walker.nextNode(); node; node = walker.nextNode()) {
        const text = (node.nodeValue || "").trim();
        if (!text) continue;
        const el = node.parentElement;
        if (!el || el.closest(SMALL_OK) || el.closest("h1, .title") || el.closest("title, style, script")) continue;
        const st = getComputedStyle(el);
        if (st.display === "none" || st.visibility === "hidden") continue;
        let px = parseFloat(st.fontSize) * zoomOf(el);
        const svgEl = el.closest("text, tspan");
        if (svgEl && svgEl.getScreenCTM) {
          const m = svgEl.getScreenCTM();
          if (m) px = parseFloat(getComputedStyle(svgEl).fontSize) * Math.hypot(m.a, m.b);
        }
        const pt = px / PT;
        if (pt < MIN_PT - EPS) {
          const key = pt.toFixed(1);
          const cur = small.get(key) || { n: 0, sample: text.slice(0, 16) };
          cur.n += 1;
          small.set(key, cur);
        }
      }
      for (const [pt, v] of small) {
        out.push(`p${n}: 内容の文字が ${pt}pt（${MIN_PT}pt 以上）×${v.n}: 「${v.sample}」ほか（slide-rules §6）`);
      }
    }
    for (const el of els) {
      const r = el.getBoundingClientRect();
      if (r.height === 0 || r.width === 0) continue;
      // 葉要素だけ見る（コンテナの巨大rectでの誤検出を避ける）
      if (el.children.length > 0 && el.tagName !== "IMG") continue;
      if (fr && r.bottom > fr.top + 1 && r.top < fr.top) {
        out.push(`p${n}: フッターと本文が重なる: <${el.tagName.toLowerCase()}> 「${(el.textContent || "").trim().slice(0, 30)}」`);
      }
      if (r.right > sr.right + 1) {
        out.push(`p${n}: 右端はみ出し ${Math.round(r.right - sr.right)}px: <${el.tagName.toLowerCase()}> 「${(el.textContent || "").trim().slice(0, 30)}」`);
      }
      if (r.bottom > sr.bottom + 1) {
        out.push(`p${n}: 下端はみ出し ${Math.round(r.bottom - sr.bottom)}px: <${el.tagName.toLowerCase()}> 「${(el.textContent || "").trim().slice(0, 30)}」`);
      }
    }
  });
  return [...new Set(out)];
});

await browser.close();
if (issues.length) {
  for (const m of issues.slice(0, Number(process.env.LAYOUT_MAX_LINES ?? 20) || issues.length)) console.log("FAIL  " + m);  // LAYOUT_MAX_LINES=0 で全件表示
  console.log(`\n${issues.length} layout FAIL`);
  process.exit(1);
}
console.log("layout OK（フッター重なり・はみ出し・下部まとめ帯なし・文字サイズ 内容12pt以上／タイトル24pt）");
