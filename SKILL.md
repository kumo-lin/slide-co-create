---
name: slide-co-create
description: ユーザーと議論しながら提案資料・報告資料・スライドデッキを経営会議品質で共同作成する。すり合わせ（Gate A）→ 論点整理（Core Question → Thesis → ストーリーライン）→ ブループリント承認（Gate B）→ サンプル承認（Gate C）と、各段階でユーザーと合意してから進める。HTML パーツ集（62型）で組み、機械チェックとフレッシュアイ・レビューを通して PDF で納める。「スライド作って」「デッキにして」「資料化して」「コンサル品質で」と言われたとき。編集可能な PPTX が要るときは、完成した PDF を pdf-to-editable に渡す。
---

# MBB スライド作成

**何を言うか**を先に決め、**どう見せ、どう検査するか**を carnot 由来の規約とパーツで固める。規約の正典は `references/slide-rules.md` で、他の文書と食い違ったらこちらが勝つ。

成果物は `~/Documents/decks/<案件名>/` に置く:

```
brief.md      Inputs for PPT Production とブループリント（Gate B で承認したもの）
deck.html     16:9・1 section = 1スライド
deck.pdf      納品物
deck_png/     目視用の各ページ PNG
```

コマンドは PowerShell で書いてある。Mac / Linux では bash / zsh の同じ意味のコマンドに読み替える。`$PY` はスキル直下の `.venv` の Python（PyMuPDF 入り）を使う:

```powershell
$SK = "$HOME/.claude/skills/slide-co-create"
$PY = "$SK/.venv/Scripts/python.exe"   # Mac / Linux は "$SK/.venv/bin/python"
$env:PYTHONIOENCODING = "utf-8"
$S  = "$SK/scripts"
```

`.venv` が無い、または `No module named 'fitz'` が出たら、セットアップが済んでいない。`python3 scripts/setup.py`（Windows は `python scripts\setup.py`）をスキルのフォルダで1回実行するようユーザーに伝える。fitz の FutureWarning は無害なので、気になれば `-W ignore` を付ける。

## 手順

### 1. Gate A: すり合わせ
`references/alignment-and-inputs.md` の Gate A の表に沿って、材料から埋まらない項目だけを1回で聞く。「おまかせ」なら既定値で埋めて表示し、そのまま進む。
**完了**: 全項目が回答済みか、既定値として明示済み。

### 2. Inputs for PPT Production
同ファイルの書式で材料を変換し、チャットに表示して `brief.md` に保存する。材料が一次資料なら先に読む。憶測で埋めない。
**完了**: 全ページに主張と proof object があり、根拠の無い主張はすべて「必要な根拠」か「未決事項」に載っている。本文の全ページで、示唆（So what）がタイトルに入る文になっている。

### 3. ブループリント → Gate B
`references/slide-rules.md` を全文読み、`references/claim-evidence.md` を読む。タイトル列（常体の主張文。示唆はタイトルに入れ、下部のまとめ帯・サブタイトルは作らない）・型番号・proof object・根拠の有無を並べ、alignment-and-inputs.md の Gate B ブロックをチャットに表示する。型は `references/archetype-catalog.md` か `assets/SlideCatalog_16x9.pdf` から、ストーリーに合わせて選ぶ。合う型がなければ自由に組む。
**完了**: ユーザーが承認した。承認までは HTML を作らない。

### 4. サンプル1〜2枚 → Gate C
Gate B で決めたサンプルのページだけを組む。

```powershell
& $PY "$S/new_deck.py" --parts b01,m05 --title "資料名" -o deck.html   # 社外向けは --confidential
& $PY "$S/check_deck.py" deck.html
& $PY "$S/render_pdf.py" deck.html
```

プレースホルダー（`Text N` / `ラベル N` / `YYYY` / `◯◯`）を実物に差し替え、グラフは表に流し込まずに描く。PNG を Read で見て、`references/sample-review.md` の症状表で自己チェックし、当てはまったら直してから見せる。ユーザーには PNG と、自己チェックで直した点を示す。
**完了**: ユーザーがサンプルを承認した。

### 5. 残りを組む
承認したサンプルと同じ組み方で全ページを作る（`new_deck.py` を全パーツで作り直し、サンプルの中身を移す）。1枚ごとに「この型のままでよいか」を疑い、表を2枚に割る・右カラムを帰結形に書き直すなどの調整をする。
**完了**: 全ページのプレースホルダーが実物に置き換わっている。

### 6. 機械チェック
```powershell
& $PY "$S/check_deck.py" deck.html
node "$S/check_layout.mjs" deck.html
```
**完了**: check_deck が FAIL 0（表紙・裏表紙・章扉の「タイトル空」WARN は許容）、check_layout が OK（下部まとめ帯と文字サイズ＝内容12pt以上・タイトル24ptの検出を含む）。check_deck が出すタイトル一覧を通し読みして、1本のストーリーになっている。`references/ai-smell-lexicon.md` の語をつぶしてある。

### 7. フレッシュアイ・レビュー
`references/content-review-prompt.md` の指示文と deck.html のパスだけを別のエージェント（Agent ツール）に渡す。作り方・意図・Gate の経緯は伝えない。返ってきた指摘を採否表（採用／不採用／保留＋理由）にし、採用分を直して手順6を再実行する。
**完了**: 採否表の採用分がすべて反映され、手順6が再び通っている。

### 8. PDF 化と全ページ目視
```powershell
& $PY "$S/render_pdf.py" deck.html
```
全 PNG を Read で見て、sample-review.md の症状表で1枚ずつ判定する。機械チェックは重なり・はみ出し・規約違反しか見ない。棒の潰れ・空の図・下半分の空き・泣き別れ・左右の下端不揃いは目視でしか分からない。
**完了**: 全ページが症状表のどれにも当てはまらない。deck.pdf をユーザーに渡し、編集用の PPTX が要るか聞く（要るなら pdf-to-editable）。

### 9. ルールの蓄積
このデッキでユーザーから受けた指摘のうち、次のデッキでも効くものを slide-rules.md の追記候補として1行ずつ示す（どの節の末尾に足すか付きで）。ユーザーが承認した行だけ、その節の末尾に追記する。節番号は変えない。追記候補には、発動条件・合否テスト・良い例と悪い例・譲れない制約・停止条件のどれかを必ず付ける。「プロっぽく」「きれいに」のような形容だけの行は、見える形の検査に書き直せないなら候補にしない。
**完了**: 候補を示し、承認分を追記した（候補が無ければ「無し」と伝える）。

## ファイル

| ファイル | 使うとき |
|---|---|
| `references/alignment-and-inputs.md` | 手順1〜3 |
| `references/claim-evidence.md` | 手順3・4（主張と根拠と見せ方の一致、型の選び方） |
| `references/sample-review.md` | 手順4・8（差し戻す症状） |
| `references/slide-rules.md` | 手順3で全文。以降は判断に迷ったとき |
| `references/archetype-catalog.md` / `assets/SlideCatalog_16x9.pdf` | 型を探すとき |
| `references/content-review-prompt.md` | 手順7 |
| `references/ai-smell-lexicon.md` | 手順6 |
| `templates/skin.css` | 色・書体・表紙・フッターの唯一の定義。ブランドを変えるときはここだけ直す（ロゴと著作権表記は無し。例は末尾のコメント） |
| `assets/SuperTemplate_62type.pptx` | PowerPoint で手組みしたいとき |

パーツの CSS を直したくなったら、まずデッキ側の `<style>` で直す。どのデッキでも効く直しなら templates/ にも反映する。

出典とライセンスは `NOTICE` を参照。
