# 伊菲学习管理系统 · 微信小程序

家长 / 孩子手机端 3 功能：**掌握情况** / **今日任务** / **上传作业**。所有管理、配置、分析维护全在后台（AI 自动处理），不进小程序。

- 方案定稿：见 Obsidian `伊菲学习管理/学习看板方案_v1.6.md`
- 数据契约：见 `docs/数据契约.md`

## 一、目录结构

```
yifei-miniprogram/
├── app.json / app.js / app.wxss      小程序入口、tabBar（3 功能）
├── project.config.json               项目配置（需填 AppID）
├── pages/
│   ├── mastery/index   掌握情况·科目列表
│   ├── mastery/detail  掌握情况·单科详情
│   ├── tasks           今日任务·勾选生成+打印
│   └── upload          上传作业·仅照片+轻纠错
├── cloudfunctions/
│   ├── upload          登记图片（仅照片，拒收视频）
│   ├── getSnapshot     读快照
│   ├── drawTask        任务池抽卡
│   ├── getUploads      读上传记录
│   ├── correctSubject  纠正学科误判
│   └── getAssets       读云存储题库/汇报（内容实时更新，无需重发小程序）
├── pipeline/           本地 WorkBuddy 管道（分析+导出+推送）
│   ├── init_subject_blocks.py  初始化 Obsidian YAML 契约块
│   ├── export_snapshot.py      Obsidian -> 快照 JSON
│   ├── cloud_sync.py           云库同步 + 云存储清理
│   ├── on_connect.py           上线即处理主链路
│   ├── task_pool.py            任务池辅助
│   └── config.sample.json      配置模板（复制为 config.json）
└── docs/数据契约.md
```

## 二、上线前准备（你侧）

1. 微信公众平台注册小程序账号（主体实名/人脸），获取 **AppID**。
2. 微信开发者工具开通**云开发**，获取 **环境 ID**。
3. 把 `project.config.json` 的 `appid` 改成你的 AppID；`app.js` 的 `envId` 改成环境 ID。
4. 右键 `cloudfunctions/` 下每个函数「上传并部署（云端安装依赖）」。
5. 在云开发控制台建两个集合：`snapshot`（插入一条 `_id: current` 的空文档）、`uploads`。
6. **题库/汇报内容（云存储下发）**：在云存储建 `assets/` 目录，上传 `questionbank.json` 与 `reports.json`；在数据库建 `assets` 集合并插入 `_id: assets_meta` 文档，含 `qb`/`rp` 两个 fileID 字段指向上述两个文件。小程序启动即经 `getAssets` 拉取并缓存；**后续只改云存储文件即可实时更新内容，无需重新发布小程序**（根目录 `questionbank.js`/`reports.js` 仅为联网失败时的离线兜底）。
7. 本地管道：`pipeline/config.sample.json` 复制为 `config.json`，填 `appid/secret/env`，`dry_run` 设 false。
   - `secret` = 公众平台「开发管理-开发设置-开发者密码(AppSecret)」；仅留本地，绝不入 git。

## 三、本地管道（AI 维护用）

```bash
pip install pyyaml requests
python pipeline/export_snapshot.py          # 试导出 snapshot.json（dry 校验）
python pipeline/on_connect.py               # 上线即处理主链路（需 config.json）
python pipeline/task_pool.py                # 打印各科目待出卡片数
```

> 真实图像分析由 WorkBuddy 自动化注入 `analyze_image` 回调（读图+归因）；`on_connect.py` 负责编排、相关性初筛与云端原图清理。

## 四、版本管理

- 代码用 Git 管理（本仓库）。Obsidian 是数据唯一事实源（其自身可开启同步）。
- 连接 GitHub 远程（拿到你的仓库 URL 后）：
  ```bash
  git remote add origin <你的GitHub仓库URL>
  git push -u origin main
  ```
- 敏感文件（`pipeline/config.json`、`project.private.config.json`）已在 `.gitignore` 中，不会上传。

## 五、纪律（后台，家长无需关心）

- 仅照片上传；视频入口即拒收。
- **非作业内容（生活照/截图/表情包）：直接删除云端原图 + 本地不留**，不分析、不污染数据。
- **作业照片：分析（学科判别+归因+写 Obsidian）完成后，删除云端原图、仅本地归档**（`archive_inbox/`，已被 `.gitignore`，不进 git）；删除前确认本地已落档。
- 上述「删云端、留本地 / 非作业全删」由 `pipeline/on_connect.py` 自动化执行；AI 交互分析时同样遵守。
- 待测板块标「待测」不假装 0 分；副科未上传不假装 0 分。
