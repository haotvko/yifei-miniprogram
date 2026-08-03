# -*- coding: utf-8 -*-
"""上线即处理主链路（由 WorkBuddy 自动化在「连接/上线」时调用，最高优先级）。

流程：
  1. 拉取云端 uploads 表所有 pending 图（v1.5 最高优先级动作）
  2. 逐张下载到本地临时文件
  3. 相关性初筛（v1.6）：调用 analyze_image 回调判定是否「作业照片」
       - 否 -> 标 rejected_irrelevant + 删除云端原图，不分析、不写 Obsidian
  4. 是作业 -> 本地落档（archive_dir）-> 由 analyze_image 完成学科判别+归因+写 Obsidian
       -> 回填 subject -> 标 done -> 删除云端原图（本地已落档）
  5. 全部处理完 -> export_snapshot 组装快照 -> push_snapshot 推云库

真实图像分析由 analyze_image 回调注入（WorkBuddy 自动化用 Read 工具读图 + 归因逻辑）。
本文件只负责 I/O 编排、相关性分支与云存储清理。
"""
import os
import json
import tempfile

try:
    import requests
except ImportError:
    requests = None

from export_snapshot import build
from cloud_sync import CloudSync
from task_pool import reset_delivered


def default_analyze(file_path):
    # 兜底占位：生产环境必须由 WorkBuddy 自动化注入真实 analyze_image
    return {"is_homework": True, "subject": None, "note": "mock-analyze"}


def run(sync, analyze_image=default_analyze, archive_dir=None, subjects_to_reset=None):
    archive_dir = archive_dir or os.path.join(os.path.dirname(__file__), "..", "archive_inbox")
    os.makedirs(archive_dir, exist_ok=True)

    pending = (sync.pull_pending().get("data") or [])
    print(f"[on_connect] pending 数量: {len(pending)}")

    for item in pending:
        doc_id = item.get("_id") or item.get("id")
        fileID = item.get("fileID")
        tmp_path = None
        raw = None

        # 1. 下载
        if fileID and not sync.dry_run and requests is not None:
            raw = sync.download_file(fileID)
            if raw:
                fd, tmp_path = tempfile.mkstemp(suffix=".jpg")
                with os.fdopen(fd, "wb") as f:
                    f.write(raw)

        # 2. 相关性初筛（v1.6：非作业直接删，不分析）
        info = analyze_image(tmp_path) if tmp_path else {"is_homework": True, "subject": None}
        if not info.get("is_homework"):
            sync.set_upload_status(doc_id, "rejected_irrelevant")
            sync.delete_file(fileID)
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
            print(f"[ignore] {doc_id} 非作业内容，已忽略并删除云端原图")
            continue

        # 3. 作业：本地落档
        if tmp_path and os.path.exists(tmp_path):
            dest = os.path.join(archive_dir, os.path.basename(fileID) or (doc_id + ".jpg"))
            os.replace(tmp_path, dest)
            print(f"[archive] {doc_id} -> {dest}")

        # 4. 更新 uploads（subject 由真实分析回填）+ 删云端原图
        sync.set_upload_status(doc_id, "done", {"subject": info.get("subject")})
        sync.delete_file(fileID)
        print(f"[done] {doc_id} 已分析 subject={info.get('subject')}")

    # 5. 导出并推送快照
    snap = build()
    sync.push_snapshot(snap)
    print("[on_connect] 快照已推送")

    # 6. AI 在线重整任务池（此处仅重置已交付标记；真实 ROI 排序由 AI 编辑「任务池候选」块完成）
    for s in (subjects_to_reset or []):
        reset_delivered(s)

    return snap


if __name__ == "__main__":
    import sys
    cfg_path = os.path.join(os.path.dirname(__file__), "config.json")
    if not os.path.exists(cfg_path):
        print("未找到 config.json，请由 config.sample.json 复制并填值（或保持 dry_run）。")
        sys.exit(1)
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    sync = CloudSync(cfg["appid"], cfg["secret"], cfg["env"], dry_run=cfg.get("dry_run", False))
    run(sync, archive_dir=cfg.get("archive_dir"), subjects_to_reset=["english", "math", "chinese"])
