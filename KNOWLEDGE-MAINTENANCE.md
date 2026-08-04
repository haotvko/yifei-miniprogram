# KNOWLEDGE-MAINTENANCE.md — 知识库 / 作业分析 / 题库任务维护（智能体接手）

> 本文是仓库内交接文档，专给负责「知识库收集整理 + 上传作业分析 + 小程序题库/任务维护」的智能体。
> 完整版（含 Obsidian Vault 清单、铁律全文）见 Obsidian `伊菲学习管理/12-知识库维护与作业分析交接.md`（本机 `D:\Obsidian\`）。
> 整体项目交接见 `HANDOFF.md`；部署见 `11-看板与项目交接手册.md`。

---

## 1. 你的 4 项职责

1. **知识库收集/整理**：Obsidian 知识库 vault（英语知识点库、提分蒸馏包、高分经验、校准总源、三科考点地图、价值排序）。
2. **现有材料理解**：读懂上述材料，作为一切动作依据（所有要求以上海为准）。
3. **上传作业分析**：读图归因 → 写回 `uploads` + 回流 Obsidian 台账 + 维护任务池。
4. **题库与任务维护**：`questionbank.js` / `reports.js` 题库、`snapshot.task_pool` 任务卡。

你**不改小程序页面代码**（那是代码维护角色的事），但你的维护结果通过云端直接驱动 App。

## 2. 知识库材料（收集整理的标的）

| 材料 | 路径（Obsidian） |
|---|---|
| 英语知识点库 | `上海初中英语知识库/`（MOC：`知识库主页(MOC)`，⚠️现行卷口径，引用以改革卷为准） |
| 提分蒸馏包 | `上海初中高分经验蒸馏/伊菲提分系统蒸馏/`（`00-MOC`+`01-方法论`+`02-三科价值排序`+`03-校准误读`） |
| 通用高分经验 | `上海初中高分经验蒸馏/`（语文_/数学_/英语_高分笔记与经验、通用_方法与习惯） |
| 校准总源（标准尺） | `伊菲学习管理/08-上海中考各学科具体要求校准` |
| 三科考点地图 | `伊菲英语学习管理/01-考点地图-改革卷`、`伊菲语文学习管理/01-考点地图`、`伊菲数学学习管理/01-考点地图` |
| 三科价值排序 | 各中枢《中考{科}价值排序》 |
| 交付规范 | `伊菲英语学习管理/06-今日内容交付规范` |

收集纪律（铁律 3.5）：必须**上海专属**；来源量足够大才蒸馏，禁少量样本草率定论；证据 🔵官方 / 🟡机构 / 🟢模拟卷 / 🔴网传(剔除)。

## 3. 上传作业分析 SOP（核心）

- **触发**：用户小程序上传 → `upload` 云函数写 `uploads` 集合 `status=pending`（含 `fileID`）。
- **分析（你做）**：读 `pending` 图 → 逐题归因：① 识别科目(语/数/英) ② 每题对错归类到该科考点 `point`（**键名须与 `snapshot.points`/`questionbank` 完全一致**）③ 提取真实错因（落笔内容，不猜）。非作业图 → `rejected_irrelevant`。
- **写回**：`uploads` 标 `done`；Obsidian 对应中枢更新 `02-台账`/`00-最新状况` + `03-提交记录`；回流 `task_pool` 候选。
- **图片纪律**：非作业→云端+本地都删；作业→落档 `archive_inbox/` + 删云端留本地。
- **数据纪律**：唯一信息渠道=真实作业落笔；上海专属；掌握度闭环验证（后续用对→掌握，用错→未掌握回流）。

## 4. 题库维护 SOP

- 文件：`questionbank.js`（源 `pipeline/build_questionbank.py`）：`questionbank[subjectKey][point]=[{q,options,answer,explain}]`，11考点/667题/每项≥50。`reports.js`：11考点 `{summary,score_origin,stats{total,correct,wrong},breakdown[],strengths[],next_step}`。
- 云端化：`questionbank.json`+`reports.json` 上传云存储 `assets/` → `getAssets` 下发（实时生效，不必重发）。
- 维护：新增考点/题型 → 改 `build_questionbank.py` → 重生成 `.js` → 同步 `.json` → 传 `assets/`。`reports` 的 `stats/score_origin/breakdown/next_step` 每次分析后更新。
- **键名对齐**：`point` 必须与 `snapshot.points` 一致（否则今日任务抽不到题）。
- 纪律：题库是练习材料库，**不碰掌握度事实源**；数学用 `^` 记号、纯 ASCII；外部基准须真题/官方口径。

## 5. 任务维护 SOP

- 数据：`snapshot.task_pool[subjectKey]`（本地兜底 `taskpool.js`）：`{id,type,title,roi,card:{title,point,rule,how,why},delivered_at}`；`word` 卡含 `word_from/word_to/ipa/collocation`（⚠️ `ipa` 非 GBK，`taskpool.js` 已丢弃）。
- 生成（铁律 3.2/3.6/3.8）：内容只来自 `02-台账`「下一刀候选」→ 按「频率×未覆盖×确定性」选最高 ROI 最小任务 → **过独立专家评审** → 出卡前先读 `04-任务卡/` 确认不重复 → 每任务双来源（主任务错题提炼 + 今日单词(英)/单点(语数)，非简单高频词）→ 格式：大字卡片+规则+短句怎么学+一句为什么；单词 中文+音标+1搭配。
- 维护：每次作业分析后回流候选；走掌握度闭环验证。

## 6. 🔴 GBK 纪律（最高频坑）

代码包内 `js/wxml/wxss/json`（含 `questionbank.js`/`reports.js`/`taskpool.js`/`pages/`/`cloudfunctions/`）**禁任何 emoji 及非 GBK 符号**。

- 数学用 `^`（`x^2` `a^3` `a^-n`），禁上标 ²³⁴⁵、禁特殊减号 −(U+2212)。
- 勾选 `●`，不用 ✓；装饰用 `【】`/CSS，不用 📊🎯📌 等 emoji。
- GBK 安全：`→ ← ＋ · （）「」【】`。
- 黑名单：`✅ ✓ 🎯 📊 🔍 🚨 📚 👋 › ▾ − • ²³⁴⁵⁶⁰ ⁻ ⁿ`。
- 生成/提交前必做：全量 GBK 扫描（`ch.encode('gbk')` 逐字符）+ `node --check`。

## 7. 数据刷新链路

```
Obsidian 00-最新状况.md → export_snapshot.py → snapshot.json → seed_db.js(部署机 tcb) → 云端 snapshot → App
questionbank.json + reports.json → 云存储 assets/ → getAssets → App（实时）
```

⚠️ 本工作区 Bash 跑 `tcb` 报 EPERM，**云端刷新须在部署机（`tcb login --flow device`）执行**。

## 8. 坑点速查

| 现象 | 处理 |
|---|---|
| 今日任务抽不到题 / 汇报空白 | `point` 键名与 `snapshot.points` 不一致 → 统一 |
| 代码包乱码 | 非 GBK 字符 → 见第 6 节 |
| 分析完数据不更新 | 未写回 Obsidian / 未跑 export+seed |
| 题库改了 App 仍旧 | 没传云存储 `assets/` |
| 任务卡同词重发 | 出卡前未读 `04-任务卡/` → 违反铁律 3.1⑤ |
| 汇报页白屏 | `report.js` require 路径少一级（三层目录需 `../../../reports.js`） |
| `tcb` EPERM | 本环境限制，部署机执行 |

## 9. 待办 / 未决

- 真实 `analyze_image` 归因由 WorkBuddy 自动化注入，新作业需跑归因→写 `uploads`→回流台账。
- 一张非作业图（`uploads/1785808801307-483284.jpg`，`_id: 3cbc26e26a7147aa046b6a273811c00c`）待确认是否标 `rejected_irrelevant`。
- 详情页「6-8 项维度清单」需求待用户确认（当前英语5/数学6）。
- 本地 `.git/index` stale，需用户 `git reset`。

## 10. 接手第一步

1. 按 Obsidian 权威版第 2 节顺序读懂材料（重点 `08-校准`+蒸馏 01/02/03+`06-规范`）。
2. 跑一次样例分析：取待分析作业图 → 归因 → 写 `uploads` + Obsidian 台账 → 回流 `task_pool`。
3. 维护题库/任务严守 GBK 纪律（第 6 节）、任务流程（第 5 节）、键名对齐（第 4 节）。
4. 改动后按第 7 节刷新（云端须在部署机）；代码提交约定见 `HANDOFF.md` 第 6 节。
