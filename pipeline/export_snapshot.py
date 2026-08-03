# -*- coding: utf-8 -*-
"""读取三科 00-最新状况.md 的「看板数据」「任务池候选」YAML 块，组装看板快照 JSON。
这是「Obsidian 单一事实源 -> 小程序派生视图」的核心转换层。
依赖：pip install pyyaml requests
"""
import os
import re
import json
import datetime

try:
    import yaml
except ImportError:
    raise SystemExit("请先安装依赖：pip install pyyaml requests")

SUBJECTS = {
    "english": ("D:/Obsidian/伊菲英语学习管理/00-最新状况.md", "英语"),
    "math": ("D:/Obsidian/伊菲数学学习管理/00-最新状况.md", "数学"),
    "chinese": ("D:/Obsidian/伊菲语文学习管理/00-最新状况.md", "语文"),
}


def read_block(md_path, header):
    text = open(md_path, encoding="utf-8").read()
    m = re.search(r"^##\s*" + re.escape(header) + r"\s*$(.*?)(?=^##\s|\Z)",
                  text, re.S | re.M)
    if not m:
        return None
    return m.group(1)


def parse_block(block):
    if not block:
        return None
    lines = [l for l in block.splitlines() if not l.strip().startswith("#")]
    clean = "\n".join(lines).strip()
    if not clean:
        return None
    return yaml.safe_load(clean)


def color_of(mp):
    if mp is None:
        return "gray"
    if mp > 0.8:
        return "green"
    if mp >= 0.5:
        return "blue"
    return "yellow"


def build():
    subjects = []
    task_pool = {"updated_at": datetime.datetime.now().astimezone().isoformat()}
    pred_each = {}
    mastery_vals = []

    for key, (path, name) in SUBJECTS.items():
        d = parse_block(read_block(path, "看板数据"))
        if not d:
            subjects.append({
                "key": key, "name": name, "status": "pending",
                "mastery_pct": None, "color": "gray", "weak_count": 0,
                "predicted_score_150": None, "key_hint": "待评估·未上传",
                "points": [], "untested": []
            })
            task_pool[key] = []
            continue

        pts = d.get("points") or []
        if not isinstance(pts, list):
            pts = []
        weak = sum(1 for p in pts if isinstance(p, dict) and p.get("status") in ("red", "yellow"))
        mp = d.get("mastery_pct")
        if mp is not None:
            mastery_vals.append(float(mp))
        pred = d.get("predicted_score_150")
        pred_each[name] = pred

        subjects.append({
            "key": key, "name": name, "status": "active",
            "mastery_pct": mp, "color": color_of(mp), "weak_count": weak,
            "predicted_score_150": pred, "key_hint": d.get("key_hint", ""),
            "points": [p for p in pts if isinstance(p, dict)],
            "untested": d.get("untested") or []
        })

        tp = parse_block(read_block(path, "任务池候选"))
        task_pool[key] = tp if isinstance(tp, list) else []

    avg = round(sum(mastery_vals) / len(mastery_vals), 3) if mastery_vals else None
    summary = {
        "subjects_scored_total": 450,
        "mastery_pct": avg,
        "predicted_score_150_each": pred_each,
        "untested_300_note": "中考750中综合/道法/历史/体育等300分待测≠0分",
        "known_future_subjects": ["物理", "化学", "道法", "历史", "体育", "跨学科"]
    }

    return {
        "generated_at": datetime.datetime.now().astimezone().isoformat(),
        "data_as_of": datetime.date.today().isoformat(),
        "evidence_level_note": "🟢真题/🟡样卷/🔴未测 仅后台记录",
        "summary": summary,
        "subjects": subjects,
        "task_pool": task_pool
    }


if __name__ == "__main__":
    out = build()
    out_path = os.path.join(os.path.dirname(__file__), "snapshot.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("snapshot written ->", out_path)
