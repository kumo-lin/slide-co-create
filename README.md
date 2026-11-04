# slide-co-create

English | [中文](README.zh-CN.md)

A Claude Code skill for co-creating executive-ready slide decks through discussion. Instead of generating slides right away, it first pins down who the deck is for and what decision it should drive, then agrees on the storyline and one or two sample slides before building every page. The output is a 16:9 PDF exported from HTML. If you need an editable PPTX, hand the finished PDF to a separate skill such as pdf-to-editable (not included in this repository).

## How it works

| Stage | What happens | Agreement with you |
|---|---|---|
| Gate A | Confirm the purpose, audience, decision to be made, and source material | Asks once, only about what the material doesn't already answer |
| Gate B | Build a blueprint: per-page title (a sentence carrying the conclusion and its implication), layout type, and evidence | No HTML is built until you approve |
| Gate C | Build one or two sample slides and show them as PNGs | The rest is built only after you approve |
| Checks | Rule linting, real-render layout checks, and a review by a separate agent | Delivered with 0 FAIL |

Key layout rules (the canonical list is `references/slide-rules.md`):

- Put the conclusion and implication in the title (up to two lines). No subtitles and no "summary" band at the bottom.
- Body text is at least 12pt; titles are fixed at 24pt. Sources, footers, page numbers, and corner tags are exempt.
- Don't mix items of different granularity (actions, effects, specifications) in the same bullet level on one slide.

The skill's instructions and rule files are written in Japanese. Claude reads them either way, so you can work with it in any language.

## Setup

Requirements: [Claude Code](https://claude.com/claude-code), Git, Python 3.9+, Node.js 18+. Works on macOS, Windows, and Linux. PDF export uses Edge or Chrome; if neither is installed, it uses the chromium that setup installs.

1. Clone into your skills folder. **The folder must be named `slide-co-create`** (SKILL.md expects this path).

   macOS / Linux:
   ```bash
   git clone https://github.com/kumo-lin/slide-co-create.git ~/.claude/skills/slide-co-create
   ```
   Windows (PowerShell):
   ```powershell
   git clone https://github.com/kumo-lin/slide-co-create.git "$HOME\.claude\skills\slide-co-create"
   ```

2. Run the setup script once. It installs PyMuPDF into `.venv`, installs playwright and chromium, and builds a two-slide test deck all the way to PDF (takes a few minutes).

   macOS / Linux:
   ```bash
   cd ~/.claude/skills/slide-co-create && python3 scripts/setup.py
   ```
   Windows (PowerShell):
   ```powershell
   cd "$HOME\.claude\skills\slide-co-create"; python scripts\setup.py
   ```
   You're ready when it prints `セットアップ完了` ("setup complete"). The test PDF is at `generated/setup_check/test.pdf`.

   On Linux (Debian / Ubuntu), first run `sudo apt install python3-venv`, and if step 2 asks for it, `sudo npx playwright install-deps chromium`.

3. Restart Claude Code (running sessions don't pick up new skills).

Troubleshooting:

| Symptom | Fix |
|---|---|
| `No module named 'fitz'` | Setup hasn't run. Do step 2 |
| `externally-managed-environment` (macOS) | You're installing into the system pip. Use `setup.py` instead of `pip install` (it installs into `.venv`) |
| `venv を作れない` ("cannot create venv", Linux) | Install `python3-venv` with `sudo apt install python3-venv`, then rerun |
| `chromium が起動しない` ("chromium won't start", Linux) | Run `sudo npx playwright install-deps chromium`, then rerun |
| `Edge / Chrome が見つからない` ("Edge / Chrome not found") | Rerun `setup.py` (it installs chromium). To use a specific browser, set the `MBB_BROWSER` environment variable to its executable path |
| `npm` not found | Install Node.js, then redo step 2 |
| PDF text renders in a different font | The skill folder was moved. Regenerate the deck with `new_deck.py` in the new location (bundled fonts are referenced by absolute path) |

## Updating

```bash
cd ~/.claude/skills/slide-co-create && git pull
```
Rerun `setup.py` only when `package.json` has changed.

## Usage

Ask Claude Code to make slides, a deck, or a presentation (for example "スライド作って", "make a deck from this"), and the skill starts. You can also invoke it explicitly with `/slide-co-create`. Output goes to `~/Documents/decks/<project-name>/`.

## Contents

| Path | What it is |
|---|---|
| `SKILL.md` | Instructions for Claude (the skill itself) |
| `references/slide-rules.md` | Canonical slide rules (~110 items). Wins over any other file on conflict |
| `references/alignment-and-inputs.md` | Gate A/B question sheet and blueprint format |
| `references/claim-evidence.md` | Mapping of claims, evidence, and visuals; choosing a layout type |
| `references/sample-review.md` | Symptom checklist for rejecting samples |
| `references/archetype-catalog.md` | List of the 62 layout types (ID and when to use) |
| `references/content-review-prompt.md` | Review prompt handed to a separate agent |
| `references/ai-smell-lexicon.md` | List of AI-sounding phrases to avoid |
| `templates/freeform_parts_16x9.html` | Base parts library (27 types) |
| `templates/freeform_parts_more_16x9.html` | Extended parts library (35 types) |
| `templates/skin.css` | Skin for colors, fonts, cover, and footer (no logo or copyright line) |
| `scripts/new_deck.py` | Builds deck HTML from a list of part IDs |
| `scripts/check_deck.py` | Rule linter (title length, bottom-band class names, leftover placeholders, etc.) |
| `scripts/check_layout.mjs` | Real-render checks (overlap, overflow, bottom band, font sizes) |
| `scripts/render_pdf.py` | Exports HTML to PDF and per-page PNGs for review |
| `scripts/setup.py` | First-time setup (`.venv`, playwright, smoke test) |
| `assets/` | Layout catalog PDF, PPTX sample book, bundled fonts (Noto Sans JP, OFL) |

## Customizing for your company

- Change colors, fonts, and footer text in `templates/skin.css` only. No logo or copyright line is included; to add yours, enable the example in the comment at the end of `skin.css` and edit the values.
- Add review feedback to `references/slide-rules.md`, one line per rule (Claude proposes candidates in step 9). When a team shares this skill, rules added locally don't reach anyone else. Submit rules that should apply to everyone as a pull request from a branch.
- To change the parts library CSS, first override it in the deck's own `<style>`. If the fix should apply to every deck, also apply it in `templates/`.
