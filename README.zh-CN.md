# slide-co-create

[English](README.md) | 中文

一个 Claude Code 技能：和你边讨论边做出能上经营会议的幻灯片。它不会一上来就生成页面，而是先确认这份资料给谁看、要对方做什么决定，再依次对齐故事线和一两页样稿，最后才做全部页面。成品是由 HTML 导出的 16:9 PDF。需要可编辑的 PPTX 时，把完成的 PDF 交给 pdf-to-editable 等其他技能处理（本仓库不包含）。

## 流程

| 阶段 | 做什么 | 和你确认的方式 |
|---|---|---|
| Gate A | 确认目的、读者、需要对方做的决定、手头材料 | 只问材料里找不到答案的项，一次问完 |
| Gate B | 做成蓝图：每页标题（写进结论和启示的一句话）、版式、依据 | 你批准之前不生成 HTML |
| Gate C | 先做一两页样稿，以 PNG 给你看 | 你批准后才做其余页面 |
| 检查 | 规则自动检查、实际渲染检查、另一个 agent 的评审 | 0 FAIL 才交付 |

主要的排版规则（以 `references/slide-rules.md` 为准）：

- 结论和启示写进标题（最多两行）。不做副标题，也不做底部的「总结」色带。
- 正文字号不小于 12pt，标题固定 24pt。出处、页脚、页码、右上角标签不受此限。
- 同一页里，不把粒度不同的内容（行动、效果、规格）放在同一层级的要点里。

技能的指令和规则文件是日语写的。Claude 照样能读懂，你用中文或其他语言和它沟通都可以。

## 安装

需要：[Claude Code](https://claude.com/claude-code)、Git、Python 3.9 以上、Node.js 18 以上。支持 macOS、Windows、Linux。导出 PDF 用 Edge 或 Chrome，两者都没有时，使用安装脚本装好的 chromium。

1. 克隆到技能目录。**文件夹名必须是 `slide-co-create`**（SKILL.md 按这个路径写死）。

   macOS / Linux：
   ```bash
   git clone https://github.com/kumo-lin/slide-co-create.git ~/.claude/skills/slide-co-create
   ```
   Windows（PowerShell）：
   ```powershell
   git clone https://github.com/kumo-lin/slide-co-create.git "$HOME\.claude\skills\slide-co-create"
   ```

2. 运行一次安装脚本。它会把 PyMuPDF 装进 `.venv`，装好 playwright 和 chromium，再用两页测试稿从生成一直跑到 PDF（需要几分钟）。

   macOS / Linux：
   ```bash
   cd ~/.claude/skills/slide-co-create && python3 scripts/setup.py
   ```
   Windows（PowerShell）：
   ```powershell
   cd "$HOME\.claude\skills\slide-co-create"; python scripts\setup.py
   ```
   最后输出 `セットアップ完了`（安装完成）就能用了。测试用 PDF 在 `generated/setup_check/test.pdf`。

   Linux（Debian / Ubuntu）需要先运行 `sudo apt install python3-venv`；如果第 2 步中途提示，再运行 `sudo npx playwright install-deps chromium`。

3. 重启 Claude Code（已经打开的会话不会加载新技能）。

常见问题：

| 现象 | 处理 |
|---|---|
| `No module named 'fitz'` | 还没运行安装脚本，执行第 2 步 |
| `externally-managed-environment`（macOS） | 你在往系统 pip 里装。不要用 `pip install`，用 `setup.py`（它装进 `.venv`） |
| `venv を作れない`（无法创建 venv，Linux） | 运行 `sudo apt install python3-venv` 后重跑 |
| `chromium が起動しない`（chromium 无法启动，Linux） | 运行 `sudo npx playwright install-deps chromium` 后重跑 |
| `Edge / Chrome が見つからない`（找不到 Edge / Chrome） | 重跑 `setup.py`（会装好 chromium）。想用指定浏览器时，把环境变量 `MBB_BROWSER` 设为它的可执行文件路径 |
| 找不到 `npm` | 先安装 Node.js，再重做第 2 步 |
| PDF 里的字体变了 | 技能文件夹被移动过。在新位置用 `new_deck.py` 重新生成幻灯片（内置字体按绝对路径引用） |

## 更新

```bash
cd ~/.claude/skills/slide-co-create && git pull
```
只有 `package.json` 变了时才需要重跑 `setup.py`。

## 使用

在 Claude Code 里说「做个幻灯片」「把这个做成 deck」「スライド作って」之类的话，技能就会启动。也可以用 `/slide-co-create` 直接调用。成品放在 `~/Documents/decks/<项目名>/`。

## 文件说明

| 路径 | 内容 |
|---|---|
| `SKILL.md` | 给 Claude 的指令（技能本体） |
| `references/slide-rules.md` | 幻灯片规则的正本（约 110 条）。和其他文件冲突时以它为准 |
| `references/alignment-and-inputs.md` | Gate A/B 的提问表和蓝图格式 |
| `references/claim-evidence.md` | 主张、依据、呈现方式的对应关系，以及如何选版式 |
| `references/sample-review.md` | 打回样稿的症状清单 |
| `references/archetype-catalog.md` | 62 种版式一览（版式 ID 和适用场景） |
| `references/content-review-prompt.md` | 交给另一个 agent 的评审提示词 |
| `references/ai-smell-lexicon.md` | 要避免的「AI 腔」表达清单 |
| `templates/freeform_parts_16x9.html` | 基础部件库（27 种） |
| `templates/freeform_parts_more_16x9.html` | 扩展部件库（35 种） |
| `templates/skin.css` | 决定配色、字体、封面、页脚的皮肤（不含 logo 和版权声明） |
| `scripts/new_deck.py` | 按部件编号生成幻灯片 HTML |
| `scripts/check_deck.py` | 规则自动检查（标题长度、底部色带的类名、残留占位符等） |
| `scripts/check_layout.mjs` | 实际渲染检查（重叠、溢出、底部色带、字号） |
| `scripts/render_pdf.py` | 把 HTML 导出为 PDF 和逐页 PNG（供目视检查） |
| `scripts/setup.py` | 首次安装（`.venv`、playwright、自检） |
| `assets/` | 版式目录 PDF、PPTX 样本、内置字体（Noto Sans JP，OFL） |

## 改成自己公司的样式

- 配色、字体、页脚文字只改 `templates/skin.css`。默认不含 logo 和版权声明；要加自家的，启用 `skin.css` 末尾注释里的示例并改值。
- 评审中收到的意见，一条一行加到 `references/slide-rules.md`（第 9 步时 Claude 会给出候选）。团队共用时，各自本地加的规则别人看不到；希望对所有人生效的规则，请开分支提 Pull Request。
- 想改部件库的 CSS 时，先在该幻灯片自己的 `<style>` 里覆盖。如果这个改动对所有幻灯片都适用，再同步改到 `templates/`。
