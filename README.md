# slide-co-create

ユーザーと議論しながら、経営会議に出せる品質のスライドを Claude Code で一緒に作るスキルです。いきなり資料を作らず、先に「誰に・何を決めてもらう資料か」を詰め、ストーリーライン、サンプル1〜2枚の順に合意してから全ページを組みます。出来上がりは HTML から書き出した PDF（16:9）で、編集できる PPTX が要るときは別スキル pdf-to-editable に渡します（このリポジトリには含まれていません）。

## 進め方

| 段階 | やること | ユーザーとの合意 |
|---|---|---|
| Gate A | 目的・読み手・決めてほしいこと・材料を確認する | 材料から埋まらない項目だけを1回で聞く |
| Gate B | ページごとのタイトル（結論と示唆を入れた文）、型、根拠をブループリントにする | 承認するまで HTML は作らない |
| Gate C | サンプル1〜2枚を組んで PNG で見せる | 承認してから残りを組む |
| 検査 | 規約の機械チェック、実レンダリング検査、別エージェントによるレビュー | FAIL 0 で納品 |

組むときの主な規約（正典は `references/slide-rules.md`）:

- 結論と示唆はタイトルに入れる（2行まで）。サブタイトルと、下部の「まとめ」帯は作らない。
- 文字サイズは、内容 12pt 以上、タイトル 24pt に固定。出典・フッター・ページ番号・右上タグは対象外。
- 1枚の中で、行動・効果・仕様のように粒度の違うものを同じ階層の箇条書きに並べない。

## セットアップ

必要なもの: [Claude Code](https://claude.com/claude-code)、Git、Python 3.9 以上、Node.js 18 以上。Mac / Windows / Linux で動く。PDF 化には Edge か Chrome を使い、どちらも無ければセットアップで入る chromium を使う。

1. スキルのフォルダに clone する。**フォルダ名は `slide-co-create` にする**（SKILL.md がこのパスを前提にしている）。

   Mac / Linux:
   ```bash
   git clone https://github.com/kumo-lin/slide-co-create.git ~/.claude/skills/slide-co-create
   ```
   Windows（PowerShell）:
   ```powershell
   git clone https://github.com/kumo-lin/slide-co-create.git "$HOME\.claude\skills\slide-co-create"
   ```

2. セットアップスクリプトを1回実行する。`.venv` に PyMuPDF を入れ、playwright と chromium を入れ、2枚のテストデッキを PDF まで通して確認する（数分かかる）。

   Mac / Linux:
   ```bash
   cd ~/.claude/skills/slide-co-create && python3 scripts/setup.py
   ```
   Windows（PowerShell）:
   ```powershell
   cd "$HOME\.claude\skills\slide-co-create"; python scripts\setup.py
   ```
   最後に「セットアップ完了」と出れば使える。確認用 PDF は `generated/setup_check/test.pdf`。

   Linux（Debian / Ubuntu）は先に `sudo apt install python3-venv` と、手順2の途中で案内が出たら `sudo npx playwright install-deps chromium` が要る。

3. Claude Code を開き直す（起動中のセッションには新しいスキルが読み込まれない）。

うまくいかないとき:

| 症状 | 対処 |
|---|---|
| `No module named 'fitz'` | `setup.py` が済んでいない。手順2を実行する |
| `externally-managed-environment`（Mac） | システムの pip に入れようとしている。`pip install` ではなく `setup.py` を使う（`.venv` に入れる） |
| `venv を作れない`（Linux） | `sudo apt install python3-venv` を入れて再実行する |
| `chromium が起動しない`（Linux） | `sudo npx playwright install-deps chromium` を実行して再実行する |
| `Edge / Chrome が見つからない` | `setup.py` を再実行する（chromium が入る）。特定のブラウザを使いたいときは、環境変数 `MBB_BROWSER` に実行ファイルのパスを入れる |
| `npm が見つからない` | Node.js を入れてから手順2をやり直す |
| PDF の文字が別の書体になる | スキルのフォルダを移動した。移動先で `new_deck.py` からデッキを作り直す（同梱フォントを絶対パスで参照しているため） |

## 更新

```bash
cd ~/.claude/skills/slide-co-create && git pull
```
`package.json` が変わったときだけ `setup.py` を再実行する。

## 使い方

Claude Code で「スライド作って」「デッキにして」「資料化して」と頼むと起動します。`/slide-co-create` で明示してもかまいません。成果物は `~/Documents/decks/<案件名>/` に置きます。

## 中身

| パス | 内容 |
|---|---|
| `SKILL.md` | Claude への指示書（スキル本体） |
| `references/slide-rules.md` | スライド規約の正典（約110項目）。食い違ったらこれが勝つ |
| `references/alignment-and-inputs.md` | Gate A/B の質問表とブループリントの書式 |
| `references/claim-evidence.md` | 主張・根拠・見せ方の対応、型の選び方 |
| `references/sample-review.md` | サンプルを差し戻す症状表 |
| `references/archetype-catalog.md` | 62型の一覧（型ID・使いどころ） |
| `references/content-review-prompt.md` | 別エージェントに渡すレビュー指示文 |
| `references/ai-smell-lexicon.md` | AI 臭い言い回しのリスト |
| `templates/freeform_parts_16x9.html` | 基本パーツ集（27型） |
| `templates/freeform_parts_more_16x9.html` | 追加パーツ集（35型） |
| `templates/skin.css` | 色・書体・表紙・フッターを決めるスキン（ロゴ・著作権表記なし） |
| `scripts/new_deck.py` | パーツ番号を並べてデッキの HTML を作る |
| `scripts/check_deck.py` | 規約の機械チェック（タイトル長、下部まとめ帯のクラス名、プレースホルダー残りなど） |
| `scripts/check_layout.mjs` | 実レンダリング検査（重なり、はみ出し、下部まとめ帯、文字サイズ） |
| `scripts/render_pdf.py` | HTML を PDF と目視用 PNG にする |
| `scripts/setup.py` | 初回セットアップ（`.venv`、playwright、動作確認） |
| `assets/` | 型カタログ PDF、PPTX 見本帳、同梱フォント（Noto Sans JP、OFL） |

## 自分の会社用に変える

- 色・書体・フッターの表記は `templates/skin.css` だけを直す。ロゴと著作権表記は入れていない。自社のものを入れるときは、`skin.css` 末尾のコメントにある例を有効にして値を直す。
- レビューで受けた指摘は、`references/slide-rules.md` に1行ずつ足していく（手順9で Claude が候補を出す）。チームで使う場合、各自のローカルで足した行は他の人に届かない。全員に効かせたいルールはブランチを切って Pull Request で出す。
- パーツ集の CSS を直したくなったら、まずデッキ側の `<style>` で直す。どのデッキでも効く直しなら `templates/` にも反映する。

## 出典とライセンス

carnot-tech/consulting-pptx-skill（MIT）をもとに、議論の前半（Gate A〜C）、スキン、文字サイズ検査、下部まとめ帯の検査を加えました。詳細は `NOTICE`、ライセンスは `LICENSE` を参照してください。
