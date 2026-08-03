# pipeline · 本地 WorkBuddy 管道

连接「微信云开发」与「Obsidian 单一事实源」的后台编排层。由 WorkBuddy 自动化在
「连接/上线」时调用（最高优先级），也支持每日定时与对话即时触发。

## 模块职责

| 文件 | 职责 |
|---|---|
| `init_subject_blocks.py` | 幂等初始化三科 `00-最新状况.md` 的 `## 看板数据` / `## 任务池候选` YAML 块 |
| `export_snapshot.py` | 解析 YAML 块 -> 组装 `snapshot.json`（看板快照契约） |
| `cloud_sync.py` | 云数据库/云存储 HTTP API 封装：推快照、拉 pending、改状态、下载/删除原图 |
| `on_connect.py` | 上线即处理主链路：拉图 -> 初筛 -> 分析落档 -> 更新 -> 删云端原图 -> 推快照 |
| `task_pool.py` | 任务池辅助：重置 delivered_at、打印待出数 |

## 快速验证（dry-run，无需凭证）

```bash
pip install pyyaml requests
python export_snapshot.py     # 生成 snapshot.json，校验 YAML 解析与组装
```

## 真实运行（需 config.json）

```bash
cp config.sample.json config.json   # 填 appid/secret/env，dry_run=false
python on_connect.py                # 拉取云端 pending -> 处理 -> 推快照
```

## 关键约定

- `config.json` 含 AppSecret，**仅留本地**，已被 `.gitignore` 忽略。
- 云端原图删除**仅**在「本地落档确认 + Obsidian 写入完成 + 快照推送成功」后执行；否则保留云端原图标 `pending/retry`。
- 相关性初筛（v1.6）：`analyze_image` 回调返回 `is_homework=False` 即标 `rejected_irrelevant` 并删云端原图，不写 Obsidian、不进任务池。
- 真实 AI 分析（逐题归因 + 学科判别 + 任务池 ROI 排序）由 WorkBuddy 自动化注入回调完成。
